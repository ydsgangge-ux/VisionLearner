# explorer/network_builder.py
"""
知识网络构建器 - 构建和分析知识网络
"""

import random
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import re

from foundation import MindMapNode, KnowledgeNode, KnowledgeType
from perception import LLMClient

# 导入愿景核心
from vision_core import get_vision_core


class KnowledgeNetworkBuilder:
    """
    知识网络构建器 - 构建和分析知识网络
    识别知识节点之间的关系和模式
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        
        # ========== 愿景核心集成 ==========
        self.vision_core = get_vision_core()

        self.relation_types = {
            "prerequisite": {"name": "先决条件", "description": "学习A需要先掌握B", "strength": 0.9},
            "related": {"name": "相关", "description": "A和B有相关性", "strength": 0.6},
            "part_of": {"name": "组成部分", "description": "A是B的一部分", "strength": 0.8},
            "instance_of": {"name": "实例", "description": "A是B的一个实例", "strength": 0.7},
            "similar_to": {"name": "相似", "description": "A和B相似", "strength": 0.5},
            "contrast_with": {"name": "对比", "description": "A和B形成对比", "strength": 0.4},
            "leads_to": {"name": "导致", "description": "A导致或产生B", "strength": 0.7},
            "analogy": {"name": "类比", "description": "A与B类似", "strength": 0.5}
        }

        self.network_metrics = [
            "degree_centrality",
            "betweenness_centrality",
            "closeness_centrality",
            "eigenvector_centrality",
            "pagerank",
            "clustering_coefficient",
            "community_detection"
        ]

    def build_from_mindmap(self,
                          mindmap_root: MindMapNode,
                          node_map: Dict[str, MindMapNode]) -> nx.DiGraph:
        """
        从思维导图构建知识网络
        """
        print(f"🔗 从思维导图构建知识网络")
        G = nx.DiGraph()
        
        # ========== 愿景核心集成：计算节点的愿景相关性 ==========
        for node_id, node in node_map.items():
            # 评估节点与文明愿景的契合度
            vision_alignment = self.vision_core.evaluate_alignment(
                f"{node.title} {node.description}",
                detailed=False
            )
            
            G.add_node(node_id,
                     title=node.title,
                     description=node.description,
                     node_type=node.node_type,
                     depth=node.depth,
                     importance=node.importance,
                     difficulty=node.difficulty,
                     vision_relevance=vision_alignment["score"],  # 愿景相关性
                     vision_priority=vision_alignment["priority"])  # 愿景优先级
        
        for node_id, node in node_map.items():
            if node.parent_id and node.parent_id in node_map:
                G.add_edge(node.parent_id, node_id, relation_type="parent_child", strength=0.9)
            for sibling_id in node.sibling_ids:
                if sibling_id in node_map:
                    G.add_edge(node_id, sibling_id, relation_type="sibling", strength=0.3)

        extra_relations = self._identify_relations_with_llm(node_map)
        for source, target, rel_type, strength in extra_relations:
            if source in G and target in G:
                G.add_edge(source, target, relation_type=rel_type, strength=strength)

        print(f"✅ 知识网络构建完成: {G.number_of_nodes()}个节点, {G.number_of_edges()}条边")
        return G

    def build_from_knowledge_nodes(self,
                                  knowledge_nodes: List[KnowledgeNode]) -> nx.DiGraph:
        """
        从知识节点构建知识网络
        """
        print(f"🔗 从知识节点构建知识网络 ({len(knowledge_nodes)}个节点)")
        G = nx.DiGraph()
        
        # ========== 愿景核心集成：计算知识节点的愿景相关性 ==========
        for node in knowledge_nodes:
            # 评估节点与文明愿景的契合度
            vision_alignment = self.vision_core.evaluate_alignment(
                f"{node.title} {node.content}",
                detailed=False
            )
            
            G.add_node(node.id,
                     title=node.title,
                     content=node.content[:100] if node.content else "",
                     knowledge_type=node.knowledge_type.value,
                     confidence=node.confidence,
                     mastery_score=node.mastery_score,
                     vision_relevance=vision_alignment["score"],  # 愿景相关性
                     vision_priority=vision_alignment["priority"])  # 愿景优先级
        
        for node in knowledge_nodes:
            for prereq_id in node.prerequisites:
                if prereq_id in G:
                    G.add_edge(prereq_id, node.id, relation_type="prerequisite", strength=0.9)
            for related_id in node.related_nodes:
                if related_id in G:
                    G.add_edge(node.id, related_id, relation_type="related", strength=0.6)

        content_relations = self._identify_content_relations(knowledge_nodes)
        for source, target, strength in content_relations:
            if source in G and target in G:
                G.add_edge(source, target, relation_type="content_similarity", strength=strength)

        semantic_relations = self._identify_semantic_relations(knowledge_nodes)
        for source, target, rel_type, strength in semantic_relations:
            if source in G and target in G:
                G.add_edge(source, target, relation_type=rel_type, strength=strength)

        print(f"✅ 知识网络构建完成: {G.number_of_nodes()}个节点, {G.number_of_edges()}条边")
        return G

    def analyze_network(self, G: nx.Graph) -> Dict[str, Any]:
        """
        分析知识网络
        """
        print(f"📊 分析知识网络")
        analysis = {
            "basic_stats": {},
            "centrality_measures": {},
            "community_structure": {},
            "key_nodes": {},
            "recommendations": []
        }

        analysis["basic_stats"] = {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "density": nx.density(G),
            "is_connected": nx.is_weakly_connected(G) if isinstance(G, nx.DiGraph) else nx.is_connected(G),
            "average_degree": sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
        }

        if G.number_of_nodes() > 0:
            degree_centrality = nx.degree_centrality(G)
            analysis["centrality_measures"]["degree"] = self._get_top_nodes(degree_centrality, 5)
            try:
                betweenness = nx.betweenness_centrality(G)
                analysis["centrality_measures"]["betweenness"] = self._get_top_nodes(betweenness, 5)
            except:
                analysis["centrality_measures"]["betweenness"] = []
            try:
                closeness = nx.closeness_centrality(G)
                analysis["centrality_measures"]["closeness"] = self._get_top_nodes(closeness, 5)
            except:
                analysis["centrality_measures"]["closeness"] = []
            try:
                pagerank = nx.pagerank(G)
                analysis["centrality_measures"]["pagerank"] = self._get_top_nodes(pagerank, 5)
            except:
                analysis["centrality_measures"]["pagerank"] = []

        try:
            if isinstance(G, nx.DiGraph):
                G_undirected = G.to_undirected()
            else:
                G_undirected = G
            import community as community_louvain
            partition = community_louvain.best_partition(G_undirected)
            communities = defaultdict(list)
            for node, cid in partition.items():
                communities[cid].append(node)
            analysis["community_structure"] = {
                "community_count": len(communities),
                "communities": {cid: len(nodes) for cid, nodes in communities.items()},
                "largest_community": max(len(nodes) for nodes in communities.values()) if communities else 0
            }
        except Exception as e:
            analysis["community_structure"] = {"error": str(e)}

        analysis["key_nodes"] = self._identify_key_nodes(G, analysis["centrality_measures"])
        analysis["recommendations"] = self._generate_network_recommendations(G, analysis)

        return analysis

    def find_learning_path(self,
                          G: nx.DiGraph,
                          start_node_id: str,
                          target_node_id: str) -> Optional[List[str]]:
        """
        查找学习路径
        """
        print(f"🛣️ 查找学习路径: {start_node_id} -> {target_node_id}")
        if start_node_id not in G or target_node_id not in G:
            print(f"❌ 节点不存在于网络中")
            return None
        try:
            weighted_G = nx.DiGraph()
            for u, v, data in G.edges(data=True):
                strength = data.get('strength', 0.5)
                weight = 1.0 / strength if strength > 0 else 100.0
                weighted_G.add_edge(u, v, weight=weight)
            path = nx.shortest_path(weighted_G, start_node_id, target_node_id, weight='weight')
            print(f"✅ 找到学习路径: {len(path)}个节点")
            return path
        except nx.NetworkXNoPath:
            print(f"❌ 未找到从 {start_node_id} 到 {target_node_id} 的路径")
            return None
        except Exception as e:
            print(f"❌ 查找学习路径失败: {str(e)}")
            return None

    def identify_knowledge_gaps(self,
                               G: nx.DiGraph,
                               mastered_nodes: List[str]) -> Dict[str, Any]:
        """
        识别知识缺口
        """
        print(f"🔍 识别知识缺口 (已掌握: {len(mastered_nodes)}个节点)")
        gaps = {
            "missing_prerequisites": [],
            "isolated_clusters": [],
            "weak_connections": [],
            "recommended_nodes": []
        }

        for node_id in G.nodes():
            if node_id in mastered_nodes:
                continue
            prerequisites = []
            for pred in G.predecessors(node_id):
                edge_data = G.get_edge_data(pred, node_id)
                if edge_data and edge_data.get('relation_type') == 'prerequisite':
                    prerequisites.append(pred)
            missing = [p for p in prerequisites if p not in mastered_nodes]
            if missing:
                gaps["missing_prerequisites"].append({
                    "node_id": node_id,
                    "node_title": G.nodes[node_id].get('title', node_id),
                    "missing_count": len(missing),
                    "missing_nodes": missing[:3]
                })

        if not nx.is_weakly_connected(G):
            components = list(nx.weakly_connected_components(G))
            mastered_component = None
            for comp in components:
                if any(n in comp for n in mastered_nodes):
                    mastered_component = comp
                    break
            if mastered_component:
                for comp in components:
                    if comp != mastered_component:
                        gaps["isolated_clusters"].append({
                            "component_size": len(comp),
                            "component_nodes": list(comp)[:5]
                        })

        weak_threshold = 0.3
        for u, v, data in G.edges(data=True):
            strength = data.get('strength', 0.5)
            if strength < weak_threshold and u in mastered_nodes and v not in mastered_nodes:
                gaps["weak_connections"].append({
                    "from_node": u,
                    "to_node": v,
                    "strength": strength,
                    "relation_type": data.get('relation_type', 'unknown')
                })

        gaps["recommended_nodes"] = self._recommend_learning_nodes(G, mastered_nodes)
        return gaps

    def _identify_relations_with_llm(self, node_map: Dict[str, MindMapNode]) -> List[Tuple[str, str, str, float]]:
        """使用大模型识别节点间关系"""
        relations = []
        nodes = list(node_map.values())
        if len(nodes) > 10:
            nodes.sort(key=lambda x: x.importance, reverse=True)
            nodes = nodes[:10]

        node_info = [f"{node.id}: {node.title} - {node.description[:50]}" for node in nodes]
        prompt = f"""请分析以下知识节点之间的关系：

节点信息：
{chr(10).join(node_info)}

请识别节点之间可能存在的关系，包括：
1. 先决条件关系（学习A需要先掌握B）
2. 相关关系（A和B有相关性）
3. 组成部分关系（A是B的一部分）
4. 相似关系（A和B相似）

对于每个识别的关系，请提供：
- 源节点ID
- 目标节点ID
- 关系类型
- 关系强度（0.0-1.0）

请以JSON数组格式返回。"""
        response = self.llm_client.call_llm(prompt=prompt, max_tokens=1000, temperature=0.4)
        if response:
            try:
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    llm_relations = json.loads(json_str)
                    for rel in llm_relations:
                        source = rel.get('source')
                        target = rel.get('target')
                        rel_type = rel.get('relation_type', 'related')
                        strength = float(rel.get('strength', 0.5))
                        if source in node_map and target in node_map:
                            relations.append((source, target, rel_type, strength))
            except Exception as e:
                print(f"❌ LLM关系识别解析失败: {str(e)}")
        return relations

    def _identify_content_relations(self, knowledge_nodes: List[KnowledgeNode]) -> List[Tuple[str, str, float]]:
        """基于内容相似性识别关系"""
        relations = []
        for i, n1 in enumerate(knowledge_nodes):
            for j, n2 in enumerate(knowledge_nodes):
                if i >= j:
                    continue
                sim = self._calculate_text_similarity(
                    f"{n1.title} {n1.content[:100]}",
                    f"{n2.title} {n2.content[:100]}"
                )
                if sim > 0.3:
                    relations.append((n1.id, n2.id, sim))
        return relations

    def _identify_semantic_relations(self, knowledge_nodes: List[KnowledgeNode]) -> List[Tuple[str, str, str, float]]:
        """识别语义关系"""
        relations = []
        if len(knowledge_nodes) > 8:
            selected = random.sample(knowledge_nodes, 8)
        else:
            selected = knowledge_nodes
        pairs = []
        for i in range(len(selected)):
            for j in range(i+1, len(selected)):
                pairs.append((selected[i], selected[j]))
        if len(pairs) > 10:
            pairs = random.sample(pairs, 10)

        for n1, n2 in pairs:
            prompt = f"""请分析以下两个知识概念之间的关系：

概念1: {n1.title}
描述: {n1.content[:100]}

概念2: {n2.title}
描述: {n2.content[:100]}

请分析它们之间的关系类型和强度：
1. 关系类型：先决条件、相关、组成部分、相似、对比等
2. 关系强度：0.0-1.0，表示关系的紧密程度
3. 关系描述：简要说明关系

请以JSON格式返回分析结果。"""
            response = self.llm_client.call_llm(prompt=prompt, max_tokens=500, temperature=0.3)
            if response:
                try:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group(0))
                        rel_type = analysis.get('relation_type', 'related')
                        strength = float(analysis.get('strength', 0.5))
                        relations.append((n1.id, n2.id, rel_type, strength))
                except:
                    pass
        return relations

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似性（简化版）"""
        if not text1 or not text2:
            return 0.0
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        if not words1 or not words2:
            return 0.0
        inter = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return inter / union if union > 0 else 0.0

    def _get_top_nodes(self, cent_dict: Dict[str, float], top_n: int) -> List[Dict[str, Any]]:
        sorted_items = sorted(cent_dict.items(), key=lambda x: x[1], reverse=True)
        return [{"node_id": nid, "centrality": val, "rank": i+1} for i, (nid, val) in enumerate(sorted_items[:top_n])]

    def _identify_key_nodes(self, G: nx.Graph, cent: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        key = {"hubs": [], "bridges": [], "foundations": [], "bottlenecks": []}
        if "degree" in cent:
            key["hubs"] = cent["degree"][:3]
        if "betweenness" in cent:
            key["bridges"] = cent["betweenness"][:3]
        if isinstance(G, nx.DiGraph):
            in_deg = dict(G.in_degree())
            sorted_in = sorted(in_deg.items(), key=lambda x: x[1], reverse=True)
            key["foundations"] = [{"node_id": nid, "in_degree": d, "rank": i+1} for i, (nid, d) in enumerate(sorted_in[:3])]
            bottlenecks = []
            for nid in G.nodes():
                in_d = G.in_degree(nid)
                out_d = G.out_degree(nid)
                if in_d > 3 and out_d < 2:
                    bottlenecks.append((nid, in_d, out_d))
            bottlenecks.sort(key=lambda x: x[1], reverse=True)
            key["bottlenecks"] = [{"node_id": nid, "in_degree": ind, "out_degree": outd, "rank": i+1}
                                   for i, (nid, ind, outd) in enumerate(bottlenecks[:3])]
        return key

    def _generate_network_recommendations(self, G: nx.Graph, analysis: Dict[str, Any]) -> List[str]:
        rec = []
        density = analysis["basic_stats"].get("density", 0)
        if density < 0.1:
            rec.append("网络连接稀疏，建议增加节点间的关联学习")
        elif density > 0.5:
            rec.append("网络连接紧密，可以考虑进行系统性的复习和整合")
        comm_count = analysis["community_structure"].get("community_count", 1)
        if comm_count > 3:
            rec.append(f"网络包含{comm_count}个知识社区，建议按社区分组学习")
        if analysis["key_nodes"].get("bottlenecks"):
            rec.append(f"识别到{len(analysis['key_nodes']['bottlenecks'])}个瓶颈节点，建议优先学习这些节点以打通知识路径")
        if not analysis["basic_stats"].get("is_connected", True):
            rec.append("网络未完全连通，可能存在孤立的知识点，建议建立连接")
        return rec

    def _recommend_learning_nodes(self, G: nx.DiGraph, mastered: List[str]) -> List[Dict[str, Any]]:
        frontier = set()
        for nid in mastered:
            if nid in G:
                for suc in G.successors(nid):
                    if suc not in mastered:
                        frontier.add(suc)
        recs = []
        for nid in frontier:
            prereqs = list(G.predecessors(nid))
            mastered_prereqs = [p for p in prereqs if p in mastered]
            prereq_ratio = len(mastered_prereqs) / len(prereqs) if prereqs else 1.0
            try:
                importance = nx.pagerank(G).get(nid, 0.5)
            except:
                importance = G.out_degree(nid) / (G.number_of_nodes() - 1) if G.number_of_nodes() > 1 else 0.5
            
            # ========== 愿景核心集成：愿景优先级影响推荐 ==========
            vision_relevance = G.nodes[nid].get('vision_relevance', 0.0)
            vision_priority = G.nodes[nid].get('vision_priority', 5)
            
            # 综合计算推荐优先级：先决条件比例(40%) + 重要性(30%) + 愿景相关性(30%)
            priority = (prereq_ratio * 0.4) + (importance * 0.3) + (vision_relevance * 0.3)
            
            # 如果愿景优先级高，额外加分
            if vision_priority >= 8:
                priority += 0.2
            
            recs.append({
                "node_id": nid,
                "node_title": G.nodes[nid].get('title', nid),
                "prerequisite_ratio": prereq_ratio,
                "importance": importance,
                "vision_relevance": vision_relevance,  # 愿景相关性
                "vision_priority": vision_priority,  # 愿景优先级
                "priority": priority,
                "ready_to_learn": prereq_ratio >= 0.8
            })
        recs.sort(key=lambda x: x["priority"], reverse=True)
        return recs[:10]