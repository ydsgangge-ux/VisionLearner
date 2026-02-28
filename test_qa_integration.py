# test_qa_integration.py
"""
测试问答系统集成
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

from main import SystemCoordinator

print("="*80)
print("问答系统集成测试")
print("="*80)

# 初始化系统
coordinator = SystemCoordinator()

# 测试1：QA系统初始化
print("\n[1/5] QA系统初始化")
print("-"*80)

print(f"QA系统已集成: {hasattr(coordinator, 'qa_system')}")
print(f"学习顾问已集成: {hasattr(coordinator, 'learning_advisor')}")

if hasattr(coordinator, 'qa_system'):
    print(f"活跃对话数: {len(coordinator.qa_system.active_conversations)}")

# 测试2：简单问答
print("\n[2/5] 简单问答测试")
print("-"*80)

test_questions = [
    "什么是Python函数？",
    "你好",
    "如何学习编程？"
]

for question in test_questions:
    print(f"\n用户：{question}")

    response = coordinator.qa_system.generate_response(
        question=question,
        conversation_id="test",
        knowledge_base={},
        mindmap_nodes={}
    )

    print(f"助手：{response['answer'][:100]}...")
    print(f"  类型：{response['question_type']}, 置信度：{response['confidence']:.2f}")
    print(f"  处理时间：{response['processing_time_ms']}ms")

# 测试3：对话历史
print("\n[3/5] 对话历史测试")
print("-"*80)

conversation = coordinator.qa_system.get_conversation_history("test")
print(f"对话轮次: {len(conversation)}")

if conversation:
    print("最近3轮对话：")
    for i, turn in enumerate(conversation[-3:], 1):
        print(f"  {i}. {turn.user_query[:30]}... → {turn.system_response[:30]}...")

# 测试4：学习指导
print("\n[4/5] 学习指导测试")
print("-"*80)

test_topics = ["Python编程", "机器学习", "数据分析"]

for topic in test_topics:
    print(f"\n主题: {topic}")
    advice = coordinator.learning_advisor.advise_on_method(topic)
    print(advice[:200] + "...")

# 测试5：进度分析
print("\n[5/5] 进度分析测试")
print("-"*80)

mock_progress = {
    "overall_progress": 0.65,
    "total_learning_time_minutes": 480,
    "avg_test_score": 72.5
}

analysis = coordinator.learning_advisor.analyze_progress(mock_progress)
print(analysis)

# 测试6：清空和导出
print("\n[6/6] 对话管理测试")
print("-"*80)

# 测试导出
conversation_export = coordinator.qa_system.export_conversation("test")
if conversation_export:
    print(f"✅ 对话导出成功")
    print(f"   对话ID: {conversation_export['conversation_id']}")
    print(f"   对话轮次: {len(conversation_export['turns'])}")
    print(f"   当前主题: {conversation_export['current_topic']}")

# 测试清空
coordinator.qa_system.clear_conversation("test")
print("✅ 对话历史已清空")

# 验证清空
conversation_after_clear = coordinator.qa_system.get_conversation_history("test")
print(f"清空后对话数: {len(conversation_after_clear)}")

# 总结
print("\n" + "="*80)
print("✅ 问答系统集成测试完成")
print("="*80)

print("\n📚 可用的问答命令：")
print("  ask <问题>        - 询问问题")
print("  clear_chat         - 清空对话历史")
print("  export_chat        - 导出对话历史")
print("  learning_advice    - 获取学习方法建议")

print("\n详细功能请参考: qa_context.py")
