#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试豆包 API 连接
"""

import os
import time

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  未安装 python-dotenv，请先安装: pip install python-dotenv")
    exit(1)

import sys
sys.path.append(os.path.dirname(__file__))

from perception import LLMClient

def test_doubao_connection():
    """测试豆包 API 连接"""
    print("=" * 60)
    print("🧪 测试豆包 API 连接")
    print("=" * 60)

    # 检查 API Key
    api_key = os.getenv("DOUBAO_API_KEY", "")
    if not api_key:
        print("❌ 未找到 DOUBAO_API_KEY 环境变量")
        print("   请在 .env 文件中配置 API Key")
        return False

    print(f"✅ API Key 已配置: {api_key[:10]}...{api_key[-6:]}")

    # 创建 LLM 客户端
    llm_client = LLMClient()

    # 测试简单请求
    test_prompt = "请用一句话介绍Python编程语言。"

    print(f"\n📤 发送测试请求...")
    print(f"   提示词: {test_prompt}")

    start_time = time.time()

    try:
        response = llm_client.call_llm(
            prompt=test_prompt,
            max_tokens=100,
            temperature=0.7
        )

        elapsed_time = time.time() - start_time

        if response:
            print(f"\n✅ API 连接成功！")
            print(f"⏱️  响应时间: {elapsed_time:.2f} 秒")
            print(f"\n📥 响应内容:")
            print("-" * 50)
            print(response[:200])
            print("-" * 50)

            # 建议
            if elapsed_time > 30:
                print(f"\n💡 建议: 响应时间较长（{elapsed_time:.2f}秒），建议增加超时时间")
                recommended_timeout = int(elapsed_time * 2)
                print(f"   建议超时时间: {recommended_timeout} 秒")
            else:
                print(f"\n💡 响应时间正常（{elapsed_time:.2f}秒）")

            return True
        else:
            print(f"\n❌ API 返回空响应")
            print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
            return False

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ API 连接失败")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
        print(f"❌ 错误信息: {str(e)}")
        return False

def test_mindmap_generation():
    """测试思维导图生成"""
    print("\n" + "=" * 60)
    print("🧠 测试思维导图生成（更长的请求）")
    print("=" * 60)

    llm_client = LLMClient()

    mindmap_prompt = """请为"学习Python编程"生成一个简单的思维导图结构，包含3-5个主要分支。"""

    print(f"\n📤 发送思维导图请求...")
    print(f"   提示词长度: {len(mindmap_prompt)} 字符")

    start_time = time.time()

    try:
        response = llm_client.call_llm(
            prompt=mindmap_prompt,
            system_prompt="你是思维导图专家，擅长创建知识结构。",
            max_tokens=800,
            temperature=0.3
        )

        elapsed_time = time.time() - start_time

        if response:
            print(f"\n✅ 思维导图生成成功！")
            print(f"⏱️  响应时间: {elapsed_time:.2f} 秒")
            print(f"📝 响应长度: {len(response)} 字符")

            # 计算建议的超时时间
            recommended_timeout = max(120, int(elapsed_time * 2.5))  # 至少120秒，或响应时间的2.5倍
            print(f"\n💡 建议超时时间: {recommended_timeout} 秒")

            return True, elapsed_time, recommended_timeout
        else:
            print(f"\n❌ 思维导图生成失败")
            print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
            return False, elapsed_time, None

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 思维导图生成异常")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
        print(f"❌ 错误信息: {str(e)}")
        return False, elapsed_time, None

if __name__ == "__main__":
    # 测试1: 简单连接测试
    success1 = test_doubao_connection()

    # 测试2: 思维导图生成测试
    success2, elapsed, recommended = test_mindmap_generation()

    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    if success1:
        print("✅ 简单连接测试: 通过")
    else:
        print("❌ 简单连接测试: 失败")

    if success2:
        print("✅ 思维导图生成: 通过")
        print(f"⏱️  实际响应时间: {elapsed:.2f} 秒")
        if recommended:
            print(f"💡 建议超时配置: {recommended} 秒")
    else:
        print("❌ 思维导图生成: 失败")

    print("=" * 60)
