# qa_context.py - 上下文理解问答系统
"""
新增模块：上下文理解问答系统
功能：基于学习历史和思维导图的智能问答
特点：记忆对话历史、检索相关知识、提供学习指导
创新：思维导图感知的问答，理解学习上下文
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# ========== 对话管理相关数据结构 ==========

@dataclass
class DialogueTurn:
    """对话轮次"""
    id: str
    user_query: str
    system_response: str
    timestamp: str
    query_type: str  # knowledge, guidance, progress, clarification, etc.
    confidence: float = 1.0  # 回答置信度
    
    # 上下文关联
    references: List[str] = field(default_factory=list)  # 引用的知识节点/思维导图节点
    follow_up_questions: List[str] = field(default_factory=list)  # 可能的后续问题
    
    # 元数据
    processing_time_ms: int = 0
    model_used: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_query": self.user_query,
            "system_response": self.system_response,
            "timestamp": self.timestamp,
            "query_type": self.query_type,
            "confidence": self.confidence,
            "references": self.references,
            "follow_up_questions": self.follow_up_questions,
            "processing_time_ms": self.processing_time_ms,
            "model_used": self.model_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueTurn':
        return cls(**data)

@dataclass
class ConversationContext:
    """对话上下文"""
    conversation_id: str
    user_id: str = "default_user"
    goal_id: Optional[str] = None  # 关联的学习目标
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 对话历史
    turns: List[DialogueTurn] = field(default_factory=list)
    current_topic: str = ""
    
    # 上下文窗口
    context_window_size: int = 10  # 保留的对话轮次数
    important_turns: List[str] = field(default_factory=list)  # 重要的对话轮次ID
    
    # 对话状态
    is_active: bool = True
    mood_tone: str = "neutral"  # 对话情绪基调
    
    def add_turn(self, turn: DialogueTurn):
        """添加对话轮次"""
        self.turns.append(turn)
        self.last_updated = datetime.now().isoformat()
        
        # 保持上下文窗口大小
        if len(self.turns) > self.context_window_size:
            # 移除非重要的旧对话
            to_keep = [t for t in self.turns if t.id in self.important_turns]
            to_keep.extend(self.turns[-5:])  # 保留最近5条
            self.turns = to_keep
    
    def get_recent_turns(self, n: int = 5) -> List[DialogueTurn]:
        """获取最近n轮对话"""
        return self.turns[-n:] if self.turns else []
    
    def get_context_summary(self) -> str:
        """生成对话上下文摘要"""
        if not self.turns:
            return "暂无对话历史"
        
        summary = f"对话主题：{self.current_topic}\n\n最近对话：\n"
        for i, turn in enumerate(self.turns[-3:], 1):
            summary += f"{i}. 用户：{turn.user_query[:50]}...\n"
            summary += f"   系统：{turn.system_response[:50]}...\n"
        
        return summary
    
    def mark_important(self, turn_id: str):
        """标记重要对话轮次"""
        if turn_id not in self.important_turns:
            self.important_turns.append(turn_id)

# ========== 问答系统核心类 ==========

class ContextAwareQASystem:
    """
    上下文感知问答系统
    基于学习历史和思维导图提供智能回答
    """
    
    def __init__(self, model_provider=None):
        """
        初始化问答系统
        
        Args:
            model_provider: 大模型提供者（如豆包/DeepSeek API）
        """
        self.model_provider = model_provider
        
        # 对话管理
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.conversation_history: Dict[str, List[ConversationContext]] = {}
        
        # 知识检索缓存
        self.knowledge_cache: Dict[str, Any] = {}
        self.cache_expiry = timedelta(hours=1)
        
        # 系统配置
        self.max_context_turns = 10
        self.enable_memory = True
        self.response_confidence_threshold = 0.7
        
        # 预定义回答模板
        self.templates = self._load_templates()
        
        # 问题分类器
        self.question_types = {
            "knowledge": ["什么是", "解释", "定义", "含义", "原理"],
            "guidance": ["如何", "怎样", "步骤", "方法", "技巧"],
            "progress": ["进度", "完成", "学习", "掌握", "复习"],
            "clarification": ["为什么", "原因", "区别", "对比", "优缺点"],
            "operation": ["开始", "停止", "暂停", "继续", "修改", "删除"]
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """加载回答模板"""
        return {
            "greeting": "您好！我是您的学习助手。我可以帮您解答关于学习内容的疑问，提供学习指导，或者查询学习进度。请问有什么可以帮您的吗？",
            "knowledge_not_found": "我目前还没有学习过这个知识点。您可以让我先学习相关内容，或者告诉我您想了解的具体方面。",
            "learning_guidance": "基于您的学习目标，我建议您按照以下步骤进行：\n1. {step1}\n2. {step2}\n3. {step3}",
            "progress_report": "您当前的学习进度是：{progress}%。已完成{completed}个知识点，剩余{remaining}个。预计还需要{time_remaining}。",
            "clarification_request": "您能再具体说明一下您想了解什么吗？比如具体哪个方面，或者您的困惑点在哪里？",
            "system_operation": "好的，我已经为您{operation}了相关操作。"
        }
    
    def classify_question(self, question: str) -> Tuple[str, float]:
        """
        分类问题类型
        
        Returns:
            (问题类型, 置信度)
        """
        question_lower = question.lower()
        
        scores = {}
        for q_type, keywords in self.question_types.items():
            score = 0
            for keyword in keywords:
                if keyword in question_lower:
                    score += 1
            scores[q_type] = score / len(keywords)
        
        # 找到最高分
        best_type = max(scores.items(), key=lambda x: x[1])
        
        # 如果没有匹配，使用通用类型
        if best_type[1] < 0.1:
            return "general", 0.5
        
        return best_type
    
    def retrieve_relevant_knowledge(self, 
                                  question: str, 
                                  knowledge_base: Optional[Dict] = None,
                                  mindmap_nodes: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        检索相关知识
        
        Args:
            question: 用户问题
            knowledge_base: 知识库 {node_id: KnowledgeNode}
            mindmap_nodes: 思维导图节点 {node_id: MindMapNode}
        
        Returns:
            相关知识点列表
        """
        relevant_items = []
        
        if knowledge_base:
            # 简单关键词匹配
            keywords = self._extract_keywords(question)
            
            for node_id, node in knowledge_base.items():
                relevance_score = self._calculate_relevance(node, keywords)
                if relevance_score > 0.3:  # 阈值
                    relevant_items.append({
                        "id": node_id,
                        "type": "knowledge",
                        "title": node.title,
                        "content": node.content[:200] + "..." if len(node.content) > 200 else node.content,
                        "relevance": relevance_score,
                        "node": node
                    })
        
        if mindmap_nodes:
            # 思维导图节点匹配
            for node_id, node in mindmap_nodes.items():
                # 检查标题和描述是否相关
                title_match = any(keyword in node.title.lower() for keyword in self._extract_keywords(question.lower()))
                desc_match = any(keyword in node.description.lower() for keyword in self._extract_keywords(question.lower()))
                
                if title_match or desc_match:
                    relevant_items.append({
                        "id": node_id,
                        "type": "mindmap",
                        "title": node.title,
                        "description": node.description,
                        "relevance": 0.7 if title_match else 0.5,
                        "node": node
                    })
        
        # 按相关性排序
        relevant_items.sort(key=lambda x: x["relevance"], reverse=True)
        
        return relevant_items[:5]  # 返回前5个最相关的
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取，实际应用中可以使用更复杂的方法
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        
        # 过滤停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        return keywords
    
    def _calculate_relevance(self, knowledge_node, keywords: List[str]) -> float:
        """计算知识节点与关键词的相关性"""
        if not keywords:
            return 0.0
        
        content_lower = (knowledge_node.title + " " + knowledge_node.content).lower()
        
        # 计算匹配分数
        score = 0.0
        for keyword in keywords:
            if keyword in content_lower:
                # 标题中的匹配权重更高
                if keyword in knowledge_node.title.lower():
                    score += 0.3
                else:
                    score += 0.1
        
        # 归一化到0-1
        return min(score, 1.0)
    
    def generate_response(self,
                         question: str,
                         conversation_id: str = "default",
                         user_id: str = "default_user",
                         knowledge_base: Optional[Dict] = None,
                         mindmap_nodes: Optional[Dict] = None,
                         learning_goal: Optional[Any] = None) -> Dict[str, Any]:
        """
        生成回答
        
        Returns:
            包含回答和元数据的字典
        """
        start_time = datetime.now()
        
        # 获取或创建对话上下文
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id
            )
        
        context = self.active_conversations[conversation_id]
        
        # 获取最近的对话历史
        recent_turns = context.get_recent_turns(3)
        context_summary = context.get_context_summary() if recent_turns else ""
        
        # 分类问题
        question_type, type_confidence = self.classify_question(question)
        
        # 检索相关知识
        relevant_knowledge = self.retrieve_relevant_knowledge(question, knowledge_base, mindmap_nodes)
        
        # 生成回答
        if self.model_provider and relevant_knowledge:
            # 使用大模型生成更智能的回答
            response = self._generate_with_model(question, relevant_knowledge, context_summary, question_type)
        else:
            # 使用模板生成回答
            response = self._generate_with_template(question, relevant_knowledge, question_type)
        
        # 创建对话轮次
        turn = DialogueTurn(
            id=f"turn_{int(datetime.now().timestamp())}_{hashlib.md5(question.encode()).hexdigest()[:6]}",
            user_query=question,
            system_response=response["answer"],
            timestamp=datetime.now().isoformat(),
            query_type=question_type,
            confidence=response.get("confidence", 0.8),
            references=[item["id"] for item in relevant_knowledge[:3]],
            processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
        )
        
        # 添加到对话历史
        context.add_turn(turn)
        
        # 更新当前话题
        if question_type == "knowledge" and relevant_knowledge:
            context.current_topic = relevant_knowledge[0]["title"]
        
        return {
            "answer": response["answer"],
            "conversation_id": conversation_id,
            "turn_id": turn.id,
            "question_type": question_type,
            "confidence": response.get("confidence", 0.8),
            "references": turn.references,
            "relevant_knowledge": [
                {
                    "id": item["id"],
                    "type": item["type"],
                    "title": item["title"],
                    "relevance": item["relevance"]
                }
                for item in relevant_knowledge[:3]
            ],
            "suggested_follow_up": response.get("follow_up", []),
            "processing_time_ms": turn.processing_time_ms
        }
    
    def _generate_with_model(self, 
                           question: str, 
                           relevant_knowledge: List[Dict], 
                           context_summary: str,
                           question_type: str) -> Dict[str, Any]:
        """使用大模型生成回答"""
        # 构建上下文提示
        context_parts = []
        
        if context_summary:
            context_parts.append(f"对话历史：\n{context_summary}\n")
        
        if relevant_knowledge:
            context_parts.append("相关知识点：")
            for i, item in enumerate(relevant_knowledge[:3], 1):
                if item["type"] == "knowledge":
                    context_parts.append(f"{i}. {item['title']}: {item['content']}")
                else:
                    context_parts.append(f"{i}. {item['title']}: {item['description']}")
        
        context = "\n".join(context_parts) if context_parts else "没有找到相关上下文信息。"
        
        # 构建提示词
        prompt = f"""你是一个智能学习助手。请基于以下信息回答用户的问题。

{context}

用户问题：{question}

请按照以下要求回答：
1. 基于提供的上下文信息回答，不要编造不知道的信息
2. 如果信息不足，诚实地告知用户
3. 回答要清晰、有条理
4. 可以适当补充相关的学习建议

请开始回答："""
        
        try:
            # 调用大模型（这里需要实际的API调用）
            if self.model_provider:
                # response = self.model_provider.generate(prompt)
                # 模拟响应
                if relevant_knowledge:
                    answer = f"根据您的查询，我找到了以下信息：\n\n"
                    for item in relevant_knowledge[:2]:
                        answer += f"• {item['title']}: "
                        if item["type"] == "knowledge":
                            answer += f"{item['content'][:150]}...\n"
                        else:
                            answer += f"{item['description']}\n"
                    answer += "\n您想深入了解哪个方面呢？"
                else:
                    answer = "我没有找到与您的问题直接相关的学习内容。您是否希望我帮您学习这个主题？"
            else:
                answer = self._generate_with_template(question, relevant_knowledge, question_type)["answer"]
            
            return {
                "answer": answer,
                "confidence": 0.8 if relevant_knowledge else 0.5,
                "follow_up": self._generate_follow_up_questions(question, relevant_knowledge)
            }
            
        except Exception as e:
            # 如果模型调用失败，回退到模板
            return self._generate_with_template(question, relevant_knowledge, question_type)
    
    def _generate_with_template(self, 
                              question: str, 
                              relevant_knowledge: List[Dict],
                              question_type: str) -> Dict[str, Any]:
        """使用模板生成回答"""
        
        if question_type == "greeting" or "你好" in question or "hi" in question.lower():
            return {
                "answer": self.templates["greeting"],
                "confidence": 0.9,
                "follow_up": ["我可以开始学习什么？", "我的学习进度如何？"]
            }
        
        if not relevant_knowledge:
            return {
                "answer": self.templates["knowledge_not_found"],
                "confidence": 0.3,
                "follow_up": ["我想学习这个主题", "换个方式问一下"]
            }
        
        if question_type == "knowledge":
            # 知识型问题
            answer = f"关于'{relevant_knowledge[0]['title']}'，"
            if relevant_knowledge[0]["type"] == "knowledge":
                answer += f"我了解到：{relevant_knowledge[0]['content'][:200]}..."
            else:
                answer += f"这是思维导图中的重要节点：{relevant_knowledge[0]['description']}"
            
            if len(relevant_knowledge) > 1:
                answer += f"\n\n相关知识点还有：{', '.join([item['title'] for item in relevant_knowledge[1:3]])}"
            
            return {
                "answer": answer,
                "confidence": 0.8,
                "follow_up": self._generate_follow_up_questions(question, relevant_knowledge)
            }
        
        elif question_type == "guidance":
            # 指导型问题
            if relevant_knowledge:
                answer = self.templates["learning_guidance"].format(
                    step1=f"学习{relevant_knowledge[0]['title']}的基础概念",
                    step2=f"理解{relevant_knowledge[0]['title']}的应用场景",
                    step3=f"练习相关技能或做测试题"
                )
            else:
                answer = "我可以为您制定学习计划。请告诉我您具体想学习什么？"
            
            return {
                "answer": answer,
                "confidence": 0.7,
                "follow_up": ["需要更详细的学习步骤吗？", "想了解学习时间安排吗？"]
            }
        
        else:
            # 默认回答
            answer = f"我找到了以下相关信息：\n"
            for i, item in enumerate(relevant_knowledge[:3], 1):
                answer += f"{i}. {item['title']} (相关度：{item['relevance']:.2f})\n"
            
            answer += "\n您想先了解哪一个呢？"
            
            return {
                "answer": answer,
                "confidence": 0.6,
                "follow_up": self._generate_follow_up_questions(question, relevant_knowledge)
            }
    
    def _generate_follow_up_questions(self, question: str, relevant_knowledge: List[Dict]) -> List[str]:
        """生成后续问题建议"""
        follow_ups = []
        
        if relevant_knowledge:
            # 基于第一个相关知识点生成后续问题
            first_item = relevant_knowledge[0]
            
            if first_item["type"] == "knowledge":
                follow_ups.extend([
                    f"{first_item['title']}的具体应用场景是什么？",
                    f"学习{first_item['title']}需要什么基础知识？",
                    f"{first_item['title']}和哪些其他概念相关？"
                ])
            else:
                follow_ups.extend([
                    f"关于{first_item['title']}的详细解释是什么？",
                    f"{first_item['title']}在思维导图中处于什么位置？",
                    f"如何深入学习{first_item['title']}？"
                ])
        
        # 通用后续问题
        follow_ups.extend([
            "我的学习进度如何？",
            "下一步建议学习什么？",
            "可以测试一下我的掌握程度吗？"
        ])
        
        return follow_ups[:3]  # 返回前3个
    
    def get_conversation_history(self, conversation_id: str) -> List[DialogueTurn]:
        """获取对话历史"""
        if conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id].turns
        return []
    
    def clear_conversation(self, conversation_id: str):
        """清空对话历史"""
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id].turns = []
    
    def export_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """导出对话"""
        if conversation_id in self.active_conversations:
            context = self.active_conversations[conversation_id]
            return {
                "conversation_id": context.conversation_id,
                "created_at": context.created_at,
                "last_updated": context.last_updated,
                "turns": [turn.to_dict() for turn in context.turns],
                "current_topic": context.current_topic
            }
        return {}

# ========== 学习指导专用问答 ==========

class LearningAdvisor:
    """
    学习指导顾问
    专门回答学习方法、进度、规划等问题
    """
    
    def __init__(self, qa_system: ContextAwareQASystem):
        self.qa_system = qa_system
        self.learning_strategies = self._load_strategies()
    
    def _load_strategies(self) -> Dict[str, Dict[str, Any]]:
        """加载学习策略库"""
        return {
            "spaced_repetition": {
                "name": "间隔重复",
                "description": "根据记忆曲线安排复习时间",
                "steps": ["初次学习", "1天后复习", "3天后复习", "1周后复习", "1月后复习"],
                "best_for": ["记忆类知识", "单词", "概念"]
            },
            "active_recall": {
                "name": "主动回忆",
                "description": "通过主动测试来加强记忆",
                "steps": ["学习后立即自测", "不看材料回忆", "检查回忆准确性", "重复薄弱环节"],
                "best_for": ["考试准备", "技能掌握"]
            },
            "interleaving": {
                "name": "交错学习",
                "description": "混合学习不同主题，提高辨别能力",
                "steps": ["学习主题A", "切换到主题B", "再学习主题C", "循环进行"],
                "best_for": ["关联概念", "复杂技能"]
            },
            "mindmap_learning": {
                "name": "思维导图学习法",
                "description": "通过构建思维导图理解知识结构",
                "steps": ["确定中心主题", "添加主要分支", "细化子分支", "添加关联", "复习整个结构"],
                "best_for": ["系统性知识", "复杂概念", "项目规划"]
            }
        }
    
    def advise_on_method(self, topic: str, current_method: str = "") -> str:
        """提供学习方法建议"""
        # 根据主题推荐方法
        topic_lower = topic.lower()
        
        recommendations = []
        
        if any(word in topic_lower for word in ["单词", "词汇", "记忆", "背诵"]):
            recommendations.append(self.learning_strategies["spaced_repetition"])
            recommendations.append(self.learning_strategies["active_recall"])
        
        elif any(word in topic_lower for word in ["概念", "理论", "原理", "系统"]):
            recommendations.append(self.learning_strategies["mindmap_learning"])
            recommendations.append(self.learning_strategies["interleaving"])
        
        elif any(word in topic_lower for word in ["技能", "操作", "实践", "项目"]):
            recommendations.append(self.learning_strategies["active_recall"])
        
        else:
            # 默认推荐
            recommendations.append(self.learning_strategies["mindmap_learning"])
            recommendations.append(self.learning_strategies["spaced_repetition"])
        
        # 生成建议
        advice = f"对于'{topic}'的学习，我建议：\n\n"
        
        for i, strategy in enumerate(recommendations[:2], 1):
            advice += f"{i}. {strategy['name']}：{strategy['description']}\n"
            advice += f"   适用：{', '.join(strategy['best_for'])}\n"
            advice += f"   步骤：{' → '.join(strategy['steps'])}\n\n"
        
        return advice
    
    def analyze_progress(self, goal_progress: Dict[str, Any]) -> str:
        """分析学习进度并提供建议"""
        overall_progress = goal_progress.get("overall_progress", 0)
        learning_time = goal_progress.get("total_learning_time_minutes", 0)
        avg_score = goal_progress.get("avg_test_score", 0)
        
        analysis = f"学习进度分析：\n"
        analysis += f"• 总体进度：{overall_progress*100:.1f}%\n"
        analysis += f"• 学习时间：{learning_time}分钟\n"
        analysis += f"• 平均测试分：{avg_score:.1f}/100\n\n"
        
        if overall_progress < 0.3:
            analysis += "🔴 刚刚开始阶段\n建议：打好基础，理解核心概念，不要急于求成。"
        elif overall_progress < 0.7:
            analysis += "🟡 稳步推进阶段\n建议：保持当前节奏，加强练习，注意复习薄弱环节。"
        elif overall_progress < 0.9:
            analysis += "🟢 接近完成阶段\n建议：进行综合复习，做模拟测试，巩固整体知识体系。"
        else:
            analysis += "✅ 基本掌握阶段\n建议：定期复习，尝试应用知识解决实际问题。"
        
        # 基于测试分数的建议
        if avg_score < 60:
            analysis += "\n\n⚠️ 测试分数偏低，建议：\n• 加强基础知识学习\n• 多做练习题\n• 寻求难点帮助"
        elif avg_score < 80:
            analysis += "\n\n📊 测试分数良好，建议：\n• 巩固已学知识\n• 尝试更高难度练习\n• 教别人以加深理解"
        else:
            analysis += "\n\n🎉 测试分数优秀，建议：\n• 挑战综合应用\n• 探索扩展知识\n• 思考知识创新应用"
        
        return analysis

# ========== 集成到原系统 ==========

def integrate_qa_with_system():
    """演示如何将问答系统集成到原系统中"""
    
    # 模拟已有的系统组件
    class MockKnowledgeBase:
        """模拟知识库"""
        def __init__(self):
            self.knowledge_nodes = {
                "k1": type('obj', (object,), {
                    'title': 'Python函数',
                    'content': '函数是一段可重复使用的代码块，可以接受参数并返回值。在Python中使用def关键字定义函数。',
                    'learning_time_minutes': 30
                })(),
                "k2": type('obj', (object,), {
                    'title': '机器学习',
                    'content': '机器学习是人工智能的一个分支，使计算机能够从数据中学习而不需要明确编程。',
                    'learning_time_minutes': 120
                })()
            }
    
    class MockMindMap:
        """模拟思维导图"""
        def __init__(self):
            self.nodes = {
                "m1": type('obj', (object,), {
                    'title': 'Python基础',
                    'description': '包含变量、函数、控制流等基础知识',
                    'depth': 1
                })(),
                "m2": type('obj', (object,), {
                    'title': '高级特性',
                    'description': '装饰器、生成器、上下文管理器等',
                    'depth': 2
                })()
            }
    
    # 初始化问答系统
    qa_system = ContextAwareQASystem()
    knowledge_base = MockKnowledgeBase()
    mindmap = MockMindMap()
    
    return qa_system, knowledge_base, mindmap

# ========== 测试代码 ==========

if __name__ == "__main__":
    print("🧠 测试上下文理解问答系统...")
    print("=" * 70)
    
    # 初始化系统
    qa_system, knowledge_base, mindmap = integrate_qa_with_system()
    
    # 模拟问题
    test_questions = [
        "什么是Python函数？",
        "如何学习机器学习？",
        "我的学习进度怎么样？",
        "Python基础包括哪些内容？",
        "你好"
    ]
    
    print("\n💬 问答测试:")
    print("-" * 50)
    
    for question in test_questions:
        print(f"\n用户：{question}")
        
        response = qa_system.generate_response(
            question=question,
            knowledge_base=knowledge_base.knowledge_nodes,
            mindmap_nodes=mindmap.nodes
        )
        
        print(f"助手：{response['answer'][:150]}...")
        print(f"  类型：{response['question_type']}, 置信度：{response['confidence']:.2f}")
        
        if response['relevant_knowledge']:
            print(f"  参考：{', '.join([item['title'] for item in response['relevant_knowledge']])}")
    
    # 测试学习指导
    print("\n\n🎓 学习指导测试:")
    print("-" * 50)
    
    advisor = LearningAdvisor(qa_system)
    
    # 学习方法建议
    print("\n1. 学习方法建议:")
    advice = advisor.advise_on_method("Python编程")
    print(advice)
    
    # 进度分析
    print("\n2. 进度分析:")
    mock_progress = {
        "overall_progress": 0.65,
        "total_learning_time_minutes": 480,
        "avg_test_score": 72.5
    }
    analysis = advisor.analyze_progress(mock_progress)
    print(analysis)
    
    # 测试对话历史
    print("\n\n📝 对话历史测试:")
    print("-" * 50)
    
    # 模拟连续对话
    conversation_id = "test_conversation"
    
    questions = [
        "什么是机器学习？",
        "它有什么应用？",
        "学习机器学习需要什么基础？"
    ]
    
    for i, question in enumerate(questions):
        print(f"\n第{i+1}轮对话:")
        print(f"用户：{question}")
        
        response = qa_system.generate_response(
            question=question,
            conversation_id=conversation_id,
            knowledge_base=knowledge_base.knowledge_nodes,
            mindmap_nodes=mindmap.nodes
        )
        
        print(f"助手：{response['answer'][:100]}...")
    
    # 查看对话历史
    print(f"\n对话历史记录（共{len(qa_system.get_conversation_history(conversation_id))}轮）：")
    for turn in qa_system.get_conversation_history(conversation_id):
        print(f"  - {turn.user_query[:30]}... → {turn.system_response[:30]}...")
    
    print("\n✅ 上下文理解问答系统测试完成")
    print("=" * 70)