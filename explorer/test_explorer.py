# test_explorer.py
"""
测试探索模块（深度知识探索与网络构建）
"""

from foundation import MindMapNode, KnowledgeNode, LearningGoal, GoalScale, KnowledgeType, LearningLevel
from explorer import ExplorerManager

if __name__ == "__main__":
    print("🧪 测试探索模块（深度知识探索与网络构建）...")
    print("=" * 70)

    manager = ExplorerManager()

    print("\n🤔 测试智能提问引擎:")
    print("-" * 50)
    test_node = MindMapNode(
        id="test_concept_node",
        title="机器学习",
        description="使计算机能够从数据中学习并做出决策的技术",
        node_type="concept",
        importance=0.8,
        difficulty=0.6
    )
    questions = manager.question_engine.generate_questions_for_node(test_node, "understanding", 3)
    print(f"✅ 为'{test_node.title}'生成了 {len(questions)} 个问题:")
    for i, q in enumerate(questions):
        print(f"  {i+1}. {q['text']}")
        print(f"     难度: {q['difficulty_description']}, 预估时间: {q['estimated_thinking_time']}秒")

    print("\n🔗 测试深度问题链:")
    print("-" * 50)
    chain = manager.question_engine.generate_deep_questions_chain(test_node, chain_length=4)
    print(f"✅ 生成了 {len(chain)} 个问题的深度问题链:")
    for i, q in enumerate(chain):
        print(f"  {i+1}. [{q['depth_name']}] {q['text']}")

    print("\n🎨 测试思维导图可视化:")
    print("-" * 50)
    root = MindMapNode(
        id="test_root",
        title="人工智能学习",
        description="人工智能相关知识的思维导图",
        depth=0,
        node_type="concept"
    )
    node_map = {root.id: root}
    topics = ["机器学习", "深度学习", "自然语言处理", "计算机视觉"]
    for i, topic in enumerate(topics):
        child = MindMapNode(
            id=f"test_child_{i}",
            title=topic,
            description=f"{topic}相关知识",
            depth=1,
            parent_id=root.id,
            node_type="concept",
            importance=0.7,
            difficulty=0.5
        )
        node_map[child.id] = child
        root.children_ids.append(child.id)
        for j in range(2):
            gc = MindMapNode(
                id=f"test_grandchild_{i}_{j}",
                title=f"{topic}子主题{j+1}",
                description=f"{topic}的详细知识点",
                depth=2,
                parent_id=child.id,
                node_type="concept",
                importance=0.5,
                difficulty=0.4
            )
            node_map[gc.id] = gc
            child.children_ids.append(gc.id)

    viz_path = manager.visualizer.visualize_mindmap(root, node_map, "png", "balanced")
    if viz_path:
        print(f"✅ 思维导图可视化完成: {viz_path}")
    else:
        print("❌ 思维导图可视化失败")

    print("\n🔗 测试知识网络构建:")
    print("-" * 50)
    knodes = []
    for i in range(8):
        node = KnowledgeNode(
            id=f"knowledge_node_{i}",
            title=f"知识概念{i+1}",
            content=f"这是知识概念{i+1}的详细内容",
            knowledge_type=KnowledgeType.CONCEPT if i % 3 == 0 else KnowledgeType.FACT,
            learning_level=LearningLevel.UNDERSTANDING,
            confidence=0.6 + i * 0.05,
            mastery_score=0.3 + i * 0.1
        )
        knodes.append(node)
    network = manager.network_builder.build_from_knowledge_nodes(knodes)
    print(f"✅ 知识网络构建完成: {network.number_of_nodes()}个节点, {network.number_of_edges()}条边")
    analysis = manager.network_builder.analyze_network(network)
    print(f"📊 网络分析:")
    print(f"  节点数量: {analysis['basic_stats'].get('node_count', 0)}")
    print(f"  边数量: {analysis['basic_stats'].get('edge_count', 0)}")
    print(f"  网络密度: {analysis['basic_stats'].get('density', 0):.3f}")

    print("\n🛣️ 测试学习路径生成:")
    print("-" * 50)
    goal = LearningGoal(
        id="test_goal",
        description="学习人工智能基础知识",
        target_knowledge_count=len(knodes),
        scale=GoalScale.SMALL
    )
    path = manager.path_generator.generate_for_goal(goal, network, [])
    print(f"✅ 学习路径生成完成:")
    print(f"  策略: {path.get('strategy', '未知')}")
    print(f"  阶段数: {len(path.get('stages', []))}")
    print(f"  总节点数: {path.get('total_nodes', 0)}")
    print(f"  预估时间: {path.get('estimated_time_hours', 0):.1f}小时")

    print("\n👤 测试个性化学习路径:")
    print("-" * 50)
    profile = {
        "user_id": "test_user",
        "learning_style": "visual",
        "available_time_hours_per_week": 8,
        "experience_level": "beginner",
        "prior_knowledge": []
    }
    ppath = manager.generate_personalized_learning_path(profile, knodes)
    print(f"✅ 个性化学习路径生成完成:")
    print(f"  学习风格: {ppath.get('learning_style', '未知')}")
    print(f"  策略: {ppath.get('strategy', '未知')}")
    print(f"  预估周数: {ppath.get('estimated_weeks', 0)}周")

    print("\n🔍 测试探索管理器:")
    print("-" * 50)
    exp = manager.explore_mindmap(root, node_map, "understanding")
    print(f"✅ 思维导图探索完成:")
    print(f"  问题数量: {len(exp.get('questions', {}))}组")
    print(f"  可视化文件: {len(exp.get('visualization', {}))}个")
    print(f"  网络分析: {len(exp.get('network_analysis', {}))}项指标")

    print("\n✅ 探索模块测试完成")
    print("=" * 70)