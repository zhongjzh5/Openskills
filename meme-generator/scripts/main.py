#!/usr/bin/env python3
"""
meme-generator 主脚本
智能表情包生成器 - 根据对话情景和个人喜好自动生成或爬取表情包
"""

import json
import sys
import os
import argparse
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

try:
    from pydantic import BaseModel, Field, ValidationError, field_validator
    import requests
    from PIL import Image, ImageDraw, ImageFont
    HAS_DEPENDENCIES = True
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: pip install -r requirements.txt")
    HAS_DEPENDENCIES = False
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 常量定义
class SourceType(str, Enum):
    GENERATE = "generate"
    SEARCH = "search"
    BOTH = "both"

class OutputFormat(str, Enum):
    IMAGE = "image"
    LINK = "link"
    BOTH = "both"

# 数据模型
class Preferences(BaseModel):
    """用户偏好设置"""
    style: str = Field(default="搞笑", description="表情包风格")
    humor_level: int = Field(default=3, ge=1, le=5, description="幽默等级 1-5")
    language: str = Field(default="zh", description="语言")
    favorite_templates: List[str] = Field(default_factory=list, description="常用模板")
    avoid_topics: List[str] = Field(default_factory=list, description="避免的话题")

class Options(BaseModel):
    """生成选项"""
    source: SourceType = Field(default=SourceType.BOTH, description="来源类型")
    output_format: OutputFormat = Field(default=OutputFormat.IMAGE, description="输出格式")
    max_results: int = Field(default=3, ge=1, le=10, description="最大结果数")
    size: str = Field(default="medium", description="图片尺寸")

class InputModel(BaseModel):
    """输入数据模型"""
    context: str = Field(..., min_length=10, max_length=1000, description="对话上下文")
    user_input: str = Field(..., min_length=2, max_length=200, description="用户输入")
    preferences: Preferences = Field(default_factory=Preferences, description="用户偏好")
    options: Options = Field(default_factory=Options, description="生成选项")

class MemeItem(BaseModel):
    """表情包项"""
    type: str = Field(..., description="类型: generated|searched")
    url: str = Field(..., description="图片链接或本地路径")
    caption: str = Field(..., description="文字描述")
    tags: List[str] = Field(default_factory=list, description="标签")
    source: str = Field(..., description="来源说明")
    match_score: float = Field(..., ge=0.0, le=1.0, description="匹配分数")

class OutputModel(BaseModel):
    """输出数据模型"""
    status: str = Field(..., description="状态: success|partial|error")
    message: str = Field(..., description="处理结果描述")
    memes: List[MemeItem] = Field(default_factory=list, description="表情包列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

# 模板管理器
class TemplateManager:
    """本地模板管理器"""

    def __init__(self, template_dir: Optional[Path] = None):
        if template_dir is None:
            self.template_dir = Path(__file__).parent.parent / "assets" / "templates"
        else:
            self.template_dir = template_dir

        # 确保模板目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # 内置模板配置
        self.builtin_templates = {
            "doge": {
                "name": "神烦狗",
                "description": "经典神烦狗表情包",
                "tags": ["搞笑", "狗", "多字"],
                "style": "搞笑",
                "text_positions": [(50, 50), (300, 100)]
            },
            "drake": {
                "name": "Drake Hotline Bling",
                "description": "Drake手势表情包",
                "tags": ["选择", "对比", "手势"],
                "style": "吐槽",
                "text_positions": [(200, 50), (200, 250)]
            },
            "change_my_mind": {
                "name": "改变我的心意",
                "description": "校园桌表情包",
                "tags": ["辩论", "坚持", "说服"],
                "style": "讽刺",
                "text_positions": [(100, 300)]
            },
            "distracted_boyfriend": {
                "name": "分心的男友",
                "description": "经典三角关系表情包",
                "tags": ["选择", "分心", "关系"],
                "style": "吐槽",
                "text_positions": [(100, 50), (300, 50), (200, 300)]
            },
            "two_buttons": {
                "name": "两个按钮",
                "description": "难以抉择的表情包",
                "tags": ["选择", "困难", "纠结"],
                "style": "搞笑",
                "text_positions": [(150, 100), (400, 100)]
            }
        }

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """获取可用模板列表"""
        templates = []

        # 添加内置模板
        for template_id, config in self.builtin_templates.items():
            templates.append({
                "id": template_id,
                **config
            })

        # 扫描本地模板文件
        for file_path in self.template_dir.glob("*.png"):
            template_id = file_path.stem
            if template_id not in self.builtin_templates:
                templates.append({
                    "id": template_id,
                    "name": template_id,
                    "description": "本地自定义模板",
                    "tags": ["自定义"],
                    "style": "自定义",
                    "text_positions": [(100, 100)]  # 默认位置
                })

        return templates

    def create_meme_from_template(
        self,
        template_id: str,
        texts: List[str],
        output_path: Path
    ) -> bool:
        """使用模板创建表情包"""
        try:
            # 检查是否内置模板
            if template_id in self.builtin_templates:
                # 对于内置模板，创建一个示例图片
                return self._create_builtin_meme(template_id, texts, output_path)
            else:
                # 对于本地模板，尝试加载图片
                template_path = self.template_dir / f"{template_id}.png"
                if template_path.exists():
                    return self._create_from_image(template_path, texts, output_path)
                else:
                    logger.warning(f"模板不存在: {template_id}")
                    return False

        except Exception as e:
            logger.error(f"创建表情包失败: {e}")
            return False

    def _get_font(self, size: int = 24) -> ImageFont.FreeTypeFont:
        """获取适合当前系统的字体"""
        import sys

        # 字体路径列表，按优先级尝试
        font_paths = []

        if sys.platform == "win32":
            # Windows 字体路径
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/arial.ttf",  # Arial
            ]
        elif sys.platform == "darwin":
            # macOS 字体路径
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # 苹方
                "/System/Library/Fonts/Helvetica.ttc",  # Helvetica
                "/System/Library/Fonts/Arial.ttf",  # Arial
            ]
        else:
            # Linux 字体路径
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # DejaVu Sans
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Liberation Sans
            ]

        # 首先尝试项目字体目录
        project_font_dir = Path(__file__).parent.parent / "assets" / "fonts"
        if project_font_dir.exists():
            for font_file in project_font_dir.glob("*.ttf"):
                font_paths.insert(0, str(font_file))
            for font_file in project_font_dir.glob("*.ttc"):
                font_paths.insert(0, str(font_file))
            for font_file in project_font_dir.glob("*.otf"):
                font_paths.insert(0, str(font_file))

        # 尝试加载字体
        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue

        # 所有尝试都失败，返回默认字体
        logger.warning("无法加载系统字体，使用默认字体")
        return ImageFont.load_default()

    def _create_builtin_meme(
        self,
        template_id: str,
        texts: List[str],
        output_path: Path
    ) -> bool:
        """创建内置模板表情包（改进的实现）"""
        try:
            width, height = 600, 400
            template_config = self.builtin_templates[template_id]

            # 根据模板ID创建不同的背景和图形
            if template_id == "doge":
                # 神烦狗风格 - 黄色背景，多文字区域
                image = Image.new('RGB', (width, height), color='#FFD700')  # 金色
                draw = ImageDraw.Draw(image)

                # 绘制简单的狗头轮廓
                draw.ellipse([(100, 50), (250, 200)], outline='black', width=3)  # 头部
                draw.ellipse([(130, 80), (160, 110)], fill='black')  # 左眼
                draw.ellipse([(190, 80), (220, 110)], fill='black')  # 右眼

                # 文字位置
                text_positions = [(50, 220), (300, 220), (50, 300), (300, 300)]

            elif template_id == "drake":
                # Drake手势 - 两个对比区域
                image = Image.new('RGB', (width, height), color='#1E1E1E')  # 深灰背景
                draw = ImageDraw.Draw(image)

                # 绘制两个对比区域
                draw.rectangle([(50, 50), (275, 350)], fill='#4CAF50', outline='white', width=2)  # 绿色区域
                draw.rectangle([(325, 50), (550, 350)], fill='#F44336', outline='white', width=2)  # 红色区域

                # 文字位置
                text_positions = [(100, 150), (375, 150)]

            elif template_id == "change_my_mind":
                # 改变心意 - 演讲台风格
                image = Image.new('RGB', (width, height), color='#E3F2FD')  # 浅蓝背景
                draw = ImageDraw.Draw(image)

                # 绘制演讲台
                draw.rectangle([(150, 150), (450, 250)], fill='#795548', outline='black', width=2)  # 桌子
                draw.ellipse([(275, 100), (325, 150)], fill='#FFC107')  # 麦克风

                # 文字位置
                text_positions = [(200, 170)]

            elif template_id == "distracted_boyfriend":
                # 分心的男友 - 三人场景
                image = Image.new('RGB', (width, height), color='#FFF3E0')  # 浅橙背景
                draw = ImageDraw.Draw(image)

                # 绘制三个人物轮廓
                draw.ellipse([(100, 100), (180, 180)], fill='#2196F3', outline='black', width=2)  # 男友
                draw.ellipse([(250, 150), (330, 230)], fill='#E91E63', outline='black', width=2)  # 女友
                draw.ellipse([(400, 100), (480, 180)], fill='#9C27B0', outline='black', width=2)  # 其他女生

                # 视线连线
                draw.line([(140, 140), (260, 170)], fill='red', width=3)

                # 文字位置
                text_positions = [(110, 190), (260, 240), (410, 190)]

            elif template_id == "two_buttons":
                # 两个按钮 - 选择困难
                image = Image.new('RGB', (width, height), color='#F5F5F5')  # 浅灰背景
                draw = ImageDraw.Draw(image)

                # 绘制两个按钮
                draw.rounded_rectangle([(100, 150), (280, 250)], radius=20, fill='#2196F3', outline='black', width=2)
                draw.rounded_rectangle([(320, 150), (500, 250)], radius=20, fill='#4CAF50', outline='black', width=2)

                # 文字位置
                text_positions = [(150, 180), (370, 180)]

            else:
                # 默认模板
                image = Image.new('RGB', (width, height), color='white')
                draw = ImageDraw.Draw(image)
                text_positions = template_config.get('text_positions', [(100, 100)])

            # 获取字体
            font = self._get_font(24)

            # 绘制模板标题
            draw.text((10, 10), f"模板: {template_config['name']}", fill='black', font=font)

            # 绘制文字
            for i, (text, pos) in enumerate(zip(texts, text_positions)):
                if i < len(text_positions):
                    # 为文字添加背景框增强可读性
                    text_bbox = draw.textbbox(pos, text, font=font)
                    padding = 5
                    draw.rectangle(
                        [text_bbox[0]-padding, text_bbox[1]-padding,
                         text_bbox[2]+padding, text_bbox[3]+padding],
                        fill='rgba(255, 255, 255, 200)',  # 半透明白色背景
                        outline='black',
                        width=1
                    )
                    draw.text(pos, text, fill='black', font=font)

            # 保存图片
            image.save(output_path, 'PNG')
            logger.info(f"创建表情包: {output_path}")
            return True

        except Exception as e:
            logger.error(f"创建内置模板失败: {e}")
            return False

    def _create_from_image(
        self,
        image_path: Path,
        texts: List[str],
        output_path: Path
    ) -> bool:
        """从图片文件创建表情包"""
        try:
            # 打开图片
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            # 使用改进的字体获取方法
            font = self._get_font(36)

            # 在固定位置添加文字（简化实现）
            positions = [(50, 50), (50, 150), (50, 250)]
            for i, text in enumerate(texts):
                if i < len(positions):
                    draw.text(positions[i], text, fill='white', font=font, stroke_width=2, stroke_fill='black')

            # 保存图片
            image.save(output_path, 'PNG')
            return True

        except Exception as e:
            logger.error(f"从图片创建失败: {e}")
            return False

# API客户端
class MemeAPIClient:
    """外部API客户端，支持多个表情包API"""

    def __init__(self, api_keys: Dict[str, Any] = None):
        self.api_keys = api_keys or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MemeGenerator/1.0 (OpenSkills)'
        })
        self.timeout = (5, 10)  # 连接5秒，读取10秒超时

    def search_memes(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索表情包，支持多个API源"""
        logger.info(f"搜索表情包: {query}, 限制: {limit}")
        results = []

        # 尝试Giphy API
        giphy_results = self._search_giphy(query, limit)
        if giphy_results:
            results.extend(giphy_results)

        # 尝试Tenor API
        tenor_results = self._search_tenor(query, limit)
        if tenor_results:
            results.extend(tenor_results)

        # 如果都没有结果，返回模拟数据
        if not results:
            results = self._get_mock_results(query, limit)

        # 限制结果数量
        return results[:limit]

    def generate_with_api(self, template_id: str, texts: List[str]) -> Optional[Dict[str, Any]]:
        """使用API生成表情包"""
        logger.info(f"API生成: 模板={template_id}, 文字={texts}")

        # 首先尝试Imgflip API
        imgflip_result = self._generate_with_imgflip(template_id, texts)
        if imgflip_result:
            return imgflip_result

        # 如果失败，尝试其他API或返回模拟数据
        logger.warning(f"API生成失败，使用模拟数据")
        return self._get_mock_generation(template_id, texts)

    def _search_giphy(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """使用Giphy API搜索表情包"""
        api_key = self.api_keys.get('giphy')
        if not api_key:
            logger.debug("Giphy API密钥未配置")
            return []

        try:
            # Giphy API端点
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                'api_key': api_key,
                'q': query,
                'limit': limit,
                'lang': 'en',
                'rating': 'pg-13'  # 安全等级
            }

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = []
            for gif in data.get('data', [])[:limit]:
                # 获取GIF的静态图片版本
                images = gif.get('images', {})
                preview_url = images.get('fixed_height', {}).get('url', '')
                if not preview_url:
                    preview_url = gif.get('url', '')

                results.append({
                    "type": "searched",
                    "url": preview_url,
                    "caption": gif.get('title', f"GIF: {query}"),
                    "tags": [query, "gif", "animated"],
                    "source": "Giphy",
                    "match_score": 0.8
                })

            logger.info(f"从Giphy获取到 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.warning(f"Giphy API调用失败: {e}")
            return []

    def _search_tenor(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """使用Tenor API搜索表情包"""
        api_key = self.api_keys.get('tenor')
        if not api_key:
            logger.debug("Tenor API密钥未配置")
            return []

        try:
            url = "https://tenor.googleapis.com/v2/search"
            params = {
                'key': api_key,
                'q': query,
                'limit': limit,
                'media_filter': 'minimal',  # 最小化数据
                'content_filter': 'high'    # 高内容安全
            }

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get('results', [])[:limit]:
                # 获取GIF的媒体信息
                media_formats = result.get('media_formats', {})
                gif_info = media_formats.get('gif', {})
                preview_url = gif_info.get('url', result.get('url', ''))

                results.append({
                    "type": "searched",
                    "url": preview_url,
                    "caption": result.get('content_description', f"Tenor GIF: {query}"),
                    "tags": [query, "gif", "tenor"] + result.get('tags', []),
                    "source": "Tenor",
                    "match_score": 0.75
                })

            logger.info(f"从Tenor获取到 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.warning(f"Tenor API调用失败: {e}")
            return []

    def _generate_with_imgflip(self, template_id: str, texts: List[str]) -> Optional[Dict[str, Any]]:
        """使用Imgflip API生成表情包"""
        # 需要Imgflip账户的用户名和密码（或API密钥）
        username = self.api_keys.get('imgflip', {}).get('username')
        password = self.api_keys.get('imgflip', {}).get('password')

        if not username or not password:
            logger.debug("Imgflip API凭证未配置")
            return None

        # 映射模板ID到Imgflip的模板ID
        template_mapping = {
            'doge': 8072285,      # 神烦狗
            'drake': 181913649,   # Drake Hotline Bling
            'change_my_mind': 129242436,  # 改变心意
            'distracted_boyfriend': 112126428,  # 分心的男友
            'two_buttons': 87743020  # 两个按钮
        }

        imgflip_template_id = template_mapping.get(template_id)
        if not imgflip_template_id:
            logger.warning(f"Imgflip不支持模板: {template_id}")
            return None

        try:
            url = "https://api.imgflip.com/caption_image"
            data = {
                'template_id': imgflip_template_id,
                'username': username,
                'password': password,
                'text0': texts[0] if len(texts) > 0 else '',
                'text1': texts[1] if len(texts) > 1 else '',
                'text2': texts[2] if len(texts) > 2 else '',
                'text3': texts[3] if len(texts) > 3 else '',
                'text4': texts[4] if len(texts) > 4 else '',
            }

            response = self.session.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            if result.get('success', False):
                return {
                    "type": "generated",
                    "url": result['data']['url'],
                    "caption": " | ".join(texts),
                    "tags": ["API生成", template_id, "imgflip"],
                    "source": "Imgflip API",
                    "match_score": 0.95
                }
            else:
                logger.warning(f"Imgflip API返回错误: {result.get('error_message', 'Unknown error')}")
                return None

        except Exception as e:
            logger.warning(f"Imgflip API调用失败: {e}")
            return None

    def _get_mock_results(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取模拟搜索结果（当API不可用时）"""
        logger.info(f"使用模拟搜索结果: {query}")

        mock_results = [
            {
                "type": "searched",
                "url": f"https://api.memegen.link/images/buzz/{i}.png",
                "caption": f"关于 '{query}' 的示例表情包 {i}",
                "tags": [query, "示例", "搞笑"],
                "source": "示例API",
                "match_score": 0.9 - (i * 0.1)
            }
            for i in range(1, limit + 1)
        ]

        return mock_results[:limit]

    def _get_mock_generation(self, template_id: str, texts: List[str]) -> Dict[str, Any]:
        """获取模拟生成结果（当API不可用时）"""
        return {
            "type": "generated",
            "url": f"https://api.memegen.link/images/{template_id}/{'_'.join(texts[:2]) or 'meme'}.png",
            "caption": " | ".join(texts) or "生成的表情包",
            "tags": ["API生成", template_id, "示例"],
            "source": "示例生成API",
            "match_score": 0.85
        }

# 上下文分析器
class ContextAnalyzer:
    """对话上下文分析器"""

    def __init__(self):
        # 简单的情感关键词映射
        self.emotion_keywords = {
            "开心": ["开心", "高兴", "快乐", "哈哈", "呵呵", "好笑", "欢乐"],
            "生气": ["生气", "愤怒", "恼火", "烦人", "讨厌", "可恶"],
            "悲伤": ["悲伤", "难过", "伤心", "失望", "郁闷", "泪"],
            "惊讶": ["惊讶", "惊奇", "震惊", "意外", "没想到"],
            "尴尬": ["尴尬", "窘迫", "不好意思", "丢脸"]
        }

        # 话题关键词
        self.topic_keywords = {
            "工作": ["工作", "上班", "加班", "项目", "任务", "deadline", "代码", "编程", "开发", "bug"],
            "学习": ["学习", "考试", "作业", "课程", "学校", "老师", "复习", "上课", "学习"],
            "生活": ["生活", "日常", "吃饭", "睡觉", "休息", "周末", "家庭", "朋友", "购物"],
            "科技": ["科技", "电脑", "手机", "软件", "编程", "AI", "互联网", "技术", "数码"],
            "娱乐": ["娱乐", "电影", "音乐", "游戏", "电视剧", "综艺", "体育", "旅游", "聚会"]
        }

    def analyze(self, context: str, user_input: str) -> Dict[str, Any]:
        """分析对话上下文"""
        text = f"{context} {user_input}"
        text_lower = text.lower()

        # 检测情感
        emotions = []
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotions.append(emotion)
                    break

        # 检测话题
        topics = []
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    topics.append(topic)
                    break

        # 提取关键词
        # 中文停用词
        stop_words = {"的", "了", "在", "是", "和", "与", "或", "就", "都", "而", "及", "以及", "这", "那", "今天", "明天"}

        # 分割文本为单词（英文）和字符（中文）
        words = []
        current_word = ""
        chinese_chars = []  # 收集连续中文字符

        for char in text_lower:
            if char.isalpha() and not ('\u4e00' <= char <= '\u9fff'):  # 英文字母
                current_word += char
            elif '\u4e00' <= char <= '\u9fff':  # 中文字符
                chinese_chars.append(char)
                if current_word:
                    words.append(current_word)
                    current_word = ""
            else:  # 非字母字符（空格、标点等）
                if current_word:
                    words.append(current_word)
                    current_word = ""
                if chinese_chars:
                    # 添加中文字符作为单个字符
                    words.extend(chinese_chars)
                    # 也添加2-3个字符的组合作为可能词语
                    for i in range(len(chinese_chars) - 1):
                        words.append(chinese_chars[i] + chinese_chars[i + 1])
                    chinese_chars = []

        if current_word:
            words.append(current_word)
        if chinese_chars:
            words.extend(chinese_chars)
            for i in range(len(chinese_chars) - 1):
                words.append(chinese_chars[i] + chinese_chars[i + 1])

        # 过滤停用词和短词
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        # 去重并限制数量
        unique_keywords = []
        seen = set()
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique_keywords.append(word)

        return {
            "emotions": list(set(emotions)),
            "topics": list(set(topics)),
            "keywords": unique_keywords[:10],  # 取前10个关键词
            "text_length": len(text),
            "has_question": "?" in text or "？" in text
        }

# 用户偏好管理器
class UserPreferenceManager:
    """管理用户偏好学习和个性化推荐"""

    def __init__(self, user_id: Optional[str] = None, data_dir: Optional[Path] = None):
        self.user_id = user_id or "default"

        # 确定数据目录
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = Path.home() / ".meme-generator" / "users" / self.user_id

        # 创建目录
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.preferences_file = self.data_dir / "preferences.json"
        self.history_file = self.data_dir / "history.jsonl"
        self.feedback_file = self.data_dir / "feedback.jsonl"

        # 学习参数
        self.learning_rate = 0.1  # 学习速率
        self.decay_factor = 0.99  # 衰减因子
        self.max_history_size = 1000

        # 加载现有偏好
        self.preferences = self._load_preferences()
        self.history = self._load_history()

    def _load_preferences(self) -> Dict[str, Any]:
        """加载用户偏好"""
        default_preferences = {
            "style_weights": {
                "搞笑": 1.0,
                "讽刺": 1.0,
                "可爱": 1.0,
                "吐槽": 1.0,
                "励志": 1.0
            },
            "template_weights": {},  # 模板ID -> 权重
            "topic_weights": {},     # 话题 -> 权重
            "emotion_weights": {},   # 情感 -> 权重
            "humor_level": 3.0,      # 平均幽默等级
            "preferred_templates": [],
            "avoided_templates": [],
            "preferred_topics": [],
            "avoided_topics": [],
            "interaction_count": 0,
            "last_updated": None
        }

        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    saved_prefs = json.load(f)
                    # 合并默认值和保存的值
                    for key, value in saved_prefs.items():
                        if key in default_preferences:
                            default_preferences[key] = value
            except Exception as e:
                logger.warning(f"加载用户偏好失败: {e}")

        return default_preferences

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载用户历史记录"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            history.append(json.loads(line))
            except Exception as e:
                logger.warning(f"加载历史记录失败: {e}")

        # 限制历史记录大小
        if len(history) > self.max_history_size:
            history = history[-self.max_history_size:]

        return history

    def save_preferences(self):
        """保存用户偏好"""
        try:
            self.preferences["last_updated"] = datetime.now().isoformat()
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存用户偏好失败: {e}")

    def record_interaction(self,
                          input_data: InputModel,
                          output: OutputModel,
                          selected_index: Optional[int] = None,
                          feedback_score: Optional[float] = None):
        """记录用户交互"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "input": {
                "context": input_data.context[:100],  # 截断避免过大
                "user_input": input_data.user_input,
                "preferences": input_data.preferences.dict(),
                "options": input_data.options.dict()
            },
            "output": {
                "status": output.status,
                "meme_count": len(output.memes),
                "memes": [
                    {
                        "type": meme.type,
                        "caption": meme.caption[:50],
                        "tags": meme.tags,
                        "source": meme.source,
                        "match_score": meme.match_score
                    }
                    for meme in output.memes[:5]  # 限制数量
                ]
            },
            "selection": selected_index,
            "feedback": feedback_score
        }

        # 添加到历史
        self.history.append(interaction)

        # 保存到文件
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(interaction, ensure_ascii=False, default=str) + '\n')
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")

        # 更新偏好
        self._update_preferences(interaction, selected_index, feedback_score)

        # 增加交互计数
        self.preferences["interaction_count"] = self.preferences.get("interaction_count", 0) + 1

    def _update_preferences(self,
                           interaction: Dict[str, Any],
                           selected_index: Optional[int],
                           feedback_score: Optional[float]):
        """基于交互更新偏好"""
        if selected_index is None and feedback_score is None:
            return  # 没有反馈，不更新

        input_prefs = interaction["input"]["preferences"]
        output_memes = interaction["output"]["memes"]

        # 如果有选择，更新选中表情包的相关权重
        if selected_index is not None and 0 <= selected_index < len(output_memes):
            selected_meme = output_memes[selected_index]

            # 更新风格权重
            style = input_prefs.get("style", "搞笑")
            current_weight = self.preferences["style_weights"].get(style, 1.0)
            self.preferences["style_weights"][style] = current_weight + self.learning_rate

            # 更新模板权重
            source = selected_meme.get("source", "")
            if "模板:" in source:
                # 提取模板ID
                template_info = source.split("模板:")[1].strip()
                template_name = template_info.split()[0] if " " in template_info else template_info
                current_weight = self.preferences["template_weights"].get(template_name, 1.0)
                self.preferences["template_weights"][template_name] = current_weight + self.learning_rate

            # 更新话题权重
            tags = selected_meme.get("tags", [])
            for tag in tags[:3]:  # 只取前3个标签
                current_weight = self.preferences["topic_weights"].get(tag, 1.0)
                self.preferences["topic_weights"][tag] = current_weight + self.learning_rate

        # 如果有反馈分数，更新幽默等级
        if feedback_score is not None:
            current_humor = self.preferences.get("humor_level", 3.0)
            # 指数移动平均
            self.preferences["humor_level"] = (current_humor * (1 - self.learning_rate) +
                                              feedback_score * self.learning_rate)

        # 应用衰减（让旧偏好逐渐减弱）
        for key in ["style_weights", "template_weights", "topic_weights", "emotion_weights"]:
            if key in self.preferences:
                for subkey in self.preferences[key]:
                    self.preferences[key][subkey] *= self.decay_factor

        # 保存更新
        self.save_preferences()

    def get_personalized_preferences(self, base_preferences: Preferences) -> Preferences:
        """获取个性化偏好（结合用户历史）"""
        personalized = base_preferences.dict()

        # 如果有足够的交互历史，调整偏好
        if self.preferences["interaction_count"] > 10:
            # 调整风格偏好
            style_weights = self.preferences["style_weights"]
            if style_weights:
                most_preferred = max(style_weights.items(), key=lambda x: x[1])[0]
                if personalized["style"] == "搞笑":  # 如果是默认值
                    personalized["style"] = most_preferred

            # 调整幽默等级
            learned_humor = self.preferences["humor_level"]
            if learned_humor > 0:
                # 混合用户设置和学习值
                personalized["humor_level"] = int(round(
                    personalized["humor_level"] * 0.3 + learned_humor * 0.7
                ))
                # 确保在1-5范围内
                personalized["humor_level"] = max(1, min(5, personalized["humor_level"]))

            # 添加常用模板到偏好
            template_weights = self.preferences["template_weights"]
            if template_weights:
                top_templates = sorted(template_weights.items(), key=lambda x: x[1], reverse=True)[:3]
                top_template_ids = [template_id for template_id, _ in top_templates]
                # 合并但不重复
                existing = set(personalized.get("favorite_templates", []))
                for template_id in top_template_ids:
                    if template_id not in existing:
                        personalized.setdefault("favorite_templates", []).append(template_id)

        return Preferences(**personalized)

    def get_recommendations(self, context: str, user_input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """基于用户历史获取推荐"""
        # 简单实现：从历史中寻找相似场景
        recommendations = []

        if not self.history:
            return recommendations

        # 分析当前上下文
        from .main import ContextAnalyzer
        analyzer = ContextAnalyzer()
        current_analysis = analyzer.analyze(context, user_input)

        # 寻找相似历史
        for record in self.history[-50:]:  # 最近50条记录
            hist_input = record["input"]
            hist_context = hist_input["context"]
            hist_user_input = hist_input["user_input"]

            # 简单相似度计算（基于共同关键词）
            hist_analysis = analyzer.analyze(hist_context, hist_user_input)
            common_topics = set(current_analysis["topics"]) & set(hist_analysis["topics"])
            common_emotions = set(current_analysis["emotions"]) & set(hist_analysis["emotions"])

            similarity = len(common_topics) * 0.5 + len(common_emotions) * 0.3

            if similarity > 0.3:  # 相似度阈值
                for meme in record["output"]["memes"]:
                    recommendations.append({
                        "meme_info": meme,
                        "similarity": similarity,
                        "timestamp": record["timestamp"]
                    })

        # 按相似度排序
        recommendations.sort(key=lambda x: x["similarity"], reverse=True)
        return recommendations[:limit]

    def clear_history(self):
        """清除用户历史记录"""
        self.history = []
        if self.history_file.exists():
            self.history_file.unlink()
        if self.feedback_file.exists():
            self.feedback_file.unlink()
        logger.info(f"已清除用户 {self.user_id} 的历史记录")

    def export_data(self, output_path: Path):
        """导出用户数据"""
        data = {
            "user_id": self.user_id,
            "preferences": self.preferences,
            "history": self.history,
            "export_date": datetime.now().isoformat()
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"用户数据已导出到: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出用户数据失败: {e}")
            return False

# 主处理器
class MemeGenerator:
    """表情包生成器主类"""

    def __init__(self, config_path: Optional[Path] = None, user_id: Optional[str] = None):
        self.template_manager = TemplateManager()

        # 先加载配置，因为API客户端需要API密钥
        self.config = self._load_config(config_path)

        # 创建API客户端，传递API密钥
        self.api_client = MemeAPIClient(self.config.get("api_keys", {}))
        self.context_analyzer = ContextAnalyzer()

        # 创建用户偏好管理器
        self.user_prefs = None
        if self.config.get("user_preferences", {}).get("learning_enabled", True):
            data_dir = Path(self.config.get("storage", {}).get("data_dir", "user_data"))
            self.user_prefs = UserPreferenceManager(user_id=user_id, data_dir=data_dir)

        # 创建输出目录
        self.output_dir = Path(self.config.get("output_dir", "output"))
        self.output_dir.mkdir(exist_ok=True)

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """加载配置文件，支持环境变量覆盖"""
        # 完整默认配置
        default_config = {
            "api_keys": {
                "imgflip": {"username": "", "password": ""},
                "giphy": "",
                "tenor": ""
            },
            "storage": {
                "output_dir": "output",
                "cache_dir": "cache",
                "max_cache_size_mb": 500,
                "cleanup_days": 30,
                "backup_enabled": False,
                "backup_dir": "backups"
            },
            "generation": {
                "default_style": "搞笑",
                "default_language": "zh",
                "quality": "medium",
                "max_text_length": 20,
                "default_font_size": 24,
                "text_stroke_width": 2,
                "text_stroke_color": "#000000",
                "min_contrast_ratio": 4.5
            },
            "safety": {
                "content_filter": True,
                "max_downloads_per_day": 100,
                "require_confirmation": True,
                "blocked_keywords": ["政治", "暴力", "色情", "仇恨", "歧视"],
                "allowed_domains": ["imgflip.com", "giphy.com", "tenor.com", "memegen.link"],
                "user_consent_required": True
            },
            "performance": {
                "max_workers": 3,
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "connection_timeout": 5,
                "read_timeout": 10,
                "cache_enabled": True,
                "cache_ttl_hours": 24
            },
            "user_preferences": {
                "learning_enabled": True,
                "history_size": 100,
                "personalization_strength": 0.7,
                "default_preferences": {
                    "style": "搞笑",
                    "humor_level": 3,
                    "language": "zh",
                    "favorite_templates": ["doge", "drake"],
                    "avoid_topics": ["政治", "宗教"]
                }
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_file_size_mb": 10,
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "advanced": {
                "context_analysis_depth": "medium",
                "matching_algorithm": "hybrid",
                "template_auto_update": True,
                "api_fallback_order": ["imgflip", "giphy", "tenor", "local"],
                "experimental_features": False,
                "debug_mode": False
            }
        }

        # 1. 加载配置文件
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 深度合并配置
                    self._deep_update(default_config, user_config)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")

        # 2. 应用环境变量覆盖
        default_config = self._apply_env_overrides(default_config)

        return default_config

    def _deep_update(self, original: Dict[str, Any], update: Dict[str, Any]) -> None:
        """深度更新字典，递归合并嵌套字典"""
        for key, value in update.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖配置"""
        import os

        # API密钥环境变量
        if os.getenv("MEME_GENERATOR_IMGFLIP_USERNAME"):
            config["api_keys"]["imgflip"]["username"] = os.getenv("MEME_GENERATOR_IMGFLIP_USERNAME")
        if os.getenv("MEME_GENERATOR_IMGFLIP_PASSWORD"):
            config["api_keys"]["imgflip"]["password"] = os.getenv("MEME_GENERATOR_IMGFLIP_PASSWORD")
        if os.getenv("MEME_GENERATOR_GIPHY_API_KEY"):
            config["api_keys"]["giphy"] = os.getenv("MEME_GENERATOR_GIPHY_API_KEY")
        if os.getenv("MEME_GENERATOR_TENOR_API_KEY"):
            config["api_keys"]["tenor"] = os.getenv("MEME_GENERATOR_TENOR_API_KEY")

        # 存储设置
        if os.getenv("MEME_GENERATOR_CACHE_DIR"):
            config["storage"]["cache_dir"] = os.getenv("MEME_GENERATOR_CACHE_DIR")
        if os.getenv("MEME_GENERATOR_OUTPUT_DIR"):
            config["storage"]["output_dir"] = os.getenv("MEME_GENERATOR_OUTPUT_DIR")

        # 性能设置
        if os.getenv("MEME_GENERATOR_MAX_WORKERS"):
            config["performance"]["max_workers"] = int(os.getenv("MEME_GENERATOR_MAX_WORKERS"))
        if os.getenv("MEME_GENERATOR_TIMEOUT_SECONDS"):
            config["performance"]["timeout_seconds"] = int(os.getenv("MEME_GENERATOR_TIMEOUT_SECONDS"))

        # 调试设置
        if os.getenv("MEME_GENERATOR_DEBUG"):
            config["advanced"]["debug_mode"] = os.getenv("MEME_GENERATOR_DEBUG").lower() == "true"
            if config["advanced"]["debug_mode"]:
                config["logging"]["level"] = "DEBUG"

        # 日志级别
        if os.getenv("MEME_GENERATOR_LOG_LEVEL"):
            config["logging"]["level"] = os.getenv("MEME_GENERATOR_LOG_LEVEL")

        return config

    def _apply_personalization(self, input_data: InputModel) -> InputModel:
        """应用个性化学习到输入数据"""
        if not self.user_prefs:
            return input_data

        try:
            # 获取个性化偏好
            personalized_prefs = self.user_prefs.get_personalized_preferences(input_data.preferences)

            # 创建新的InputModel
            personalized_input = InputModel(
                context=input_data.context,
                user_input=input_data.user_input,
                preferences=personalized_prefs,
                options=input_data.options
            )

            logger.debug(f"已应用个性化偏好: {personalized_prefs.dict()}")
            return personalized_input

        except Exception as e:
            logger.warning(f"应用个性化偏好失败: {e}")
            return input_data

    def process(self, input_data: InputModel, record_interaction: bool = True) -> OutputModel:
        """处理生成请求"""
        start_time = datetime.now()

        try:
            # 应用个性化偏好
            personalized_input = self._apply_personalization(input_data)

            # 分析上下文
            analysis = self.context_analyzer.analyze(
                personalized_input.context,
                personalized_input.user_input
            )

            logger.info(f"上下文分析: {analysis}")

            # 根据选项决定生成策略
            memes = []

            if personalized_input.options.source in [SourceType.GENERATE, SourceType.BOTH]:
                generated = self._generate_memes(personalized_input, analysis)
                memes.extend(generated)

            if personalized_input.options.source in [SourceType.SEARCH, SourceType.BOTH]:
                searched = self._search_memes(personalized_input, analysis)
                memes.extend(searched)

            # 限制结果数量
            memes = memes[:personalized_input.options.max_results]

            # 准备输出
            processing_time = (datetime.now() - start_time).total_seconds()

            output = OutputModel(
                status="success" if memes else "partial",
                message=f"成功生成 {len(memes)} 个表情包" if memes else "未找到匹配的表情包",
                memes=memes,
                metadata={
                    "processing_time": processing_time,
                    "analysis": analysis,
                    "preferences_applied": personalized_input.preferences.dict(),
                    "options_used": personalized_input.options.dict(),
                    "personalization_applied": personalized_input is not input_data
                }
            )

            # 记录交互（如果启用）
            if record_interaction and self.user_prefs:
                try:
                    self.user_prefs.record_interaction(input_data, output)
                    logger.debug("已记录用户交互")
                except Exception as e:
                    logger.warning(f"记录用户交互失败: {e}")

            return output

        except Exception as e:
            logger.error(f"处理失败: {e}")
            return OutputModel(
                status="error",
                message=f"处理失败: {str(e)}",
                memes=[],
                metadata={"error": str(e), "processing_time": (datetime.now() - start_time).total_seconds()}
            )

    def _generate_memes(self, input_data: InputModel, analysis: Dict[str, Any]) -> List[MemeItem]:
        """生成表情包"""
        memes = []

        # 获取可用模板
        templates = self.template_manager.get_available_templates()

        # 根据偏好筛选模板
        filtered_templates = self._filter_templates(templates, input_data.preferences, analysis)

        # 为每个模板生成表情包
        for template in filtered_templates[:3]:  # 最多3个模板
            # 生成文字内容
            texts = self._generate_texts(template, input_data, analysis)

            # 创建输出文件
            output_filename = f"meme_{template['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            output_path = self.output_dir / output_filename

            # 生成图片
            if self.template_manager.create_meme_from_template(template['id'], texts, output_path):
                meme = MemeItem(
                    type="generated",
                    url=str(output_path.absolute()),
                    caption=" | ".join(texts),
                    tags=template.get('tags', []) + analysis.get('topics', []),
                    source=f"本地模板: {template['name']}",
                    match_score=self._calculate_match_score(template, input_data.preferences, analysis)
                )
                memes.append(meme)

        return memes

    def _search_memes(self, input_data: InputModel, analysis: Dict[str, Any]) -> List[MemeItem]:
        """搜索表情包"""
        # 构建搜索查询
        query_parts = []

        # 添加情感关键词
        if analysis['emotions']:
            query_parts.append(analysis['emotions'][0])

        # 添加话题关键词
        if analysis['topics']:
            query_parts.append(analysis['topics'][0])

        # 添加用户输入中的关键词
        query_parts.append(input_data.user_input[:20])

        query = " ".join(query_parts)

        # 调用API搜索
        api_results = self.api_client.search_memes(query, limit=input_data.options.max_results)

        # 转换为MemeItem
        memes = []
        for result in api_results:
            meme = MemeItem(**result)
            memes.append(meme)

        return memes

    def _filter_templates(self, templates: List[Dict[str, Any]], preferences: Preferences, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据偏好和上下文筛选模板"""
        filtered = []

        for template in templates:
            score = 0

            # 风格匹配
            if preferences.style in template.get('style', ''):
                score += 2

            # 偏好模板优先
            if template['id'] in preferences.favorite_templates:
                score += 3

            # 话题匹配
            template_tags = set(template.get('tags', []))
            analysis_topics = set(analysis.get('topics', []))
            if template_tags.intersection(analysis_topics):
                score += 1

            # 情感匹配
            if any(emotion in str(template.get('tags', [])) for emotion in analysis.get('emotions', [])):
                score += 1

            if score > 0:
                filtered.append((score, template))

        # 按分数排序
        filtered.sort(key=lambda x: x[0], reverse=True)
        return [template for _, template in filtered]

    def _generate_texts(self, template: Dict[str, Any], input_data: InputModel, analysis: Dict[str, Any]) -> List[str]:
        """生成文字内容"""
        # 这里可以实现更智能的文字生成
        # 目前使用简单的规则

        texts = []

        # 根据情感生成文字
        emotions = analysis.get('emotions', [])
        if emotions:
            emotion_texts = {
                "开心": ["哈哈哈", "笑死我了", "太开心了"],
                "生气": ["气死我了", "太生气了", "无语"],
                "悲伤": ["好难过", "想哭", "伤心"],
                "惊讶": ["惊呆了", "太意外了", "没想到"],
                "尴尬": ["好尴尬", "社死现场", "没脸见人"]
            }

            for emotion in emotions:
                if emotion in emotion_texts:
                    texts.append(emotion_texts[emotion][0])
                    break

        # 添加用户输入的关键词
        words = input_data.user_input.split()
        if words:
            texts.append(words[0])

        # 添加模板相关的文字
        template_name = template.get('name', '')
        if template_name and len(texts) < 2:
            texts.append(f"关于{template_name}")

        # 确保至少有一个文字
        if not texts:
            texts.append("有趣的表情包")

        return texts[:3]  # 最多3段文字

    def _calculate_match_score(self, template: Dict[str, Any], preferences: Preferences, analysis: Dict[str, Any]) -> float:
        """计算匹配分数"""
        score = 0.5  # 基础分

        # 风格匹配
        if preferences.style in template.get('style', ''):
            score += 0.2

        # 偏好模板
        if template['id'] in preferences.favorite_templates:
            score += 0.3

        # 限制在0-1之间
        return min(max(score, 0.0), 1.0)

# 命令行接口
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='智能表情包生成器')

    # 主要参数
    parser.add_argument('--context', type=str, help='对话上下文')
    parser.add_argument('--input', type=str, required=True, help='用户输入指令')

    # 配置文件
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--preferences', type=str, help='偏好配置文件路径')

    # 输出选项
    parser.add_argument('--output', type=str, default='output.json', help='输出文件路径')
    parser.add_argument('--output-dir', type=str, default='output', help='图片输出目录')

    # 调试选项
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--list-templates', action='store_true', help='列出所有模板')

    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()

    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # 检查依赖
    if not HAS_DEPENDENCIES:
        print("缺少必要依赖，请安装requirements.txt中的包")
        return 1

    # 列出模板
    if args.list_templates:
        manager = TemplateManager()
        templates = manager.get_available_templates()
        print(f"可用模板 ({len(templates)}个):")
        for template in templates:
            print(f"  - {template['id']}: {template['name']} ({template['style']})")
        return 0

    # 加载配置文件
    config_path = Path(args.config) if args.config else None
    preferences_path = Path(args.preferences) if args.preferences else None

    # 加载偏好设置
    preferences = Preferences()
    if preferences_path and preferences_path.exists():
        try:
            with open(preferences_path, 'r', encoding='utf-8') as f:
                pref_data = json.load(f)
                preferences = Preferences(**pref_data)
        except Exception as e:
            logger.warning(f"加载偏好设置失败: {e}")

    # 创建输入数据
    try:
        input_data = InputModel(
            context=args.context or "默认对话上下文",
            user_input=args.input,
            preferences=preferences,
            options=Options()  # 使用默认选项
        )
    except ValidationError as e:
        print(f"输入数据验证失败: {e}")
        return 1

    # 创建生成器并处理
    generator = MemeGenerator(config_path)
    output = generator.process(input_data)

    # 输出结果
    output_dict = output.dict()

    # 保存到文件
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2, default=str)

    # 打印摘要
    print(f"状态: {output.status}")
    print(f"消息: {output.message}")
    print(f"生成表情包: {len(output.memes)}个")

    if output.memes:
        print("\n表情包列表:")
        for i, meme in enumerate(output.memes, 1):
            print(f"  {i}. [{meme.type}] {meme.caption}")
            print(f"     来源: {meme.source}, 分数: {meme.match_score:.2f}")
            print(f"     路径: {meme.url}")

    print(f"\n详细结果已保存到: {output_path}")

    return 0 if output.status == "success" else 1

if __name__ == "__main__":
    sys.exit(main())