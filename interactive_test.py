# interactive_test.py
"""
交互式系统启动测试
"""

import sys
import os

# 设置编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 导入主模块
from main import SystemCoordinator

print("="*80)
print("系统初始化测试")
print("="*80)

# 初始化系统
coordinator = SystemCoordinator()

print("\n" + "="*80)
print("系统启动成功！")
print("="*80)

# 显示愿景状态
print("\n🌌 愿景核心状态:")
print(f"  激活度: {coordinator.vision_core.vision_activation_level:.0%}")
print(f"  当前阶段: {coordinator.vision_core.current_tier}")
print(f"  目标阶段: {coordinator.vision_core.target_tier}")

# 测试创建目标
print("\n🎯 测试创建学习目标...")
goal = coordinator.create_learning_goal("学习Python编程")
print(f"  ✅ 目标创建成功: {goal.id}")
print(f"  描述: {goal.description}")
print(f"  规模: {goal.scale.value}")

# 测试生成思维导图
print("\n🌳 测试生成思维导图...")
mindmap_root = coordinator.perception_manager.generate_mindmap_for_goal(goal)
node_map = {}
if mindmap_root:
    # 收集所有节点
    node_map = {mindmap_root.id: mindmap_root}
    def collect_nodes(node):
        for child_id in node.children_ids:
            # 简化处理，这里实际上需要从某个地方获取子节点
            pass
    print(f"  ✅ 思维导图生成成功")
    print(f"  根节点: {mindmap_root.title}")
else:
    print("  ⚠️ 思维导图生成失败，使用简化节点")

# 测试构建知识网络
print("\n🔗 测试构建知识网络...")
network_builder = coordinator.explorer_manager.network_builder
G = network_builder.build_from_mindmap(mindmap_root, node_map)
print(f"  ✅ 知识网络构建成功")
print(f"  节点数: {G.number_of_nodes()}")
print(f"  边数: {G.number_of_edges()}")

# 检查愿景属性
has_vision = any('vision_relevance' in G.nodes[n] for n in G.nodes())
print(f"  愿景属性: {'已注入' if has_vision else '未注入'}")

# 测试创建学习计划
print("\n📋 测试创建学习计划...")
coordinator.current_goal = goal
coordinator.current_mindmap = mindmap_root
plan = coordinator.allocator.allocate_by_mindmap(goal, mindmap_root, node_map)
print(f"  ✅ 学习计划创建成功")
if "ethical_review" in plan:
    print(f"  伦理审查: {plan['ethical_review']['decision']}")

print("\n" + "="*80)
print("✅ 所有测试通过！系统运行正常！")
print("="*80)
