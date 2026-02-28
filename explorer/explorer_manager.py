# explorer/explorer_manager.py
"""
探索管理器 - 整合深度知识探索功能
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

from foundation import MindMapNode, KnowledgeNode, LearningGoal
from perception import LLMClient
from .question_engine import IntelligentQuestionEngine
from .visualizer import MindMapVisualizer
from .network_builder import KnowledgeNetworkBuilder
from .path_generator import LearningPathGenerator


class ExplorerManager:
    """探索管理器 - 整合深度知识探索功能"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.llm_client = LLMClient()
            self.question_engine = IntelligentQuestionEngine(self.llm_client)
            self.visualizer = MindMapVisualizer()
            self.network_builder = KnowledgeNetworkBuilder(self.llm_client)
            self.path_generator = LearningPathGenerator(self.network_builder, self.llm_client)
            self._initialized = True

    def explore_mindmap(self,
                       mindmap_root: MindMapNode,
                       node_map: Dict[str, MindMapNode],
                       depth_level: str = "understanding") -> Dict[str, Any]:
        """
        探索思维导图
        """
        print(f"🔍 探索思维导图: {mindmap_root.title}")
        result = {
            "mindmap_id": mindmap_root.id,
            "mindmap_title": mindmap_root.title,
            "explored_at": datetime.now().isoformat(),
            "depth_level": depth_level,
            "questions": {},
            "visualization": {},
            "network_analysis": {},
            "learning_path": {}
        }

        questions = self.question_engine.generate_questions_for_mindmap(
            mindmap_root, node_map, depth_level, 2
        )
        result["questions"] = questions

        viz_path = self.visualizer.visualize_mindmap(
            mindmap_root, node_map, "png", "balanced", True
        )
        if viz_path:
            result["visualization"]["mindmap"] = viz_path

        network = self.network_builder.build_from_mindmap(mindmap_root, node_map)
        analysis = self.network_builder.analyze_network(network)
        result["network_analysis"] = analysis

        net_viz = self.visualizer.visualize_knowledge_network(
            list(node_map.values()),
            list(network.edges(data=True))
        )
        if net_viz:
            result["visualization"]["knowledge_network"] = net_viz

        html = self.visualizer.create_interactive_html(mindmap_root, node_map, questions)
        if html:
            result["visualization"]["interactive_html"] = html

        print(f"✅ 思维导图探索完成: {len(questions)}组问题, {len(analysis.get('key_nodes', {}))}个关键节点")
        return result

    def explore_knowledge_nodes(self,
                               knowledge_nodes: List[KnowledgeNode],
                               current_mastery: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        探索知识节点
        """
        print(f"🔍 探索知识节点 ({len(knowledge_nodes)}个)")
        result = {
            "knowledge_nodes_count": len(knowledge_nodes),
            "explored_at": datetime.now().isoformat(),
            "questions": [],
            "network_analysis": {},
            "learning_path": {},
            "knowledge_gaps": {}
        }

        important = sorted(
            knowledge_nodes,
            key=lambda x: x.confidence * x.mastery_score,
            reverse=True
        )[:3]
        for node in important:
            chain = self.question_engine.generate_deep_questions_chain(node, chain_length=4)
            result["questions"].extend(chain)

        network = self.network_builder.build_from_knowledge_nodes(knowledge_nodes)
        analysis = self.network_builder.analyze_network(network)
        result["network_analysis"] = analysis

        net_viz = self.visualizer.visualize_knowledge_network(knowledge_nodes)
        if net_viz:
            result["visualization"] = net_viz

        if current_mastery is None:
            current_mastery = []
        else:
            gaps = self.network_builder.identify_knowledge_gaps(network, current_mastery)
            result["knowledge_gaps"] = gaps

        goal = LearningGoal(
            id="exploration_goal",
            description=f"学习{len(knowledge_nodes)}个知识节点",
            target_knowledge_count=len(knowledge_nodes)
        )
        path = self.path_generator.generate_for_goal(goal, network, current_mastery)
        result["learning_path"] = path

        print(f"✅ 知识节点探索完成: {len(result['questions'])}个问题, {len(path.get('stages', []))}个学习阶段")
        return result

    def generate_personalized_learning_path(self,
                                          user_profile: Dict[str, Any],
                                          knowledge_nodes: List[KnowledgeNode]) -> Dict[str, Any]:
        """
        生成个性化学习路径
        """
        print(f"👤 生成个性化学习路径")
        network = self.network_builder.build_from_knowledge_nodes(knowledge_nodes)
        path = self.path_generator.generate_personalized_path(user_profile, network)
        return path

    def adjust_learning_path(self,
                           current_path: Dict[str, Any],
                           progress_data: Dict[str, Any],
                           knowledge_nodes: List[KnowledgeNode]) -> Dict[str, Any]:
        """
        调整学习路径
        """
        print(f"🔄 调整学习路径")
        network = self.network_builder.build_from_knowledge_nodes(knowledge_nodes)
        adjusted = self.path_generator.adjust_path_based_on_progress(
            current_path, progress_data, network
        )
        return adjusted