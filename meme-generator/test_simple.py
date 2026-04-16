#!/usr/bin/env python3
"""
简单测试脚本 - 验证核心功能
"""
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 测试数据模型
print("测试1: 数据模型...")
try:
    from scripts.main import InputModel, Preferences, Options
    input_data = InputModel(
        context="这是一个测试对话上下文，用于验证输入模型。",
        user_input="生成测试表情包",
        preferences=Preferences(style="搞笑", humor_level=3),
        options=Options(source="generate", max_results=2)
    )
    print("✓ 数据模型测试通过")
except Exception as e:
    print(f"✗ 数据模型测试失败: {e}")

# 测试TemplateManager
print("\n测试2: TemplateManager...")
try:
    from scripts.main import TemplateManager
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    manager = TemplateManager(Path(temp_dir))

    # 测试获取模板
    templates = manager.get_available_templates()
    print(f"✓ 获取到 {len(templates)} 个模板")

    # 测试创建表情包
    output_path = Path(temp_dir) / "test_meme.png"
    result = manager.create_meme_from_template(
        "doge",
        ["测试文字1", "测试文字2"],
        output_path
    )

    if result and output_path.exists():
        print("✓ 表情包创建成功")
    else:
        print("✗ 表情包创建失败")

    # 清理
    shutil.rmtree(temp_dir)
except Exception as e:
    print(f"✗ TemplateManager测试失败: {e}")

# 测试ContextAnalyzer
print("\n测试3: ContextAnalyzer...")
try:
    from scripts.main import ContextAnalyzer
    analyzer = ContextAnalyzer()

    analysis = analyzer.analyze(
        "今天工作很开心，项目顺利完成",
        "生成开心的表情包"
    )

    print(f"✓ 情感分析: {analysis.get('emotions', [])}")
    print(f"✓ 话题分析: {analysis.get('topics', [])}")
    print(f"✓ 关键词: {analysis.get('keywords', [])[:3]}")
except Exception as e:
    print(f"✗ ContextAnalyzer测试失败: {e}")

# 测试简单生成
print("\n测试4: 简单生成测试...")
try:
    from scripts.main import MemeGenerator, InputModel, Preferences, Options

    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()

    # 禁用个性化学习以简化测试
    import os
    os.environ["MEME_GENERATOR_DEBUG"] = "true"

    generator = MemeGenerator()
    generator.output_dir = Path(temp_dir)

    input_data = InputModel(
        context="测试简单生成功能",
        user_input="生成测试表情包",
        options=Options(source="generate", max_results=1)
    )

    output = generator.process(input_data, record_interaction=False)

    print(f"✓ 生成状态: {output.status}")
    print(f"✓ 生成数量: {len(output.memes)}")

    if output.memes:
        for i, meme in enumerate(output.memes):
            print(f"  表情包 {i+1}: {meme.caption}")

    # 清理
    import shutil
    shutil.rmtree(temp_dir)
except Exception as e:
    print(f"✗ 简单生成测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试命令行接口
print("\n测试5: 命令行接口...")
try:
    import subprocess
    import tempfile
    import json

    output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False).name

    result = subprocess.run([
        sys.executable, "scripts/main.py",
        "--context", "命令行测试",
        "--input", "生成测试表情包",
        "--output", output_file
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ 命令行执行成功")

        # 检查输出文件
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✓ 输出状态: {data.get('status')}")
        print(f"✓ 生成数量: {len(data.get('memes', []))}")
    else:
        print(f"✗ 命令行执行失败: {result.stderr}")

    # 清理
    import os
    if os.path.exists(output_file):
        os.unlink(output_file)

except Exception as e:
    print(f"✗ 命令行接口测试失败: {e}")

print("\n测试完成!")