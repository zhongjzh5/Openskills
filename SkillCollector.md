# OpenSkills 技能收集系统设计方案

## 一、系统概述

### 1.1 设计目标
为OpenSkills项目高效收集"高频、可重复、可验收"的AI技能，建立结构化的技能数据库，支持后续的技能开发、评估和社区建设。

### 1.2 核心原则
- **自动化优先**：尽可能自动化收集、解析、评估流程
- **多源聚合**：从多个数据源收集技能信息，避免单一来源偏差
- **质量导向**：聚焦"高频、可验收、可封装"的高质量技能
- **可扩展性**：系统设计支持新的数据源和评估维度

### 1.3 系统架构
```
┌─────────────────────────────────────────────────────┐
│                  技能收集系统                        │
├─────────────────────────────────────────────────────┤
│  数据源层       │ 处理层        │ 存储层            │
│  - GitHub      │ - 爬取/解析   │ - 技能数据库      │
│  - SkillHub    │ - 评估打分    │ - 技能目录        │
│  - 社区论坛    │ - 去重合并    │ - 汇总报告        │
│  - 官方市场    │ - 分类标记    │                   │
└─────────────────────────────────────────────────────┘
```

---

## 二、数据源清单与访问方法

### 2.1 主要数据源

#### 2.1.1 GitHub（技能代码仓库）
```yaml
数据源:
  - keyuyuan/skillhub-awesome-skills
  - OpenAI/skills
  - Vercel-labs/agent-skills
  - Microck/ordinary-claude-skills
  - joneqian/claude-skills-suite

访问方法:
  - GitHub REST API v3
  - GitHub GraphQL API
  - 直接爬取README和目录结构

API限制:
  - 认证用户: 5000请求/小时
  - 未认证用户: 60请求/小时
```

#### 2.1.2 SkillHub平台（技能市场）
```yaml
数据源:
  - SkillHub (skillshub.wtf) - 5900+技能
  - SkillHub (skillhub.club) - MCP服务器技能
  - 腾讯SkillHub (skillhub.tencent.com) - 13000+技能

API端点:
  - 搜索: GET https://skillshub.wtf/api/resolve?q={query}
  - 技能详情: GET https://skillshub.wtf/api/skills/{id}
  - 标签筛选: GET https://skillshub.wtf/api/tags/{tag}

认证:
  - API密钥（从开发者控制台获取）
  - 速率限制: 60请求/分钟（读取）
```

#### 2.1.3 社区和论坛
```yaml
数据源:
  - Reddit: r/ClaudeCode, r/AIAgents
  - Discord: Claude社区服务器
  - 知乎: AI助手相关话题
  - CSDN/博客园: 技术博客

访问方法:
  - RSS订阅
  - Web爬虫
  - API接口（如有）
```

#### 2.1.4 官方市场
```yaml
数据源:
  - Claude Code插件市场
  - Cursor技能市场
  - GitHub Copilot扩展市场

访问方法:
  - 官方API（如有）
  - 网页爬取
  - 用户贡献
```

### 2.2 数据收集策略

#### 2.2.1 分层收集
```python
# 优先级层次
PRIORITY_SOURCES = {
    "P0": [
        "skillhub-awesome-skills",  # 精选集合，质量高
        "OpenAI/skills",           # 官方技能，权威性高
        "skillshub.wtf/api"        # 大规模技能市场
    ],
    "P1": [
        "Vercel-labs/agent-skills",
        "GitHub trending skills",
        "社区推荐技能"
    ],
    "P2": [
        "个人仓库技能",
        "未验证社区技能",
        "实验性技能"
    ]
}
```

#### 2.2.2 增量收集
```python
# 增量更新策略
UPDATE_STRATEGY = {
    "高频更新": {
        "sources": ["skillshub.wtf", "GitHub trending"],
        "interval": "daily",
        "method": "增量API查询"
    },
    "定期更新": {
        "sources": ["awesome列表", "官方市场"],
        "interval": "weekly",
        "method": "完整扫描"
    },
    "触发更新": {
        "sources": ["社区推荐", "用户提交"],
        "interval": "on-demand",
        "method": "手动触发"
    }
}
```

---

## 三、技能爬取与解析工具

### 3.1 核心工具设计

#### 3.1.1 统一数据模型
```python
# models/skill.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class SkillMetadata(BaseModel):
    """技能元数据模型"""
    id: str = Field(..., description="技能唯一标识")
    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能功能描述")
    source: str = Field(..., description="数据源")
    source_url: str = Field(..., description="源地址")
    
    # 基础信息
    author: Optional[str] = None
    license: Optional[str] = None
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 技术信息
    language: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    runtime: Optional[str] = None
    
    # 统计信息
    stars: Optional[int] = None
    forks: Optional[int] = None
    downloads: Optional[int] = None
    usage_count: Optional[int] = None
    
    # 分类标签
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    
    # OpenSkills评估维度
    frequency_score: Optional[float] = None  # 高频性
    testability_score: Optional[float] = None  # 可验收性
    feasibility_score: Optional[float] = None  # 可行性
    single_responsibility_score: Optional[float] = None  # 单一职责
    safety_score: Optional[float] = None  # 安全性
    activity_score: Optional[float] = None  # 活跃度
    
    # 原始数据
    raw_data: Dict = Field(default_factory=dict)
```

#### 3.1.2 爬取引擎架构
```python
# crawlers/base_crawler.py
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from typing import List, Dict, Any

class BaseCrawler(ABC):
    """爬取器基类"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = None
        
    @abstractmethod
    async def fetch_skills(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取技能列表"""
        pass
    
    @abstractmethod
    async def fetch_skill_detail(self, skill_id: str) -> Dict[str, Any]:
        """获取技能详情"""
        pass
    
    @abstractmethod
    def parse_skill(self, raw_data: Dict[str, Any]) -> SkillMetadata:
        """解析原始数据为技能元数据"""
        pass

# crawlers/github_crawler.py
class GitHubCrawler(BaseCrawler):
    """GitHub技能爬取器"""
    
    def __init__(self):
        super().__init__("github", "https://api.github.com")
        self.token = os.getenv("GITHUB_TOKEN")
    
    async def fetch_skills(self, limit: int = 100) -> List[Dict[str, Any]]:
        """搜索GitHub上的技能仓库"""
        headers = {"Authorization": f"token {self.token}"} if self.token else {}
        
        # 搜索关键词
        search_queries = [
            "claude skill",
            "ai agent skill",
            "mcp server",
            "openclaw skill",
            "cursor plugin"
        ]
        
        skills = []
        for query in search_queries:
            url = f"{self.base_url}/search/repositories?q={query}&sort=stars&order=desc"
            async with self.session.get(url, headers=headers) as response:
                data = await response.json()
                skills.extend(data.get("items", []))
                
                if len(skills) >= limit:
                    break
        
        return skills[:limit]

# crawlers/skillhub_crawler.py
class SkillHubCrawler(BaseCrawler):
    """SkillHub平台爬取器"""
    
    def __init__(self):
        super().__init__("skillhub", "https://skillshub.wtf/api")
        self.api_key = os.getenv("SKILLHUB_API_KEY")
    
    async def fetch_skills(self, limit: int = 100) -> List[Dict[str, Any]]:
        """从SkillHub API获取技能"""
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        
        # 分页获取技能
        skills = []
        page = 1
        
        while len(skills) < limit:
            url = f"{self.base_url}/skills?page={page}&limit=50"
            async with self.session.get(url, headers=headers) as response:
                data = await response.json()
                if not data:
                    break
                skills.extend(data)
                page += 1
        
        return skills[:limit]
```

### 3.2 解析器设计

#### 3.2.1 SKILL.md解析器
```python
# parsers/skill_md_parser.py
import yaml
import re
from pathlib import Path

class SkillMdParser:
    """解析SKILL.md文件"""
    
    def __init__(self):
        self.frontmatter_pattern = r"^---\n(.*?)\n---\n"
        self.content_pattern = r"^---\n.*?\n---\n(.*)"
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """解析SKILL.md文件"""
        content = file_path.read_text(encoding="utf-8")
        
        # 提取frontmatter
        frontmatter_match = re.search(self.frontmatter_pattern, content, re.DOTALL)
        if frontmatter_match:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
        else:
            frontmatter = {}
        
        # 提取正文内容
        content_match = re.search(self.content_pattern, content, re.DOTALL)
        if content_match:
            main_content = content_match.group(1)
        else:
            main_content = content
        
        # 解析触发条件
        triggers = self._extract_triggers(main_content)
        
        # 解析安全边界
        safety = self._extract_safety(main_content)
        
        return {
            "frontmatter": frontmatter,
            "triggers": triggers,
            "safety": safety,
            "raw_content": content
        }
    
    def _extract_triggers(self, content: str) -> Dict[str, Any]:
        """提取触发条件"""
        triggers = {
            "keywords": [],
            "context_patterns": [],
            "file_types": []
        }
        
        # 搜索关键词模式
        keyword_patterns = [
            r"keywords?:\s*\[(.*?)\]",
            r"触发词[：:]\s*(.*?)\n"
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # 解析数组或逗号分隔列表
                items = re.findall(r'"([^"]+)"|\'([^\']+)\'|([^,\s]+)', match)
                for item in items:
                    keyword = next(filter(None, item), "")
                    if keyword:
                        triggers["keywords"].append(keyword)
        
        return triggers
    
    def _extract_safety(self, content: str) -> Dict[str, Any]:
        """提取安全边界"""
        safety = {
            "forbidden_operations": [],
            "permission_requirements": [],
            "confirmation_required": False
        }
        
        # 查找安全相关部分
        safety_section_pattern = r"#+\s*安全[^#]*?(?=#|$)"
        safety_match = re.search(safety_section_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if safety_match:
            safety_text = safety_match.group(0)
            
            # 查找禁止操作
            forbidden_pattern = r"禁止[：:]\s*(.*?)\n"
            forbidden_match = re.search(forbidden_pattern, safety_text)
            if forbidden_match:
                operations = re.split(r"[，,]", forbidden_match.group(1))
                safety["forbidden_operations"] = [op.strip() for op in operations if op.strip()]
            
            # 查找确认要求
            confirm_pattern = r"需要确认|确认.*?需要"
            if re.search(confirm_pattern, safety_text, re.IGNORECASE):
                safety["confirmation_required"] = True
        
        return safety
```

#### 3.2.2 仓库结构分析器
```python
# parsers/repo_analyzer.py
import os
from pathlib import Path
from typing import List, Dict

class RepoStructureAnalyzer:
    """分析GitHub仓库结构"""
    
    def analyze(self, repo_path: Path) -> Dict[str, Any]:
        """分析仓库结构"""
        structure = {
            "has_skill_md": False,
            "has_scripts": False,
            "has_tests": False,
            "has_docs": False,
            "script_languages": [],
            "dependencies": [],
            "structure_score": 0
        }
        
        # 检查关键文件
        if (repo_path / "SKILL.md").exists():
            structure["has_skill_md"] = True
            structure["structure_score"] += 30
        
        # 检查scripts目录
        scripts_dir = repo_path / "scripts"
        if scripts_dir.exists() and scripts_dir.is_dir():
            structure["has_scripts"] = True
            structure["structure_score"] += 20
            
            # 分析脚本语言
            for script_file in scripts_dir.iterdir():
                if script_file.suffix in [".py", ".js", ".sh", ".ts"]:
                    structure["script_languages"].append(script_file.suffix[1:])
        
        # 检查tests目录
        tests_dir = repo_path / "tests"
        if tests_dir.exists() and tests_dir.is_dir():
            structure["has_tests"] = True
            structure["structure_score"] += 20
        
        # 检查docs目录
        docs_dir = repo_path / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            structure["has_docs"] = True
            structure["structure_score"] += 15
        
        # 检查其他常见文件
        common_files = ["README.md", "requirements.txt", "package.json", "pyproject.toml"]
        for file_name in common_files:
            if (repo_path / file_name).exists():
                structure["structure_score"] += 5
        
        return structure
```

### 3.3 数据处理管道

#### 3.3.1 数据处理流程
```python
# pipelines/skill_pipeline.py
import asyncio
from typing import List
from dataclasses import dataclass
from crawlers import GitHubCrawler, SkillHubCrawler
from parsers import SkillMdParser, RepoStructureAnalyzer
from models import SkillMetadata

@dataclass
class PipelineConfig:
    """管道配置"""
    sources: List[str]
    limit_per_source: int = 100
    enable_parsing: bool = True
    enable_scoring: bool = True
    output_format: str = "json"

class SkillCollectionPipeline:
    """技能收集管道"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.crawlers = self._init_crawlers()
        self.parser = SkillMdParser()
        self.analyzer = RepoStructureAnalyzer()
        self.skills: List[SkillMetadata] = []
    
    def _init_crawlers(self) -> Dict[str, BaseCrawler]:
        """初始化爬取器"""
        crawlers = {}
        
        if "github" in self.config.sources:
            crawlers["github"] = GitHubCrawler()
        
        if "skillhub" in self.config.sources:
            crawlers["skillhub"] = SkillHubCrawler()
        
        return crawlers
    
    async def run(self) -> List[SkillMetadata]:
        """运行收集管道"""
        tasks = []
        
        # 并行收集所有数据源
        for name, crawler in self.crawlers.items():
            task = asyncio.create_task(
                self._collect_from_source(name, crawler)
            )
            tasks.append(task)
        
        # 等待所有收集任务完成
        results = await asyncio.gather(*tasks)
        
        # 合并结果
        for result in results:
            self.skills.extend(result)
        
        # 去重处理
        self.skills = self._deduplicate_skills(self.skills)
        
        # 解析和评估（如果启用）
        if self.config.enable_parsing:
            self.skills = await self._parse_skills(self.skills)
        
        if self.config.enable_scoring:
            self.skills = await self._score_skills(self.skills)
        
        return self.skills
    
    async def _collect_from_source(self, source_name: str, crawler: BaseCrawler) -> List[SkillMetadata]:
        """从单个数据源收集"""
        print(f"开始从 {source_name} 收集技能...")
        
        try:
            # 获取原始数据
            raw_skills = await crawler.fetch_skills(self.config.limit_per_source)
            
            # 转换为标准模型
            skills = []
            for raw_skill in raw_skills:
                try:
                    skill = crawler.parse_skill(raw_skill)
                    skills.append(skill)
                except Exception as e:
                    print(f"解析技能失败: {e}")
            
            print(f"从 {source_name} 收集到 {len(skills)} 个技能")
            return skills
            
        except Exception as e:
            print(f"从 {source_name} 收集失败: {e}")
            return []
    
    def _deduplicate_skills(self, skills: List[SkillMetadata]) -> List[SkillMetadata]:
        """去重技能"""
        seen = set()
        deduplicated = []
        
        for skill in skills:
            # 基于名称和描述创建唯一标识
            skill_key = f"{skill.name}_{skill.description[:50]}"
            
            if skill_key not in seen:
                seen.add(skill_key)
                deduplicated.append(skill)
        
        return deduplicated
```

---

## 四、技能评估与打分系统

### 4.1 评估维度定义

#### 4.1.1 OpenSkills核心评估维度
```python
# evaluators/base_evaluator.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from models import SkillMetadata

class BaseEvaluator(ABC):
    """评估器基类"""
    
    def __init__(self, weight: float = 1.0):
        self.weight = weight
    
    @abstractmethod
    async def evaluate(self, skill: SkillMetadata) -> float:
        """评估技能并返回分数（0-5）"""
        pass
    
    @abstractmethod
    def get_criteria(self) -> Dict[str, Any]:
        """返回评估标准说明"""
        pass

# evaluators/frequency_evaluator.py
class FrequencyEvaluator(BaseEvaluator):
    """高频性评估器"""
    
    def __init__(self):
        super().__init__(weight=1.2)  # 高频性权重较高
    
    async def evaluate(self, skill: SkillMetadata) -> float:
        """评估使用频率"""
        score = 0.0
        
        # 基于GitHub stars
        if skill.stars:
            if skill.stars > 1000:
                score += 2.0
            elif skill.stars > 100:
                score += 1.0
        
        # 基于下载量/使用量
        if skill.downloads:
            if skill.downloads > 10000:
                score += 2.0
            elif skill.downloads > 1000:
                score += 1.0
        
        # 基于更新频率
        if skill.updated_at:
            days_since_update = (datetime.now() - skill.updated_at).days
            if days_since_update < 30:
                score += 1.0
            elif days_since_update < 90:
                score += 0.5
        
        return min(score, 5.0)  # 限制在0-5分
    
    def get_criteria(self) -> Dict[str, Any]:
        return {
            "name": "高频性评估",
            "description": "评估技能的使用频率和流行度",
            "metrics": ["GitHub stars", "下载量", "更新频率"],
            "weight": self.weight
        }

# evaluators/testability_evaluator.py
class TestabilityEvaluator(BaseEvaluator):
    """可验收性评估器"""
    
    def __init__(self):
        super().__init__(weight=1.1)
    
    async def evaluate(self, skill: SkillMetadata) -> float:
        """评估可测试性和验收性"""
        score = 0.0
        
        # 检查是否有测试
        if "has_tests" in skill.raw_data and skill.raw_data["has_tests"]:
            score += 2.0
        
        # 检查是否有清晰的输入输出定义
        if skill.raw_data.get("interfaces"):
            score += 1.5
        
        # 检查是否有使用示例
        if skill.raw_data.get("examples"):
            score += 1.0
        
        # 检查是否有明确的成功标准
        if "success_criteria" in skill.raw_data:
            score += 0.5
        
        return min(score, 5.0)
```

#### 4.1.2 完整评估器集合
```python
# evaluators/registry.py
from typing import Dict, Type
from evaluators import (
    FrequencyEvaluator, TestabilityEvaluator, FeasibilityEvaluator,
    SingleResponsibilityEvaluator, SafetyEvaluator, ActivityEvaluator
)

class EvaluatorRegistry:
    """评估器注册表"""
    
    def __init__(self):
        self.evaluators: Dict[str, BaseEvaluator] = {}
        self._register_default_evaluators()
    
    def _register_default_evaluators(self):
        """注册默认评估器"""
        self.register("frequency", FrequencyEvaluator())
        self.register("testability", TestabilityEvaluator())
        self.register("feasibility", FeasibilityEvaluator())
        self.register("single_responsibility", SingleResponsibilityEvaluator())
        self.register("safety", SafetyEvaluator())
        self.register("activity", ActivityEvaluator())
    
    def register(self, name: str, evaluator: BaseEvaluator):
        """注册评估器"""
        self.evaluators[name] = evaluator
    
    def get_evaluator(self, name: str) -> BaseEvaluator:
        """获取评估器"""
        return self.evaluators.get(name)
    
    def get_all_evaluators(self) -> Dict[str, BaseEvaluator]:
        """获取所有评估器"""
        return self.evaluators.copy()
```

### 4.2 打分算法

#### 4.2.1 综合评分算法
```python
# scoring/weighted_scorer.py
from typing import List, Dict
from models import SkillMetadata
from evaluators import EvaluatorRegistry

class WeightedScorer:
    """加权评分器"""
    
    def __init__(self, evaluator_registry: EvaluatorRegistry):
        self.evaluator_registry = evaluator_registry
    
    async def score_skill(self, skill: SkillMetadata) -> Dict[str, float]:
        """为技能打分"""
        scores = {}
        total_weight = 0.0
        weighted_sum = 0.0
        
        # 运行所有评估器
        evaluators = self.evaluator_registry.get_all_evaluators()
        
        for name, evaluator in evaluators.items():
            try:
                score = await evaluator.evaluate(skill)
                scores[name] = score
                
                # 计算加权总分
                weighted_sum += score * evaluator.weight
                total_weight += evaluator.weight
                
            except Exception as e:
                print(f"评估器 {name} 失败: {e}")
                scores[name] = 0.0
        
        # 计算加权平均分
        if total_weight > 0:
            weighted_average = weighted_sum / total_weight
        else:
            weighted_average = 0.0
        
        scores["weighted_average"] = weighted_average
        
        # 更新技能对象
        skill.frequency_score = scores.get("frequency", 0)
        skill.testability_score = scores.get("testability", 0)
        skill.feasibility_score = scores.get("feasibility", 0)
        skill.single_responsibility_score = scores.get("single_responsibility", 0)
        skill.safety_score = scores.get("safety", 0)
        skill.activity_score = scores.get("activity", 0)
        
        return scores
```

#### 4.2.2 优先级分类算法
```python
# scoring/priority_classifier.py
from typing import List, Dict
from models import SkillMetadata

class PriorityClassifier:
    """优先级分类器"""
    
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or {
            "p0_threshold": 4.0,  # P0: 立即开发
            "p1_threshold": 3.0,  # P1: 第二批开发
            "p2_threshold": 2.0   # P2: 考虑开发
        }
    
    def classify(self, skill: SkillMetadata) -> str:
        """分类技能优先级"""
        weighted_score = self._calculate_final_score(skill)
        
        if weighted_score >= self.thresholds["p0_threshold"]:
            return "P0"
        elif weighted_score >= self.thresholds["p1_threshold"]:
            return "P1"
        elif weighted_score >= self.thresholds["p2_threshold"]:
            return "P2"
        else:
            return "P3"  # 暂不开发
    
    def _calculate_final_score(self, skill: SkillMetadata) -> float:
        """计算最终分数"""
        scores = [
            (skill.frequency_score or 0) * 1.2,
            (skill.testability_score or 0) * 1.1,
            (skill.feasibility_score or 0) * 1.0,
            (skill.single_responsibility_score or 0) * 0.9,
            (skill.safety_score or 0) * 1.3,  # 安全性权重高
            (skill.activity_score or 0) * 1.0
        ]
        
        total_weight = 1.2 + 1.1 + 1.0 + 0.9 + 1.3 + 1.0
        weighted_sum = sum(scores)
        
        return weighted_sum / total_weight
```

---

## 五、技能数据库与汇总报告

### 5.1 数据库设计

#### 5.1.1 SQLite数据库模式
```sql
-- database/schema.sql
-- 技能主表
CREATE TABLE skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    source TEXT NOT NULL,
    source_url TEXT,
    
    -- 基础信息
    author TEXT,
    license TEXT,
    version TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- 技术信息
    language TEXT,
    runtime TEXT,
    
    -- 统计信息
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    
    -- 评估分数
    frequency_score REAL,
    testability_score REAL,
    feasibility_score REAL,
    single_responsibility_score REAL,
    safety_score REAL,
    activity_score REAL,
    weighted_score REAL,
    
    -- 分类信息
    priority TEXT DEFAULT 'P3',
    status TEXT DEFAULT 'collected',
    
    -- 元数据
    raw_data TEXT,  -- JSON格式原始数据
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT
);

-- 技能-标签关联表
CREATE TABLE skill_tags (
    skill_id TEXT,
    tag_id INTEGER,
    PRIMARY KEY (skill_id, tag_id),
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- 数据源表
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    url TEXT,
    last_collected TIMESTAMP,
    skill_count INTEGER DEFAULT 0
);

-- 收集日志表
CREATE TABLE collection_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    skills_collected INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    error_message TEXT,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
```

#### 5.1.2 数据库操作类
```python
# database/skill_repository.py
import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import SkillMetadata

class SkillRepository:
    """技能数据库仓库"""
    
    def __init__(self, db_path: str = "skills.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 读取schema文件并执行
            with open("database/schema.sql", "r") as f:
                schema = f.read()
            
            conn.executescript(schema)
            conn.commit()
    
    def save_skill(self, skill: SkillMetadata) -> bool:
        """保存技能到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查是否已存在
                cursor.execute("SELECT id FROM skills WHERE id = ?", (skill.id,))
                exists = cursor.fetchone()
                
                if exists:
                    # 更新现有记录
                    query = """
                    UPDATE skills SET
                        name = ?, description = ?, source = ?, source_url = ?,
                        author = ?, license = ?, version = ?,
                        created_at = ?, updated_at = ?,
                        language = ?, runtime = ?,
                        stars = ?, forks = ?, downloads = ?, usage_count = ?,
                        frequency_score = ?, testability_score = ?, feasibility_score = ?,
                        single_responsibility_score = ?, safety_score = ?, activity_score = ?,
                        weighted_score = ?, priority = ?, status = ?,
                        raw_data = ?, updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """
                else:
                    # 插入新记录
                    query = """
                    INSERT INTO skills (
                        id, name, description, source, source_url,
                        author, license, version, created_at, updated_at,
                        language, runtime,
                        stars, forks, downloads, usage_count,
                        frequency_score, testability_score, feasibility_score,
                        single_responsibility_score, safety_score, activity_score,
                        weighted_score, priority, status, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                
                # 准备数据
                raw_data_json = json.dumps(skill.raw_data) if skill.raw_data else "{}"
                
                # 计算加权分数
                weighted_score = self._calculate_weighted_score(skill)
                
                # 执行查询
                cursor.execute(query, (
                    skill.id, skill.name, skill.description, skill.source, skill.source_url,
                    skill.author, skill.license, skill.version,
                    skill.created_at.isoformat() if skill.created_at else None,
                    skill.updated_at.isoformat() if skill.updated_at else None,
                    skill.language, skill.runtime,
                    skill.stars, skill.forks, skill.downloads, skill.usage_count,
                    skill.frequency_score, skill.testability_score, skill.feasibility_score,
                    skill.single_responsibility_score, skill.safety_score, skill.activity_score,
                    weighted_score, self._determine_priority(weighted_score), "active",
                    raw_data_json
                ))
                
                # 保存标签
                self._save_skill_tags(cursor, skill.id, skill.tags)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"保存技能失败: {e}")
            return False
    
    def _calculate_weighted_score(self, skill: SkillMetadata) -> float:
        """计算加权分数"""
        scores = [
            (skill.frequency_score or 0) * 1.2,
            (skill.testability_score or 0) * 1.1,
            (skill.feasibility_score or 0) * 1.0,
            (skill.single_responsibility_score or 0) * 0.9,
            (skill.safety_score or 0) * 1.3,
            (skill.activity_score or 0) * 1.0
        ]
        
        total_weight = 1.2 + 1.1 + 1.0 + 0.9 + 1.3 + 1.0
        weighted_sum = sum(scores)
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _determine_priority(self, score: float) -> str:
        """根据分数确定优先级"""
        if score >= 4.0:
            return "P0"
        elif score >= 3.0:
            return "P1"
        elif score >= 2.0:
            return "P2"
        else:
            return "P3"
```

### 5.2 汇总报告生成

#### 5.2.1 报告模板系统
```python
# reporting/report_generator.py
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Template
from models import SkillMetadata

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_markdown_report(self, skills: List[SkillMetadata], title: str = "技能收集报告") -> str:
        """生成Markdown格式报告"""
        # 统计数据
        stats = self._calculate_statistics(skills)
        
        # 按优先级分组
        skills_by_priority = self._group_by_priority(skills)
        
        # 使用Jinja2模板
        template_str = """
# {{ title }}

**生成时间**: {{ timestamp }}  
**技能总数**: {{ stats.total_skills }}

## 统计概览

| 优先级 | 数量 | 平均分数 | 占比 |
|--------|------|----------|------|
{% for priority, data in stats.by_priority.items() %}
| {{ priority }} | {{ data.count }} | {{ "%.2f"|format(data.avg_score) }} | {{ "%.1f%%"|format(data.percentage) }} |
{% endfor %}

## 技能详情

{% for priority in ['P0', 'P1', 'P2', 'P3'] %}
{% if skills_by_priority[priority] %}

### {{ priority }} 优先级 ({{ skills_by_priority[priority]|length }}个)

| 名称 | 描述 | 来源 | 高频性 | 可验收性 | 可行性 | 单一职责 | 安全性 | 活跃度 | 总分 |
|------|------|------|--------|----------|--------|----------|--------|--------|------|
{% for skill in skills_by_priority[priority] %}
| [{{ skill.name }}]({{ skill.source_url }}) | {{ skill.description[:50] }}... | {{ skill.source }} | {{ skill.frequency_score or 0 }} | {{ skill.testability_score or 0 }} | {{ skill.feasibility_score or 0 }} | {{ skill.single_responsibility_score or 0 }} | {{ skill.safety_score or 0 }} | {{ skill.activity_score or 0 }} | {{ "%.2f"|format(weighted_score(skill)) }} |
{% endfor %}

{% endif %}
{% endfor %}

## 数据源统计

| 数据源 | 技能数量 | 平均分数 |
|--------|----------|----------|
{% for source, data in stats.by_source.items() %}
| {{ source }} | {{ data.count }} | {{ "%.2f"|format(data.avg_score) }} |
{% endfor %}
        """
        
        template = Template(template_str)
        
        # 自定义过滤器
        def weighted_score(skill):
            scores = [
                (skill.frequency_score or 0) * 1.2,
                (skill.testability_score or 0) * 1.1,
                (skill.feasibility_score or 0) * 1.0,
                (skill.single_responsibility_score or 0) * 0.9,
                (skill.safety_score or 0) * 1.3,
                (skill.activity_score or 0) * 1.0
            ]
            total_weight = 1.2 + 1.1 + 1.0 + 0.9 + 1.3 + 1.0
            return sum(scores) / total_weight if total_weight > 0 else 0
        
        template.filters['weighted_score'] = weighted_score
        
        # 渲染报告
        report = template.render(
            title=title,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stats=stats,
            skills_by_priority=skills_by_priority
        )
        
        # 保存文件
        report_path = self.output_dir / f"skill_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.write_text(report, encoding="utf-8")
        
        return str(report_path)
```

#### 5.2.2 数据导出功能
```python
# reporting/data_exporter.py
import csv
import json
from typing import List
from pathlib import Path
from models import SkillMetadata

class DataExporter:
    """数据导出器"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, skills: List[SkillMetadata], filename: str = None) -> str:
        """导出为JSON格式"""
        if filename is None:
            filename = f"skills_{datetime.now().strftime('%Y%m%d')}.json"
        
        filepath = self.output_dir / filename
        
        # 转换为字典列表
        skills_data = []
        for skill in skills:
            skill_dict = skill.dict()
            skills_data.append(skill_dict)
        
        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(skills_data, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)
    
    def export_to_csv(self, skills: List[SkillMetadata], filename: str = None) -> str:
        """导出为CSV格式"""
        if filename is None:
            filename = f"skills_{datetime.now().strftime('%Y%m%d')}.csv"
        
        filepath = self.output_dir / filename
        
        # 定义CSV列
        fieldnames = [
            'id', 'name', 'description', 'source', 'source_url',
            'author', 'license', 'version', 'language', 'runtime',
            'stars', 'forks', 'downloads', 'usage_count',
            'frequency_score', 'testability_score', 'feasibility_score',
            'single_responsibility_score', 'safety_score', 'activity_score',
            'weighted_score', 'priority', 'tags'
        ]
        
        # 写入CSV文件
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for skill in skills:
                row = {
                    'id': skill.id,
                    'name': skill.name,
                    'description': skill.description[:200] if skill.description else '',
                    'source': skill.source,
                    'source_url': skill.source_url,
                    'author': skill.author or '',
                    'license': skill.license or '',
                    'version': skill.version or '',
                    'language': skill.language or '',
                    'runtime': skill.runtime or '',
                    'stars': skill.stars or 0,
                    'forks': skill.forks or 0,
                    'downloads': skill.downloads or 0,
                    'usage_count': skill.usage_count or 0,
                    'frequency_score': skill.frequency_score or 0,
                    'testability_score': skill.testability_score or 0,
                    'feasibility_score': skill.feasibility_score or 0,
                    'single_responsibility_score': skill.single_responsibility_score or 0,
                    'safety_score': skill.safety_score or 0,
                    'activity_score': skill.activity_score or 0,
                    'weighted_score': self._calculate_weighted_score(skill),
                    'priority': self._determine_priority(skill),
                    'tags': ','.join(skill.tags) if skill.tags else ''
                }
                writer.writerow(row)
        
        return str(filepath)
```

---

## 六、快速开始指南

### 6.1 环境准备

#### 6.1.1 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 6.1.2 配置文件
```yaml
# config/config.yaml
crawlers:
  github:
    enabled: true
    token: ${GITHUB_TOKEN}  # 从环境变量读取
    rate_limit: 60  # 请求/分钟
    
  skillhub:
    enabled: true
    api_key: ${SKILLHUB_API_KEY}
    base_url: "https://skillshub.wtf/api"
    
database:
  path: "data/skills.db"
  auto_backup: true
  
evaluators:
  enabled: true
  weights:
    frequency: 1.2
    testability: 1.1
    feasibility: 1.0
    single_responsibility: 0.9
    safety: 1.3
    activity: 1.0

reporting:
  output_dir: "reports"
  formats: ["markdown", "json", "csv"]
```

### 6.2 运行收集脚本

#### 6.2.1 简单收集
```python
# scripts/collect_skills.py
import asyncio
import os
from dotenv import load_dotenv
from pipelines import SkillCollectionPipeline
from database import SkillRepository
from reporting import ReportGenerator, DataExporter

# 加载环境变量
load_dotenv()

async def main():
    # 配置管道
    config = PipelineConfig(
        sources=["github", "skillhub"],
        limit_per_source=50,
        enable_parsing=True,
        enable_scoring=True
    )
    
    # 创建管道
    pipeline = SkillCollectionPipeline(config)
    
    print("开始收集技能...")
    skills = await pipeline.run()
    print(f"收集完成，共收集到 {len(skills)} 个技能")
    
    # 保存到数据库
    repo = SkillRepository()
    saved_count = 0
    for skill in skills:
        if repo.save_skill(skill):
            saved_count += 1
    
    print(f"保存到数据库: {saved_count} 个技能")
    
    # 生成报告
    generator = ReportGenerator()
    report_path = generator.generate_markdown_report(skills)
    print(f"报告已生成: {report_path}")
    
    # 导出数据
    exporter = DataExporter()
    json_path = exporter.export_to_json(skills)
    csv_path = exporter.export_to_csv(skills)
    print(f"数据已导出: {json_path}, {csv_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 6.2.2 定时收集（使用cron或任务调度）
```bash
# scripts/scheduled_collect.sh
#!/bin/bash

# 环境设置
cd /path/to/openskills
source venv/bin/activate

# 运行收集脚本
python scripts/collect_skills.py

# 可选：发送通知
if [ $? -eq 0 ]; then
    echo "技能收集成功完成"
else
    echo "技能收集失败"
fi
```

### 6.3 查看结果

#### 6.3.1 查询技能数据库
```python
# scripts/query_skills.py
import sqlite3
import pandas as pd

def query_top_skills(limit: int = 20):
    """查询最高分技能"""
    conn = sqlite3.connect("data/skills.db")
    
    query = """
    SELECT 
        name, description, source, 
        frequency_score, testability_score, feasibility_score,
        single_responsibility_score, safety_score, activity_score,
        weighted_score, priority
    FROM skills 
    WHERE priority IN ('P0', 'P1')
    ORDER BY weighted_score DESC
    LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    
    return df

# 使用示例
if __name__ == "__main__":
    top_skills = query_top_skills(10)
    print(top_skills.to_string())
```

---

## 七、维护与扩展

### 7.1 系统维护

#### 7.1.1 数据质量监控
```python
# monitoring/quality_monitor.py
import sqlite3
from datetime import datetime, timedelta

class QualityMonitor:
    """数据质量监控器"""
    
    def check_data_quality(self, db_path: str) -> Dict[str, Any]:
        """检查数据质量"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        checks = {}
        
        # 检查技能总数
        cursor.execute("SELECT COUNT(*) FROM skills")
        checks["total_skills"] = cursor.fetchone()[0]
        
        # 检查最近更新时间
        cursor.execute("SELECT MAX(updated) FROM skills")
        latest_update = cursor.fetchone()[0]
        if latest_update:
            latest_date = datetime.fromisoformat(latest_update)
            days_old = (datetime.now() - latest_date).days
            checks["days_since_last_update"] = days_old
        
        # 检查数据完整性
        cursor.execute("""
        SELECT 
            COUNT(CASE WHEN name IS NULL OR name = '' THEN 1 END) as missing_names,
            COUNT(CASE WHEN description IS NULL OR description = '' THEN 1 END) as missing_descriptions,
            COUNT(CASE WHEN source IS NULL OR source = '' THEN 1 END) as missing_sources
        FROM skills
        """)
        
        missing_data = cursor.fetchone()
        checks["missing_names"] = missing_data[0]
        checks["missing_descriptions"] = missing_data[1]
        checks["missing_sources"] = missing_data[2]
        
        conn.close()
        
        return checks
```

#### 7.1.2 性能优化
- **增量更新**：只收集新增或更新的技能
- **缓存机制**：缓存API响应，减少重复请求
- **并行处理**：使用asyncio并行处理多个数据源
- **数据库索引**：为常用查询字段创建索引

### 7.2 系统扩展

#### 7.2.1 添加新数据源
```python
# 添加新爬取器的步骤
# 1. 创建新的爬取器类
class NewSourceCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("newsource", "https://api.newsource.com")
    
    async def fetch_skills(self, limit: int = 100):
        # 实现具体逻辑
        pass
    
    def parse_skill(self, raw_data):
        # 实现解析逻辑
        pass

# 2. 注册到管道配置中
config.sources.append("newsource")

# 3. 在管道初始化中添加
if "newsource" in config.sources:
    crawlers["newsource"] = NewSourceCrawler()
```

#### 7.2.2 添加新评估维度
```python
# 添加新评估器的步骤
# 1. 创建新的评估器类
class NewDimensionEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__(weight=1.0)
    
    async def evaluate(self, skill):
        # 实现评估逻辑
        pass
    
    def get_criteria(self):
        return {
            "name": "新维度",
            "description": "新维度的评估标准",
            "metrics": ["指标1", "指标2"],
            "weight": self.weight
        }

# 2. 注册到评估器注册表
evaluator_registry.register("new_dimension", NewDimensionEvaluator())
```

---

## 八、最佳实践与建议

### 8.1 收集策略

#### 8.1.1 分级收集
1. **日常收集**：高频数据源（GitHub trending，SkillHub最新）
2. **每周收集**：完整扫描主要数据源
3. **月度评估**：重新评估所有技能分数

#### 8.1.2 质量控制
- **人工审核**：对P0优先级技能进行人工验证
- **社区反馈**：邀请社区成员验证技能质量
- **A/B测试**：实际测试技能效果

### 8.2 技术建议

#### 8.2.1 避免被封禁
- **遵守速率限制**：每个API都有速率限制，严格遵守
- **设置User-Agent**：标识自己是合法爬虫
- **使用缓存**：减少重复请求

#### 8.2.2 错误处理
- **重试机制**：网络错误时自动重试
- **优雅降级**：某个数据源失败时不影响其他
- **详细日志**：记录所有错误信息便于调试

### 8.3 社区协作

#### 8.3.1 开放贡献
- **公开技能数据库**：让社区查看和验证收集结果
- **接受技能提交**：允许用户提交新发现的技能
- **社区评分**：让社区成员对技能进行评分

#### 8.3.2 透明运营
- **公开收集方法**：让社区了解技能如何被收集和评估
- **定期发布报告**：分享收集结果和洞见
- **接受反馈**：根据社区反馈改进收集系统

---

## 九、预期成果

### 9.1 短期目标（1-2周）
- 建立基础收集系统，收集500-1000个技能
- 识别50-100个P0/P1优先级技能
- 生成首次技能收集报告

### 9.2 中期目标（1-2月）
- 建立完整的技能数据库（2000+技能）
- 开发Web界面查看技能数据
- 建立自动化收集和报告系统

### 9.3 长期目标（3-6月）
- 建立行业领先的技能情报系统
- 与OpenSkills开发流程深度集成
- 成为AI技能生态的权威数据源

---

## 附录

### A. 相关资源
- [GitHub REST API文档](https://docs.github.com/en/rest)
- [SkillHub API文档](https://skillshub.wtf/docs)
- [OpenSkills项目文档](https://github.com/openskills/docs)

### B. 示例输出
- **技能报告示例**：[reports/skill_report_20250415.md](reports/skill_report_20250415.md)
- **技能数据库**：[data/skills.db](data/skills.db)
- **导出数据**：[exports/skills_20250415.json](exports/skills_20250415.json)

### C. 故障排除
1. **API限制错误**：检查环境变量中的API密钥，降低请求频率
2. **数据库连接失败**：检查文件权限，确保数据库目录可写
3. **解析错误**：检查原始数据格式，更新解析器逻辑

---

**版本**: 1.0  
**最后更新**: 2026-04-15  
**状态**: 草案  

*本系统将根据实际使用情况进行持续优化和改进。*