# perception.py - 多模态感知与知识提取（重构版）
"""
第2段：多模态感知与知识提取
功能：集成大模型、生成思维导图、多模态知识提取、主动学习触发
特点：大模型驱动的思维导图生成、多模态知识提取、主动学习机制
创新：基于大模型的思维导图生成，支持多模态输入的知识提取
"""

import json
import re
import base64
import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import hashlib
import time
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载 .env 文件
except ImportError:
    pass  # 如果没有安装 python-dotenv，继续运行但不会加载 .env 文件

# 导入第1段的基础模块
from foundation import (
    MindMapNode, KnowledgeNode, LearningGoal, LearningLevel, 
    KnowledgeType, GoalScale, ModalityType, MindMapStyle,
    IMindMapGenerator, IMultimodalRecognizer, generate_id,
    FoundationManager
)

# 导入愿景核心
from vision_core import CivilizationalVisionCore, get_vision_core

# ========== 大模型集成配置 ==========

class LLMConfig:
    """大模型配置类"""
    
    def __init__(self):
        # 支持的模型列表
        self.supported_models = {
            "doubao": {
                "name": "豆包大模型",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "model_id": "doubao-seed-1-8-251228",
                "capabilities": ["text_generation", "mindmap_generation", "question_generation"],
                "context_length": 32000,
                "requires_auth": True
            },
            "spark": {
                "name": "讯飞星火大模型",
                "base_url": "https://spark-api-open.xf-yun.com/v1",
                "model_id": "lite",
                "capabilities": ["text_generation", "question_generation"],
                "context_length": 4000,
                "requires_auth": True
            },
            "deepseek": {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com",
                "capabilities": ["text_generation", "mindmap_generation", "question_generation", "code_generation"],
                "context_length": 64000,
                "requires_auth": True
            },
            "openai": {
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1",
                "capabilities": ["text_generation", "mindmap_generation", "question_generation", "vision"],
                "context_length": 128000,
                "requires_auth": True
            },
            "mock": {
                "name": "模拟模型",
                "base_url": "",
                "capabilities": ["text_generation", "mindmap_generation", "question_generation"],
                "context_length": 4000,
                "requires_auth": False
            }
        }

        # 默认模型（使用豆包生成思维导图）
        self.default_model = "doubao"

        # API密钥配置（从环境变量读取）
        self.api_keys = {
            "doubao": os.getenv("DOUBAO_API_KEY", ""),
            "spark": {
                "api_password": os.getenv("SPARK_API_PASSWORD", ""),
                "appid": os.getenv("SPARK_APPID", ""),
                "api_secret": os.getenv("SPARK_API_SECRET", ""),
                "api_key": os.getenv("SPARK_API_KEY", "")
            },
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", "")
        }
        
        # 请求超时配置
        self.timeout = 300.0  # 秒（300秒，思维导图生成较慢）

        # 重试配置
        self.max_retries = 3
        self.retry_delay = 3.0  # 延迟增加到3秒
        
        # 缓存配置
        self.enable_cache = True
        self.cache_dir = Path("cache/llm")
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """获取模型配置"""
        return self.supported_models.get(model_name, self.supported_models[self.default_model])
    
    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否可用（有API密钥或不需要认证）"""
        config = self.get_model_config(model_name)

        if not config["requires_auth"]:
            return True

        api_key = self.api_keys.get(model_name)

        # 讯飞的特殊处理（密钥是字典）
        if model_name == "spark":
            return bool(api_key and isinstance(api_key, dict) and api_key.get('api_password'))

        # 其他模型（密钥是字符串）
        return bool(api_key and isinstance(api_key, str) and api_key.strip())
    
    def get_available_models(self) -> List[str]:
        """获取所有可用的模型"""
        available = []
        for model_name in self.supported_models:
            if self.is_model_available(model_name):
                available.append(model_name)
        
        return available

# ========== 大模型客户端 ==========

class LLMClient:
    """大模型客户端 - 统一接口调用不同的大模型"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.current_model = self.config.default_model
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "AutonomousCognitiveLearningSystem/2.0"
        })
        
        # 初始化愿景核心（思想钢印）
        self.vision_core = get_vision_core()
    
    def switch_model(self, model_name: str) -> bool:
        """切换当前使用的模型"""
        if model_name in self.config.supported_models and self.config.is_model_available(model_name):
            self.current_model = model_name
            return True
        return False

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return self.config.get_available_models()
    
    def get_cache_key(self, prompt: str, model: str, max_tokens: int) -> str:
        """生成缓存键"""
        content = f"{model}_{max_tokens}_{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_from_cache(self, cache_key: str) -> Optional[str]:
        """从缓存获取结果"""
        if not self.config.enable_cache:
            return None
        
        cache_file = self.config.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                # 检查缓存是否过期（7天）
                cached_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
                if datetime.now() - cached_time < timedelta(days=7):
                    return cached.get("response")
            except:
                pass
        
        return None
    
    def save_to_cache(self, cache_key: str, response: str) -> None:
        """保存结果到缓存"""
        if not self.config.enable_cache:
            return
        
        cache_file = self.config.cache_dir / f"{cache_key}.json"
        try:
            cache_data = {
                "response": response,
                "cached_at": datetime.now().isoformat(),
                "model": self.current_model
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def call_llm(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                max_tokens: int = 2000,
                temperature: float = 0.7,
                model: Optional[str] = None,
                apply_vision: bool = True) -> Optional[str]:
        """
        调用大模型生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            max_tokens: 最大token数
            temperature: 温度参数
            model: 指定模型，如不指定使用当前模型
            apply_vision: 是否应用愿景层（思想钢印）
        
        Returns:
            模型生成的文本，失败时返回None
        """
        model_name = model or self.current_model
        model_config = self.config.get_model_config(model_name)
        
        # 检查模型可用性
        if not self.config.is_model_available(model_name):
            print(f"⚠️ 模型 {model_name} 不可用，请检查API密钥")
            return None
        
        # ========== 愿景核心集成：注入愿景上下文 ==========
        if apply_vision:
            vision_context = self.vision_core.generate_vision_context(prompt)
            if vision_context:
                # 将愿景上下文注入到提示词中
                prompt = f"{vision_context}\n\n{prompt}"
                print("🌌 愿景上下文已注入")
        
        # 检查缓存
        cache_key = self.get_cache_key(prompt, model_name, max_tokens)
        cached_response = self.get_from_cache(cache_key)
        if cached_response:
            print(f"📦 使用缓存结果 (模型: {model_name})")
            return cached_response
        
        print(f"🤖 调用大模型: {model_config['name']} (模型: {model_name})")
        
        # 根据模型类型调用不同的API
        try:
            if model_name == "mock":
                response = self._call_mock(prompt, system_prompt, max_tokens, temperature)
            elif model_name == "doubao":
                response = self._call_doubao(prompt, system_prompt, max_tokens, temperature)
            elif model_name == "spark":
                response = self._call_spark(prompt, system_prompt, max_tokens, temperature)
            elif model_name == "deepseek":
                response = self._call_deepseek(prompt, system_prompt, max_tokens, temperature)
            elif model_name == "openai":
                response = self._call_openai(prompt, system_prompt, max_tokens, temperature)
            else:
                print(f"❌ 不支持的模型: {model_name}")
                return None
            
            # ========== 愿景核心集成：应用愿景层 ==========
            if apply_vision and response:
                response = self.vision_core.apply_vision_layer(response, prompt)
            
            # 保存到缓存
            if response:
                self.save_to_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            print(f"❌ 调用大模型失败: {str(e)}")
            return None
    
    def _call_mock(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """模拟模型调用 - 用于测试和开发"""
        # 模拟思考时间
        time.sleep(0.5)
        
        # 根据提示类型生成不同的响应
        prompt_lower = prompt.lower()
        
        if "思维导图" in prompt or "知识结构" in prompt:
            # 生成模拟的思维导图结构
            return self._generate_mock_mindmap(prompt)
        elif "问题" in prompt or "提问" in prompt:
            # 生成模拟问题
            return self._generate_mock_questions(prompt)
        elif "总结" in prompt or "摘要" in prompt:
            # 生成模拟摘要
            return f"这是关于'{prompt[:30]}...'的摘要：\n\n这是一个模拟生成的摘要，用于测试系统功能。在实际使用中，这里会是由大模型生成的真实内容。"
        else:
            # 通用响应
            return f"这是对'{prompt[:30]}...'的模拟响应。\n\n在实际使用中，这里会是由{self.current_model}大模型生成的真实内容。请配置真实的大模型API密钥以获取真实响应。"
    
    def _call_doubao(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Optional[str]:
        """调用豆包大模型"""
        api_key = self.config.api_keys.get("doubao")
        if not api_key:
            return None

        try:
            url = f"{self.config.get_model_config('doubao')['base_url']}/chat/completions"

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.config.get_model_config('doubao')['model_id'],
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except Exception as e:
            print(f"❌ 调用豆包大模型失败: {str(e)}")
            return None
    
    def _call_deepseek(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Optional[str]:
        """调用DeepSeek大模型"""
        api_key = self.config.api_keys.get("deepseek")
        if not api_key:
            return None
        
        try:
            url = f"{self.config.get_model_config('deepseek')['base_url']}/chat/completions"
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
        except Exception as e:
            print(f"❌ 调用DeepSeek大模型失败: {str(e)}")
            return None
    
    def _call_openai(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Optional[str]:
        """调用OpenAI大模型"""
        api_key = self.config.api_keys.get("openai")
        if not api_key:
            return None
        
        try:
            url = f"{self.config.get_model_config('openai')['base_url']}/chat/completions"
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "gpt-4-turbo-preview",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
        except Exception as e:
            print(f"❌ 调用OpenAI大模型失败: {str(e)}")
            return None

    def _call_spark(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Optional[str]:
        """调用讯飞星火大模型"""
        spark_config = self.config.api_keys.get("spark")
        if not spark_config:
            return None

        try:
            # 使用 HTTP 接口（更简单）
            url = f"{self.config.get_model_config('spark')['base_url']}/chat/completions"

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 讯飞认证格式
            auth_header = spark_config.get('api_password', '')

            payload = {
                "model": "lite",  # Spark Lite
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {auth_header}",
                "Content-Type": "application/json"
            }

            response = self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

        except Exception as e:
            print(f"❌ 调用讯飞星火大模型失败: {str(e)}")
            return None
    
    def _generate_mock_mindmap(self, prompt: str) -> str:
        """生成模拟思维导图结构"""
        # 提取主题
        topic_match = re.search(r'关于(.+?)的|学习(.+?)(?:的|$)', prompt)
        topic = topic_match.group(1) if topic_match else "未知主题"
        
        mock_mindmap = f"""# {topic} 思维导图

## 核心概念
- 基本定义：{topic}的基础概念和定义
- 主要特点：{topic}的关键特征和属性
- 应用场景：{topic}的主要应用领域

## 知识体系
### 理论基础
1. 基本原理：支撑{topic}的核心理论
2. 发展历史：{topic}的起源和发展历程
3. 关键人物：对{topic}有重要贡献的研究者

### 实践应用
1. 方法技巧：{topic}的实践方法和技巧
2. 工具资源：学习和应用{topic}的工具和资源
3. 案例分析：{topic}的实际应用案例

## 学习路径
### 入门阶段
- 前置知识：学习{topic}需要的基础知识
- 学习资源：推荐的入门学习材料
- 练习方法：巩固基础知识的练习方式

### 进阶阶段
- 深入学习：{topic}的高级主题和复杂概念
- 项目实践：通过实际项目深化理解
- 交流讨论：与他人交流讨论提升理解

## 评估标准
- 知识掌握：对{topic}各个方面的理解程度
- 应用能力：将{topic}应用于实际问题的能力
- 创新能力：基于{topic}进行创新思考的能力

---
*这是一个由模拟大模型生成的思维导图结构，用于测试和学习目的。*
"""
        return mock_mindmap
    
    def _generate_mock_questions(self, prompt: str) -> str:
        """生成模拟问题"""
        # 提取主题
        topic_match = re.search(r'关于(.+?)的问题|(.+?)的相关问题', prompt)
        topic = topic_match.group(1) if topic_match else "该主题"
        
        mock_questions = f"""关于{topic}的重要问题：

## 基础理解问题
1. {topic}的基本定义是什么？
2. {topic}的主要特点有哪些？
3. {topic}与其他相关概念的区别是什么？

## 深度思考问题
4. {topic}的核心原理是什么？
5. {topic}的发展历程中有哪些关键节点？
6. 掌握{topic}对个人或社会有什么价值？

## 应用实践问题
7. 如何将{topic}应用于实际问题解决？
8. 学习{topic}的有效方法有哪些？
9. 评估{topic}掌握程度的标准是什么？

## 创新思考问题
10. {topic}未来可能的发展方向是什么？
11. {topic}与其他领域结合可能产生什么创新？
12. 如何基于{topic}提出新的见解或解决方案？

---
*这些问题是模拟生成的，用于引导对{topic}的深入学习。*
"""
        return mock_questions

# ========== 思维导图生成器 ==========

class MindMapGenerator(IMindMapGenerator):
    """
    思维导图生成器 - 大模型驱动的思维导图生成
    核心功能：将学习目标转换为层次化的思维导图结构
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.foundation = FoundationManager()
        
        # 思维导图生成模板
        self.generation_templates = {
            "standard": """请为以下学习目标生成一个思维导图结构：

学习目标：{goal_description}

要求：
1. 生成一个层次清晰的思维导图，深度为{depth}层
2. 每一层包含5-8个主要分支
3. 每个节点包含：标题、简要描述、重要性(0.0-1.0)、难度(0.0-1.0)、预估学习时间(分钟)
4. 思维导图风格：{style}
5. 特别关注：{focus_areas}

请以JSON格式返回思维导图结构，格式如下：
{{
  "root_node": {{
    "id": "根节点ID",
    "title": "根节点标题",
    "description": "根节点描述",
    "importance": 1.0,
    "difficulty": 0.5,
    "estimated_time_minutes": 总预估时间
  }},
  "nodes": [
    {{
      "id": "节点ID",
      "title": "节点标题",
      "description": "节点描述",
      "depth": 深度,
      "node_type": "节点类型",
      "importance": 重要性,
      "difficulty": 难度,
      "estimated_time_minutes": 预估时间,
      "parent_id": "父节点ID",
      "prerequisites": ["先决条件节点ID"],
      "tags": ["标签1", "标签2"]
    }}
  ]
}}""",
            
            "detailed": """作为知识结构专家，请为以下学习目标创建详细的思维导图：

学习目标：{goal_description}
目标规模：{scale}
学习深度：{learning_depth}

请生成一个{depth}层的思维导图，要求：
1. 第1层：核心主题（3-5个）
2. 第2层：关键概念（每个主题下4-6个）
3. 第3层：具体知识点（每个概念下3-5个）
4. 第4层：应用示例（可选）
5. 第5层：练习任务（可选）

为每个节点提供：
- 节点类型（concept, skill, example, practice, principle, fact）
- 重要性评分（0.0-1.0）
- 难度评分（0.0-1.0）
- 预估学习时间（分钟）
- 先决条件关系
- 相关标签

思维导图风格：{style}
关注重点：{focus_areas}

请返回结构化的JSON数据。"""
        }
        
        # 节点类型映射
        self.node_type_mapping = {
            "概念": "concept",
            "原理": "principle", 
            "技能": "skill",
            "方法": "skill",
            "示例": "example",
            "练习": "practice",
            "事实": "fact",
            "系统": "system",
            "模式": "pattern",
            "策略": "strategy"
        }
    
    def generate_for_goal(self, goal: LearningGoal) -> Optional[MindMapNode]:
        """
        为学习目标生成思维导图
        
        Args:
            goal: 学习目标
            
        Returns:
            思维导图根节点，失败时返回None
        """
        print(f"🧠 为学习目标生成思维导图: {goal.description}")
        
        # 根据目标规模选择生成策略
        if goal.scale == GoalScale.MICRO:
            depth = 2
            template = "standard"
        elif goal.scale == GoalScale.SMALL:
            depth = 3
            template = "standard"
        elif goal.scale == GoalScale.MEDIUM:
            depth = 4
            template = "detailed"
        else:  # LARGE 或 MASSIVE
            depth = goal.mindmap_depth
            template = "detailed"
        
        # 构建提示词
        prompt_template = self.generation_templates[template]
        
        # 确定关注领域
        focus_areas = self._determine_focus_areas(goal.description)
        
        prompt = prompt_template.format(
            goal_description=goal.description,
            depth=depth,
            style=goal.mindmap_style.value,
            focus_areas=", ".join(focus_areas),
            scale=goal.scale.value,
            learning_depth=goal.learning_depth_strategy
        )
        
        # 系统提示
        system_prompt = """你是一个专业的知识结构设计师和思维导图专家。你的任务是将学习目标转化为结构化的思维导图。
        请确保思维导图：
        1. 逻辑清晰，层次分明
        2. 覆盖学习目标的核心内容
        3. 节点关系合理（父子关系、先决条件）
        4. 重要性、难度评分合理
        5. 预估学习时间符合实际
        
        请只返回JSON格式的思维导图数据，不要有其他解释。"""
        
        # 调用大模型
        response = self.llm_client.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000,
            temperature=0.3
        )
        
        if not response:
            print("❌ 思维导图生成失败")
            return self._generate_fallback_mindmap(goal)
        
        # 解析响应
        mindmap_data = self._parse_mindmap_response(response, goal)
        if mindmap_data:
            root_node = mindmap_data["root_node"]
            
            # 更新目标中的思维导图信息
            goal.mindmap_root_id = root_node.id
            goal.mindmap_generated_at = datetime.now().isoformat()
            goal.mindmap_confidence = mindmap_data.get("confidence", 0.8)
            
            print(f"✅ 思维导图生成成功，包含 {len(mindmap_data['nodes'])} 个节点")
            return root_node
        else:
            print("⚠️ 思维导图解析失败，使用备选方案")
            return self._generate_fallback_mindmap(goal)
    
    def generate_from_text(self, text: str, depth: int = 3) -> Optional[MindMapNode]:
        """
        从文本生成思维导图
        
        Args:
            text: 输入文本
            depth: 思维导图深度
            
        Returns:
            思维导图根节点
        """
        print(f"🧠 从文本生成思维导图 (深度: {depth})")
        
        prompt = f"""请将以下文本内容转换为一个{depth}层的思维导图结构：

文本内容：
{text}

要求：
1. 提取文本的核心概念和关键信息
2. 组织成层次化的思维导图结构
3. 每个节点包含标题、简要描述、重要性评分
4. 体现概念之间的逻辑关系

请返回JSON格式的思维导图数据。"""
        
        response = self.llm_client.call_llm(
            prompt=prompt,
            system_prompt="你是文本分析和知识提取专家，擅长从文本中提取结构化知识。",
            max_tokens=3000,
            temperature=0.4
        )
        
        if not response:
            return None
        
        # 尝试解析响应
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # 转换为MindMapNode
                return self._convert_dict_to_mindmap(data)
            else:
                # 如果不是JSON格式，创建简单思维导图
                return self._create_simple_mindmap_from_text(text, depth)
                
        except Exception as e:
            print(f"❌ 思维导图解析失败: {str(e)}")
            return self._create_simple_mindmap_from_text(text, depth)
    
    def refine_mindmap(self, mindmap: MindMapNode, feedback: Dict[str, Any]) -> MindMapNode:
        """
        根据反馈精炼思维导图
        
        Args:
            mindmap: 原始思维导图
            feedback: 用户反馈
            
        Returns:
            精炼后的思维导图
        """
        print("🔧 根据反馈精炼思维导图")
        
        # 将思维导图转换为文本描述
        mindmap_description = self._mindmap_to_description(mindmap)
        
        prompt = f"""请根据用户反馈精炼以下思维导图：

原始思维导图：
{mindmap_description}

用户反馈：
{json.dumps(feedback, ensure_ascii=False, indent=2)}

精炼要求：
1. 根据反馈调整节点内容和结构
2. 保持思维导图的逻辑一致性
3. 优化重要性评分和难度评分
4. 调整预估学习时间

请返回精炼后的思维导图JSON数据。"""
        
        response = self.llm_client.call_llm(
            prompt=prompt,
            system_prompt="你是思维导图优化专家，擅长根据反馈改进知识结构。",
            max_tokens=3000,
            temperature=0.3
        )
        
        if response:
            try:
                # 尝试解析JSON响应
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    # 转换为MindMapNode
                    refined_mindmap = self._convert_dict_to_mindmap(data)
                    if refined_mindmap:
                        return refined_mindmap
            except Exception as e:
                print(f"❌ 思维导图精炼失败: {str(e)}")
        
        # 如果精炼失败，返回原始思维导图
        print("⚠️ 思维导图精炼失败，返回原始版本")
        return mindmap
    
    def _determine_focus_areas(self, description: str) -> List[str]:
        """从描述中确定关注领域"""
        focus_areas = ["基础知识", "核心概念", "实践应用"]
        
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["理论", "原理", "概念"]):
            focus_areas.append("理论深度")
        
        if any(word in description_lower for word in ["实践", "应用", "操作", "技能"]):
            focus_areas.append("技能训练")
        
        if any(word in description_lower for word in ["系统", "体系", "完整"]):
            focus_areas.append("系统架构")
        
        if any(word in description_lower for word in ["创新", "创造", "设计"]):
            focus_areas.append("创新思维")
        
        return list(set(focus_areas))  # 去重
    
    def _parse_mindmap_response(self, response: str, goal: LearningGoal) -> Optional[Dict[str, Any]]:
        """解析大模型返回的思维导图数据"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                print("❌ 响应中未找到JSON数据")
                return None
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # 验证数据结构
            if "root_node" not in data or "nodes" not in data:
                print("❌ 响应数据结构不正确")
                return None
            
            # 转换为MindMapNode对象
            root_node_dict = data["root_node"]
            nodes_dict = data["nodes"]
            
            # 创建根节点
            root_node = self._create_mindmap_node_from_dict(root_node_dict, is_root=True)
            
            # 创建所有节点
            node_map = {root_node.id: root_node}
            
            for node_dict in nodes_dict:
                node = self._create_mindmap_node_from_dict(node_dict)
                node_map[node.id] = node
            
            # 建立节点关系
            for node in node_map.values():
                if node.parent_id and node.parent_id in node_map:
                    parent_node = node_map[node.parent_id]
                    if node.id not in parent_node.children_ids:
                        parent_node.children_ids.append(node.id)
            
            return {
                "root_node": root_node,
                "nodes": list(node_map.values()),
                "confidence": data.get("confidence", 0.8)
            }
            
        except Exception as e:
            print(f"❌ 思维导图解析失败: {str(e)}")
            return None
    
    def _create_mindmap_node_from_dict(self, node_dict: Dict[str, Any], is_root: bool = False) -> MindMapNode:
        """从字典创建思维导图节点"""
        # 确保ID存在
        if "id" not in node_dict or not node_dict["id"]:
            node_dict["id"] = generate_id("mindmap_")
        
        # 确保标题存在
        if "title" not in node_dict or not node_dict["title"]:
            node_dict["title"] = "未命名节点"
        
        # 处理节点类型
        node_type = node_dict.get("node_type", "concept")
        if node_type in self.node_type_mapping:
            node_type = self.node_type_mapping[node_type]
        
        # 创建节点
        node = MindMapNode(
            id=node_dict["id"],
            title=node_dict["title"],
            description=node_dict.get("description", ""),
            depth=node_dict.get("depth", 0),
            node_type=node_type,
            importance=float(node_dict.get("importance", 0.5)),
            difficulty=float(node_dict.get("difficulty", 0.5)),
            estimated_time_minutes=int(node_dict.get("estimated_time_minutes", 30)),
            parent_id=node_dict.get("parent_id"),
            prerequisites=node_dict.get("prerequisites", []),
            tags=node_dict.get("tags", []),
            generated_by=self.llm_client.current_model,
            generated_at=datetime.now().isoformat(),
            generation_prompt=node_dict.get("generation_prompt", "")
        )
        
        return node
    
    def _generate_fallback_mindmap(self, goal: LearningGoal) -> MindMapNode:
        """生成备选思维导图（当大模型失败时）"""
        print("🔄 使用备选方案生成思维导图")
        
        # 创建根节点
        root_node = MindMapNode(
            id=generate_id("mindmap_fallback_"),
            title=f"学习目标: {goal.description[:30]}...",
            description=f"这是学习目标'{goal.description}'的思维导图",
            depth=0,
            importance=1.0,
            difficulty=0.5,
            estimated_time_minutes=goal.target_knowledge_count * 5,  # 每个知识点5分钟
            generated_by="fallback_generator",
            generated_at=datetime.now().isoformat()
        )
        
        # 根据目标规模创建子节点
        if goal.scale == GoalScale.MICRO:
            # 微目标：直接知识点
            for i in range(min(goal.target_knowledge_count, 10)):
                child = MindMapNode(
                    id=generate_id(f"mindmap_child_{i}_"),
                    title=f"知识点 {i+1}",
                    description=f"学习目标中的第{i+1}个知识点",
                    depth=1,
                    parent_id=root_node.id,
                    importance=0.7,
                    difficulty=0.5,
                    estimated_time_minutes=30
                )
                root_node.children_ids.append(child.id)
        
        elif goal.scale == GoalScale.SMALL:
            # 小目标：分组学习
            groups = ["基础知识", "核心概念", "实践应用", "拓展延伸"]
            for i, group in enumerate(groups):
                child = MindMapNode(
                    id=generate_id(f"mindmap_group_{i}_"),
                    title=group,
                    description=f"{goal.description}的{group}部分",
                    depth=1,
                    parent_id=root_node.id,
                    importance=0.8 if i < 2 else 0.6,
                    difficulty=0.5,
                    estimated_time_minutes=60
                )
                root_node.children_ids.append(child.id)
        
        else:
            # 中/大目标：层次化结构
            main_categories = ["理论基础", "方法技巧", "应用实践", "评估反思"]
            for i, category in enumerate(main_categories):
                category_node = MindMapNode(
                    id=generate_id(f"mindmap_cat_{i}_"),
                    title=category,
                    description=f"{goal.description}的{category}模块",
                    depth=1,
                    parent_id=root_node.id,
                    importance=0.9 if i < 2 else 0.7,
                    difficulty=0.6,
                    estimated_time_minutes=120
                )
                root_node.children_ids.append(category_node.id)
                
                # 为每个类别添加子节点
                sub_topics = ["核心概念", "关键技能", "典型案例", "常见问题"]
                for j, topic in enumerate(sub_topics):
                    sub_node = MindMapNode(
                        id=generate_id(f"mindmap_sub_{i}_{j}_"),
                        title=topic,
                        description=f"{category}中的{topic}",
                        depth=2,
                        parent_id=category_node.id,
                        importance=0.7,
                        difficulty=0.5,
                        estimated_time_minutes=45
                    )
                    category_node.children_ids.append(sub_node.id)
        
        return root_node
    
    def _convert_dict_to_mindmap(self, data: Dict[str, Any]) -> Optional[MindMapNode]:
        """将字典转换为思维导图节点"""
        try:
            if "root" in data:
                # 树形结构
                return self._build_mindmap_from_tree(data["root"], None)
            elif "nodes" in data and isinstance(data["nodes"], list):
                # 节点列表
                return self._build_mindmap_from_list(data["nodes"])
            else:
                return None
        except Exception as e:
            print(f"❌ 转换失败: {str(e)}")
            return None
    
    def _build_mindmap_from_tree(self, tree_data: Dict[str, Any], parent_id: Optional[str]) -> MindMapNode:
        """从树形结构构建思维导图"""
        # 创建当前节点
        node = MindMapNode(
            id=tree_data.get("id", generate_id("mindmap_")),
            title=tree_data.get("title", "未命名"),
            description=tree_data.get("description", ""),
            depth=tree_data.get("depth", 0),
            parent_id=parent_id,
            importance=tree_data.get("importance", 0.5),
            difficulty=tree_data.get("difficulty", 0.5),
            estimated_time_minutes=tree_data.get("estimated_time_minutes", 30)
        )
        
        # 递归构建子节点
        children = tree_data.get("children", [])
        for child_data in children:
            child_node = self._build_mindmap_from_tree(child_data, node.id)
            node.children_ids.append(child_node.id)
        
        return node
    
    def _build_mindmap_from_list(self, nodes_data: List[Dict[str, Any]]) -> Optional[MindMapNode]:
        """从节点列表构建思维导图"""
        if not nodes_data:
            return None
        
        # 创建所有节点
        node_map = {}
        root_node = None
        
        for node_data in nodes_data:
            node = MindMapNode(
                id=node_data.get("id", generate_id("mindmap_")),
                title=node_data.get("title", "未命名"),
                description=node_data.get("description", ""),
                depth=node_data.get("depth", 0),
                parent_id=node_data.get("parent_id"),
                importance=node_data.get("importance", 0.5),
                difficulty=node_data.get("difficulty", 0.5),
                estimated_time_minutes=node_data.get("estimated_time_minutes", 30)
            )
            
            node_map[node.id] = node
            
            # 找到根节点
            if node.depth == 0 or (not node.parent_id and root_node is None):
                root_node = node
        
        # 建立父子关系
        for node in node_map.values():
            if node.parent_id and node.parent_id in node_map:
                parent = node_map[node.parent_id]
                if node.id not in parent.children_ids:
                    parent.children_ids.append(node.id)
        
        return root_node or list(node_map.values())[0]
    
    def _create_simple_mindmap_from_text(self, text: str, depth: int) -> MindMapNode:
        """从文本创建简单思维导图"""
        # 提取关键词
        words = re.findall(r'\b\w{2,}\b', text.lower())
        from collections import Counter
        word_freq = Counter(words)
        
        # 获取最常见的关键词
        top_keywords = [word for word, _ in word_freq.most_common(10)]
        
        # 创建根节点
        root_node = MindMapNode(
            id=generate_id("mindmap_simple_"),
            title="文本分析结果",
            description=f"基于文本生成的简单思维导图（深度: {depth}）",
            depth=0
        )
        
        # 根据深度创建结构
        if depth >= 1:
            # 第一层：主要主题
            themes = ["核心概念", "关键信息", "相关主题"]
            for i, theme in enumerate(themes):
                theme_node = MindMapNode(
                    id=generate_id(f"mindmap_theme_{i}_"),
                    title=theme,
                    description=f"文本中的{theme}",
                    depth=1,
                    parent_id=root_node.id
                )
                root_node.children_ids.append(theme_node.id)
                
                if depth >= 2 and i == 0:  # 为核心概念添加子节点
                    # 添加关键词作为子节点
                    for j, keyword in enumerate(top_keywords[:5]):
                        keyword_node = MindMapNode(
                            id=generate_id(f"mindmap_keyword_{i}_{j}_"),
                            title=keyword,
                            description=f"文本中的关键词: {keyword}",
                            depth=2,
                            parent_id=theme_node.id
                        )
                        theme_node.children_ids.append(keyword_node.id)
        
        return root_node
    
    def _mindmap_to_description(self, mindmap: MindMapNode) -> str:
        """将思维导图转换为文本描述"""
        description = f"思维导图: {mindmap.title}\n"
        description += f"描述: {mindmap.description}\n"
        description += f"深度: {mindmap.depth}\n"
        description += f"节点数量: 未知（需要完整节点图）\n"
        description += f"生成时间: {mindmap.generated_at}\n"
        description += f"生成模型: {mindmap.generated_by}\n"
        
        return description

# ========== 多模态识别器 ==========

class MultimodalRecognizer(IMultimodalRecognizer):
    """
    多模态识别器 - 支持文本、图像、音频等多种模态的知识提取
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        
        # 图像识别配置
        self.image_recognition_config = {
            "max_size": (1024, 1024),
            "supported_formats": [".jpg", ".jpeg", ".png", ".bmp", ".gif"],
            "max_file_size": 10 * 1024 * 1024  # 10MB
        }
        
        # 音频识别配置
        self.audio_recognition_config = {
            "max_duration": 300,  # 5分钟
            "supported_formats": [".mp3", ".wav", ".m4a", ".flac"],
            "max_file_size": 50 * 1024 * 1024  # 50MB
        }
    
    def recognize_image(self, image_data: Any) -> Dict[str, Any]:
        """
        识别图片内容
        
        Args:
            image_data: 图片数据（base64字符串、文件路径或URL）
            
        Returns:
            识别结果字典
        """
        print("🖼️ 识别图片内容")
        
        result = {
            "success": False,
            "modality": ModalityType.IMAGE.value,
            "content_type": "unknown",
            "text_description": "",
            "extracted_concepts": [],
            "confidence": 0.0,
            "metadata": {}
        }
        
        try:
            # 准备图片数据
            image_base64 = self._prepare_image_data(image_data)
            if not image_base64:
                result["error"] = "无法处理图片数据"
                return result
            
            # 使用大模型进行图片识别
            prompt = """请详细描述这张图片的内容，包括：
1. 图片中的主要对象和场景
2. 颜色、风格和构图特点
3. 可能表达的主题或情感
4. 如果包含文字，提取所有文字内容
5. 图片可能的应用场景或相关知识

请提供结构化的描述。"""
            
            # 构建多模态请求（如果支持）
            if self.llm_client.current_model == "openai":
                # OpenAI支持视觉API
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
                
                response = self.llm_client.call_llm(
                    prompt=json.dumps(messages),  # 特殊处理
                    max_tokens=1000,
                    temperature=0.3
                )
            else:
                # 对于不支持视觉的模型，返回模拟结果
                response = self._simulate_image_recognition(image_base64)
            
            if response:
                result["success"] = True
                result["text_description"] = response
                result["confidence"] = 0.8
                
                # 提取概念
                result["extracted_concepts"] = self.extract_concepts({"text": response})
                
                # 分析内容类型
                content_type = self._analyze_content_type(response)
                result["content_type"] = content_type
                result["metadata"]["content_type"] = content_type
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 图片识别失败: {str(e)}")
        
        return result
    
    def recognize_audio(self, audio_data: Any) -> Dict[str, Any]:
        """
        识别音频内容
        
        Args:
            audio_data: 音频数据（base64字符串、文件路径或URL）
            
        Returns:
            识别结果字典
        """
        print("🎵 识别音频内容")
        
        result = {
            "success": False,
            "modality": ModalityType.AUDIO.value,
            "content_type": "unknown",
            "transcription": "",
            "summary": "",
            "extracted_concepts": [],
            "confidence": 0.0,
            "metadata": {}
        }
        
        try:
            # 在实际系统中，这里会调用语音识别API
            # 目前使用模拟实现
            
            # 模拟处理
            audio_info = self._simulate_audio_processing(audio_data)
            
            if audio_info:
                result["success"] = True
                result["transcription"] = audio_info.get("transcription", "")
                result["summary"] = audio_info.get("summary", "")
                result["confidence"] = audio_info.get("confidence", 0.7)
                
                # 提取概念
                combined_text = f"{result['transcription']} {result['summary']}"
                result["extracted_concepts"] = self.extract_concepts({"text": combined_text})
                
                # 分析内容类型
                content_type = self._analyze_content_type(combined_text)
                result["content_type"] = content_type
                result["metadata"]["duration"] = audio_info.get("duration", 0)
                result["metadata"]["content_type"] = content_type
            else:
                result["error"] = "音频处理失败"
                
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 音频识别失败: {str(e)}")
        
        return result
    
    def recognize_text(self, text: str) -> Dict[str, Any]:
        """
        深度分析文本内容
        
        Args:
            text: 输入文本
            
        Returns:
            分析结果字典
        """
        print("📝 深度分析文本内容")
        
        result = {
            "success": False,
            "modality": ModalityType.TEXT.value,
            "content_type": "unknown",
            "summary": "",
            "key_points": [],
            "extracted_concepts": [],
            "complexity_score": 0.0,
            "knowledge_type": "unknown",
            "confidence": 0.0,
            "metadata": {}
        }
        
        try:
            # 使用大模型分析文本
            prompt = f"""请深度分析以下文本内容：

文本内容：
{text[:2000]}  # 限制长度

请提供以下分析：
1. 文本摘要（100-200字）
2. 3-5个关键点
3. 主要涉及的概念或主题
4. 文本复杂度评分（0.0-1.0）
5. 知识类型（概念、事实、原理、技能等）
6. 潜在的学习价值

请以JSON格式返回分析结果。"""
            
            response = self.llm_client.call_llm(
                prompt=prompt,
                system_prompt="你是文本分析专家，擅长从文本中提取结构化知识。",
                max_tokens=1500,
                temperature=0.3
            )
            
            if response:
                # 尝试解析JSON响应
                try:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        analysis = json.loads(json_str)
                        
                        result["success"] = True
                        result["summary"] = analysis.get("summary", "")
                        result["key_points"] = analysis.get("key_points", [])
                        result["complexity_score"] = analysis.get("complexity_score", 0.5)
                        result["knowledge_type"] = analysis.get("knowledge_type", "unknown")
                        result["confidence"] = analysis.get("confidence", 0.8)
                        
                        # 提取概念
                        combined_text = f"{result['summary']} {' '.join(result['key_points'])}"
                        result["extracted_concepts"] = self.extract_concepts({"text": combined_text})
                        
                        # 分析内容类型
                        content_type = self._analyze_content_type(text)
                        result["content_type"] = content_type
                        result["metadata"]["length"] = len(text)
                        result["metadata"]["content_type"] = content_type
                        
                        return result
                except:
                    # 如果JSON解析失败，使用文本响应
                    pass
                
                # 使用响应文本作为摘要
                result["success"] = True
                result["summary"] = response[:500]
                result["key_points"] = self._extract_key_points_from_text(response)
                result["complexity_score"] = self._estimate_text_complexity(text)
                result["knowledge_type"] = self._detect_knowledge_type(text)
                result["confidence"] = 0.7
                
                # 提取概念
                result["extracted_concepts"] = self.extract_concepts({"text": text})
                
                # 分析内容类型
                content_type = self._analyze_content_type(text)
                result["content_type"] = content_type
                result["metadata"]["length"] = len(text)
                result["metadata"]["content_type"] = content_type
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 文本分析失败: {str(e)}")
        
        return result
    
    def extract_concepts(self, recognition_result: Dict[str, Any]) -> List[str]:
        """
        从识别结果中提取概念
        
        Args:
            recognition_result: 识别结果字典
            
        Returns:
            提取的概念列表
        """
        concepts = []
        
        try:
            # 从不同字段提取文本
            text_parts = []
            
            if "text_description" in recognition_result:
                text_parts.append(recognition_result["text_description"])
            
            if "transcription" in recognition_result:
                text_parts.append(recognition_result["transcription"])
            
            if "summary" in recognition_result:
                text_parts.append(recognition_result["summary"])
            
            if "text" in recognition_result:
                text_parts.append(recognition_result["text"])
            
            # 合并文本
            combined_text = " ".join(text_parts)
            
            if not combined_text:
                return concepts
            
            # 使用大模型提取概念
            prompt = f"""请从以下文本中提取重要的概念、术语和主题：

文本：
{combined_text[:1000]}

要求：
1. 提取5-10个最重要的概念
2. 每个概念应该是名词或名词短语
3. 按重要性排序
4. 排除常见词汇和停用词

请以JSON数组格式返回概念列表。"""
            
            response = self.llm_client.call_llm(
                prompt=prompt,
                max_tokens=500,
                temperature=0.2
            )
            
            if response:
                # 尝试解析JSON
                try:
                    json_match = re.search(r'\[.*\]', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        extracted_concepts = json.loads(json_str)
                        if isinstance(extracted_concepts, list):
                            concepts = extracted_concepts[:10]  # 限制数量
                except:
                    # 如果不是JSON，尝试提取关键词
                    concepts = self._extract_keywords(combined_text)
            else:
                # 备选方案：使用简单关键词提取
                concepts = self._extract_keywords(combined_text)
            
        except Exception as e:
            print(f"❌ 概念提取失败: {str(e)}")
            # 使用简单关键词提取作为备选
            text = recognition_result.get("text", "") or recognition_result.get("summary", "")
            if text:
                concepts = self._extract_keywords(text)
        
        return concepts[:10]  # 返回前10个概念
    
    def _prepare_image_data(self, image_data: Any) -> Optional[str]:
        """准备图片数据为base64格式"""
        if isinstance(image_data, str):
            # 检查是否为base64字符串
            if image_data.startswith("data:image") or len(image_data) > 1000:
                # 可能是base64，尝试提取
                if "base64," in image_data:
                    return image_data.split("base64,")[1]
                return image_data
            
            # 检查是否为文件路径
            elif Path(image_data).exists():
                try:
                    with open(image_data, "rb") as f:
                        image_bytes = f.read()
                    return base64.b64encode(image_bytes).decode("utf-8")
                except:
                    return None
            
            # 检查是否为URL（简化处理）
            elif image_data.startswith("http"):
                try:
                    response = requests.get(image_data, timeout=10)
                    if response.status_code == 200:
                        return base64.b64encode(response.content).decode("utf-8")
                except:
                    return None
        
        elif isinstance(image_data, bytes):
            # 直接是字节数据
            return base64.b64encode(image_data).decode("utf-8")
        
        return None
    
    def _simulate_image_recognition(self, image_base64: str) -> str:
        """模拟图片识别"""
        # 在实际系统中，这里会调用实际的图片识别API
        # 目前返回模拟描述
        
        descriptions = [
            "这是一张包含多种元素的图片，可能涉及自然景观或人工建筑。图片色彩丰富，构图平衡。",
            "图片中显示了文本和图形的结合，可能是一个信息图表或教育材料。",
            "这是一张人物或物体的特写图片，焦点清晰，背景虚化，具有艺术效果。",
            "图片展示了某种技术或科学概念的可视化，包含图表、公式或示意图。",
            "这是一张风景或建筑图片，展现了特定的风格或文化特征。"
        ]
        
        # 基于base64长度选择描述（模拟不同内容）
        index = min(len(image_base64) // 1000, len(descriptions) - 1)
        return descriptions[index]
    
    def _simulate_audio_processing(self, audio_data: Any) -> Optional[Dict[str, Any]]:
        """模拟音频处理"""
        # 在实际系统中，这里会调用语音识别API
        # 目前返回模拟结果
        
        transcriptions = [
            "这是一个关于人工智能的讲座，讨论了机器学习的基本原理和应用场景。",
            "这段音频包含了日常对话，涉及购物、天气等生活话题。",
            "这是一段音乐或歌曲，具有特定的节奏和旋律。",
            "音频内容是关于历史事件的讲述，包含了具体的时间、地点和人物。",
            "这段录音是技术教程，讲解了某种软件或工具的使用方法。"
        ]
        
        summaries = [
            "讲座介绍了人工智能的基本概念和发展历程，重点讨论了机器学习算法。",
            "日常对话反映了常见的生活场景，语言简单直接。",
            "音乐作品展现了特定的音乐风格和情感表达。",
            "历史讲述提供了对过去事件的深入分析和解读。",
            "技术教程详细说明了软件功能的操作步骤和注意事项。"
        ]
        
        # 随机选择（在实际中会根据音频内容确定）
        import random
        index = random.randint(0, len(transcriptions) - 1)
        
        return {
            "transcription": transcriptions[index],
            "summary": summaries[index],
            "confidence": 0.7 + random.random() * 0.2,
            "duration": random.randint(30, 300)  # 30秒到5分钟
        }
    
    def _extract_key_points_from_text(self, text: str) -> List[str]:
        """从文本中提取关键点"""
        # 简单实现：提取包含数字或重要词汇的句子
        sentences = re.split(r'[.!?。！？]+', text)
        
        key_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # 判断是否为重要句子
            important_keywords = ["关键", "重要", "核心", "主要", "重点", "首先", "其次", "最后", "总之", "总结"]
            contains_number = bool(re.search(r'\d+', sentence))
            contains_important = any(keyword in sentence for keyword in important_keywords)
            
            if contains_number or contains_important or len(sentence) > 50:
                key_points.append(sentence[:100])  # 截断长度
        
        return key_points[:5]  # 最多5个关键点
    
    def _estimate_text_complexity(self, text: str) -> float:
        """估计文本复杂度"""
        if not text:
            return 0.0
        
        # 基于多个因素计算复杂度
        factors = []
        
        # 1. 长度因子
        length = len(text)
        length_factor = min(length / 1000, 1.0)  # 1000字为上限
        factors.append(length_factor * 0.3)
        
        # 2. 词汇多样性因子（简单实现）
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        if words:
            diversity = len(unique_words) / len(words)
            factors.append(diversity * 0.3)
        
        # 3. 句子长度因子
        sentences = re.split(r'[.!?。！？]+', text)
        if sentences:
            avg_sentence_length = sum(len(s) for s in sentences if s.strip()) / len(sentences)
            sentence_factor = min(avg_sentence_length / 100, 1.0)  # 100字/句为上限
            factors.append(sentence_factor * 0.2)
        
        # 4. 专业术语因子（简单检测）
        technical_terms = ["原理", "算法", "函数", "变量", "系统", "结构", "模型", "理论"]
        term_count = sum(1 for term in technical_terms if term in text)
        term_factor = min(term_count / 10, 1.0)  # 10个术语为上限
        factors.append(term_factor * 0.2)
        
        # 计算平均复杂度
        if factors:
            complexity = sum(factors) / len(factors)
            return min(complexity, 1.0)
        else:
            return 0.5
    
    def _detect_knowledge_type(self, text: str) -> str:
        """检测知识类型"""
        text_lower = text.lower()
        
        type_keywords = {
            "概念": ["概念", "定义", "含义", "是什么"],
            "事实": ["事实", "数据", "统计", "调查", "研究显示"],
            "原理": ["原理", "理论", "定律", "法则", "公式"],
            "技能": ["技能", "方法", "技巧", "步骤", "操作", "如何"],
            "过程": ["过程", "流程", "步骤", "阶段", "发展"],
            "系统": ["系统", "体系", "架构", "框架", "结构"]
        }
        
        for knowledge_type, keywords in type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return knowledge_type
        
        return "未知"
    
    def _analyze_content_type(self, text: str) -> str:
        """分析内容类型"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["教程", "指南", "步骤", "如何做", "操作方法"]):
            return "教程"
        elif any(word in text_lower for word in ["概念", "定义", "理论", "原理"]):
            return "概念解释"
        elif any(word in text_lower for word in ["案例", "例子", "示例", "实例"]):
            return "案例分析"
        elif any(word in text_lower for word in ["问题", "疑问", "解答", "为什么"]):
            return "问答"
        elif any(word in text_lower for word in ["总结", "概要", "摘要", "要点"]):
            return "总结"
        elif any(word in text_lower for word in ["故事", "经历", "事件", "历史"]):
            return "叙事"
        elif any(word in text_lower for word in ["数据", "统计", "图表", "数字"]):
            return "数据分析"
        else:
            return "通用文本"
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词（简单实现）"""
        # 移除停用词
        stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        
        # 提取词语
        words = re.findall(r'[\u4e00-\u9fff]{2,}|\b\w{3,}\b', text.lower())
        
        # 统计词频
        from collections import Counter
        word_freq = Counter(words)
        
        # 过滤停用词和单字
        keywords = []
        for word, freq in word_freq.most_common():
            if word not in stopwords and freq > 1:
                keywords.append(word)
            if len(keywords) >= max_keywords:
                break
        
        return keywords

# ========== 知识提取器 ==========

class KnowledgeExtractor:
    """
    知识提取器 - 从多模态内容中提取结构化知识
    """
    
    def __init__(self, multimodal_recognizer: Optional[MultimodalRecognizer] = None):
        self.recognizer = multimodal_recognizer or MultimodalRecognizer()
        self.foundation = FoundationManager()
    
    def extract_from_text(self, text: str, source: str = "unknown") -> List[KnowledgeNode]:
        """
        从文本中提取知识节点
        
        Args:
            text: 输入文本
            source: 来源标识
            
        Returns:
            提取的知识节点列表
        """
        print(f"📚 从文本提取知识 (来源: {source})")
        
        # 分析文本
        analysis = self.recognizer.recognize_text(text)
        
        if not analysis.get("success", False):
            print("❌ 文本分析失败")
            return []
        
        # 创建知识节点
        knowledge_nodes = []
        
        # 主节点（基于摘要）
        if analysis.get("summary"):
            main_node = KnowledgeNode(
                id=generate_id("knowledge_", source),
                title=f"知识: {analysis.get('content_type', '文本')}",
                content=analysis["summary"],
                summary=analysis["summary"][:100] + "..." if len(analysis["summary"]) > 100 else analysis["summary"],
                knowledge_type=KnowledgeType(analysis.get("knowledge_type", "概念")),
                learning_level=LearningLevel.UNDERSTANDING,
                modality=ModalityType.TEXT,
                confidence=analysis.get("confidence", 0.7),
                source=source,
                tags=[analysis.get("content_type", "文本"), "文本提取"]
            )
            knowledge_nodes.append(main_node)
        
        # 关键点子节点
        key_points = analysis.get("key_points", [])
        for i, point in enumerate(key_points):
            if not point.strip():
                continue
            
            point_node = KnowledgeNode(
                id=generate_id(f"keypoint_{i}_", source),
                title=f"关键点 {i+1}",
                content=point,
                summary=point[:80] + "..." if len(point) > 80 else point,
                knowledge_type=KnowledgeType.FACT,
                learning_level=LearningLevel.FAMILIARITY,
                modality=ModalityType.TEXT,
                parent_id=knowledge_nodes[0].id if knowledge_nodes else None,
                confidence=0.7,
                source=source,
                tags=["关键点", "要点"]
            )
            knowledge_nodes.append(point_node)
        
        # 概念节点
        concepts = analysis.get("extracted_concepts", [])
        for i, concept in enumerate(concepts[:5]):  # 最多5个概念
            concept_node = KnowledgeNode(
                id=generate_id(f"concept_{i}_", concept),
                title=concept,
                content=f"关于{concept}的概念解释",
                summary=f"{concept}的基本概念和定义",
                knowledge_type=KnowledgeType.CONCEPT,
                learning_level=LearningLevel.EXPOSURE,
                modality=ModalityType.TEXT,
                confidence=0.6,
                source=source,
                tags=["概念", "术语"]
            )
            knowledge_nodes.append(concept_node)
        
        print(f"✅ 从文本提取了 {len(knowledge_nodes)} 个知识节点")
        return knowledge_nodes
    
    def extract_from_image(self, image_data: Any, source: str = "unknown") -> List[KnowledgeNode]:
        """
        从图片中提取知识节点
        
        Args:
            image_data: 图片数据
            source: 来源标识
            
        Returns:
            提取的知识节点列表
        """
        print(f"🖼️ 从图片提取知识 (来源: {source})")
        
        # 识别图片内容
        recognition = self.recognizer.recognize_image(image_data)
        
        if not recognition.get("success", False):
            print("❌ 图片识别失败")
            return []
        
        # 创建知识节点
        knowledge_nodes = []
        
        # 主节点（基于图片描述）
        if recognition.get("text_description"):
            main_node = KnowledgeNode(
                id=generate_id("image_knowledge_", source),
                title=f"图片内容: {recognition.get('content_type', '图像')}",
                content=recognition["text_description"],
                summary=recognition["text_description"][:100] + "..." if len(recognition["text_description"]) > 100 else recognition["text_description"],
                knowledge_type=KnowledgeType.CONCEPT,
                learning_level=LearningLevel.EXPOSURE,
                modality=ModalityType.IMAGE,
                confidence=recognition.get("confidence", 0.6),
                source=source,
                image_data=image_data if isinstance(image_data, str) and image_data.startswith("data:image") else None,
                tags=["图片", recognition.get("content_type", "图像"), "视觉"]
            )
            knowledge_nodes.append(main_node)
        
        # 概念节点
        concepts = recognition.get("extracted_concepts", [])
        for i, concept in enumerate(concepts[:3]):  # 最多3个概念
            concept_node = KnowledgeNode(
                id=generate_id(f"image_concept_{i}_", concept),
                title=f"图片中的概念: {concept}",
                content=f"图片中出现的{concept}的相关知识",
                summary=f"从图片中提取的概念: {concept}",
                knowledge_type=KnowledgeType.CONCEPT,
                learning_level=LearningLevel.EXPOSURE,
                modality=ModalityType.IMAGE,
                parent_id=knowledge_nodes[0].id if knowledge_nodes else None,
                confidence=0.5,
                source=source,
                tags=["图片概念", "视觉识别"]
            )
            knowledge_nodes.append(concept_node)
        
        print(f"✅ 从图片提取了 {len(knowledge_nodes)} 个知识节点")
        return knowledge_nodes
    
    def extract_from_audio(self, audio_data: Any, source: str = "unknown") -> List[KnowledgeNode]:
        """
        从音频中提取知识节点
        
        Args:
            audio_data: 音频数据
            source: 来源标识
            
        Returns:
            提取的知识节点列表
        """
        print(f"🎵 从音频提取知识 (来源: {source})")
        
        # 识别音频内容
        recognition = self.recognizer.recognize_audio(audio_data)
        
        if not recognition.get("success", False):
            print("❌ 音频识别失败")
            return []
        
        # 创建知识节点
        knowledge_nodes = []
        
        # 主节点（基于转录文本）
        if recognition.get("transcription"):
            main_node = KnowledgeNode(
                id=generate_id("audio_knowledge_", source),
                title=f"音频内容: {recognition.get('content_type', '音频')}",
                content=recognition["transcription"],
                summary=recognition.get("summary", recognition["transcription"][:100] + "...") if len(recognition["transcription"]) > 100 else recognition["transcription"],
                knowledge_type=KnowledgeType.CONCEPT,
                learning_level=LearningLevel.FAMILIARITY,
                modality=ModalityType.AUDIO,
                confidence=recognition.get("confidence", 0.6),
                source=source,
                audio_data=audio_data if isinstance(audio_data, str) and audio_data.startswith("data:audio") else None,
                tags=["音频", recognition.get("content_type", "音频"), "听觉"]
            )
            knowledge_nodes.append(main_node)
        
        # 总结节点
        if recognition.get("summary") and recognition["summary"] != recognition.get("transcription", ""):
            summary_node = KnowledgeNode(
                id=generate_id("audio_summary_", source),
                title="音频摘要",
                content=recognition["summary"],
                summary=recognition["summary"][:80] + "..." if len(recognition["summary"]) > 80 else recognition["summary"],
                knowledge_type=KnowledgeType.SUMMARY,
                learning_level=LearningLevel.UNDERSTANDING,
                modality=ModalityType.AUDIO,
                parent_id=knowledge_nodes[0].id if knowledge_nodes else None,
                confidence=0.7,
                source=source,
                tags=["摘要", "总结"]
            )
            knowledge_nodes.append(summary_node)
        
        # 概念节点
        concepts = recognition.get("extracted_concepts", [])
        for i, concept in enumerate(concepts[:3]):  # 最多3个概念
            concept_node = KnowledgeNode(
                id=generate_id(f"audio_concept_{i}_", concept),
                title=f"音频中的概念: {concept}",
                content=f"音频中提到的{concept}的相关知识",
                summary=f"从音频中提取的概念: {concept}",
                knowledge_type=KnowledgeType.CONCEPT,
                learning_level=LearningLevel.EXPOSURE,
                modality=ModalityType.AUDIO,
                parent_id=knowledge_nodes[0].id if knowledge_nodes else None,
                confidence=0.5,
                source=source,
                tags=["音频概念", "语音识别"]
            )
            knowledge_nodes.append(concept_node)
        
        print(f"✅ 从音频提取了 {len(knowledge_nodes)} 个知识节点")
        return knowledge_nodes
    
    def extract_from_multimodal(self, content_dict: Dict[str, Any], source: str = "unknown") -> List[KnowledgeNode]:
        """
        从多模态内容中提取知识节点
        
        Args:
            content_dict: 包含多种模态内容的字典
            source: 来源标识
            
        Returns:
            提取的知识节点列表
        """
        print(f"🌐 从多模态内容提取知识 (来源: {source})")
        
        knowledge_nodes = []
        
        # 提取文本内容
        if "text" in content_dict and content_dict["text"]:
            text_nodes = self.extract_from_text(content_dict["text"], f"{source}_text")
            knowledge_nodes.extend(text_nodes)
        
        # 提取图片内容
        if "image" in content_dict and content_dict["image"]:
            image_nodes = self.extract_from_image(content_dict["image"], f"{source}_image")
            knowledge_nodes.extend(image_nodes)
        
        # 提取音频内容
        if "audio" in content_dict and content_dict["audio"]:
            audio_nodes = self.extract_from_audio(content_dict["audio"], f"{source}_audio")
            knowledge_nodes.extend(audio_nodes)
        
        # 创建多模态整合节点（如果有多种模态）
        if len([k for k in content_dict.keys() if k in ["text", "image", "audio"] and content_dict[k]]) > 1:
            integrated_node = KnowledgeNode(
                id=generate_id("multimodal_integrated_", source),
                title="多模态知识整合",
                content=f"整合了{len([k for k in content_dict.keys() if k in ['text', 'image', 'audio'] and content_dict[k]])}种模态的知识内容",
                summary="多模态内容的知识整合",
                knowledge_type=KnowledgeType.SYSTEM,
                learning_level=LearningLevel.UNDERSTANDING,
                modality=ModalityType.MULTIMODAL,
                confidence=0.8,
                source=source,
                tags=["多模态", "整合", "跨模态"]
            )
            knowledge_nodes.append(integrated_node)
        
        print(f"✅ 从多模态内容提取了 {len(knowledge_nodes)} 个知识节点")
        return knowledge_nodes

# ========== 主动学习触发器 ==========

class ActiveLearningTrigger:
    """
    主动学习触发器 - 监测学习状态，触发主动学习行为
    """
    
    def __init__(self, mindmap_generator: Optional[MindMapGenerator] = None,
                 knowledge_extractor: Optional[KnowledgeExtractor] = None):
        self.mindmap_generator = mindmap_generator or MindMapGenerator()
        self.knowledge_extractor = knowledge_extractor or KnowledgeExtractor()
        self.foundation = FoundationManager()
        
        # 触发条件配置
        self.trigger_conditions = {
            "confusion": {
                "description": "知识混淆检测",
                "threshold": 0.3,  # 置信度低于30%
                "action": "generate_clarification"
            },
            "knowledge_gap": {
                "description": "知识缺口检测",
                "threshold": 0.4,  # 掌握度低于40%
                "action": "suggest_prerequisites"
            },
            "stagnation": {
                "description": "学习停滞检测",
                "threshold": 3,  # 连续3次无进步
                "action": "adjust_strategy"
            },
            "curiosity": {
                "description": "好奇心触发",
                "threshold": 0.8,  # 掌握度高于80%
                "action": "suggest_advanced_topics"
            },
            "low_engagement": {
                "description": "低参与度检测",
                "threshold": 0.2,  # 交互频率低于20%
                "action": "increase_interactivity"
            }
        }
        
        # 学习历史记录
        self.learning_history = {}
    
    def monitor_learning_state(self, goal: LearningGoal, knowledge_nodes: List[KnowledgeNode]) -> Dict[str, Any]:
        """
        监测学习状态
        
        Args:
            goal: 学习目标
            knowledge_nodes: 相关知识节点
            
        Returns:
            监测结果和触发动作
        """
        print(f"📊 监测学习状态: {goal.description}")
        
        monitoring_result = {
            "goal_id": goal.id,
            "timestamp": datetime.now().isoformat(),
            "overall_progress": goal.overall_progress,
            "confidence_scores": [],
            "mastery_scores": [],
            "detected_issues": [],
            "triggered_actions": [],
            "recommendations": []
        }
        
        # 收集统计信息
        for node in knowledge_nodes:
            monitoring_result["confidence_scores"].append(node.confidence)
            monitoring_result["mastery_scores"].append(node.mastery_score)
        
        # 检测触发条件
        triggers = self._detect_triggers(goal, knowledge_nodes, monitoring_result)
        
        # 执行触发动作
        for trigger in triggers:
            action_result = self._execute_trigger_action(trigger, goal, knowledge_nodes)
            if action_result:
                monitoring_result["triggered_actions"].append(action_result)
        
        # 生成推荐
        recommendations = self._generate_recommendations(goal, knowledge_nodes, monitoring_result)
        monitoring_result["recommendations"] = recommendations
        
        # 更新学习历史
        self._update_learning_history(goal.id, monitoring_result)
        
        return monitoring_result
    
    def trigger_active_learning(self, trigger_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        触发主动学习行为
        
        Args:
            trigger_type: 触发类型
            context: 上下文信息
            
        Returns:
            主动学习结果
        """
        print(f"🚀 触发主动学习: {trigger_type}")
        
        result = {
            "trigger_type": trigger_type,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "actions_taken": [],
            "generated_content": None,
            "recommendations": []
        }
        
        if trigger_type == "confusion":
            # 生成澄清内容
            clarification = self._generate_clarification(context)
            if clarification:
                result["success"] = True
                result["actions_taken"].append("生成知识澄清")
                result["generated_content"] = clarification
        
        elif trigger_type == "knowledge_gap":
            # 建议先决知识
            prerequisites = self._suggest_prerequisites(context)
            if prerequisites:
                result["success"] = True
                result["actions_taken"].append("建议先决知识")
                result["generated_content"] = prerequisites
        
        elif trigger_type == "stagnation":
            # 调整学习策略
            strategy_adjustment = self._adjust_learning_strategy(context)
            if strategy_adjustment:
                result["success"] = True
                result["actions_taken"].append("调整学习策略")
                result["generated_content"] = strategy_adjustment
        
        elif trigger_type == "curiosity":
            # 建议进阶主题
            advanced_topics = self._suggest_advanced_topics(context)
            if advanced_topics:
                result["success"] = True
                result["actions_taken"].append("建议进阶主题")
                result["generated_content"] = advanced_topics
        
        elif trigger_type == "low_engagement":
            # 增加互动性
            interactivity_plan = self._increase_interactivity(context)
            if interactivity_plan:
                result["success"] = True
                result["actions_taken"].append("增加学习互动性")
                result["generated_content"] = interactivity_plan
        
        else:
            result["error"] = f"未知触发类型: {trigger_type}"
        
        return result
    
    def _detect_triggers(self, goal: LearningGoal, knowledge_nodes: List[KnowledgeNode], 
                        monitoring_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测触发条件"""
        triggers = []
        
        # 计算平均置信度和掌握度
        if monitoring_result["confidence_scores"]:
            avg_confidence = sum(monitoring_result["confidence_scores"]) / len(monitoring_result["confidence_scores"])
            
            # 检测知识混淆
            if avg_confidence < self.trigger_conditions["confusion"]["threshold"]:
                triggers.append({
                    "type": "confusion",
                    "description": f"平均置信度较低: {avg_confidence:.2f}",
                    "severity": "high"
                })
                monitoring_result["detected_issues"].append("知识混淆")
        
        if monitoring_result["mastery_scores"]:
            avg_mastery = sum(monitoring_result["mastery_scores"]) / len(monitoring_result["mastery_scores"])
            
            # 检测知识缺口
            if avg_mastery < self.trigger_conditions["knowledge_gap"]["threshold"]:
                triggers.append({
                    "type": "knowledge_gap",
                    "description": f"平均掌握度较低: {avg_mastery:.2f}",
                    "severity": "medium"
                })
                monitoring_result["detected_issues"].append("知识缺口")
            
            # 检测好奇心（掌握度高但仍有学习空间）
            if avg_mastery > self.trigger_conditions["curiosity"]["threshold"] and goal.overall_progress < 0.9:
                triggers.append({
                    "type": "curiosity",
                    "description": f"掌握度较高但目标未完成: {avg_mastery:.2f}",
                    "severity": "low"
                })
        
        # 检测学习停滞（从历史记录）
        history = self.learning_history.get(goal.id, [])
        if len(history) >= 3:
            recent_progress = [h.get("overall_progress", 0) for h in history[-3:]]
            if all(abs(recent_progress[i] - recent_progress[i-1]) < 0.05 for i in range(1, len(recent_progress))):
                triggers.append({
                    "type": "stagnation",
                    "description": "连续3次监测进度无明显变化",
                    "severity": "medium"
                })
                monitoring_result["detected_issues"].append("学习停滞")
        
        return triggers
    
    def _execute_trigger_action(self, trigger: Dict[str, Any], goal: LearningGoal, 
                              knowledge_nodes: List[KnowledgeNode]) -> Optional[Dict[str, Any]]:
        """执行触发动作"""
        trigger_type = trigger.get("type")
        
        if not trigger_type or trigger_type not in self.trigger_conditions:
            return None
        
        # 构建上下文
        context = {
            "goal": goal,
            "knowledge_nodes": knowledge_nodes,
            "trigger": trigger,
            "timestamp": datetime.now().isoformat()
        }
        
        # 触发主动学习
        return self.trigger_active_learning(trigger_type, context)
    
    def _generate_recommendations(self, goal: LearningGoal, knowledge_nodes: List[KnowledgeNode],
                                monitoring_result: Dict[str, Any]) -> List[str]:
        """生成学习推荐"""
        recommendations = []
        
        # 基于进度推荐
        if goal.overall_progress < 0.3:
            recommendations.append("当前处于学习初期，建议先建立整体认知框架")
        elif goal.overall_progress < 0.7:
            recommendations.append("当前处于学习中段，建议加强核心概念的理解和应用")
        else:
            recommendations.append("当前处于学习后期，建议进行综合复习和实际应用")
        
        # 基于检测到的问题推荐
        issues = monitoring_result.get("detected_issues", [])
        if "知识混淆" in issues:
            recommendations.append("检测到知识混淆，建议重新学习基础概念")
        if "知识缺口" in issues:
            recommendations.append("检测到知识缺口，建议补充相关先决知识")
        if "学习停滞" in issues:
            recommendations.append("检测到学习停滞，建议调整学习策略或休息")
        
        # 基于时间推荐
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            recommendations.append("早晨学习效率高，建议进行新知识学习")
        elif 14 <= current_hour < 18:
            recommendations.append("下午适合进行练习和复习")
        elif 20 <= current_hour < 22:
            recommendations.append("晚上适合进行知识整理和总结")
        
        return recommendations[:3]  # 最多3条推荐
    
    def _update_learning_history(self, goal_id: str, monitoring_result: Dict[str, Any]) -> None:
        """更新学习历史"""
        if goal_id not in self.learning_history:
            self.learning_history[goal_id] = []
        
        # 简化记录
        history_entry = {
            "timestamp": monitoring_result["timestamp"],
            "overall_progress": monitoring_result["overall_progress"],
            "avg_confidence": sum(monitoring_result["confidence_scores"]) / len(monitoring_result["confidence_scores"]) if monitoring_result["confidence_scores"] else 0,
            "avg_mastery": sum(monitoring_result["mastery_scores"]) / len(monitoring_result["mastery_scores"]) if monitoring_result["mastery_scores"] else 0,
            "issues": monitoring_result["detected_issues"]
        }
        
        self.learning_history[goal_id].append(history_entry)
        
        # 限制历史记录长度
        if len(self.learning_history[goal_id]) > 10:
            self.learning_history[goal_id] = self.learning_history[goal_id][-10:]
    
    def _generate_clarification(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """生成知识澄清"""
        goal = context.get("goal")
        if not goal:
            return None
        
        # 使用大模型生成澄清内容
        prompt = f"""请为以下学习目标中的混淆知识点提供澄清：

学习目标：{goal.description}
当前进度：{goal.overall_progress:.1%}

检测到学习混淆，请：
1. 重新解释核心概念
2. 提供更简单的例子
3. 澄清常见误解
4. 建议学习步骤

请提供结构化的澄清内容。"""
        
        llm_client = LLMClient()
        response = llm_client.call_llm(prompt=prompt, max_tokens=1500)
        
        if response:
            return {
                "type": "clarification",
                "content": response,
                "suggested_actions": [
                    "重新阅读基础概念",
                    "尝试更简单的练习",
                    "寻求具体示例"
                ]
            }
        
        return None
    
    def _suggest_prerequisites(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """建议先决知识"""
        goal = context.get("goal")
        if not goal:
            return None
        
        prompt = f"""为以下学习目标建议必要的先决知识：

学习目标：{goal.description}
目标规模：{goal.scale.value}
当前进度：{goal.overall_progress:.1%}

请：
1. 列出3-5个最重要的先决知识领域
2. 为每个领域提供简要说明
3. 建议学习顺序
4. 推荐学习资源（如果有）

请提供结构化的建议。"""
        
        llm_client = LLMClient()
        response = llm_client.call_llm(prompt=prompt, max_tokens=1500)
        
        if response:
            return {
                "type": "prerequisites",
                "content": response,
                "suggested_actions": [
                    "学习建议的先决知识",
                    "按建议顺序逐步学习",
                    "寻找推荐的学习资源"
                ]
            }
        
        return None
    
    def _adjust_learning_strategy(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """调整学习策略"""
        goal = context.get("goal")
        if not goal:
            return None
        
        prompt = f"""检测到学习停滞，请为以下学习目标调整学习策略：

学习目标：{goal.description}
当前策略：{goal.strategy.value}
当前进度：{goal.overall_progress:.1%}
学习时间：{goal.total_learning_time_minutes}分钟

请：
1. 分析可能的学习障碍
2. 建议2-3种替代学习策略
3. 调整学习计划建议
4. 提供突破学习停滞的具体方法

请提供结构化的策略调整建议。"""
        
        llm_client = LLMClient()
        response = llm_client.call_llm(prompt=prompt, max_tokens=1500)
        
        if response:
            return {
                "type": "strategy_adjustment",
                "content": response,
                "suggested_actions": [
                    "尝试新的学习策略",
                    "调整学习时间和频率",
                    "设置更小的里程碑"
                ]
            }
        
        return None
    
    def _suggest_advanced_topics(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """建议进阶主题"""
        goal = context.get("goal")
        if not goal:
            return None
        
        prompt = f"""为已完成基础学习的学习者建议进阶主题：

学习目标：{goal.description}
当前进度：{goal.overall_progress:.1%}
掌握程度：较高

请：
1. 建议3-5个相关的进阶主题
2. 说明每个主题的学习价值
3. 提供学习路径建议
4. 推荐深入学习的资源

请提供结构化的进阶学习建议。"""
        
        llm_client = LLMClient()
        response = llm_client.call_llm(prompt=prompt, max_tokens=1500)
        
        if response:
            return {
                "type": "advanced_topics",
                "content": response,
                "suggested_actions": [
                    "探索建议的进阶主题",
                    "深入研究感兴趣的方向",
                    "尝试实际项目应用"
                ]
            }
        
        return None
    
    def _increase_interactivity(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """增加学习互动性"""
        goal = context.get("goal")
        if not goal:
            return None
        
        prompt = f"""为以下学习目标设计增加互动性的学习活动：

学习目标：{goal.description}
当前进度：{goal.overall_progress:.1%}
检测到低参与度

请：
1. 设计3-5个互动学习活动
2. 说明每个活动的实施方法
3. 预估每个活动的时间
4. 提供评估互动效果的方法

请提供结构化的互动学习计划。"""
        
        llm_client = LLMClient()
        response = llm_client.call_llm(prompt=prompt, max_tokens=1500)
        
        if response:
            return {
                "type": "interactivity_plan",
                "content": response,
                "suggested_actions": [
                    "尝试设计的互动活动",
                    "增加学习中的实践环节",
                    "与他人讨论学习内容"
                ]
            }
        
        return None

# ========== 感知管理器 ==========

class PerceptionManager:
    """感知管理器 - 整合多模态感知与知识提取功能"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.llm_config = LLMConfig()
            self.llm_client = LLMClient(self.llm_config)
            self.mindmap_generator = MindMapGenerator(self.llm_client)
            self.multimodal_recognizer = MultimodalRecognizer(self.llm_client)
            self.knowledge_extractor = KnowledgeExtractor(self.multimodal_recognizer)
            self.active_learning_trigger = ActiveLearningTrigger(self.mindmap_generator, self.knowledge_extractor)
            self._initialized = True
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return self.llm_config.get_available_models()
    
    def switch_model(self, model_name: str) -> bool:
        """切换当前模型"""
        return self.llm_client.switch_model(model_name)
    
    def generate_mindmap_for_goal(self, goal: LearningGoal) -> Optional[MindMapNode]:
        """为学习目标生成思维导图"""
        return self.mindmap_generator.generate_for_goal(goal)
    
    def extract_knowledge_from_text(self, text: str, source: str = "unknown") -> List[KnowledgeNode]:
        """从文本提取知识"""
        return self.knowledge_extractor.extract_from_text(text, source)
    
    def extract_knowledge_from_image(self, image_data: Any, source: str = "unknown") -> List[KnowledgeNode]:
        """从图片提取知识"""
        return self.knowledge_extractor.extract_from_image(image_data, source)
    
    def extract_knowledge_from_multimodal(self, content_dict: Dict[str, Any], source: str = "unknown") -> List[KnowledgeNode]:
        """从多模态内容提取知识"""
        return self.knowledge_extractor.extract_from_multimodal(content_dict, source)
    
    def monitor_and_trigger(self, goal: LearningGoal, knowledge_nodes: List[KnowledgeNode]) -> Dict[str, Any]:
        """监测学习状态并触发主动学习"""
        return self.active_learning_trigger.monitor_learning_state(goal, knowledge_nodes)

# ========== 测试代码 ==========

if __name__ == "__main__":
    print("🧪 测试感知模块（多模态感知与知识提取）...")
    print("=" * 70)
    
    # 初始化管理器
    manager = PerceptionManager()
    
    print(f"🤖 可用模型: {', '.join(manager.get_available_models())}")
    
    # 测试思维导图生成
    print("\n🧠 测试思维导图生成:")
    print("-" * 50)
    
    foundation = FoundationManager()
    test_goal = foundation.create_learning_goal("学习Python编程基础")
    test_goal.target_knowledge_count = 50
    test_goal.scale = GoalScale.SMALL
    
    mindmap = manager.generate_mindmap_for_goal(test_goal)
    
    if mindmap:
        print(f"✅ 思维导图生成成功")
        print(f"   根节点: {mindmap.title}")
        print(f"   描述: {mindmap.description}")
        print(f"   子节点数量: {len(mindmap.children_ids)}")
        print(f"   预估学习时间: {mindmap.estimated_time_minutes}分钟")
    else:
        print("❌ 思维导图生成失败")
    
    # 测试文本知识提取
    print("\n📝 测试文本知识提取:")
    print("-" * 50)
    
    test_text = """人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。
    这些任务包括视觉感知、语音识别、决策制定和语言翻译等。机器学习是人工智能的一个重要子领域，
    它使计算机能够在没有明确编程的情况下学习。深度学习是机器学习的一种，使用神经网络模拟人脑的工作方式。"""
    
    text_nodes = manager.extract_knowledge_from_text(test_text, "test_text")
    
    print(f"✅ 提取了 {len(text_nodes)} 个知识节点")
    for i, node in enumerate(text_nodes[:3]):  # 显示前3个
        print(f"   {i+1}. {node.title} ({node.knowledge_type.value})")
        print(f"      摘要: {node.summary[:60]}...")
    
    # 测试多模态知识提取（模拟）
    print("\n🌐 测试多模态知识提取（模拟）:")
    print("-" * 50)
    
    multimodal_content = {
        "text": "深度学习在图像识别领域有广泛应用，卷积神经网络是其中的关键技术。",
        "image": "data:image/simulated;base64,simulated_image_data",
        "audio": "data:audio/simulated;base64,simulated_audio_data"
    }
    
    multimodal_nodes = manager.extract_knowledge_from_multimodal(multimodal_content, "test_multimodal")
    
    print(f"✅ 提取了 {len(multimodal_nodes)} 个知识节点")
    modalities = [node.modality.value for node in multimodal_nodes]
    print(f"   模态分布: {', '.join(set(modalities))}")
    
    # 测试主动学习触发
    print("\n🚀 测试主动学习触发:")
    print("-" * 50)
    
    # 创建测试知识节点（低置信度模拟混淆）
    test_knowledge_nodes = []
    for i in range(5):
        node = KnowledgeNode(
            id=f"test_node_{i}",
            title=f"测试概念 {i+1}",
            content=f"测试概念 {i+1} 的内容",
            summary=f"测试概念 {i+1} 的摘要",
            confidence=0.2 + i * 0.1,  # 置信度从0.2到0.6
            mastery_score=0.3 + i * 0.1  # 掌握度从0.3到0.7
        )
        test_knowledge_nodes.append(node)
    
    monitoring_result = manager.monitor_and_trigger(test_goal, test_knowledge_nodes)
    
    print(f"✅ 学习状态监测完成")
    print(f"   整体进度: {monitoring_result['overall_progress']:.1%}")
    print(f"   平均置信度: {sum(monitoring_result['confidence_scores'])/len(monitoring_result['confidence_scores']):.2f}")
    print(f"   检测到的问题: {', '.join(monitoring_result['detected_issues']) if monitoring_result['detected_issues'] else '无'}")
    print(f"   触发动作: {len(monitoring_result['triggered_actions'])} 个")
    
    if monitoring_result['recommendations']:
        print(f"   学习推荐:")
        for rec in monitoring_result['recommendations']:
            print(f"     • {rec}")
    
    # 测试主动学习触发功能
    print("\n🎯 测试直接触发主动学习:")
    print("-" * 50)
    
    trigger_context = {
        "goal": test_goal,
        "knowledge_nodes": test_knowledge_nodes,
        "trigger": {"type": "confusion", "description": "测试混淆触发"}
    }
    
    active_learning_result = manager.active_learning_trigger.trigger_active_learning("confusion", trigger_context)
    
    if active_learning_result.get("success"):
        print(f"✅ 主动学习触发成功")
        print(f"   触发类型: {active_learning_result['trigger_type']}")
        print(f"   执行动作: {', '.join(active_learning_result['actions_taken'])}")
    else:
        print(f"❌ 主动学习触发失败: {active_learning_result.get('error', '未知错误')}")
    
    print("\n✅ 感知模块测试完成")
    print("=" * 70)