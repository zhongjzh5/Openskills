# 表情包模板资源

## 目录结构
```
assets/
├── templates/          # 表情包模板图片
├── fonts/             # 字体文件
├── backgrounds/       # 背景图片
└── examples/          # 示例输出
```

## 模板管理

### 内置模板
系统内置以下经典表情包模板：

| 模板ID | 名称 | 描述 | 推荐文字数量 |
|--------|------|------|--------------|
| `doge` | 神烦狗 | 经典多文字神烦狗模板 | 2-4 |
| `drake` | Drake Hotline Bling | 手势选择模板 | 2 |
| `change_my_mind` | 改变我的心意 | 辩论说服模板 | 1 |
| `distracted_boyfriend` | 分心的男友 | 三角关系模板 | 3 |
| `two_buttons` | 两个按钮 | 选择困难模板 | 2 |

### 模板格式要求
- **图片格式**: PNG（推荐）或JPG
- **尺寸建议**: 600×400像素（最小300×300，最大1200×800）
- **文件命名**: 使用英文小写和下划线，如`my_template.png`
- **配置文件**: 每个模板可配一个同名的JSON配置文件

### 模板配置文件示例
```json
{
  "name": "我的模板",
  "description": "模板描述",
  "tags": ["搞笑", "工作", "日常"],
  "style": "搞笑",
  "text_positions": [
    {"x": 50, "y": 50, "width": 200, "height": 100, "color": "white", "font_size": 24},
    {"x": 300, "y": 150, "width": 200, "height": 100, "color": "black", "font_size": 20}
  ],
  "text_align": "center",
  "max_text_length": 20
}
```

## 字体资源

### 推荐字体
- **中文字体**: 思源黑体、微软雅黑、苹方
- **英文字体**: Arial、Impact、Comic Sans MS
- **创意字体**: 可使用特殊字体增加趣味性

### 字体安装
1. 将字体文件放入`fonts/`目录
2. 字体文件支持格式：TTF、OTF
3. 系统会自动加载目录下所有字体文件

## 背景图片

### 使用场景
- 自定义模板的背景
- 文字叠加的底图
- 表情包合成素材

### 要求
- 高分辨率，建议1200×800以上
- 简洁背景，避免干扰文字
- 适当留白，方便添加文字

## 自定义模板制作指南

### 步骤1：准备图片
1. 选择或制作合适的基础图片
2. 调整尺寸到推荐大小（600×400）
3. 优化图片质量，确保清晰度

### 步骤2：设计文字区域
1. 确定文字放置位置
2. 考虑文字颜色与背景的对比度
3. 预留足够的空间避免文字溢出

### 步骤3：创建配置文件
1. 复制示例配置文件
2. 根据图片调整文字位置参数
3. 添加合适的标签和描述

### 步骤4：测试模板
1. 将图片和配置文件放入`templates/`目录
2. 运行测试脚本验证模板效果
3. 调整参数直到满意

## 示例输出

`examples/`目录包含使用系统生成的示例表情包，可用于：
- 测试模板效果
- 演示不同风格
- 用户参考和学习

## 模板分享

### 导出模板
```bash
# 导出单个模板
python scripts/export_template.py --template my_template --output my_template.zip

# 导出所有模板
python scripts/export_template.py --all --output all_templates.zip
```

### 导入模板
```bash
# 导入模板包
python scripts/import_template.py --file template_package.zip

# 从URL导入
python scripts/import_template.py --url https://example.com/templates.zip
```

## 最佳实践

### 设计原则
1. **简洁明了**：避免过多元素干扰
2. **文字可读**：确保文字清晰易读
3. **风格统一**：保持模板风格一致
4. **版权合规**：使用无版权或已获授权素材

### 性能优化
1. **图片压缩**：在质量可接受范围内压缩图片
2. **缓存利用**：系统会缓存模板提高加载速度
3. **懒加载**：需要时才加载模板资源

### 质量控制
1. **预览检查**：生成前预览效果
2. **批量测试**：使用测试脚本批量验证
3. **用户反馈**：收集用户使用反馈持续改进

## 故障排除

### 常见问题

#### 1. 模板加载失败
- **可能原因**: 图片文件损坏或格式不支持
- **解决方案**: 检查图片格式，转换为PNG格式

#### 2. 文字位置不准
- **可能原因**: 配置文件中的坐标错误
- **解决方案**: 使用预览工具调整坐标

#### 3. 字体不显示
- **可能原因**: 字体文件缺失或损坏
- **解决方案**: 检查字体文件，重新安装

#### 4. 生成质量差
- **可能原因**: 原始图片分辨率太低
- **解决方案**: 使用更高分辨率的图片

### 调试工具
```bash
# 检查模板
python scripts/check_template.py --template my_template

# 预览模板
python scripts/preview_template.py --template my_template --text "测试文字"

# 批量检查
python scripts/check_all_templates.py
```

## 更新与维护

### 模板更新
系统会定期检查模板更新：
1. **自动更新**：从官方仓库获取新模板
2. **手动更新**：用户可以手动导入新模板
3. **社区贡献**：接受社区提交的模板

### 资源清理
```bash
# 清理未使用的模板
python scripts/cleanup_templates.py --unused

# 优化图片缓存
python scripts/optimize_cache.py

# 检查资源完整性
python scripts/check_resources.py
```

---

## 贡献指南

欢迎贡献新的表情包模板：

1. **Fork项目**并创建新分支
2. **添加模板**到`templates/`目录
3. **创建配置文件**描述模板特性
4. **提交Pull Request**并附上示例输出

### 贡献要求
- 模板必须为原创或已获授权
- 提供清晰的文档和示例
- 通过所有测试检查
- 遵循项目代码规范

---

**最后更新**: 2026-04-15  
**维护者**: OpenSkills 设计团队

*更多资源和教程请访问：https://docs.openskills.dev/meme-generator/templates*