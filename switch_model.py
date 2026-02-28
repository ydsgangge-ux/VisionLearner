#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
切换 LLM 模型工具
用于在豆包、讯飞、DeepSeek、OpenAI 之间切换
"""

import os
import sys

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  未安装 python-dotenv，请先安装: pip install python-dotenv")
    exit(1)

import sys
sys.path.append(os.path.dirname(__file__))

from perception import LLMClient, LLMConfig

def list_available_models():
    """列出所有可用模型"""
    print("=" * 60)
    print("📋 可用的 LLM 模型")
    print("=" * 60)

    client = LLMClient()
    config = LLMConfig()
    available = client.get_available_models()

    for model_id, model_info in config.supported_models.items():
        is_available = model_id in available
        status = "✅ 可用" if is_available else "❌ 不可用"

        print(f"\n【{model_id}】 {model_info['name']}")
        print(f"   状态: {status}")
        print(f"   功能: {', '.join(model_info['capabilities'])}")
        print(f"   上下文: {model_info['context_length']} tokens")

        if not is_available and model_info['requires_auth']:
            print(f"   ⚠️  需要配置 API 密钥")

    print("\n" + "=" * 60)
    print(f"当前使用的模型: {client.current_model}")
    print("=" * 60)

def switch_model(model_id):
    """切换到指定模型"""
    client = LLMClient()
    config = LLMConfig()

    # 检查模型是否存在
    if model_id not in config.supported_models:
        print(f"❌ 错误: 模型 '{model_id}' 不存在")
        list_available_models()
        return False

    # 检查模型是否可用
    if not config.is_model_available(model_id):
        print(f"❌ 错误: 模型 '{model_id}' 不可用（缺少 API 密钥）")
        print("\n请检查 .env 文件中的配置：")

        if model_id == "doubao":
            print("   DOUBAO_API_KEY=你的密钥")
        elif model_id == "spark":
            print("   SPARK_API_PASSWORD=你的密码")
            print("   SPARK_APPID=你的APPID")
            print("   SPARK_API_SECRET=你的密钥")
            print("   SPARK_API_KEY=你的Key")
        elif model_id == "deepseek":
            print("   DEEPSEEK_API_KEY=你的密钥")
        elif model_id == "openai":
            print("   OPENAI_API_KEY=你的密钥")

        return False

    # 切换模型
    old_model = client.current_model
    success = client.switch_model(model_id)

    if success:
        model_info = config.supported_models[model_id]
        print(f"✅ 模型切换成功！")
        print(f"   从: {old_model}")
        print(f"   到: {model_id} ({model_info['name']})")
        print(f"\n💡 新模型特性:")
        print(f"   - 上下文长度: {model_info['context_length']} tokens")
        print(f"   - 功能: {', '.join(model_info['capabilities'])}")
        return True
    else:
        print(f"❌ 模型切换失败")
        return False

def test_current_model():
    """测试当前模型"""
    print("=" * 60)
    print("🧪 测试当前模型")
    print("=" * 60)

    client = LLMClient()
    config = LLMConfig()
    model_info = config.supported_models[client.current_model]

    print(f"当前模型: {client.current_model} ({model_info['name']})")
    print(f"发送测试请求...\n")

    try:
        import time
        start = time.time()

        response = client.call_llm(
            prompt="请用一句话介绍你自己。",
            max_tokens=100,
            temperature=0.7
        )

        elapsed = time.time() - start

        if response:
            print(f"✅ 测试成功！")
            print(f"⏱️  响应时间: {elapsed:.2f} 秒")
            print(f"\n📥 响应内容:")
            print("-" * 50)
            print(response[:200])
            print("-" * 50)
        else:
            print(f"❌ 测试失败: 模型返回空响应")

    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

    print("=" * 60)

def main():
    """主函数"""
    print("\n🔄 LLM 模型切换工具\n")

    if len(sys.argv) < 2:
        print("用法:")
        print("  python switch_model.py list           # 列出所有可用模型")
        print("  python switch_model.py test           # 测试当前模型")
        print("  python switch_model.py <model_id>     # 切换到指定模型")
        print("\n可用模型 ID:")
        print("  doubao   - 豆包大模型（推荐用于思维导图）")
        print("  spark    - 讯飞星火（适合学习知识点）")
        print("  deepseek - DeepSeek（需要配置 API 密钥）")
        print("  openai   - OpenAI（需要配置 API 密钥）")
        print("  mock     - 模拟模型（测试用）")
        return

    command = sys.argv[1]

    if command == "list":
        list_available_models()
    elif command == "test":
        test_current_model()
    elif command in LLMConfig().supported_models:
        switch_model(command)
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'list' 查看所有可用模型")

if __name__ == "__main__":
    main()
