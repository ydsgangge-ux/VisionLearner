# explorer/question_engine.py
"""
智能提问引擎 - 基于思维导图的深度提问系统
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict

from foundation import MindMapNode, KnowledgeNode, generate_id
from perception import LLMClient


class IntelligentQuestionEngine:
    """
    智能提问引擎 - 基于思维导图的深度提问系统
    通过系统性提问促进深度知识探索
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

        # 提问模板库
        self.question_templates = {
            "concept": [
                "什么是{concept}？",
                "{concept}的核心特征是什么？",
                "{concept}与其他相关概念有什么区别？",
                "{concept}在现实中有哪些应用？"
            ],
            "principle": [
                "{principle}的基本原理是什么？",
                "{principle}是如何运作的？",
                "{principle}背后的理论基础是什么？",
                "如何验证{principle}的正确性？"
            ],
            "skill": [
                "如何掌握{skill}？",
                "{skill}的关键步骤是什么？",
                "实践{skill}时需要注意什么？",
                "如何评估{skill}的掌握程度？"
            ],
            "process": [
                "{process}的主要阶段是什么？",
                "如何优化{process}的效率？",
                "{process}中的关键决策点是什么？",
                "如何评估{process}的效果？"
            ],
            "system": [
                "{system}的主要组成部分是什么？",
                "{system}各组件如何相互作用？",
                "如何设计一个有效的{system}？",
                "{system}的评估标准是什么？"
            ],
            "example": [
                "这个例子说明了什么原理？",
                "这个例子中的关键点是什么？",
                "如何将这个例子应用到其他场景？",
                "这个例子有哪些局限性？"
            ],
            "general": [
                "关于{concept}，你最想了解什么？",
                "学习{concept}最大的困难是什么？",
                "{concept}未来可能如何发展？",
                "如何将{concept}与其他知识结合？"
            ]
        }

        # 提问深度级别
        self.question_depths = {
            "surface": {
                "name": "表面理解",
                "questions": ["是什么", "有什么", "什么时候", "谁", "哪里"],
                "thinking_time": 30
            },
            "understanding": {
                "name": "理解掌握",
                "questions": ["为什么", "如何", "怎么样", "解释", "说明"],
                "thinking_time": 60
            },
            "application": {
                "name": "应用实践",
                "questions": ["如何应用", "如何解决", "如何改进", "如何使用"],
                "thinking_time": 90
            },
            "analysis": {
                "name": "分析评估",
                "questions": ["有什么联系", "有什么差异", "有什么影响", "分析", "比较"],
                "thinking_time": 120
            },
            "evaluation": {
                "name": "评价创造",
                "questions": ["有什么价值", "有什么局限", "如何评价", "批判", "判断"],
                "thinking_time": 150
            },
            "creation": {
                "name": "创新整合",
                "questions": ["如何创新", "如何设计", "如何整合", "创建", "发明"],
                "thinking_time": 180
            }
        }

        # 问题难度级别
        self.difficulty_levels = {
            "easy": {
                "description": "基础理解",
                "keywords": ["定义", "是什么", "举例", "描述"],
                "thinking_time": 30
            },
            "medium": {
                "description": "分析应用",
                "keywords": ["为什么", "如何", "比较", "应用"],
                "thinking_time": 60
            },
            "hard": {
                "description": "综合创新",
                "keywords": ["设计", "评估", "创新", "批判"],
                "thinking_time": 120
            }
        }

    def generate_questions_for_node(self,
                                  node: Union[MindMapNode, KnowledgeNode],
                                  depth_level: str = "understanding",
                                  count: int = 5) -> List[Dict[str, Any]]:
        """
        为节点生成问题
        """
        print(f"🤔 为节点生成问题: {node.title}")

        questions = []
        node_type = self._determine_node_type(node)
        template_key = node_type if node_type in self.question_templates else "general"
        templates = self.question_templates.get(template_key, self.question_templates["general"])

        depth_info = self.question_depths.get(depth_level, self.question_depths["understanding"])
        depth_questions = depth_info["questions"]

        selected_templates = []
        for template in templates:
            for depth_q in depth_questions:
                if depth_q in template:
                    selected_templates.append(template)
                    break
        if not selected_templates:
            selected_templates = templates

        for i in range(min(count, len(selected_templates))):
            template = selected_templates[i % len(selected_templates)]
            question_text = template.format(
                concept=node.title,
                principle=node.title,
                skill=node.title,
                process=node.title,
                system=node.title,
                example=node.title
            )
            difficulty = self._determine_difficulty(question_text, depth_level)
            question = {
                "id": generate_id(f"question_{i}_"),
                "text": question_text,
                "node_id": node.id,
                "node_title": node.title,
                "node_type": node_type,
                "depth_level": depth_level,
                "depth_name": depth_info["name"],
                "difficulty": difficulty,
                "difficulty_description": self.difficulty_levels[difficulty]["description"],
                "estimated_thinking_time": self.difficulty_levels[difficulty]["thinking_time"],
                "generated_at": datetime.now().isoformat(),
                "tags": [node_type, depth_level, difficulty]
            }
            questions.append(question)

        if len(questions) < count:
            additional_questions = self._generate_questions_with_llm(
                node, depth_level, count - len(questions)
            )
            questions.extend(additional_questions)

        print(f"✅ 生成了 {len(questions)} 个问题")
        return questions

    def generate_questions_for_mindmap(self,
                                     mindmap_root: MindMapNode,
                                     node_map: Dict[str, MindMapNode],
                                     depth_level: str = "understanding",
                                     questions_per_node: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        为整个思维导图生成问题
        """
        print(f"🧠 为思维导图生成问题 (深度: {depth_level})")
        all_questions = defaultdict(list)
        for node_id, node in node_map.items():
            questions = self.generate_questions_for_node(node, depth_level, questions_per_node)
            if questions:
                all_questions[node_id] = questions
        return dict(all_questions)

    def generate_deep_questions_chain(self,
                                    start_node: Union[MindMapNode, KnowledgeNode],
                                    node_map: Optional[Dict[str, Any]] = None,
                                    chain_length: int = 5) -> List[Dict[str, Any]]:
        """
        生成深度问题链
        """
        print(f"🔗 生成深度问题链 (起始: {start_node.title})")
        question_chain = []
        initial_questions = self.generate_questions_for_node(start_node, "analysis", 1)
        if not initial_questions:
            return question_chain
        current_question = initial_questions[0]
        question_chain.append(current_question)

        chain_prompt = f"""基于以下问题生成一个深度问题链：

初始问题：{current_question['text']}
上下文：关于{start_node.title}

请生成一个包含{chain_length-1}个后续问题的问题链，要求：
1. 每个问题都基于前一个问题的答案
2. 问题逐渐深入，从理解到应用到分析到创新
3. 问题之间要有逻辑联系
4. 每个问题应该是开放式的，促进深度思考

请以JSON数组格式返回问题链，每个问题包含：
- text: 问题文本
- depth_level: 问题深度级别
- reasoning: 为什么提出这个问题
"""
        response = self.llm_client.call_llm(
            prompt=chain_prompt,
            system_prompt="你是问题设计专家，擅长创建连贯的深度问题链。",
            max_tokens=1500,
            temperature=0.7
        )
        if response:
            try:
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    chain_questions = json.loads(json_str)
                    for i, q_data in enumerate(chain_questions):
                        if len(question_chain) >= chain_length:
                            break
                        question = {
                            "id": generate_id(f"chain_{i}_"),
                            "text": q_data.get("text", f"问题 {i+1}"),
                            "node_id": start_node.id,
                            "node_title": start_node.title,
                            "depth_level": q_data.get("depth_level", "analysis"),
                            "depth_name": self.question_depths.get(
                                q_data.get("depth_level", "analysis"), {}
                            ).get("name", "分析评估"),
                            "difficulty": "hard",
                            "difficulty_description": "综合创新",
                            "estimated_thinking_time": 120,
                            "is_chained": True,
                            "chain_index": i + 1,
                            "reasoning": q_data.get("reasoning", ""),
                            "generated_at": datetime.now().isoformat()
                        }
                        question_chain.append(question)
            except Exception as e:
                print(f"❌ 问题链解析失败: {str(e)}")

        if len(question_chain) < chain_length:
            remaining = chain_length - len(question_chain)
            additional_questions = self.generate_questions_for_node(start_node, "evaluation", remaining)
            for i, q in enumerate(additional_questions):
                if len(question_chain) >= chain_length:
                    break
                q["is_chained"] = True
                q["chain_index"] = len(question_chain) + 1
                question_chain.append(q)

        print(f"✅ 生成了 {len(question_chain)} 个问题的深度问题链")
        return question_chain

    def generate_comparison_questions(self,
                                    node1: Union[MindMapNode, KnowledgeNode],
                                    node2: Union[MindMapNode, KnowledgeNode]) -> List[Dict[str, Any]]:
        """
        生成比较性问题
        """
        print(f"⚖️ 生成比较性问题: {node1.title} vs {node2.title}")
        comparison_questions = []
        comparison_templates = [
            "{concept1}和{concept2}有什么相同点？",
            "{concept1}和{concept2}有什么不同点？",
            "在什么情况下应该使用{concept1}而不是{concept2}？",
            "{concept1}和{concept2}如何相互影响？",
            "学习{concept1}对理解{concept2}有什么帮助？"
        ]
        for i, template in enumerate(comparison_templates):
            question_text = template.format(concept1=node1.title, concept2=node2.title)
            question = {
                "id": generate_id(f"comparison_{i}_"),
                "text": question_text,
                "node_ids": [node1.id, node2.id],
                "node_titles": [node1.title, node2.title],
                "question_type": "comparison",
                "depth_level": "analysis",
                "depth_name": "分析评估",
                "difficulty": "medium",
                "difficulty_description": "分析应用",
                "estimated_thinking_time": 90,
                "generated_at": datetime.now().isoformat(),
                "tags": ["比较", "分析", "关系"]
            }
            comparison_questions.append(question)

        comparison_prompt = f"""请生成一些深入比较{node1.title}和{node2.title}的问题：

要求：
1. 关注两者的本质区别和联系
2. 考虑实际应用场景
3. 包含高级分析性问题
4. 促进深度思考和理解

请生成3-5个比较性问题。"""
        response = self.llm_client.call_llm(prompt=comparison_prompt, max_tokens=800, temperature=0.6)
        if response:
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and ('?' in line or '？' in line):
                    clean_line = re.sub(r'^\d+[\.\)]?\s*', '', line)
                    question = {
                        "id": generate_id("comparison_llm_"),
                        "text": clean_line,
                        "node_ids": [node1.id, node2.id],
                        "node_titles": [node1.title, node2.title],
                        "question_type": "comparison",
                        "depth_level": "analysis",
                        "depth_name": "分析评估",
                        "difficulty": "hard",
                        "difficulty_description": "综合创新",
                        "estimated_thinking_time": 120,
                        "generated_at": datetime.now().isoformat(),
                        "tags": ["比较", "深度分析", "大模型生成"]
                    }
                    comparison_questions.append(question)

        print(f"✅ 生成了 {len(comparison_questions)} 个比较性问题")
        return comparison_questions

    def evaluate_answer_quality(self,
                              question: Dict[str, Any],
                              answer: str,
                              reference_material: Optional[str] = None) -> Dict[str, Any]:
        """
        评估回答质量
        """
        print(f"📊 评估回答质量: {question['text'][:50]}...")
        evaluation = {
            "question_id": question["id"],
            "question_text": question["text"],
            "answer": answer,
            "evaluated_at": datetime.now().isoformat(),
            "scores": {},
            "feedback": "",
            "suggestions": []
        }
        prompt = f"""请评估以下回答的质量：

问题：{question['text']}
用户回答：{answer}

评估标准：
1. 准确性（0-10分）：回答是否准确反映了相关知识
2. 完整性（0-10分）：回答是否全面覆盖了问题的各个方面
3. 深度（0-10分）：回答是否展现了深入思考
4. 清晰度（0-10分）：回答是否表达清晰、条理分明

请提供：
1. 四个维度的分数
2. 总体反馈（指出优点和改进空间）
3. 具体的改进建议

{"参考资料：" + reference_material if reference_material else ""}
"""
        response = self.llm_client.call_llm(
            prompt=prompt,
            system_prompt="你是评估专家，擅长评估学习回答的质量。",
            max_tokens=1000,
            temperature=0.3
        )
        if response:
            scores = {"accuracy": 5.0, "completeness": 5.0, "depth": 5.0, "clarity": 5.0}
            score_patterns = {
                "accuracy": r"准确性[：:]?\s*(\d+(?:\.\d+)?)/10",
                "completeness": r"完整性[：:]?\s*(\d+(?:\.\d+)?)/10",
                "depth": r"深度[：:]?\s*(\d+(?:\.\d+)?)/10",
                "clarity": r"清晰度[：:]?\s*(\d+(?:\.\d+)?)/10"
            }
            for key, pattern in score_patterns.items():
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    try:
                        scores[key] = float(match.group(1))
                    except:
                        pass
            evaluation["scores"] = scores
            avg_score = sum(scores.values()) / len(scores)
            evaluation["average_score"] = avg_score

            lines = response.split('\n')
            feedback_lines = []
            suggestion_lines = []
            in_feedback = False
            in_suggestions = False
            for line in lines:
                line_lower = line.lower()
                if "反馈" in line_lower or "评价" in line_lower:
                    in_feedback = True
                    in_suggestions = False
                elif "建议" in line_lower:
                    in_feedback = False
                    in_suggestions = True
                elif "---" in line or "====" in line:
                    break
                if in_feedback and line.strip() and "反馈" not in line_lower:
                    feedback_lines.append(line.strip())
                elif in_suggestions and line.strip() and "建议" not in line_lower:
                    suggestion_lines.append(line.strip())
            evaluation["feedback"] = " ".join(feedback_lines) or "回答评估完成"
            evaluation["suggestions"] = suggestion_lines

            if avg_score >= 8.0:
                evaluation["mastery_level"] = "精通"
                evaluation["mastery_description"] = "对该问题有深入理解和准确回答"
            elif avg_score >= 6.0:
                evaluation["mastery_level"] = "掌握"
                evaluation["mastery_description"] = "基本理解并正确回答了问题"
            elif avg_score >= 4.0:
                evaluation["mastery_level"] = "理解"
                evaluation["mastery_description"] = "部分理解但回答不够完整准确"
            else:
                evaluation["mastery_level"] = "初学"
                evaluation["mastery_description"] = "需要进一步学习和理解"
        else:
            evaluation["feedback"] = "自动评估完成，建议参考标准答案进一步学习。"
            evaluation["scores"] = {"accuracy": 5.0, "completeness": 5.0, "depth": 5.0, "clarity": 5.0}
            evaluation["average_score"] = 5.0
            evaluation["mastery_level"] = "评估中"
        return evaluation

    def _determine_node_type(self, node: Union[MindMapNode, KnowledgeNode]) -> str:
        """确定节点类型"""
        if isinstance(node, MindMapNode):
            return node.node_type if hasattr(node, 'node_type') else "concept"
        elif isinstance(node, KnowledgeNode):
            type_mapping = {
                KnowledgeType.CONCEPT: "concept",
                KnowledgeType.FACT: "concept",
                KnowledgeType.PRINCIPLE: "principle",
                KnowledgeType.SKILL: "skill",
                KnowledgeType.PROCESS: "process",
                KnowledgeType.SYSTEM: "system",
                KnowledgeType.EXAMPLE: "example"
            }
            return type_mapping.get(node.knowledge_type, "concept")
        else:
            return "concept"

    def _determine_difficulty(self, question_text: str, depth_level: str) -> str:
        """确定问题难度"""
        if depth_level in ["evaluation", "creation"]:
            return "hard"
        elif depth_level in ["application", "analysis"]:
            return "medium"
        else:
            return "easy"

    def _generate_questions_with_llm(self,
                                   node: Union[MindMapNode, KnowledgeNode],
                                   depth_level: str,
                                   count: int) -> List[Dict[str, Any]]:
        """使用大模型生成问题"""
        node_type = self._determine_node_type(node)
        depth_info = self.question_depths.get(depth_level, self.question_depths["understanding"])
        prompt = f"""请为以下{node_type}生成{count}个深度问题：

主题：{node.title}
描述：{getattr(node, 'description', getattr(node, 'content', ''))[:200]}
问题深度：{depth_info['name']}
问题类型：{depth_level}

要求：
1. 问题应该促进深度思考
2. 问题应该与主题密切相关
3. 问题应该是开放式的
4. 问题应该适合{node_type}类型

请返回JSON数组格式，每个问题包含：
- text: 问题文本
- reasoning: 为什么提出这个问题
"""
        response = self.llm_client.call_llm(prompt=prompt, max_tokens=800, temperature=0.7)
        questions = []
        if response:
            try:
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    llm_questions = json.loads(json_str)
                    for i, q_data in enumerate(llm_questions):
                        if i >= count:
                            break
                        question = {
                            "id": generate_id(f"llm_question_{i}_"),
                            "text": q_data.get("text", f"关于{node.title}的问题"),
                            "node_id": node.id,
                            "node_title": node.title,
                            "node_type": node_type,
                            "depth_level": depth_level,
                            "depth_name": depth_info["name"],
                            "difficulty": self._determine_difficulty(q_data.get("text", ""), depth_level),
                            "difficulty_description": self.difficulty_levels[self._determine_difficulty(q_data.get("text", ""), depth_level)]["description"],
                            "estimated_thinking_time": self.difficulty_levels[self._determine_difficulty(q_data.get("text", ""), depth_level)]["thinking_time"],
                            "generated_by": "llm",
                            "reasoning": q_data.get("reasoning", ""),
                            "generated_at": datetime.now().isoformat()
                        }
                        questions.append(question)
            except Exception as e:
                print(f"❌ LLM问题生成解析失败: {str(e)}")
        return questions