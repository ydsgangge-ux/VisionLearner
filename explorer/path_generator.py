# explorer/path_generator.py
"""
学习路径生成器 - 基于知识网络生成个性化学习路径
"""

import math
import random
import networkx as nx
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

from foundation import LearningGoal, GoalScale
from .network_builder import KnowledgeNetworkBuilder


class LearningPathGenerator:
    """
    学习路径生成器 - 基于知识网络生成个性化学习路径
    """

    def __init__(self,
                 network_builder: Optional[KnowledgeNetworkBuilder] = None,
                 llm_client: Optional['LLMClient'] = None):
        self.network_builder = network_builder or KnowledgeNetworkBuilder()
        self.llm_client = llm_client

        self.path_strategies = {
            "sequential": {"name": "顺序学习", "description": "按依赖关系顺序学习", "suitable_for": ["初学者", "系统性知识"]},
            "spiral": {"name": "螺旋式学习", "description": "多次循环，每次加深理解", "suitable_for": ["复杂概念", "技能学习"]},
            "modular": {"name": "模块化学习", "description": "按模块分组学习", "suitable_for": ["大规模知识", "并行学习"]},
            "priority": {"name": "优先级学习", "description": "按重要性优先级学习", "suitable_for": ["时间有限", "考试准备"]},
            "adaptive": {"name": "自适应学习", "description": "根据学习情况动态调整", "suitable_for": ["个性化学习", "持续学习"]}
        }

        self.learning_stages = {
            "exploration": {"name": "探索阶段", "duration_ratio": 0.2, "focus": ["概览", "核心概念", "建立认知"]},
            "foundation": {"name": "基础阶段", "duration_ratio": 0.3, "focus": ["基本原理", "关键技能", "建立基础"]},
            "deepening": {"name": "深化阶段", "duration_ratio": 0.3, "focus": ["深度理解", "复杂应用", "建立联系"]},
            "integration": {"name": "整合阶段", "duration_ratio": 0.2, "focus": ["系统整合", "创新应用", "建立体系"]}
        }

    def generate_for_goal(self,
                         goal: LearningGoal,
                         knowledge_network: nx.DiGraph,
                         current_knowledge: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        为目标生成学习路径
        """
        print(f"🛣️ 为学习目标生成学习路径: {goal.description}")
        learning_path = {
            "goal_id": goal.id,
            "goal_description": goal.description,
            "generated_at": datetime.now().isoformat(),
            "strategy": "adaptive",
            "stages": [],
            "total_nodes": 0,
            "estimated_time_hours": 0,
            "recommendations": []
        }

        strategy = self._determine_strategy(goal, knowledge_network)
        learning_path["strategy"] = strategy

        all_nodes = list(knowledge_network.nodes())
        if current_knowledge is None:
            current_knowledge = []
        nodes_to_learn = [nid for nid in all_nodes if nid not in current_knowledge]

        if not nodes_to_learn:
            learning_path["message"] = "所有知识节点都已掌握"
            return learning_path

        learning_path["total_nodes"] = len(nodes_to_learn)

        if strategy == "sequential":
            stages = self._generate_sequential_path(nodes_to_learn, knowledge_network)
        elif strategy == "spiral":
            stages = self._generate_spiral_path(nodes_to_learn, knowledge_network, goal)
        elif strategy == "modular":
            stages = self._generate_modular_path(nodes_to_learn, knowledge_network)
        elif strategy == "priority":
            stages = self._generate_priority_path(nodes_to_learn, knowledge_network)
        else:  # adaptive
            stages = self._generate_adaptive_path(nodes_to_learn, knowledge_network, current_knowledge)

        total_time = 0
        for stage in stages:
            t = self._estimate_stage_time(stage, knowledge_network)
            stage["estimated_time_hours"] = t
            total_time += t

        learning_path["stages"] = stages
        learning_path["estimated_time_hours"] = total_time
        learning_path["recommendations"] = self._generate_path_recommendations(learning_path, knowledge_network, current_knowledge)

        print(f"✅ 学习路径生成完成: {len(stages)}个阶段, {total_time:.1f}小时")
        return learning_path

    def generate_personalized_path(self,
                                 user_profile: Dict[str, Any],
                                 knowledge_network: nx.DiGraph,
                                 learning_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        生成个性化学习路径
        """
        print(f"👤 生成个性化学习路径")
        style = user_profile.get("learning_style", "balanced")
        avail_time = user_profile.get("available_time_hours_per_week", 10)
        prior = user_profile.get("prior_knowledge", [])
        goals = user_profile.get("learning_goals", [])

        strategy = self._determine_personalized_strategy(user_profile)

        all_nodes = list(knowledge_network.nodes())
        to_learn = [nid for nid in all_nodes if nid not in prior]

        if style == "visual":
            visual = self._identify_visual_nodes(knowledge_network)
            to_learn = self._prioritize_nodes(to_learn, visual)
        elif style == "auditory":
            auditory = self._identify_auditory_nodes(knowledge_network)
            to_learn = self._prioritize_nodes(to_learn, auditory)
        elif style == "kinesthetic":
            practice = self._identify_practice_nodes(knowledge_network)
            to_learn = self._prioritize_nodes(to_learn, practice)

        intensity = self._determine_learning_intensity(avail_time)

        path = {
            "user_id": user_profile.get("user_id", "unknown"),
            "learning_style": style,
            "strategy": strategy,
            "intensity": intensity,
            "available_time_hours_per_week": avail_time,
            "generated_at": datetime.now().isoformat(),
            "stages": [],
            "total_nodes": len(to_learn),
            "estimated_weeks": 0
        }

        if strategy == "sequential":
            stages = self._generate_sequential_path(to_learn, knowledge_network)
        else:
            stages = self._generate_adaptive_path(to_learn, knowledge_network, prior)

        stages = self._adjust_stages_for_intensity(stages, intensity)

        total_hours = sum(s.get("estimated_time_hours", 0) for s in stages)
        weeks = math.ceil(total_hours / avail_time) if avail_time > 0 else 0

        path["stages"] = stages
        path["estimated_time_hours"] = total_hours
        path["estimated_weeks"] = weeks
        path["personalized_recommendations"] = self._generate_personalized_recommendations(user_profile, path, knowledge_network)

        return path

    def adjust_path_based_on_progress(self,
                                    current_path: Dict[str, Any],
                                    progress_data: Dict[str, Any],
                                    knowledge_network: nx.DiGraph) -> Dict[str, Any]:
        """
        基于学习进度调整学习路径
        """
        print(f"🔄 基于进度调整学习路径")
        mastered = progress_data.get("mastered_nodes", [])
        struggling = progress_data.get("struggling_nodes", [])
        speed = progress_data.get("learning_speed", 1.0)

        adjusted = current_path.copy()
        adjusted["adjusted_at"] = datetime.now().isoformat()
        adjusted["adjustment_reason"] = []

        remaining_nodes = []
        for stage in adjusted.get("stages", []):
            orig = stage.get("node_ids", [])
            remain = [nid for nid in orig if nid not in mastered]
            if len(remain) < len(orig):
                stage["node_ids"] = remain
                stage["node_count"] = len(remain)
                adjusted["adjustment_reason"].append(f"阶段'{stage['name']}'移除了{len(orig)-len(remain)}个已掌握节点")
            remaining_nodes.extend(remain)

        adjusted["total_nodes"] = len(remaining_nodes)
        adjusted["mastered_nodes"] = len(mastered)

        if struggling:
            review = {
                "name": "难点复习",
                "description": f"针对{len(struggling)}个学习困难的节点进行复习",
                "node_ids": struggling,
                "node_count": len(struggling),
                "focus": ["复习巩固", "克服难点", "额外练习"],
                "estimated_time_hours": len(struggling) * 0.5,
                "is_adjustment": True
            }
            stages = adjusted.get("stages", [])
            if len(stages) > 1:
                stages.insert(1, review)
            else:
                stages.append(review)
            adjusted["stages"] = stages
            adjusted["adjustment_reason"].append(f"添加了难点复习阶段，包含{len(struggling)}个节点")

        if speed != 1.0:
            for stage in adjusted.get("stages", []):
                stage_h = stage.get("estimated_time_hours", 0)
                stage["estimated_time_hours"] = stage_h / speed if speed > 0 else stage_h
            orig_total = adjusted.get("estimated_time_hours", 0)
            adjusted["estimated_time_hours"] = orig_total / speed if speed > 0 else orig_total
            if speed < 0.8:
                adjusted["adjustment_reason"].append(f"检测到学习速度较慢({speed:.1f}x)，已增加时间估计")
            elif speed > 1.2:
                adjusted["adjustment_reason"].append(f"检测到学习速度较快({speed:.1f}x)，已减少时间估计")

        total = sum(s.get("estimated_time_hours", 0) for s in adjusted.get("stages", []))
        adjusted["estimated_time_hours"] = total

        print(f"✅ 学习路径调整完成: {len(adjusted.get('stages', []))}个阶段, {total:.1f}小时")
        return adjusted

    def _determine_strategy(self, goal: LearningGoal, knowledge_network: nx.DiGraph) -> str:
        if goal.scale in [GoalScale.MICRO, GoalScale.SMALL]:
            return "sequential"
        elif goal.scale == GoalScale.MEDIUM:
            return "spiral"
        elif goal.scale == GoalScale.LARGE:
            return "modular"
        elif goal.scale == GoalScale.MASSIVE:
            return "priority"
        else:
            return "adaptive"

    def _determine_personalized_strategy(self, profile: Dict[str, Any]) -> str:
        style = profile.get("learning_style", "balanced")
        time_avail = profile.get("time_availability", "medium")
        exp = profile.get("experience_level", "intermediate")
        if time_avail == "low":
            return "priority"
        elif exp == "beginner":
            return "sequential"
        elif style == "exploratory":
            return "spiral"
        elif time_avail == "high" and exp == "advanced":
            return "modular"
        else:
            return "adaptive"

    def _generate_sequential_path(self, nodes: List[str], G: nx.DiGraph) -> List[Dict[str, Any]]:
        try:
            sub = G.subgraph(nodes)
            sorted_nodes = list(nx.topological_sort(sub))
        except:
            imp = {}
            for nid in nodes:
                in_deg = G.in_degree(nid)
                out_deg = G.out_degree(nid)
                imp[nid] = in_deg + out_deg
            sorted_nodes = sorted(nodes, key=lambda x: imp.get(x, 0), reverse=True)

        stages = []
        stage_count = min(4, max(1, len(sorted_nodes) // 5))
        per_stage = math.ceil(len(sorted_nodes) / stage_count)
        for i in range(stage_count):
            start = i * per_stage
            end = min((i+1)*per_stage, len(sorted_nodes))
            stages.append({
                "name": f"阶段 {i+1}",
                "description": f"顺序学习第{i+1}部分",
                "node_ids": sorted_nodes[start:end],
                "node_count": end-start,
                "focus": ["顺序学习", "依赖关系", "逐步深入"],
                "order": "sequential"
            })
        return stages

    def _generate_spiral_path(self, nodes: List[str], G: nx.DiGraph, goal: LearningGoal) -> List[Dict[str, Any]]:
        core = self._identify_core_nodes(nodes, G)
        stages = []
        if core:
            stages.append({
                "name": "螺旋第1轮: 核心探索",
                "description": "探索核心概念，建立整体认知",
                "node_ids": core[:min(5, len(core))],
                "node_count": min(5, len(core)),
                "focus": ["核心概念", "整体认知", "初步了解"],
                "depth": "surface"
            })
        remaining = [n for n in nodes if n not in core]
        if remaining:
            stages.append({
                "name": "螺旋第2轮: 基础建立",
                "description": "学习基础知识，建立理解框架",
                "node_ids": remaining[:min(8, len(remaining))],
                "node_count": min(8, len(remaining)),
                "focus": ["基础知识", "建立框架", "深入理解"],
                "depth": "understanding"
            })
        if nodes:
            stages.append({
                "name": "螺旋第3轮: 深化理解",
                "description": "深化理解，建立联系",
                "node_ids": nodes[:min(10, len(nodes))],
                "node_count": min(10, len(nodes)),
                "focus": ["深度理解", "建立联系", "分析应用"],
                "depth": "analysis"
            })
            stages.append({
                "name": "螺旋第4轮: 整合应用",
                "description": "整合知识，实践应用",
                "node_ids": nodes[:min(8, len(nodes))],
                "node_count": min(8, len(nodes)),
                "focus": ["整合知识", "实践应用", "创新思考"],
                "depth": "application"
            })
        return stages

    def _generate_modular_path(self, nodes: List[str], G: nx.DiGraph) -> List[Dict[str, Any]]:
        try:
            if isinstance(G, nx.DiGraph):
                und = G.to_undirected()
            else:
                und = G
            sub = und.subgraph(nodes)
            import community as community_louvain
            part = community_louvain.best_partition(sub)
            comms = defaultdict(list)
            for node, cid in part.items():
                comms[cid].append(node)
            stages = []
            for i, (cid, members) in enumerate(comms.items()):
                stages.append({
                    "name": f"模块 {i+1}",
                    "description": f"学习知识模块{i+1}，包含{len(members)}个相关概念",
                    "node_ids": members,
                    "node_count": len(members),
                    "community_id": cid,
                    "focus": ["模块学习", "内部关联", "并行掌握"]
                })
            stages.sort(key=lambda x: x["node_count"], reverse=True)
            return stages
        except Exception:
            return self._generate_random_modular_path(nodes)

    def _generate_priority_path(self, nodes: List[str], G: nx.DiGraph) -> List[Dict[str, Any]]:
        prio = {}
        for nid in nodes:
            try:
                cent = nx.degree_centrality(G).get(nid, 0)
            except:
                cent = 0
            prereq = G.in_degree(nid)
            imp = G.nodes[nid].get('importance', 0.5)
            prio[nid] = cent * 0.4 + (prereq/10) * 0.3 + imp * 0.3
        sorted_nodes = sorted(nodes, key=lambda x: prio.get(x, 0), reverse=True)
        stages = []
        if sorted_nodes:
            high_cnt = max(1, int(len(sorted_nodes)*0.3))
            stages.append({
                "name": "高优先级",
                "description": "学习最重要的核心概念",
                "node_ids": sorted_nodes[:high_cnt],
                "node_count": high_cnt,
                "priority": "high",
                "focus": ["核心概念", "关键知识", "高效学习"]
            })
            mid_cnt = max(1, int(len(sorted_nodes)*0.4))
            stages.append({
                "name": "中优先级",
                "description": "学习重要的支持性知识",
                "node_ids": sorted_nodes[high_cnt:high_cnt+mid_cnt],
                "node_count": mid_cnt,
                "priority": "medium",
                "focus": ["支持知识", "建立基础", "系统学习"]
            })
            if high_cnt+mid_cnt < len(sorted_nodes):
                stages.append({
                    "name": "低优先级",
                    "description": "学习补充性知识",
                    "node_ids": sorted_nodes[high_cnt+mid_cnt:],
                    "node_count": len(sorted_nodes)-high_cnt-mid_cnt,
                    "priority": "low",
                    "focus": ["补充知识", "拓展学习", "完善体系"]
                })
        return stages

    def _generate_adaptive_path(self, nodes: List[str], G: nx.DiGraph, current: List[str]) -> List[Dict[str, Any]]:
        gaps = self.network_builder.identify_knowledge_gaps(G, current)
        stages = []
        missing = []
        for g in gaps.get("missing_prerequisites", []):
            missing.extend(g.get("missing_nodes", []))
        if missing:
            missing = list(set(missing))
            stages.append({
                "name": "先决条件学习",
                "description": f"填补{len(missing)}个先决知识缺口",
                "node_ids": missing[:10],
                "node_count": min(10, len(missing)),
                "focus": ["先决知识", "基础准备", "打通路径"],
                "is_gap_filling": True
            })
        recs = gaps.get("recommended_nodes", [])
        if recs:
            ready = [r["node_id"] for r in recs if r.get("ready_to_learn", False)]
            if ready:
                stages.append({
                    "name": "推荐学习",
                    "description": f"学习{len(ready)}个推荐的知识节点",
                    "node_ids": ready[:8],
                    "node_count": min(8, len(ready)),
                    "focus": ["推荐学习", "高效路径", "适时学习"]
                })
        remaining = [n for n in nodes if n not in missing and n not in [r["node_id"] for r in recs]]
        if remaining:
            imp = {nid: G.nodes[nid].get('importance', 0.5) for nid in remaining}
            sorted_rem = sorted(remaining, key=lambda x: imp.get(x, 0), reverse=True)
            stages.append({
                "name": "扩展学习",
                "description": f"学习{len(sorted_rem[:6])}个扩展知识节点",
                "node_ids": sorted_rem[:6],
                "node_count": min(6, len(sorted_rem)),
                "focus": ["扩展知识", "完善体系", "深化理解"]
            })
        return stages

    def _generate_random_modular_path(self, nodes: List[str]) -> List[Dict[str, Any]]:
        import random
        shuffled = nodes[:]
        random.shuffle(shuffled)
        stage_cnt = min(4, max(1, len(shuffled)//3))
        per = math.ceil(len(shuffled) / stage_cnt)
        stages = []
        for i in range(stage_cnt):
            start = i*per
            end = min((i+1)*per, len(shuffled))
            stages.append({
                "name": f"模块 {i+1}",
                "description": f"学习知识模块{i+1}",
                "node_ids": shuffled[start:end],
                "node_count": end-start,
                "focus": ["模块学习", "知识分组", "系统掌握"]
            })
        return stages

    def _identify_core_nodes(self, nodes: List[str], G: nx.DiGraph) -> List[str]:
        core = []
        try:
            cent = nx.degree_centrality(G)
            for nid in nodes:
                if cent.get(nid, 0) > 0.1:
                    core.append(nid)
        except:
            pass
        if len(core) < 3:
            try:
                pr = nx.pagerank(G)
                sorted_nodes = sorted(nodes, key=lambda x: pr.get(x, 0), reverse=True)
                core = sorted_nodes[:min(5, len(sorted_nodes))]
            except:
                core = nodes[:min(5, len(nodes))]
        return core

    def _identify_visual_nodes(self, G: nx.DiGraph) -> List[str]:
        vis = []
        for nid, data in G.nodes(data=True):
            title = data.get('title', '').lower()
            if any(kw in title for kw in ['图', '表', '视觉', '可视化', '图表']):
                vis.append(nid)
        return vis

    def _identify_auditory_nodes(self, G: nx.DiGraph) -> List[str]:
        aud = []
        for nid, data in G.nodes(data=True):
            title = data.get('title', '').lower()
            if any(kw in title for kw in ['音频', '声音', '听力', '讲解', '讲座']):
                aud.append(nid)
        return aud

    def _identify_practice_nodes(self, G: nx.DiGraph) -> List[str]:
        prac = []
        for nid, data in G.nodes(data=True):
            title = data.get('title', '').lower()
            if any(kw in title for kw in ['练习', '实践', '操作', '实验', '项目']):
                prac.append(nid)
        return prac

    def _prioritize_nodes(self, all_nodes: List[str], preferred: List[str]) -> List[str]:
        result = []
        for n in preferred:
            if n in all_nodes and n not in result:
                result.append(n)
        for n in all_nodes:
            if n not in result:
                result.append(n)
        return result

    def _determine_learning_intensity(self, avail: float) -> str:
        if avail < 5:
            return "low"
        elif avail < 15:
            return "medium"
        else:
            return "high"

    def _adjust_stages_for_intensity(self, stages: List[Dict[str, Any]], intensity: str) -> List[Dict[str, Any]]:
        if intensity == "low":
            adj = []
            for s in stages:
                node_ids = s.get("node_ids", [])
                if len(node_ids) > 4:
                    s["node_ids"] = node_ids[:4]
                    s["node_count"] = 4
                    s["description"] += "（低强度调整）"
                adj.append(s)
            return adj
        elif intensity == "high":
            if len(stages) > 3:
                merged = {
                    "name": "高强度学习阶段1",
                    "description": "合并的高强度学习阶段",
                    "node_ids": [],
                    "node_count": 0,
                    "focus": ["高强度", "集中学习", "快速推进"]
                }
                for s in stages[:2]:
                    merged["node_ids"].extend(s.get("node_ids", []))
                merged["node_ids"] = list(set(merged["node_ids"]))
                merged["node_count"] = len(merged["node_ids"])
                return [merged] + stages[2:]
            else:
                return stages
        else:
            return stages

    def _estimate_stage_time(self, stage: Dict[str, Any], G: nx.DiGraph) -> float:
        cnt = stage.get("node_count", 0)
        base = cnt * 0.5
        depth = stage.get("depth", "understanding")
        if depth == "surface":
            base *= 0.7
        elif depth in ["analysis", "application"]:
            base *= 1.3
        if stage.get("is_gap_filling"):
            base *= 1.2
        return round(base, 1)

    def _generate_path_recommendations(self, path: Dict[str, Any], G: nx.DiGraph, current: List[str]) -> List[str]:
        rec = []
        strat = path.get("strategy", "adaptive")
        total = path.get("total_nodes", 0)
        hours = path.get("estimated_time_hours", 0)
        if strat == "sequential":
            rec.append("建议按顺序学习，不要跳过的前面的内容")
        elif strat == "spiral":
            rec.append("建议多次循环学习，每次加深理解")
        elif strat == "modular":
            rec.append("建议按模块学习，可以并行学习不同模块")
        elif strat == "priority":
            rec.append("建议优先学习高优先级内容，时间有限时可以跳过低优先级内容")
        elif strat == "adaptive":
            rec.append("建议根据学习情况动态调整学习计划")
        if total > 50:
            rec.append("学习内容较多，建议制定长期计划并坚持执行")
        elif total < 10:
            rec.append("学习内容较少，可以快速完成")
        if hours > 40:
            rec.append(f"预计需要{hours:.0f}小时，建议分散在几周内完成")
        elif hours > 20:
            rec.append(f"预计需要{hours:.0f}小时，建议在一周内集中学习")
        else:
            rec.append(f"预计需要{hours:.0f}小时，可以在几天内完成")
        if not current:
            rec.append("从零开始学习，建议先建立整体认知")
        elif len(current) > 10:
            rec.append("已有一定基础，可以快速推进学习")
        return rec

    def _generate_personalized_recommendations(self, profile: Dict[str, Any], path: Dict[str, Any], G: nx.DiGraph) -> List[str]:
        rec = []
        style = profile.get("learning_style", "balanced")
        avail = profile.get("available_time_hours_per_week", 10)
        if style == "visual":
            rec.append("作为视觉型学习者，建议多使用图表、思维导图等可视化工具")
        elif style == "auditory":
            rec.append("作为听觉型学习者，建议多听讲解、参与讨论")
        elif style == "kinesthetic":
            rec.append("作为动觉型学习者，建议多动手实践、做练习")
        if avail < 5:
            rec.append("每周学习时间有限，建议制定高效的学习计划")
        elif avail > 20:
            rec.append("每周学习时间充足，可以按计划稳步推进")
        weeks = path.get("estimated_weeks", 0)
        if weeks > 8:
            rec.append(f"预计需要{weeks}周，建议设置阶段性目标保持动力")
        return rec