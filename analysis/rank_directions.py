#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频方向筛选脚本
- 读取 data/feedback.csv
- 按 taxonomy/tags.yml 自动打标
- 输出 Top15 方向到 reports/top_directions.md
"""

import csv
import yaml
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

DATA_PATH = Path("data/feedback.csv")
TAXONOMY_PATH = Path("taxonomy/tags.yml")
OUTPUT_PATH = Path("reports/top_directions.md")

def load_taxonomy():
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_feedback():
    rows = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def tag_feedback(rows, taxonomy):
    """按关键词自动打标（简单匹配，可扩展）"""
    directions = taxonomy.get("directions", {})
    for row in rows:
        text = (row.get("text", "") + " " + row.get("tags", "")).lower()
        matched = []
        for dir_key, dir_meta in directions.items():
            for kw in dir_meta.get("keywords", []):
                if kw.lower() in text:
                    matched.append(dir_key)
                    break
        row["_auto_tags"] = list(set(matched))
    return rows

def rank_directions(rows):
    """按出现频次排序方向"""
    counter = Counter()
    for row in rows:
        for tag in row.get("_auto_tags", []):
            counter[tag] += 1
    return counter.most_common(15)

def render_report(top15, rows, taxonomy):
    lines = []
    lines.append("# Top15 高频方向报告")
    lines.append(f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n总需求数：{len(rows)} 条")
    lines.append("\n---\n")

    for idx, (dir_key, count) in enumerate(top15, 1):
        dir_meta = taxonomy["directions"].get(dir_key, {})
        lines.append(f"## {idx}. {dir_key}")
        lines.append(f"- **需求数**：{count}")
        lines.append(f"- **描述**：{dir_meta.get('description', '无')}")
        lines.append(f"- **风险等级**：{dir_meta.get('risk_level', 'unknown')}")
        lines.append(f"- **是否允许网络**：{dir_meta.get('allow_network', False)}")
        lines.append("\n### 代表需求示例")
        examples = [r for r in rows if dir_key in r.get("_auto_tags", [])][:3]
        for e in examples:
            lines.append(f"- **{e['id']}**：{e['text'][:80]}{'...' if len(e['text'])>80 else ''}  \n  来源：{e['source']} | 频率：{e['frequency']}")
        lines.append("\n---\n")
    return "\n".join(lines)

def main():
    taxonomy = load_taxonomy()
    rows = load_feedback()
    rows = tag_feedback(rows, taxonomy)
    top15 = rank_directions(rows)
    report = render_report(top15, rows, taxonomy)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 报告已生成：{OUTPUT_PATH}")

if __name__ == "__main__":
    main()
