# explorer/visualizer.py
"""
思维导图可视化器 - 将思维导图转换为可视化图表
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from pathlib import Path

from foundation import MindMapNode, KnowledgeNode


class MindMapVisualizer:
    """
    思维导图可视化器 - 将思维导图转换为可视化图表
    支持多种输出格式和可视化风格
    """

    def __init__(self):
        # 设置中文字体（尝试找到支持中文的字体）
        import matplotlib.font_manager as fm

        # 尝试常见的中文系统字体
        chinese_fonts = [
            'Microsoft YaHei',  # 微软雅黑
            'SimHei',  # 黑体
            'SimSun',  # 宋体
            'KaiTi',  # 楷体
            'FangSong',  # 仿宋
            'STXihei',  # 华文细黑
            'STSong',  # 华文宋体
            'PingFang SC',  # 苹方
            'Heiti SC',  # 黑体
            'WenQuanYi Micro Hei',  # 文泉驿微米黑
        ]

        # 查找第一个可用的中文字体
        font_found = False
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        for font_name in chinese_fonts:
            if font_name in available_fonts:
                plt.rcParams['font.sans-serif'] = [font_name]
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                font_found = True
                print(f"✓ 使用中文字体: {font_name}")
                break

        if not font_found:
            print("⚠️  未找到中文字体，中文字符可能显示为方块")

        # 可视化配置
        self.visualization_config = {
            "node_size": {
                "root": 3000,
                "depth_1": 2000,
                "depth_2": 1500,
                "depth_3": 1000,
                "depth_4": 800,
                "default": 1000
            },
            "node_color": {
                "root": "#FF6B6B",     # 红色
                "concept": "#4ECDC4",   # 青色
                "skill": "#FFD166",     # 黄色
                "example": "#06D6A0",   # 绿色
                "practice": "#118AB2",  # 蓝色
                "principle": "#EF476F", # 粉色
                "fact": "#073B4C",      # 深蓝
                "default": "#999999"    # 灰色
            },
            "layout": {
                "spacing": 2.0,
                "layer_spacing": 1.5,
                "node_spacing": 1.0
            },
            "font": {
                "family": "SimHei, Microsoft YaHei, sans-serif",
                "size": {
                    "root": 14,
                    "depth_1": 12,
                    "depth_2": 11,
                    "depth_3": 10,
                    "default": 10
                }
            }
        }

        self.output_formats = ["png", "svg", "pdf", "jpg"]
        self.default_format = "png"
        self.output_dir = Path("visualizations")
        self.output_dir.mkdir(exist_ok=True)

    def visualize_mindmap(self,
                         mindmap_root: MindMapNode,
                         node_map: Dict[str, MindMapNode],
                         output_format: str = "png",
                         style: str = "balanced",
                         show_progress: bool = False) -> Optional[str]:
        """
        可视化思维导图
        """
        print(f"🎨 可视化思维导图: {mindmap_root.title}")
        if output_format not in self.output_formats:
            print(f"❌ 不支持的输出格式: {output_format}")
            output_format = self.default_format

        try:
            G = nx.DiGraph()
            for node_id, node in node_map.items():
                G.add_node(node_id, **self._get_node_attributes(node, show_progress))
            for node_id, node in node_map.items():
                if node.parent_id and node.parent_id in node_map:
                    G.add_edge(node.parent_id, node_id)

            plt.figure(figsize=(16, 12))
            pos = self._create_layout(G, mindmap_root.id, style)

            node_colors = [G.nodes[n].get('color', '#999999') for n in G.nodes()]
            node_sizes = [G.nodes[n].get('size', 1000) for n in G.nodes()]

            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9)
            nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20,
                                    edge_color='#666666', width=1.5, alpha=0.6)

            labels = {n: G.nodes[n].get('label', n[:8]) for n in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=10, font_family='sans-serif')

            plt.title(f"思维导图: {mindmap_root.title}", fontsize=16, pad=20)
            self._add_legend(plt, node_map)
            plt.axis('off')
            plt.tight_layout()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mindmap_{mindmap_root.id[:8]}_{timestamp}.{output_format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"✅ 思维导图已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ 思维导图可视化失败: {str(e)}")
            plt.close()
            return None

    def visualize_knowledge_network(self,
                                  knowledge_nodes: List[KnowledgeNode],
                                  relations: Optional[List[Tuple[str, str, str]]] = None,
                                  output_format: str = "png") -> Optional[str]:
        """
        可视化知识网络
        """
        print(f"🌐 可视化知识网络 ({len(knowledge_nodes)}个节点)")
        if output_format not in self.output_formats:
            output_format = self.default_format

        try:
            G = nx.DiGraph()
            for node in knowledge_nodes:
                G.add_node(node.id,
                         label=node.title[:15],
                         knowledge_type=node.knowledge_type.value,
                         color=self._get_knowledge_node_color(node),
                         size=self._get_knowledge_node_size(node))
            if relations:
                for source, target, rel_type in relations:
                    if source in G and target in G:
                        G.add_edge(source, target, relation=rel_type, label=rel_type[:10])
            else:
                for node in knowledge_nodes:
                    for prereq in node.prerequisites:
                        if prereq in G:
                            G.add_edge(prereq, node.id, relation="先决条件", label="先决")
                    for related in node.related_nodes:
                        if related in G:
                            G.add_edge(node.id, related, relation="相关", label="相关")

            plt.figure(figsize=(14, 10))
            pos = nx.spring_layout(G, k=2, iterations=50)

            node_types = defaultdict(list)
            for node_id, data in G.nodes(data=True):
                node_types[data.get('knowledge_type', '未知')].append(node_id)

            colors = plt.cm.tab20.colors
            for i, (ntype, nlist) in enumerate(node_types.items()):
                color = colors[i % len(colors)]
                nx.draw_networkx_nodes(G, pos, nodelist=nlist,
                                     node_color=[color],
                                     node_size=[G.nodes[nid].get('size', 800) for nid in nlist],
                                     label=ntype, alpha=0.8)

            edge_colors = []
            edge_styles = []
            edge_widths = []
            for u, v, data in G.edges(data=True):
                rel = data.get('relation', '未知')
                if rel == "先决条件":
                    edge_colors.append('red')
                    edge_styles.append('solid')
                    edge_widths.append(2.0)
                elif rel == "相关":
                    edge_colors.append('blue')
                    edge_styles.append('dashed')
                    edge_widths.append(1.5)
                else:
                    edge_colors.append('gray')
                    edge_styles.append('dotted')
                    edge_widths.append(1.0)

            nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                                 style=edge_styles, width=edge_widths,
                                 alpha=0.6, arrowstyle='-|>', arrowsize=15)

            labels = {n: G.nodes[n].get('label', n[:8]) for n in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=9, font_family='sans-serif')

            edge_labels = {(u, v): data['label'] for u, v, data in G.edges(data=True) if 'label' in data}
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, label_pos=0.5)

            plt.title(f"知识网络 ({len(knowledge_nodes)}个节点, {G.number_of_edges()}个关系)", fontsize=14, pad=20)
            plt.legend(title="知识类型", loc='upper left', bbox_to_anchor=(1, 1))
            plt.axis('off')
            plt.tight_layout()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"knowledge_network_{timestamp}.{output_format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"✅ 知识网络已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ 知识网络可视化失败: {str(e)}")
            plt.close()
            return None

    def create_interactive_html(self,
                              mindmap_root: MindMapNode,
                              node_map: Dict[str, MindMapNode],
                              questions: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Optional[str]:
        """
        创建交互式HTML可视化
        """
        print(f"🖥️ 创建交互式HTML可视化")
        try:
            html_content = self._generate_html_content(mindmap_root, node_map, questions)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mindmap_interactive_{timestamp}.html"
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ 交互式HTML已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ 创建交互式HTML失败: {str(e)}")
            return None

    def _get_node_attributes(self, node: MindMapNode, show_progress: bool = False) -> Dict[str, Any]:
        """获取节点的可视化属性"""
        size_key = f"depth_{node.depth}" if node.depth <= 4 else "default"
        node_size = self.visualization_config["node_size"].get(
            size_key, self.visualization_config["node_size"]["default"]
        )
        node_color = self.visualization_config["node_color"].get(
            node.node_type, self.visualization_config["node_color"]["default"]
        )
        if node.depth == 0:
            node_color = self.visualization_config["node_color"]["root"]
        if show_progress and hasattr(node, 'learning_status'):
            label = f"{node.title}\n({node.learning_status})"
        else:
            label = node.title
        if len(label) > 20:
            label = label[:18] + "..."
        return {
            "label": label,
            "title": node.title,
            "depth": node.depth,
            "node_type": node.node_type,
            "color": node_color,
            "size": node_size,
            "description": node.description[:50] if node.description else ""
        }

    def _get_knowledge_node_color(self, node: KnowledgeNode) -> str:
        """获取知识节点的颜色"""
        color_map = {
            "概念": "#4ECDC4",
            "事实": "#118AB2",
            "原理": "#EF476F",
            "技能": "#FFD166",
            "过程": "#06D6A0",
            "系统": "#073B4C",
            "示例": "#FF9A76",
            "练习": "#7209B7",
            "策略": "#F72585",
            "模式": "#3A86FF"
        }
        return color_map.get(node.knowledge_type.value, "#999999")

    def _get_knowledge_node_size(self, node: KnowledgeNode) -> int:
        """获取知识节点的大小"""
        base_size = 800
        confidence_factor = 0.5 + node.confidence  # 0.5-1.5
        mastery_factor = 0.5 + node.mastery_score  # 0.5-1.5
        size = int(base_size * confidence_factor * mastery_factor)
        return min(size, 2000)

    def _create_layout(self, G: nx.DiGraph, root_id: str, style: str) -> Dict[str, Tuple[float, float]]:
        """创建布局"""
        if style == "hierarchical":
            return self._hierarchical_layout(G, root_id)
        elif style == "radial":
            return nx.shell_layout(G)
        elif style == "spring":
            return nx.spring_layout(G, k=2, iterations=50)
        else:
            return nx.multipartite_layout(G, subset_key="depth")

    def _hierarchical_layout(self, G: nx.DiGraph, root_id: str) -> Dict[str, Tuple[float, float]]:
        """创建层次化布局"""
        pos = {}
        depth_groups = defaultdict(list)
        for node_id in G.nodes():
            depth = G.nodes[node_id].get('depth', 0)
            depth_groups[depth].append(node_id)
        max_depth = max(depth_groups.keys()) if depth_groups else 0
        for depth, nodes in depth_groups.items():
            y = max_depth - depth
            node_count = len(nodes)
            for i, node_id in enumerate(nodes):
                x = i - (node_count - 1) / 2
                pos[node_id] = (x, y)
        return pos

    def _add_legend(self, plt, node_map: Dict[str, MindMapNode]) -> None:
        """添加图例"""
        node_types = set(node.node_type for node in node_map.values())
        from matplotlib.patches import Patch
        legend_elements = []
        for node_type in sorted(node_types):
            color = self.visualization_config["node_color"].get(
                node_type, self.visualization_config["node_color"]["default"]
            )
            legend_elements.append(Patch(facecolor=color, edgecolor='black', label=node_type))
        if legend_elements:
            plt.legend(handles=legend_elements, title="节点类型", loc='upper right', bbox_to_anchor=(1.15, 1))

    def _generate_html_content(self,
                             mindmap_root: MindMapNode,
                             node_map: Dict[str, MindMapNode],
                             questions: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> str:
        """生成HTML内容"""
        import json
        nodes_data = []
        for node_id, node in node_map.items():
            node_info = {
                "id": node_id,
                "title": node.title,
                "description": node.description,
                "depth": node.depth,
                "node_type": node.node_type,
                "importance": node.importance,
                "difficulty": node.difficulty,
                "learning_status": node.learning_status,
                "estimated_time_minutes": node.estimated_time_minutes
            }
            if questions and node_id in questions:
                node_info["questions"] = questions[node_id][:3]
            nodes_data.append(node_info)

        edges_data = []
        for node_id, node in node_map.items():
            if node.parent_id and node.parent_id in node_map:
                edges_data.append({"from": node.parent_id, "to": node_id, "type": "parent-child"})

        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>思维导图: {mindmap_root.title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header .description {{
            color: #666;
            font-size: 16px;
        }}
        .mindmap-container {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: auto;
            position: relative;
        }}
        .node {{
            cursor: pointer;
            transition: all 0.3s;
        }}
        .node:hover {{
            transform: scale(1.05);
        }}
        .node-text {{
            font-size: 12px;
            text-anchor: middle;
            pointer-events: none;
            fill: white;
            font-weight: bold;
        }}
        .controls {{
            margin-top: 20px;
            text-align: center;
        }}
        .btn {{
            background: #4ECDC4;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
            font-size: 14px;
        }}
        .btn:hover {{
            background: #3DBBB2;
        }}
        .details-panel {{
            margin-top: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 5px;
            display: none;
        }}
        .details-panel.active {{
            display: block;
        }}
        .node-info h3 {{
            color: #333;
            margin-top: 0;
        }}
        .questions-list {{
            margin-top: 20px;
        }}
        .question-item {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #4ECDC4;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
            justify-content: center;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-right: 15px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 {mindmap_root.title}</h1>
            <div class="description">{mindmap_root.description}</div>
            <div class="meta-info">
                <span>节点数量: {len(node_map)} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        </div>

        <div class="controls">
            <button class="btn" onclick="resetView()">重置视图</button>
            <button class="btn" onclick="zoomIn()">放大</button>
            <button class="btn" onclick="zoomOut()">缩小</button>
            <button class="btn" onclick="exportPNG()">导出PNG</button>
        </div>

        <div class="mindmap-container" id="mindmap"></div>

        <div class="legend" id="legend">
            <!-- 图例将由JavaScript动态生成 -->
        </div>

        <div class="details-panel" id="detailsPanel">
            <div class="node-info" id="nodeInfo">
                <!-- 节点详情将动态加载 -->
            </div>
        </div>
    </div>

    <script>
        // 数据
        const nodesData = {json.dumps(nodes_data, ensure_ascii=False)};
        const edgesData = {json.dumps(edges_data, ensure_ascii=False)};

        // 节点类型颜色映射
        const nodeColors = {json.dumps(self.visualization_config["node_color"], ensure_ascii=False)};

        // 初始化变量
        let selectedNodeId = null;

        // 创建思维导图
        function createMindMap() {{
            const container = document.getElementById('mindmap');
            const width = container.clientWidth;
            const height = container.clientHeight;

            const svg = d3.select('#mindmap')
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('id', 'mindmap-svg');

            const g = svg.append('g').attr('id', 'mindmap-g');

            const simulation = d3.forceSimulation(nodesData)
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('link', d3.forceLink(edgesData).id(d => d.id).distance(100))
                .force('collision', d3.forceCollide().radius(40));

            const link = g.append('g').attr('class', 'links')
                .selectAll('line').data(edgesData).enter()
                .append('line').attr('stroke', '#999').attr('stroke-width', 1.5).attr('stroke-opacity', 0.6);

            const node = g.append('g').attr('class', 'nodes')
                .selectAll('circle').data(nodesData).enter()
                .append('circle').attr('class', 'node')
                .attr('r', d => {{
                    if (d.depth === 0) return 30;
                    if (d.depth === 1) return 25;
                    if (d.depth === 2) return 20;
                    return 15;
                }})
                .attr('fill', d => nodeColors[d.node_type] || nodeColors.default)
                .attr('stroke', '#fff').attr('stroke-width', 2)
                .call(d3.drag()
                    .on('start', dragStarted)
                    .on('drag', dragged)
                    .on('end', dragEnded))
                .on('click', nodeClicked);

            const text = g.append('g').attr('class', 'labels')
                .selectAll('text').data(nodesData).enter()
                .append('text').attr('class', 'node-text')
                .text(d => d.title.length > 15 ? d.title.substring(0, 12) + '...' : d.title)
                .attr('font-size', d => {{
                    if (d.depth === 0) return '14px';
                    if (d.depth === 1) return '12px';
                    return '10px';
                }});

            simulation.on('tick', () => {{
                link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
                node.attr('cx', d => d.x).attr('cy', d => d.y);
                text.attr('x', d => d.x).attr('y', d => d.y);
            }});

            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => g.attr('transform', event.transform));
            svg.call(zoom);

            createLegend();
        }}

        function createLegend() {{
            const legend = document.getElementById('legend');
            const uniqueTypes = [...new Set(nodesData.map(n => n.node_type))];
            uniqueTypes.forEach(type => {{
                const item = document.createElement('div'); item.className = 'legend-item';
                const colorBox = document.createElement('div'); colorBox.className = 'legend-color';
                colorBox.style.backgroundColor = nodeColors[type] || nodeColors.default;
                const label = document.createElement('span'); label.textContent = type;
                item.appendChild(colorBox); item.appendChild(label);
                legend.appendChild(item);
            }});
        }}

        function nodeClicked(event, d) {{
            d3.selectAll('.node').attr('stroke', '#fff').attr('stroke-width', 2);
            d3.select(event.currentTarget).attr('stroke', '#FF6B6B').attr('stroke-width', 4);
            selectedNodeId = d.id;
            showNodeDetails(d);
        }}

        function showNodeDetails(nodeData) {{
            const panel = document.getElementById('detailsPanel');
            const infoDiv = document.getElementById('nodeInfo');
            let html = `
                <h3>📌 ${{nodeData.title}}</h3>
                <p><strong>描述:</strong> ${{nodeData.description || '无描述'}}</p>
                <p><strong>类型:</strong> ${{nodeData.node_type}}</p>
                <p><strong>深度:</strong> ${{nodeData.depth}}</p>
                <p><strong>重要性:</strong> ${{(nodeData.importance * 100).toFixed(0)}}%</p>
                <p><strong>难度:</strong> ${{(nodeData.difficulty * 100).toFixed(0)}}%</p>
                <p><strong>学习状态:</strong> ${{nodeData.learning_status}}</p>
                <p><strong>预估时间:</strong> ${{nodeData.estimated_time_minutes}}分钟</p>
            `;
            if (nodeData.questions && nodeData.questions.length > 0) {{
                html += `<div class="questions-list"><h4>💭 相关问题 (${{nodeData.questions.length}}个):</h4>`;
                nodeData.questions.forEach((q, i) => {{
                    html += `
                        <div class="question-item">
                            <p><strong>问题 ${{i+1}}:</strong> ${{q.text}}</p>
                            <p><small>难度: ${{q.difficulty_description}} | 预估思考时间: ${{q.estimated_thinking_time}}秒</small></p>
                        </div>
                    `;
                }});
                html += `</div>`;
            }}
            infoDiv.innerHTML = html;
            panel.classList.add('active');
        }}

        function dragStarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
        }}
        function dragged(event, d) {{
            d.fx = event.x; d.fy = event.y;
        }}
        function dragEnded(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
        }}

        function resetView() {{
            const svg = d3.select('#mindmap-svg');
            svg.transition().duration(750).call(d3.zoom().transform, d3.zoomIdentity);
        }}
        function zoomIn() {{
            const svg = d3.select('#mindmap-svg');
            svg.transition().duration(750).call(d3.zoom().scaleBy, 1.3);
        }}
        function zoomOut() {{
            const svg = d3.select('#mindmap-svg');
            svg.transition().duration(750).call(d3.zoom().scaleBy, 0.7);
        }}
        function exportPNG() {{
            alert('导出PNG功能需要后端支持，请联系系统管理员。');
        }}

        window.onload = function() {{
            createMindMap();
        }};
    </script>
</body>
</html>
"""
        return html_template