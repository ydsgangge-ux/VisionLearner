import json
import re
import math
import random
import heapq
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import statistics

from foundation import (
    MindMapNode, KnowledgeNode, LearningGoal, LearningLevel,
    KnowledgeType, GoalScale, LearningStrategy, MindMapStyle,
    ProgressGranularity, generate_id, FoundationManager,
    TimeEstimationModel
)
from explorer import (
    KnowledgeNetworkBuilder, LearningPathGenerator,
    ExplorerManager
)

# 导入愿景核心
from vision_core import get_vision_core


class HierarchicalLearningAllocator:
    """
    层次化学习分配器 - 基于思维导图进行层次化学习任务分配
    将学习目标分解为不同层次的学习任务
    """

    def __init__(self, time_model: Optional[TimeEstimationModel] = None):
        self.time_model = time_model or TimeEstimationModel()
        
        # ========== 愿景核心集成 ==========
        self.vision_core = get_vision_core()

        # 层次分配策略
        self.allocation_strategies = {
            "depth_first": {
                "name": "深度优先",
                "description": "按深度优先顺序分配学习任务",
                "priority": ["importance", "depth", "difficulty"]
            },
            "breadth_first": {
                "name": "广度优先",
                "description": "按广度优先顺序分配学习任务",
                "priority": ["depth", "importance", "difficulty"]
            },
            "importance_first": {
                "name": "重要性优先",
                "description": "按重要性优先分配学习任务",
                "priority": ["importance", "difficulty", "depth"]
            },
            "balanced": {
                "name": "均衡分配",
                "description": "均衡考虑多个因素分配学习任务",
                "priority": ["composite_score", "depth", "prerequisites"]
            },
            "adaptive": {
                "name": "自适应分配",
                "description": "根据学习情况动态调整分配策略",
                "priority": ["dynamic_adjustment", "learning_history", "progress"]
            }
        }

        # 学习层次配置
        self.learning_levels_config = {
            "exploration": {
                "name": "探索层",
                "depth_range": [0, 1],
                "focus": ["整体认知", "核心概念", "建立框架"],
                "allocation_ratio": 0.2
            },
            "foundation": {
                "name": "基础层",
                "depth_range": [2, 3],
                "focus": ["基础知识", "关键技能", "建立基础"],
                "allocation_ratio": 0.3
            },
            "deepening": {
                "name": "深化层",
                "depth_range": [4, 5],
                "focus": ["深度理解", "复杂应用", "建立联系"],
                "allocation_ratio": 0.3
            },
            "integration": {
                "name": "整合层",
                "depth_range": [6, float('inf')],
                "focus": ["系统整合", "创新应用", "建立体系"],
                "allocation_ratio": 0.2
            }
        }

        # 分配历史记录
        self.allocation_history = defaultdict(list)

    def allocate_by_mindmap(self,
                          goal: LearningGoal,
                          mindmap_root: MindMapNode,
                          node_map: Dict[str, MindMapNode],
                          strategy: str = "balanced",
                          available_time_minutes: Optional[int] = None) -> Dict[str, Any]:
        """
        基于思维导图进行层次化学习分配

        Args:
            goal: 学习目标
            mindmap_root: 思维导图根节点
            node_map: 节点映射
            strategy: 分配策略
            available_time_minutes: 可用学习时间（分钟）

        Returns:
            分配计划
        """
        print(f"📊 基于思维导图进行层次化学习分配 (策略: {strategy})")
        
        # ========== 愿景核心集成：伦理审查学习目标 ==========
        ethical_review = self.vision_core.make_ethical_decision(
            f"学习目标: {goal.description}\n内容: {len(node_map)}个知识节点"
        )
        
        if ethical_review["decision"] == "拒绝":
            print(f"⚠️ 愿景核心伦理审查: {ethical_review['decision']}")
            for reason in ethical_review["reasoning"]:
                print(f"   - {reason}")
            # 即使被拒绝，也返回计划但标记风险
            allocation_plan = {
                "goal_id": goal.id,
                "mindmap_id": mindmap_root.id,
                "strategy": strategy,
                "allocated_at": datetime.now().isoformat(),
                "ethical_review": ethical_review,
                "warning": "愿景核心标记此学习目标存在潜在问题",
                "hierarchical_breakdown": {},
                "learning_sequences": [],
                "time_allocation": {},
                "recommendations": ethical_review.get("reasoning", [])
            }
            return allocation_plan

        allocation_plan = {
            "goal_id": goal.id,
            "mindmap_id": mindmap_root.id,
            "strategy": strategy,
            "allocated_at": datetime.now().isoformat(),
            "total_nodes": len(node_map),
            "hierarchical_breakdown": {},
            "learning_sequences": [],
            "time_allocation": {},
            "recommendations": []
        }

        # 验证策略
        if strategy not in self.allocation_strategies:
            print(f"⚠️ 未知策略 {strategy}，使用均衡策略")
            strategy = "balanced"

        # 分析思维导图结构
        structure_analysis = self._analyze_mindmap_structure(node_map)
        allocation_plan["structure_analysis"] = structure_analysis

        # 层次化分解
        hierarchical_nodes = self._hierarchical_decomposition(node_map)
        allocation_plan["hierarchical_breakdown"] = hierarchical_nodes

        # 计算节点优先级
        prioritized_nodes = self._calculate_node_priorities(
            node_map, strategy, goal
        )

        # 生成学习序列
        learning_sequences = self._generate_learning_sequences(
            prioritized_nodes, node_map, strategy, available_time_minutes
        )
        allocation_plan["learning_sequences"] = learning_sequences

        # 分配学习时间
        time_allocation = self._allocate_learning_time(
            learning_sequences, node_map, available_time_minutes
        )
        allocation_plan["time_allocation"] = time_allocation

        # 生成分配建议
        recommendations = self._generate_allocation_recommendations(
            allocation_plan, goal, node_map
        )
        allocation_plan["recommendations"] = recommendations

        # 记录分配历史
        self._record_allocation_history(goal.id, allocation_plan)

        print(f"✅ 层次化分配完成: {len(learning_sequences)}个学习序列，{time_allocation.get('total_minutes', 0)}分钟")
        return allocation_plan

    def allocate_by_knowledge_network(self,
                                    goal: LearningGoal,
                                    knowledge_network: Any,  # NetworkX图
                                    current_mastery: List[str] = None,
                                    strategy: str = "balanced") -> Dict[str, Any]:
        """
        基于知识网络进行学习分配

        Args:
            goal: 学习目标
            knowledge_network: 知识网络
            current_mastery: 当前已掌握节点
            strategy: 分配策略

        Returns:
            分配计划
        """
        print(f"🔗 基于知识网络进行学习分配 (策略: {strategy})")

        allocation_plan = {
            "goal_id": goal.id,
            "strategy": strategy,
            "allocated_at": datetime.now().isoformat(),
            "network_analysis": {},
            "learning_paths": [],
            "priority_nodes": [],
            "recommendations": []
        }

        try:
            import networkx as nx

            # 网络分析
            network_stats = {
                "node_count": knowledge_network.number_of_nodes(),
                "edge_count": knowledge_network.number_of_edges(),
                "density": nx.density(knowledge_network) if isinstance(knowledge_network, nx.Graph) else 0,
                "connected_components": nx.number_weakly_connected_components(knowledge_network)
                if isinstance(knowledge_network, nx.DiGraph)
                else nx.number_connected_components(knowledge_network)
            }
            allocation_plan["network_analysis"] = network_stats

            # 确定未掌握节点
            all_nodes = list(knowledge_network.nodes())
            if current_mastery is None:
                current_mastery = []

            nodes_to_learn = [node for node in all_nodes if node not in current_mastery]

            if not nodes_to_learn:
                allocation_plan["message"] = "所有节点已掌握"
                return allocation_plan

            # 根据策略计算节点优先级
            if strategy == "prerequisite_based":
                # 基于先决条件的拓扑排序
                try:
                    sorted_nodes = list(nx.topological_sort(knowledge_network))
                    # 过滤已掌握节点和排序
                    learning_order = [node for node in sorted_nodes if node in nodes_to_learn]
                except:
                    # 如果有环，使用简单排序
                    learning_order = nodes_to_learn
            elif strategy == "centrality_based":
                # 基于中心性排序
                try:
                    centrality = nx.degree_centrality(knowledge_network)
                    nodes_to_learn.sort(key=lambda x: centrality.get(x, 0), reverse=True)
                    learning_order = nodes_to_learn
                except:
                    learning_order = nodes_to_learn
            else:  # balanced
                # 均衡考虑多个因素
                learning_order = self._balance_multiple_factors(
                    nodes_to_learn, knowledge_network
                )

            # 创建学习路径
            learning_paths = self._create_network_learning_paths(
                learning_order, knowledge_network, goal
            )
            allocation_plan["learning_paths"] = learning_paths

            # 识别关键节点
            key_nodes = self._identify_key_network_nodes(
                knowledge_network, nodes_to_learn
            )
            allocation_plan["priority_nodes"] = key_nodes

            # 生成建议
            recommendations = self._generate_network_allocation_recommendations(
                allocation_plan, goal, knowledge_network
            )
            allocation_plan["recommendations"] = recommendations

        except Exception as e:
            print(f"❌ 知识网络分配失败: {str(e)}")
            allocation_plan["error"] = str(e)

        return allocation_plan

    def adjust_allocation(self,
                         original_plan: Dict[str, Any],
                         progress_data: Dict[str, Any],
                         node_map: Dict[str, MindMapNode]) -> Dict[str, Any]:
        """
        基于学习进度调整分配计划

        Args:
            original_plan: 原始分配计划
            progress_data: 进度数据
            node_map: 节点映射

        Returns:
            调整后的分配计划
        """
        print(f"🔄 基于进度调整分配计划")

        # 创建调整后的计划副本
        adjusted_plan = original_plan.copy()
        adjusted_plan["adjusted_at"] = datetime.now().isoformat()
        adjusted_plan["adjustment_reasons"] = []

        # 提取进度信息
        mastered_nodes = progress_data.get("mastered_nodes", [])
        struggling_nodes = progress_data.get("struggling_nodes", [])
        learning_speed = progress_data.get("learning_speed", 1.0)
        engagement_level = progress_data.get("engagement_level", 0.5)

        # 调整学习序列
        if "learning_sequences" in adjusted_plan:
            original_sequences = adjusted_plan["learning_sequences"]
            adjusted_sequences = []

            for seq in original_sequences:
                # 过滤已掌握的节点
                original_nodes = seq.get("node_ids", [])
                remaining_nodes = [n for n in original_nodes if n not in mastered_nodes]

                if not remaining_nodes:
                    # 如果序列中所有节点都已掌握，跳过该序列
                    adjusted_plan["adjustment_reasons"].append(
                        f"跳过序列 '{seq.get('name', '未知')}'，所有节点已掌握"
                    )
                    continue

                # 如果有学习困难的节点，添加额外支持
                struggling_in_seq = [n for n in struggling_nodes if n in original_nodes]
                if struggling_in_seq and len(remaining_nodes) > 0:
                    # 为困难节点添加标记
                    seq["has_struggling_nodes"] = True
                    seq["struggling_node_count"] = len(struggling_in_seq)
                    seq["recommended_support"] = "额外练习和复习"

                    adjusted_plan["adjustment_reasons"].append(
                        f"序列 '{seq.get('name', '未知')}' 包含 {len(struggling_in_seq)} 个困难节点"
                    )

                # 更新序列
                seq["node_ids"] = remaining_nodes
                seq["node_count"] = len(remaining_nodes)
                adjusted_sequences.append(seq)

            adjusted_plan["learning_sequences"] = adjusted_sequences
            adjusted_plan["remaining_nodes"] = sum(seq["node_count"] for seq in adjusted_sequences)

        # 调整时间分配
        if "time_allocation" in adjusted_plan:
            original_time = adjusted_plan["time_allocation"]

            # 根据学习速度调整时间
            if learning_speed != 1.0:
                for key in ["estimated_minutes", "daily_minutes", "weekly_minutes"]:
                    if key in original_time:
                        original_time[key] = int(original_time[key] / learning_speed)

                if learning_speed < 0.8:
                    adjusted_plan["adjustment_reasons"].append(
                        f"学习速度较慢 ({learning_speed:.2f}x)，增加时间分配"
                    )
                elif learning_speed > 1.2:
                    adjusted_plan["adjustment_reasons"].append(
                        f"学习速度较快 ({learning_speed:.2f}x)，减少时间分配"
                    )

            # 根据参与度调整
            if engagement_level < 0.3:
                # 低参与度，减少每日学习量
                if "daily_minutes" in original_time:
                    original_time["daily_minutes"] = int(original_time["daily_minutes"] * 0.7)
                    adjusted_plan["adjustment_reasons"].append(
                        "检测到低参与度，减少每日学习量"
                    )

            adjusted_plan["time_allocation"] = original_time

        # 更新分配策略（如果需要）
        if len(struggling_nodes) > len(mastered_nodes) * 0.3:  # 超过30%的节点有困难
            adjusted_plan["strategy"] = "adaptive"
            adjusted_plan["adjustment_reasons"].append(
                "大量节点学习困难，切换到自适应策略"
            )

        # 生成新的建议
        adjusted_plan["recommendations"] = self._generate_adjustment_recommendations(
            adjusted_plan, progress_data, node_map
        )

        print(f"✅ 分配计划调整完成: {len(adjusted_plan.get('adjustment_reasons', []))}项调整")
        return adjusted_plan

    def _analyze_mindmap_structure(self, node_map: Dict[str, MindMapNode]) -> Dict[str, Any]:
        """分析思维导图结构"""
        analysis = {
            "total_nodes": len(node_map),
            "depth_distribution": defaultdict(int),
            "type_distribution": defaultdict(int),
            "importance_stats": {},
            "difficulty_stats": {},
            "connection_stats": {}
        }

        # 收集节点信息
        depths = []
        importances = []
        difficulties = []
        child_counts = []

        for node in node_map.values():
            # 深度分布
            analysis["depth_distribution"][node.depth] += 1
            depths.append(node.depth)

            # 类型分布
            analysis["type_distribution"][node.node_type] += 1

            # 重要性
            importances.append(node.importance)

            # 难度
            difficulties.append(node.difficulty)

            # 子节点数量
            child_counts.append(len(node.children_ids))

        # 计算统计信息
        if importances:
            analysis["importance_stats"] = {
                "mean": statistics.mean(importances),
                "median": statistics.median(importances),
                "min": min(importances),
                "max": max(importances)
            }

        if difficulties:
            analysis["difficulty_stats"] = {
                "mean": statistics.mean(difficulties),
                "median": statistics.median(difficulties),
                "min": min(difficulties),
                "max": max(difficulties)
            }

        if child_counts:
            analysis["connection_stats"] = {
                "total_children": sum(child_counts),
                "avg_children": statistics.mean(child_counts),
                "max_children": max(child_counts),
                "leaf_nodes": sum(1 for c in child_counts if c == 0)
            }

        # 最大深度
        if depths:
            analysis["max_depth"] = max(depths)
            analysis["avg_depth"] = statistics.mean(depths)

        return analysis

    def _hierarchical_decomposition(self, node_map: Dict[str, MindMapNode]) -> Dict[str, List[str]]:
        """层次化分解节点"""
        hierarchical_nodes = defaultdict(list)

        for node_id, node in node_map.items():
            # 根据深度确定层次
            if node.depth <= 1:
                level = "exploration"
            elif node.depth <= 3:
                level = "foundation"
            elif node.depth <= 5:
                level = "deepening"
            else:
                level = "integration"

            hierarchical_nodes[level].append(node_id)

        return dict(hierarchical_nodes)

    def _calculate_node_priorities(self,
                                 node_map: Dict[str, MindMapNode],
                                 strategy: str,
                                 goal: LearningGoal) -> List[Tuple[str, float]]:
        """计算节点优先级"""
        priorities = []

        strategy_config = self.allocation_strategies.get(strategy, self.allocation_strategies["balanced"])
        priority_factors = strategy_config.get("priority", [])

        for node_id, node in node_map.items():
            # 计算每个因素的分数
            factor_scores = {}

            # 重要性分数
            factor_scores["importance"] = node.importance

            # 难度分数（难度越低，优先级越高）
            factor_scores["difficulty"] = 1.0 - node.difficulty

            # 深度分数（深度越浅，优先级越高）
            factor_scores["depth"] = 1.0 / (node.depth + 1)

            # 先决条件分数（先决条件越少，优先级越高）
            prereq_factor = 1.0
            if node.prerequisites:
                prereq_factor = 1.0 / (len(node.prerequisites) + 1)
            factor_scores["prerequisites"] = prereq_factor

            # 预估时间分数（时间越短，优先级越高）
            time_factor = 1.0
            if node.estimated_time_minutes > 0:
                time_factor = 30.0 / node.estimated_time_minutes  # 30分钟为基准
                time_factor = min(max(time_factor, 0.1), 2.0)  # 限制在0.1-2.0之间
            factor_scores["time"] = time_factor

            # 学习状态分数（未学习的优先级高）
            status_factor = 1.0
            if node.learning_status == "mastered":
                status_factor = 0.1
            elif node.learning_status == "learning":
                status_factor = 0.5
            elif node.learning_status == "reviewing":
                status_factor = 0.3
            factor_scores["status"] = status_factor

            # 计算综合分数
            composite_score = 0.0
            weight_sum = 0.0

            # 根据策略分配权重
            weights = {
                "importance": 0.3,
                "difficulty": 0.2,
                "depth": 0.15,
                "prerequisites": 0.15,
                "time": 0.1,
                "status": 0.1
            }

            # 调整策略权重
            if strategy == "depth_first":
                weights["depth"] = 0.4
                weights["importance"] = 0.2
            elif strategy == "breadth_first":
                weights["depth"] = 0.5
            elif strategy == "importance_first":
                weights["importance"] = 0.5
                weights["depth"] = 0.1

            for factor, weight in weights.items():
                composite_score += factor_scores.get(factor, 0.5) * weight
                weight_sum += weight

            if weight_sum > 0:
                composite_score /= weight_sum

            # 添加随机因子避免完全相同分数
            composite_score += random.uniform(-0.01, 0.01)

            priorities.append((node_id, composite_score))

        # 按优先级排序
        priorities.sort(key=lambda x: x[1], reverse=True)

        return priorities

    def _generate_learning_sequences(self,
                                   prioritized_nodes: List[Tuple[str, float]],
                                   node_map: Dict[str, MindMapNode],
                                   strategy: str,
                                   available_time_minutes: Optional[int]) -> List[Dict[str, Any]]:
        """生成学习序列"""
        sequences = []

        # 确定序列数量（基于节点总数）
        total_nodes = len(prioritized_nodes)
        if total_nodes <= 5:
            sequence_count = 1
        elif total_nodes <= 15:
            sequence_count = 2
        elif total_nodes <= 30:
            sequence_count = 3
        else:
            sequence_count = max(3, total_nodes // 10)

        # 确定每个序列的节点数量
        nodes_per_sequence = math.ceil(total_nodes / sequence_count)

        # 根据策略调整序列生成
        if strategy == "depth_first":
            # 深度优先：每个序列包含一个分支的节点
            sequences = self._create_depth_first_sequences(prioritized_nodes, node_map)
        elif strategy == "breadth_first":
            # 广度优先：每个序列包含同一深度的节点
            sequences = self._create_breadth_first_sequences(prioritized_nodes, node_map)
        else:
            # 其他策略：按优先级分组
            for i in range(sequence_count):
                start_idx = i * nodes_per_sequence
                end_idx = min((i + 1) * nodes_per_sequence, total_nodes)

                sequence_nodes = prioritized_nodes[start_idx:end_idx]
                node_ids = [node_id for node_id, _ in sequence_nodes]

                sequence = {
                    "id": generate_id(f"sequence_{i}_"),
                    "name": f"学习序列 {i+1}",
                    "description": f"包含{len(node_ids)}个知识节点的学习序列",
                    "node_ids": node_ids,
                    "node_count": len(node_ids),
                    "avg_priority": statistics.mean([score for _, score in sequence_nodes]) if sequence_nodes else 0,
                    "estimated_time_minutes": sum(node_map[nid].estimated_time_minutes for nid in node_ids if nid in node_map)
                }

                sequences.append(sequence)

        # 如果提供了可用时间，调整序列
        if available_time_minutes:
            sequences = self._adjust_sequences_for_time(sequences, available_time_minutes)

        return sequences

    def _create_depth_first_sequences(self,
                                    prioritized_nodes: List[Tuple[str, float]],
                                    node_map: Dict[str, MindMapNode]) -> List[Dict[str, Any]]:
        """创建深度优先学习序列"""
        sequences = []

        # 按深度分组
        depth_groups = defaultdict(list)
        for node_id, _ in prioritized_nodes:
            node = node_map.get(node_id)
            if node:
                depth_groups[node.depth].append(node_id)

        # 创建序列：每个序列专注于一个深度范围
        current_sequence = []
        current_depth = 0

        for depth in sorted(depth_groups.keys()):
            # 如果深度跳跃太大，开始新序列
            if depth - current_depth > 1 and current_sequence:
                sequence = {
                    "id": generate_id("depth_seq_"),
                    "name": f"深度{current_depth}学习序列",
                    "description": f"专注于深度{current_depth}的知识节点",
                    "node_ids": current_sequence,
                    "node_count": len(current_sequence),
                    "depth_range": [current_depth, current_depth],
                    "strategy": "depth_first"
                }
                sequences.append(sequence)
                current_sequence = []

            # 添加当前深度的节点
            current_sequence.extend(depth_groups[depth])
            current_depth = depth

        # 添加最后一个序列
        if current_sequence:
            sequence = {
                "id": generate_id("depth_seq_"),
                "name": f"深度{current_depth}学习序列",
                "description": f"专注于深度{current_depth}的知识节点",
                "node_ids": current_sequence,
                "node_count": len(current_sequence),
                "depth_range": [current_depth, current_depth],
                "strategy": "depth_first"
            }
            sequences.append(sequence)

        return sequences

    def _create_breadth_first_sequences(self,
                                       prioritized_nodes: List[Tuple[str, float]],
                                       node_map: Dict[str, MindMapNode]) -> List[Dict[str, Any]]:
        """创建广度优先学习序列"""
        sequences = []

        # 收集根节点和主要分支
        root_nodes = []
        for node_id, _ in prioritized_nodes:
            node = node_map.get(node_id)
            if node and node.depth == 0:
                root_nodes.append(node_id)

        # 如果没有明确的根节点，使用所有节点
        if not root_nodes:
            # 按优先级分组
            return self._generate_learning_sequences(prioritized_nodes, node_map, "balanced", None)

        # 为每个根节点创建序列
        for i, root_id in enumerate(root_nodes):
            # 收集该根节点的所有后代节点
            descendant_nodes = self._get_descendant_nodes(root_id, node_map)

            if descendant_nodes:
                sequence = {
                    "id": generate_id(f"breadth_seq_{i}_"),
                    "name": f"分支学习序列 {i+1}",
                    "description": f"学习以'{node_map[root_id].title}'为核心的知识分支",
                    "node_ids": descendant_nodes,
                    "node_count": len(descendant_nodes),
                    "root_node": root_id,
                    "strategy": "breadth_first"
                }
                sequences.append(sequence)

        # 如果序列太少，添加剩余节点
        if len(sequences) < 2 and prioritized_nodes:
            all_node_ids = [node_id for node_id, _ in prioritized_nodes]
            used_nodes = set()
            for seq in sequences:
                used_nodes.update(seq["node_ids"])

            remaining_nodes = [nid for nid in all_node_ids if nid not in used_nodes]
            if remaining_nodes:
                sequence = {
                    "id": generate_id("breadth_seq_remaining_"),
                    "name": "补充学习序列",
                    "description": "学习剩余的知识节点",
                    "node_ids": remaining_nodes,
                    "node_count": len(remaining_nodes),
                    "strategy": "breadth_first"
                }
                sequences.append(sequence)

        return sequences

    def _get_descendant_nodes(self, root_id: str, node_map: Dict[str, MindMapNode]) -> List[str]:
        """获取某个节点的所有后代节点"""
        descendants = []

        def collect_descendants(node_id: str):
            node = node_map.get(node_id)
            if not node:
                return

            for child_id in node.children_ids:
                if child_id not in descendants:
                    descendants.append(child_id)
                    collect_descendants(child_id)

        collect_descendants(root_id)
        return descendants

    def _adjust_sequences_for_time(self,
                                 sequences: List[Dict[str, Any]],
                                 available_time_minutes: int) -> List[Dict[str, Any]]:
        """根据可用时间调整学习序列"""
        if not sequences:
            return sequences

        # 计算总预估时间
        total_estimated = sum(seq.get("estimated_time_minutes", 0) for seq in sequences)

        if total_estimated <= available_time_minutes:
            # 时间充足，不需要调整
            return sequences

        # 时间不足，需要调整
        print(f"⚠️ 时间不足: 预估{total_estimated}分钟，可用{available_time_minutes}分钟")

        # 计算调整比例
        adjustment_ratio = available_time_minutes / total_estimated

        adjusted_sequences = []
        for seq in sequences:
            original_nodes = seq.get("node_ids", [])
            original_time = seq.get("estimated_time_minutes", 0)

            # 调整节点数量
            if original_nodes:
                # 保留高优先级节点（假设节点按优先级排序）
                keep_count = max(1, int(len(original_nodes) * adjustment_ratio))
                adjusted_nodes = original_nodes[:keep_count]

                adjusted_seq = seq.copy()
                adjusted_seq["node_ids"] = adjusted_nodes
                adjusted_seq["node_count"] = len(adjusted_nodes)
                adjusted_seq["estimated_time_minutes"] = int(original_time * adjustment_ratio)
                adjusted_seq["time_adjusted"] = True
                adjusted_seq["original_node_count"] = len(original_nodes)

                adjusted_sequences.append(adjusted_seq)

        return adjusted_sequences

    def _allocate_learning_time(self,
                              sequences: List[Dict[str, Any]],
                              node_map: Dict[str, MindMapNode],
                              available_time_minutes: Optional[int]) -> Dict[str, Any]:
        """分配学习时间"""
        time_allocation = {
            "total_sequences": len(sequences),
            "sequence_allocation": []
        }

        # 计算总预估时间
        total_estimated = sum(seq.get("estimated_time_minutes", 0) for seq in sequences)
        time_allocation["total_estimated_minutes"] = total_estimated

        # 如果提供了可用时间，计算比例分配
        if available_time_minutes:
            time_allocation["available_minutes"] = available_time_minutes

            if total_estimated > 0:
                # 计算每个序列的时间分配比例
                for seq in sequences:
                    seq_time = seq.get("estimated_time_minutes", 0)
                    if total_estimated > 0:
                        time_ratio = seq_time / total_estimated
                        allocated_time = int(available_time_minutes * time_ratio)
                    else:
                        allocated_time = 0

                    seq_allocation = {
                        "sequence_id": seq.get("id", ""),
                        "sequence_name": seq.get("name", ""),
                        "estimated_minutes": seq_time,
                        "allocated_minutes": allocated_time,
                        "time_ratio": time_ratio if total_estimated > 0 else 0
                    }
                    time_allocation["sequence_allocation"].append(seq_allocation)

                time_allocation["total_allocated_minutes"] = sum(
                    alloc["allocated_minutes"] for alloc in time_allocation["sequence_allocation"]
                )

            # 建议每日学习时间
            if available_time_minutes > 0:
                # 假设学习周期为2周（14天）
                daily_minutes = int(available_time_minutes / 14)
                weekly_minutes = daily_minutes * 7

                time_allocation["daily_recommendation"] = {
                    "minutes": daily_minutes,
                    "description": f"建议每日学习{daily_minutes}分钟"
                }
                time_allocation["weekly_recommendation"] = {
                    "minutes": weekly_minutes,
                    "description": f"建议每周学习{weekly_minutes}分钟"
                }

        # 如果没有提供可用时间，使用预估时间
        else:
            time_allocation["using_estimated_times"] = True
            time_allocation["recommendation"] = "使用节点预估时间进行分配"

            for seq in sequences:
                seq_time = seq.get("estimated_time_minutes", 0)
                seq_allocation = {
                    "sequence_id": seq.get("id", ""),
                    "sequence_name": seq.get("name", ""),
                    "allocated_minutes": seq_time,
                    "note": "使用节点预估时间"
                }
                time_allocation["sequence_allocation"].append(seq_allocation)

        return time_allocation

    def _balance_multiple_factors(self,
                                nodes: List[str],
                                knowledge_network: Any) -> List[str]:
        """均衡考虑多个因素排序节点"""
        try:
            import networkx as nx

            # 计算多个中心性指标
            centrality_measures = {}

            # 度中心性
            try:
                degree_centrality = nx.degree_centrality(knowledge_network)
                centrality_measures["degree"] = degree_centrality
            except:
                pass

            # PageRank
            try:
                pagerank = nx.pagerank(knowledge_network)
                centrality_measures["pagerank"] = pagerank
            except:
                pass

            # 综合分数
            composite_scores = {}
            for node in nodes:
                scores = []
                for measure_name, measure_dict in centrality_measures.items():
                    if node in measure_dict:
                        scores.append(measure_dict[node])

                if scores:
                    # 使用平均分
                    composite_scores[node] = statistics.mean(scores)
                else:
                    # 如果没有中心性分数，使用随机分数
                    composite_scores[node] = random.random()

            # 按综合分数排序
            sorted_nodes = sorted(nodes, key=lambda x: composite_scores.get(x, 0), reverse=True)
            return sorted_nodes

        except Exception as e:
            print(f"❌ 多因素平衡失败: {str(e)}")
            return nodes  # 返回原始顺序

    def _create_network_learning_paths(self,
                                      learning_order: List[str],
                                      knowledge_network: Any,
                                      goal: LearningGoal) -> List[Dict[str, Any]]:
        """创建网络学习路径"""
        paths = []

        # 将学习顺序分组为路径
        if len(learning_order) <= 10:
            # 节点少，一个路径
            paths.append({
                "name": "主要学习路径",
                "node_ids": learning_order,
                "node_count": len(learning_order),
                "description": "完整的学习路径"
            })
        else:
            # 节点多，分成多个路径
            path_count = min(4, max(2, len(learning_order) // 5))
            nodes_per_path = math.ceil(len(learning_order) / path_count)

            for i in range(path_count):
                start_idx = i * nodes_per_path
                end_idx = min((i + 1) * nodes_per_path, len(learning_order))

                path_nodes = learning_order[start_idx:end_idx]

                paths.append({
                    "name": f"学习路径 {i+1}",
                    "node_ids": path_nodes,
                    "node_count": len(path_nodes),
                    "description": f"学习路径第{i+1}部分"
                })

        return paths

    def _identify_key_network_nodes(self,
                                   knowledge_network: Any,
                                   nodes_to_learn: List[str]) -> List[Dict[str, Any]]:
        """识别关键网络节点"""
        key_nodes = []

        try:
            import networkx as nx

            # 计算介数中心性（识别桥接节点）
            try:
                betweenness = nx.betweenness_centrality(knowledge_network)
                for node in nodes_to_learn:
                    if node in betweenness and betweenness[node] > 0.1:  # 阈值
                        key_nodes.append({
                            "node_id": node,
                            "importance": "high",
                            "reason": "桥接节点（高介数中心性）",
                            "centrality": betweenness[node]
                        })
            except:
                pass

            # 如果没有找到桥接节点，使用度中心性
            if not key_nodes:
                try:
                    degree_centrality = nx.degree_centrality(knowledge_network)
                    top_nodes = sorted(
                        nodes_to_learn,
                        key=lambda x: degree_centrality.get(x, 0),
                        reverse=True
                    )[:3]  # 取前3个

                    for node in top_nodes:
                        key_nodes.append({
                            "node_id": node,
                            "importance": "high",
                            "reason": "高连接度节点",
                            "centrality": degree_centrality.get(node, 0)
                        })
                except:
                    pass

        except Exception as e:
            print(f"❌ 关键节点识别失败: {str(e)}")

        # 如果没有找到关键节点，选择前几个节点
        if not key_nodes and nodes_to_learn:
            for i, node in enumerate(nodes_to_learn[:3]):
                key_nodes.append({
                    "node_id": node,
                    "importance": "medium",
                    "reason": "学习顺序靠前",
                    "order": i + 1
                })

        return key_nodes

    def _generate_allocation_recommendations(self,
                                           allocation_plan: Dict[str, Any],
                                           goal: LearningGoal,
                                           node_map: Dict[str, MindMapNode]) -> List[str]:
        """生成分配建议"""
        recommendations = []

        total_nodes = allocation_plan.get("total_nodes", 0)
        sequence_count = len(allocation_plan.get("learning_sequences", []))
        total_time = allocation_plan.get("time_allocation", {}).get("total_estimated_minutes", 0)

        # 基于节点数量的建议
        if total_nodes > 50:
            recommendations.append(f"学习内容较多（{total_nodes}个节点），建议制定长期计划")
        elif total_nodes < 10:
            recommendations.append(f"学习内容较少（{total_nodes}个节点），可以快速完成")

        # 基于序列数量的建议
        if sequence_count > 3:
            recommendations.append(f"分为{sequence_count}个学习序列，建议按顺序逐步完成")

        # 基于时间的建议
        if total_time > 0:
            total_hours = total_time / 60
            if total_hours > 20:
                recommendations.append(f"预计需要{total_hours:.1f}小时，建议分散在几周内学习")
            elif total_hours > 5:
                recommendations.append(f"预计需要{total_hours:.1f}小时，建议在一周内完成")
            else:
                recommendations.append(f"预计需要{total_hours:.1f}小时，可以在几天内完成")

        # 基于策略的建议
        strategy = allocation_plan.get("strategy", "balanced")
        if strategy == "depth_first":
            recommendations.append("使用深度优先策略，适合系统性深入学习")
        elif strategy == "breadth_first":
            recommendations.append("使用广度优先策略，适合建立整体认知框架")
        elif strategy == "importance_first":
            recommendations.append("使用重要性优先策略，适合时间有限的情况")

        # 基于目标规模的建议
        if goal.scale in [GoalScale.LARGE, GoalScale.MASSIVE]:
            recommendations.append("大规模学习目标，建议定期复习和进度检查")

        return recommendations

    def _generate_network_allocation_recommendations(self,
                                                   allocation_plan: Dict[str, Any],
                                                   goal: LearningGoal,
                                                   knowledge_network: Any) -> List[str]:
        """生成网络分配建议"""
        recommendations = []

        network_stats = allocation_plan.get("network_analysis", {})
        node_count = network_stats.get("node_count", 0)
        path_count = len(allocation_plan.get("learning_paths", []))

        if node_count > 30:
            recommendations.append(f"知识网络包含{node_count}个节点，建议按路径分阶段学习")

        if path_count > 1:
            recommendations.append(f"分为{path_count}条学习路径，可以并行或顺序学习")

        if allocation_plan.get("priority_nodes"):
            priority_count = len(allocation_plan["priority_nodes"])
            recommendations.append(f"识别出{priority_count}个关键节点，建议优先学习")

        return recommendations

    def _generate_adjustment_recommendations(self,
                                           adjusted_plan: Dict[str, Any],
                                           progress_data: Dict[str, Any],
                                           node_map: Dict[str, MindMapNode]) -> List[str]:
        """生成调整建议"""
        recommendations = []

        # 基于调整原因
        adjustment_reasons = adjusted_plan.get("adjustment_reasons", [])
        for reason in adjustment_reasons:
            if "学习速度较慢" in reason:
                recommendations.append("检测到学习速度较慢，建议增加学习时间或调整学习方法")
            elif "学习速度较快" in reason:
                recommendations.append("检测到学习速度较快，可以适当增加学习内容")
            elif "低参与度" in reason:
                recommendations.append("检测到低参与度，建议调整学习内容或增加互动")
            elif "学习困难" in reason:
                recommendations.append("检测到学习困难，建议增加练习和复习")

        # 基于剩余节点
        remaining_nodes = adjusted_plan.get("remaining_nodes", 0)
        if remaining_nodes > 0:
            mastered_nodes = progress_data.get("mastered_nodes", [])
            if mastered_nodes:
                progress_rate = len(mastered_nodes) / (len(mastered_nodes) + remaining_nodes)
                if progress_rate > 0.7:
                    recommendations.append(f"已完成{progress_rate:.0%}，继续保持当前学习节奏")
                elif progress_rate < 0.3:
                    recommendations.append(f"完成度较低({progress_rate:.0%})，建议加强学习")

        # 基于学习序列
        sequences = adjusted_plan.get("learning_sequences", [])
        if sequences:
            struggling_sequences = [s for s in sequences if s.get("has_struggling_nodes", False)]
            if struggling_sequences:
                recommendations.append(f"{len(struggling_sequences)}个学习序列包含困难节点，建议重点关注")

        return recommendations

    def _record_allocation_history(self, goal_id: str, allocation_plan: Dict[str, Any]) -> None:
        """记录分配历史"""
        history_entry = {
            "timestamp": allocation_plan.get("allocated_at", datetime.now().isoformat()),
            "strategy": allocation_plan.get("strategy"),
            "total_nodes": allocation_plan.get("total_nodes", 0),
            "sequence_count": len(allocation_plan.get("learning_sequences", [])),
            "estimated_minutes": allocation_plan.get("time_allocation", {}).get("total_estimated_minutes", 0)
        }

        self.allocation_history[goal_id].append(history_entry)

        # 限制历史记录长度
        if len(self.allocation_history[goal_id]) > 10:
            self.allocation_history[goal_id] = self.allocation_history[goal_id][-10:]