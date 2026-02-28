# test_apis.py
"""
测试豆包和讯飞 API 连接
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

from perception import LLMClient

print("="*80)
print("API 连接测试")
print("="*80)

# 初始化 LLM 客户端
llm_client = LLMClient()

# 测试1：豆包 API（生成思维导图）
print("\n[测试1] 豆包 API - 生成思维导图")
print("-"*80)

llm_client.switch_model("doubao")

prompt = """请为"学习Python编程"生成一个简洁的思维导图结构。
要求：
1. 返回Markdown格式的思维导图
2. 包含3-5个主要分支
3. 每个分支包含2-3个子节点
4. 使用 # ## ### 表示层级"""

print(f"提示词: {prompt[:80]}...")
print("\n正在调用豆包 API...")

try:
    response = llm_client.call_llm(prompt, max_tokens=1000, temperature=0.7, apply_vision=True)

    if response:
        print("\n✅ 豆包 API 调用成功！\n")
        print("响应内容:")
        print("-"*80)
        print(response[:500])
        print("-"*80)
    else:
        print("\n❌ 豆包 API 调用失败（返回None）")

except Exception as e:
    print(f"\n❌ 豆包 API 调用出错: {str(e)}")

# 等待一下，避免请求过快
import time
time.sleep(2)

# 测试2：讯飞 API（学习知识点）
print("\n\n[测试2] 讯飞 API - 学习知识点")
print("-"*80)

llm_client.switch_model("spark")

prompt = """请简单解释Python中的列表推导式是什么，并给出一个简单的例子。"""

print(f"提示词: {prompt}")
print("\n正在调用讯飞 API...")

try:
    response = llm_client.call_llm(prompt, max_tokens=500, temperature=0.7, apply_vision=True)

    if response:
        print("\n✅ 讯飞 API 调用成功！\n")
        print("响应内容:")
        print("-"*80)
        print(response)
        print("-"*80)
    else:
        print("\n❌ 讯飞 API 调用失败（返回None）")

except Exception as e:
    print(f"\n❌ 讯飞 API 调用出错: {str(e)}")

# 测试3：检查模型可用性
print("\n\n[测试3] 模型可用性检查")
print("-"*80)

available_models = llm_client.get_available_models()

for model_name in ["doubao", "spark", "deepseek", "openai", "mock"]:
    is_available = llm_client.config.is_model_available(model_name)
    status = "✅ 可用" if is_available else "❌ 不可用"
    print(f"  {model_name}: {status}")

    if is_available and model_name != "mock":
        config = llm_client.config.get_model_config(model_name)
        print(f"    名称: {config['name']}")
        print(f"    上下文长度: {config['context_length']}")
        print(f"    能力: {', '.join(config['capabilities'])}")

# 测试4：愿景核心集成
print("\n\n[测试4] 愿景核心集成")
print("-"*80)

print(f"愿景核心已集成: {hasattr(llm_client, 'vision_core')}")

if hasattr(llm_client, 'vision_core'):
    print(f"愿景激活度: {llm_client.vision_core.vision_activation_level:.0%}")
    print(f"当前文明阶段: {llm_client.vision_core.current_tier}")

    # 测试愿景评估
    test_content = "学习Python编程"
    alignment = llm_client.vision_core.evaluate_alignment(test_content)

    print(f"\n愿景评估测试:")
    print(f"  内容: {test_content}")
    print(f"  评分: {alignment['score']:.2f}/1.0")
    print(f"  优先级: {alignment['priority']}/10")
    print(f"  战略性: {'是' if alignment['is_strategic'] else '否'}")

# 总结
print("\n" + "="*80)
print("测试完成！")
print("="*80)

print("\n使用说明:")
print("  - 豆包 API: 用于生成思维导图")
print("  - 讯飞 API: 用于学习知识点和问答")
print("  - 愿景核心: 自动集成到所有 LLM 调用中")
print("\n详细配置请查看: API配置说明.md")
