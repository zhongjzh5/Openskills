# meme-generator 使用指南

## 快速开始

### 安装与配置

#### 1. 环境准备
```bash
# 克隆项目或下载技能包
git clone https://github.com/openskills/meme-generator.git
cd meme-generator

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 基本配置
```bash
# 创建配置文件
cp config.example.json config.json

# 编辑配置文件，添加API密钥（可选）
# 如果需要使用外部API服务（如Imgflip、Giphy）
```

#### 3. 验证安装
```bash
# 列出可用模板
python scripts/main.py --list-templates

# 测试生成
python scripts/main.py --context "测试对话" --input "生成测试表情包"
```

### 第一个表情包

#### 示例1：简单生成
```bash
python scripts/main.py \
  --context "今天工作完成了，心情很好" \
  --input "生成一个开心的表情包"
```

#### 示例2：带偏好设置
创建偏好文件 `my_preferences.json`:
```json
{
  "style": "搞笑",
  "humor_level": 4,
  "favorite_templates": ["doge", "drake"]
}
```

然后运行：
```bash
python scripts/main.py \
  --context "项目上线成功，团队很兴奋" \
  --input "庆祝一下" \
  --preferences my_preferences.json \
  --output celebration.json
```

---

## 核心功能详解

### 1. 上下文感知生成

#### 工作原理
系统会自动分析对话上下文，提取：
- **情感倾向**：开心、生气、悲伤、惊讶、尴尬
- **话题关键词**：工作、学习、生活、科技、娱乐
- **用户意图**：表达情绪、寻求建议、分享信息等

#### 示例分析
```python
输入上下文: "今天调试了一个很难的bug，终于解决了"
用户输入: "生成一个程序员相关的表情包"

分析结果:
- 情感: 开心、成就感
- 话题: 工作、科技
- 意图: 分享成功、表达喜悦
```

### 2. 个性化设置

#### 偏好维度
```json
{
  "style": "搞笑|讽刺|可爱|吐槽|励志",  // 表情包风格
  "humor_level": 1-5,                    // 幽默程度
  "language": "zh|en",                   // 语言偏好
  "favorite_templates": ["doge", "..."], // 常用模板
  "avoid_topics": ["政治", "宗教"]       // 避免的话题
}
```

#### 偏好学习
系统会从用户使用中学习：
- **显式偏好**：用户直接设置的参数
- **隐式偏好**：从用户选择中推断的喜好
- **情景偏好**：特定场景下的偏好模式

### 3. 多源获取策略

#### 生成模式 (generate)
- **本地模板**：使用内置或自定义模板生成
- **优点**：快速、无需网络、完全控制
- **适用场景**：快速响应、隐私敏感、离线使用

#### 搜索模式 (search)
- **外部API**：从Imgflip、Giphy等平台搜索
- **优点**：海量资源、实时更新、多样性强
- **适用场景**：寻找特定内容、需要新鲜感

#### 混合模式 (both)
- **智能结合**：同时使用生成和搜索
- **优点**：兼顾速度和质量
- **适用场景**：大多数日常使用

### 4. 智能匹配算法

#### 匹配分数计算
```python
匹配分数 = 基础分(0.5)
         + 风格匹配(0-0.2)
         + 偏好模板(0-0.3)
         + 话题相关(0-0.1)
         + 情感匹配(0-0.1)

# 分数范围: 0.0 - 1.0
# 分数越高表示越符合用户需求
```

#### 排序策略
1. **分数优先**：匹配分数最高的优先显示
2. **多样性控制**：避免连续显示相似内容
3. **新鲜度加权**：新内容获得适当加分
4. **流行度考量**：热门内容更容易被推荐

---

## 高级用法

### 1. 批量处理

#### 批量生成
```bash
# 从文件读取多个请求
python scripts/batch_processor.py \
  --input requests.jsonl \
  --output-dir batch_output \
  --parallel 3
```

#### 请求文件格式 (JSON Lines)
```json
{"context": "请求1上下文", "user_input": "请求1输入"}
{"context": "请求2上下文", "user_input": "请求2输入"}
```

### 2. API集成

#### 作为库使用
```python
from scripts.main import MemeGenerator, InputModel, Preferences, Options

# 创建生成器
generator = MemeGenerator()

# 准备输入
input_data = InputModel(
    context="对话上下文",
    user_input="用户输入",
    preferences=Preferences(style="搞笑"),
    options=Options(source="both")
)

# 生成表情包
result = generator.process(input_data)

# 处理结果
if result.status == "success":
    for meme in result.memes:
        print(f"表情包: {meme.caption}")
        print(f"路径: {meme.url}")
```

#### REST API服务
```bash
# 启动API服务器
python scripts/api_server.py --port 8080

# 使用curl测试
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "context": "API测试",
    "user_input": "生成表情包"
  }'
```

### 3. 自定义模板

#### 创建模板
1. **准备图片**：600×400像素的PNG图片
2. **创建配置**：同名的JSON配置文件
3. **放置目录**：放入 `assets/templates/` 目录
4. **测试验证**：运行测试脚本验证

#### 模板配置示例
```json
{
  "name": "我的自定义模板",
  "description": "用于特定场景的表情包",
  "tags": ["自定义", "工作", "幽默"],
  "style": "搞笑",
  "text_positions": [
    {
      "x": 50,
      "y": 50,
      "width": 200,
      "height": 100,
      "color": "#FFFFFF",
      "font_size": 24,
      "align": "center"
    }
  ]
}
```

### 4. 扩展功能

#### 情感分析增强
```python
# 集成更高级的情感分析
from scripts.enhanced_analyzer import EnhancedAnalyzer

analyzer = EnhancedAnalyzer()
analysis = analyzer.analyze("文本内容", use_deep_learning=True)
```

#### 多语言支持
```python
# 支持多种语言
input_data = InputModel(
    context="English conversation context",
    user_input="Generate a meme",
    preferences=Preferences(language="en"),
    options=Options()
)
```

#### 实时推荐
```python
# 基于用户行为的实时推荐
from scripts.recommendation import RecommendationEngine

engine = RecommendationEngine(user_id="user123")
recommendations = engine.get_recommendations(
    context="当前对话",
    history=user_history
)
```

---

## 配置详解

### 配置文件结构
```json
{
  "api_keys": {
    "imgflip": {
      "username": "your_username",
      "password": "your_password"
    },
    "giphy": "your_giphy_api_key"
  },
  "storage": {
    "cache_dir": "~/.meme-generator/cache",
    "max_cache_size_mb": 500,
    "cleanup_days": 30
  },
  "generation": {
    "default_style": "搞笑",
    "default_language": "zh",
    "quality": "medium",
    "max_text_length": 20
  },
  "safety": {
    "content_filter": true,
    "max_downloads_per_day": 100,
    "require_confirmation": true,
    "blocked_keywords": ["政治", "暴力", "色情"]
  },
  "performance": {
    "max_workers": 3,
    "timeout_seconds": 30,
    "retry_attempts": 3
  }
}
```

### 环境变量
```bash
# API密钥
export MEME_GENERATOR_IMGFLIP_USERNAME="your_username"
export MEME_GENERATOR_IMGFLIP_PASSWORD="your_password"
export MEME_GENERATOR_GIPHY_API_KEY="your_key"

# 系统设置
export MEME_GENERATOR_CACHE_DIR="/custom/cache/path"
export MEME_GENERATOR_DEBUG="true"
export MEME_GENERATOR_LOG_LEVEL="INFO"

# 性能设置
export MEME_GENERATOR_MAX_WORKERS="5"
export MEME_GENERATOR_TIMEOUT="60"
```

### 配置优先级
1. **命令行参数**：最高优先级
2. **环境变量**：次高优先级
3. **配置文件**：默认配置
4. **代码默认值**：最低优先级

---

## 使用场景示例

### 场景1：日常聊天

#### 需求
在聊天对话中快速回应，增加趣味性

#### 配置
```json
{
  "preferences": {
    "style": "搞笑",
    "humor_level": 3,
    "favorite_templates": ["doge", "drake"]
  },
  "options": {
    "source": "generate",
    "max_results": 2,
    "output_format": "image"
  }
}
```

#### 使用方式
```bash
# 快速响应
python scripts/quick_response.py \
  --context "$(pbpaste)" \  # 从剪贴板获取上下文
  --input "回应"
```

### 场景2：内容创作

#### 需求
为社交媒体创作系列表情包

#### 配置
```json
{
  "preferences": {
    "style": "励志",
    "humor_level": 2,
    "language": "zh"
  },
  "options": {
    "source": "both",
    "max_results": 10,
    "output_format": "both",
    "size": "large"
  }
}
```

#### 使用方式
```bash
# 批量创作
python scripts/content_creator.py \
  --theme "程序员日常" \
  --count 20 \
  --output-dir social_media
```

### 场景3：团队协作

#### 需求
团队内部使用的个性化表情包

#### 配置
```json
{
  "preferences": {
    "style": "吐槽",
    "humor_level": 4,
    "favorite_templates": ["distracted_boyfriend", "two_buttons"]
  },
  "options": {
    "source": "generate",
    "max_results": 3
  }
}
```

#### 使用方式
```bash
# 集成到团队聊天工具
python scripts/chat_integration.py \
  --platform "slack" \
  --config team_config.json
```

### 场景4：个性化学习

#### 需求
根据个人兴趣定制表情包推荐

#### 配置
```json
{
  "preferences": {
    "style": "可爱",
    "humor_level": 3,
    "favorite_templates": [],
    "avoid_topics": []
  },
  "learning": {
    "enabled": true,
    "history_size": 100,
    "update_frequency": "daily"
  }
}
```

#### 使用方式
```bash
# 学习模式
python scripts/learning_mode.py \
  --input history.json \
  --train \
  --output model.pkl
```

---

## 故障排除

### 常见问题

#### 1. 安装问题
**症状**: `ImportError` 或依赖包安装失败
**解决方案**:
```bash
# 更新pip
python -m pip install --upgrade pip

# 使用清华镜像源（国内用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 逐个安装依赖
pip install Pillow
pip install requests
pip install pydantic
```

#### 2. 网络问题
**症状**: API调用失败或超时
**解决方案**:
```bash
# 测试网络连接
curl https://api.imgflip.com

# 使用代理（如果需要）
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"

# 切换到离线模式
python scripts/main.py --source generate ...
```

#### 3. 权限问题
**症状**: 无法写入文件或目录
**解决方案**:
```bash
# 检查目录权限
ls -la ~/.meme-generator/

# 修复权限
chmod 755 ~/.meme-generator
chmod 644 ~/.meme-generator/*.json

# 使用其他目录
export MEME_GENERATOR_CACHE_DIR="/tmp/meme-cache"
```

#### 4. 性能问题
**症状**: 生成速度慢或内存占用高
**解决方案**:
```bash
# 减少同时处理数量
python scripts/main.py --max-results 1 ...

# 降低图片质量
# 在配置文件中设置 "quality": "low"

# 清理缓存
python scripts/clean_cache.py --all
```

### 调试模式

启用调试模式获取详细信息：
```bash
python scripts/main.py --debug --context "测试" --input "测试"
```

调试信息包括：
- 每个处理阶段的耗时
- 使用的模板和API
- 匹配分数计算过程
- 错误堆栈跟踪

### 日志文件

日志文件位置：
- 主日志：`~/.meme-generator/logs/app.log`
- 错误日志：`~/.meme-generator/logs/error.log`
- 访问日志：`~/.meme-generator/logs/access.log`

查看日志：
```bash
# 实时查看日志
tail -f ~/.meme-generator/logs/app.log

# 搜索错误
grep "ERROR" ~/.meme-generator/logs/app.log

# 按日期查看
cat ~/.meme-generator/logs/app.log | grep "2026-04-15"
```

---

## 最佳实践

### 1. 性能优化
- **缓存利用**：充分利用本地缓存减少网络请求
- **批量处理**：多个请求一起处理提高效率
- **资源管理**：及时释放图片资源避免内存泄漏
- **异步处理**：耗时操作使用异步避免阻塞

### 2. 用户体验
- **快速响应**：首次响应时间控制在2秒内
- **渐进加载**：先显示结果再加载图片
- **错误友好**：明确的错误提示和解决方案
- **学习反馈**：从用户行为中持续改进

### 3. 代码质量
- **类型提示**：使用Pydantic进行数据验证
- **错误处理**：完善的异常处理和恢复机制
- **测试覆盖**：保持高测试覆盖率
- **文档完整**：代码和文档同步更新

### 4. 安全隐私
- **本地存储**：用户数据存储在本地
- **内容过滤**：自动过滤敏感内容
- **权限控制**：最小必要权限原则
- **透明告知**：清楚告知数据使用方式

---

## 更新与维护

### 版本更新
```bash
# 检查更新
python scripts/check_update.py

# 自动更新
python scripts/update.py --auto

# 手动更新
git pull origin main
pip install -r requirements.txt --upgrade
```

### 数据备份
```bash
# 备份用户数据
python scripts/backup.py --output backup_$(date +%Y%m%d).zip

# 恢复备份
python scripts/restore.py --file backup_20260415.zip

# 定期备份（使用cron）
0 2 * * * cd /path/to/meme-generator && python scripts/backup.py --auto
```

### 监控告警
```bash
# 健康检查
python scripts/health_check.py

# 性能监控
python scripts/monitor.py --dashboard

# 设置告警
python scripts/alert.py --config alerts.json
```

---

## 获取帮助

### 官方资源
- **文档网站**: https://docs.openskills.dev/meme-generator
- **GitHub仓库**: https://github.com/openskills/meme-generator
- **问题追踪**: https://github.com/openskills/meme-generator/issues

### 社区支持
- **讨论论坛**: https://community.openskills.dev
- **Discord频道**: https://discord.gg/openskills
- **QQ群**: 123456789

### 技术支持
- **邮箱**: support@openskills.dev
- **工单系统**: https://support.openskills.dev
- **在线聊天**: 网站右下角聊天窗口

### 贡献代码
1. Fork项目仓库
2. 创建功能分支
3. 提交Pull Request
4. 通过代码审查
5. 合并到主分支

---

## 附录

### 快捷键参考
```bash
# 命令行快捷键
Ctrl+C          # 取消当前操作
Ctrl+D          # 退出程序
Ctrl+Z          # 暂停程序（后台运行）

# 在Python交互模式中
import sys
sys.argv = ['--context', '测试', '--input', '测试']
from scripts.main import main
main()
```

### 配置文件示例
完整配置文件示例见 `config.example.json`

### 示例脚本
- `scripts/quick_demo.py` - 快速演示脚本
- `scripts/benchmark.py` - 性能测试脚本
- `scripts/export_data.py` - 数据导出脚本
- `scripts/import_data.py` - 数据导入脚本

---

**最后更新**: 2026-04-15  
**文档版本**: 1.0  
**适用版本**: meme-generator v1.0.0+

*如有问题或建议，请通过GitHub Issues反馈。*