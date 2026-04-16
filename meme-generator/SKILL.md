---
name: meme-generator
version: 1.0.0
author: OpenSkills Team
license: MIT
description: 智能表情包生成器 - 根据对话情景和个人喜好自动生成或爬取表情包
---

# 技能概述

`meme-generator` 是一个智能表情包生成技能，能够：

1. **情景感知生成**：读取LLM对话上下文，自动生成符合当前情景的表情包
2. **个性化定制**：支持用户设置个人喜好，生成符合个性的专属表情包
3. **多源获取**：从本地模板库和外部图库爬取合适的表情包素材
4. **智能适配**：根据情绪、话题、对话风格自动匹配最佳表情包

## 适用场景

- 在聊天对话中需要幽默回应时
- 需要表达特定情绪或态度时
- 个性化社交媒体内容创作
- 自动化内容生成和配图

---

# 触发条件

## 关键词触发
- 主要关键词：`表情包`、`meme`、`生成表情`、`搞笑图片`、`斗图`
- 次要关键词：`幽默`、`搞笑`、`配图`、`图片生成`、`表情`
- 英文关键词：`generate meme`、`create meme`、`funny picture`、`meme maker`

## 上下文模式触发
- 当用户表达情绪时：`我好开心`、`太生气了`、`好尴尬`、`无语`
- 当用户讨论话题时：`关于这个...`、`对于...的看法`、`讨论...`
- 当用户需要视觉辅助时：`配个图`、`加个表情`、`用图片表达`

## 文件类型触发
- 支持处理包含情绪关键词的文本文件
- 支持处理对话记录文件（.txt, .json, .csv）

---

# 安全边界

## 禁止的操作
- ❌ 爬取受版权保护的商业图片库
- ❌ 生成涉及暴力、色情、政治敏感内容的表情包
- ❌ 未经用户确认的大规模图片下载
- ❌ 修改系统文件或用户私人图片

## 权限要求
- ✅ 网络访问权限：用于爬取公开图库（如Imgflip、Giphy API）
- ✅ 文件写入权限：保存生成的表情包到本地目录
- ✅ 文件读取权限：读取用户偏好配置和本地模板
- ✅ 临时文件创建权限：处理图片时需要的临时空间

## 确认机制
- 🔔 当需要下载超过10张图片时，需要用户确认
- 🔔 当使用付费API时，需要用户确认费用
- 🔔 当生成内容可能涉及敏感话题时，需要用户确认

## 数据隐私
- 📊 用户偏好设置仅保存在本地
- 📊 不收集或上传用户对话内容
- 📊 爬取的图片仅用于即时生成，不长期存储

---

# 接口定义

## 输入格式 (JSON)
```json
{
  "context": "当前对话上下文文本",
  "user_input": "用户输入的生成指令",
  "preferences": {
    "style": "搞笑|讽刺|可爱|吐槽|励志",
    "humor_level": 1-5,
    "language": "zh|en",
    "favorite_templates": ["doge", " Drake", "改变心意"],
    "avoid_topics": ["政治", "宗教", "暴力"]
  },
  "options": {
    "source": "generate|search|both",
    "output_format": "image|link|both",
    "max_results": 1-10,
    "size": "small|medium|large"
  }
}
```

## 输出格式 (JSON)
```json
{
  "status": "success|partial|error",
  "message": "处理结果描述",
  "memes": [
    {
      "type": "generated|searched",
      "url": "图片链接或本地路径",
      "caption": "表情包文字描述",
      "tags": ["标签1", "标签2"],
      "source": "来源说明",
      "match_score": 0.0-1.0
    }
  ],
  "metadata": {
    "processing_time": "处理时间(秒)",
    "sources_used": ["来源列表"],
    "preferences_applied": "应用的偏好设置"
  }
}
```

## 参数验证规则

### 必需参数
- `context`: 字符串，最少10字符，最多1000字符
- `user_input`: 字符串，最少2字符，最多200字符

### 可选参数
- `preferences`: 对象，可部分提供
- `options`: 对象，默认值如下：
  ```json
  {
    "source": "both",
    "output_format": "image",
    "max_results": 3,
    "size": "medium"
  }
  ```

### 验证失败处理
- 缺少必需参数 → 返回错误，提示缺少的参数
- 参数格式错误 → 返回错误，显示正确格式示例
- 参数值超出范围 → 自动调整到最近的有效值

---

# 使用示例

## 示例1：基本表情包生成
```json
输入：
{
  "context": "用户说：今天工作好累，想找点乐子",
  "user_input": "生成一个搞笑的表情包",
  "preferences": {
    "style": "搞笑",
    "humor_level": 4
  }
}

输出：
{
  "status": "success",
  "message": "成功生成3个表情包",
  "memes": [
    {
      "type": "generated",
      "url": "/tmp/meme_work_tired_1.png",
      "caption": "上班的我 vs 下班的我",
      "tags": ["工作", "累", "搞笑"],
      "source": "本地模板生成",
      "match_score": 0.92
    }
  ]
}
```

## 示例2：个性化表情包生成
```json
输入：
{
  "context": "用户讨论编程bug很难找",
  "user_input": "生成一个程序员相关的表情包",
  "preferences": {
    "style": "吐槽",
    "favorite_templates": ["程序员", "bug", "调试"],
    "avoid_topics": []
  },
  "options": {
    "source": "generate",
    "max_results": 2
  }
}
```

## 示例3：多源搜索和生成
```json
输入：
{
  "context": "庆祝项目成功上线",
  "user_input": "找些庆祝的表情包",
  "options": {
    "source": "both",
    "max_results": 5,
    "output_format": "link"
  }
}
```

## 示例4：CLI调用方式
```bash
# 基本调用
python scripts/main.py --context "今天天气真好" --input "生成开心表情包"

# 使用配置文件
python scripts/main.py --config user_preferences.json

# 批量处理
python scripts/main.py --batch dialog_records.txt --output memes_output/
```

---

# 故障排除

## 常见问题及解决方案

### 1. 网络连接失败
**症状**：爬取外部图库时失败，返回网络错误
**解决方案**：
- 检查网络连接
- 验证API密钥是否正确
- 尝试切换到本地生成模式
- 检查防火墙设置

### 2. 模板文件缺失
**症状**：本地模板无法加载，提示文件不存在
**解决方案**：
- 运行初始化脚本：`python scripts/init_templates.py`
- 检查assets/templates目录权限
- 从备用源下载模板

### 3. 图片生成失败
**症状**：生成的表情包图片损坏或无法打开
**解决方案**：
- 检查Pillow库是否正确安装：`pip install Pillow`
- 验证字体文件是否存在
- 检查临时目录写入权限

### 4. API限制达到
**症状**：外部API返回速率限制错误
**解决方案**：
- 等待限制重置（通常1小时）
- 切换到其他API源
- 使用本地生成模式
- 申请更高的API限额

### 5. 内存不足
**症状**：处理大量图片时内存错误
**解决方案**：
- 减少`max_results`参数值
- 使用`output_format: "link"`减少内存使用
- 分批处理大量请求

## 调试模式

启用调试模式获取详细信息：
```bash
python scripts/main.py --debug --context "测试" --input "生成测试表情包"
```

调试信息包括：
- 每个处理步骤的耗时
- 使用的API和模板
- 匹配分数计算详情
- 错误堆栈跟踪

---

# 高级功能

## 个性化学习
技能会从用户反馈中学习：
- 用户喜欢的表情包类型
- 常用的幽默风格
- 偏好的话题和表达方式

学习数据保存在本地：`~/.meme-generator/preferences.json`

## 模板管理系统
支持自定义模板：
1. **导入模板**：添加自定义图片模板
2. **编辑模板**：调整文字位置和样式
3. **分享模板**：导出模板供他人使用

## 智能推荐系统
基于以下因素推荐最佳表情包：
- 对话情绪分析
- 话题相关性
- 用户历史偏好
- 流行趋势

## 批量处理
支持批量生成表情包：
- 从文件读取多个对话场景
- 批量爬取相关图片
- 自动分类和整理结果

---

# 配置选项

## 配置文件位置
- 主配置：`~/.meme-generator/config.json`
- 用户偏好：`~/.meme-generator/preferences.json`
- 模板目录：`~/.meme-generator/templates/`

## 主要配置项
```json
{
  "api_keys": {
    "imgflip": "your_imgflip_key",
    "giphy": "your_giphy_key"
  },
  "storage": {
    "local_templates": true,
    "cache_external": true,
    "max_cache_size_mb": 100
  },
  "generation": {
    "default_style": "搞笑",
    "default_language": "zh",
    "quality": "medium"
  },
  "safety": {
    "content_filter": true,
    "max_downloads_per_day": 100,
    "require_confirmation": true
  }
}
```

## 环境变量
```
MEME_GENERATOR_API_KEY_IMGFLIP=your_key
MEME_GENERATOR_API_KEY_GIPHY=your_key
MEME_GENERATOR_DEBUG=true
MEME_GENERATOR_CACHE_DIR=/custom/cache/path
```

---

# 更新与维护

## 版本更新
检查更新：
```bash
python scripts/check_update.py
```

自动更新（如支持）：
```bash
python scripts/update.py
```

## 数据维护
清理缓存：
```bash
python scripts/clean_cache.py --days 30
```

备份用户数据：
```bash
python scripts/backup.py --output backup.zip
```

## 问题反馈
发现问题时：
1. 启用调试模式重现问题
2. 收集调试输出
3. 提交到问题追踪系统
4. 或发送到：support@openskills.dev

---

# 许可证与贡献

## 许可证
本技能使用MIT许可证，允许自由使用、修改和分发。

## 贡献指南
欢迎贡献：
1. 提交新的表情包模板
2. 改进匹配算法
3. 添加新的API支持
4. 修复bug或改进文档

贡献流程：
1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 通过代码审查

## 致谢
- 使用Pillow进行图像处理
- 使用Requests进行网络请求
- 使用Imgflip、Giphy等API服务
- 开源社区提供的模板资源

---

**最后更新**: 2026-04-15  
**技能状态**: 正式发布  
**兼容性**: Python 3.8+, 支持Windows/Linux/macOS  

*如需帮助或有问题，请查阅文档或联系支持团队。*