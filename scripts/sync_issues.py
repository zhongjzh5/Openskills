#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync GitHub Issues to data/feedback.csv
- Fetch issues with specified label or [Skill] prefix
- Append to CSV (avoid duplicates)
"""

import os
import csv
import requests
import urllib3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Disable SSL warnings (dev only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # zhongjzh5/Openskills
LABEL = os.getenv("GITHUB_LABEL", "feedback")
CSV_PATH = Path("data/feedback.csv")
API_BASE = f"https://api.github.com/repos/{REPO}"

def get_existing_ids():
    if not CSV_PATH.exists():
        return set()
    ids = set()
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.add(int(row["id"]))
    return ids

def fetch_issues():
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"{API_BASE}/issues?state=all"
    issues = []
    page = 1
    while True:
        resp = requests.get(url + f"&page={page}&per_page=100", headers=headers, verify=False)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        issues.extend(batch)
        page += 1
    return issues

def parse_issue(issue):
    body = issue.get("body", "")
    def extract_field(marker):
        for line in body.split("\n"):
            if line.startswith(f"- **{marker}**"):
                return line.split(":", 1)[-1].strip()
        return ""

    freq_map = {"每天": "daily", "每周": "weekly", "每月": "monthly", "一次性": "once"}
    freq_raw = extract_field("使用频率")
    frequency = freq_map.get(freq_raw, "unknown")

    tags_raw = extract_field("建议标签")
    tags = tags_raw.replace(" ", "") if tags_raw else ""

    votes = issue.get("reactions", {}).get("+1", 0)

    return {
        "id": issue["number"],
        "source": "github_issue",
        "text": issue["title"],
        "created_at": issue["created_at"][:10],
        "frequency": frequency,
        "tags": tags,
        "link": issue["html_url"],
        "votes": votes,
    }

def append_to_csv(rows):
    fieldnames = ["id", "source", "text", "created_at", "frequency", "tags", "link", "votes"]
    write_header = not CSV_PATH.exists()
    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

def main():
    if not TOKEN:
        print("❌ 请设置 GITHUB_TOKEN 到 .env")
        return

    existing_ids = get_existing_ids()
    issues = fetch_issues()
    new_rows = []
    for issue in issues:
        iid = issue["number"]
        if iid in existing_ids:
            continue
        # if issue has feedback or bug label OR title starts with [Skill], treat as valid
        has_label = any(l["name"] in [LABEL, "bug"] for l in issue.get("labels", []))
        has_skill_prefix = issue["title"].startswith("[Skill]")
        if not (has_label or has_skill_prefix):
            continue
        parsed = parse_issue(issue)
        new_rows.append(parsed)
        print(f"✅ 新增 Issue #{iid}: {parsed['text'][:50]}...")

    if not new_rows:
        print("📭 没有新 Issue")
        return

    append_to_csv(new_rows)
    print(f"📄 已追加 {len(new_rows)} 条到 {CSV_PATH}")
    print("🔁 请运行 `python analysis/rank_directions.py` 更新报告")

if __name__ == "__main__":
    main()