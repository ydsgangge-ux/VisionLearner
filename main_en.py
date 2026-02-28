#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main_en.py - English version main program
"""
English version of main program
Set environment variable APP_LANGUAGE=en to use English interface
"""

import sys
import os

# 设置语言为英语
os.environ["APP_LANGUAGE"] = "en"

# 导入原主程序
from main import *

# 覆盖帮助文本为英文
ENGLISH_HELP = """
📚 Autonomous Cognitive Learning System - English Interface
==================================================================

🎯 Goal Management:
  create <description>       - Create a learning goal
  list                      - List all goals
  select <ID>              - Select a goal

📋 Learning Planning:
  plan                      - Create learning plan
  schedule                  - Schedule learning sessions
  learn                     - Start learning

📊 Progress Monitoring:
  monitor                   - Monitor learning progress
  explore                   - Explore mindmap

🤖 Q&A System:
  ask <question>            - Ask a question
  clear_chat                - Clear chat history
  export_chat               - Export chat history
  learning_advice <topic>    - Get learning advice

🌌 Vision Core:
  vision                    - Show vision core status
  vision_manifesto           - Show vision manifesto
  vision_decisions           - Show ethical decision records

⚙️ System Management:
  status                    - Show system status
  save                      - Save system state
  load                      - Load system state
  config                    - Show configuration
  stats                     - Show statistics
  help                      - Show this help message
  quit / exit              - Exit system

🌍 Language Settings:
  lang zh                  - Switch to Chinese
  lang en                  - Switch to English

💡 Tips:
  - Use 'create' to start a new learning goal
  - Use 'plan' to generate a learning mindmap
  - Use 'ask' to interact with the AI assistant
  - Use 'quit' to save and exit

==================================================================
"""

# 重写主循环中的帮助输出
def run_english_interface():
    """运行英语界面"""
    from i18n import I18n, Language
    
    # 初始化英语翻译
    i18n = I18n(language=Language.ENGLISH)
    
    # 显示欢迎信息
    print("\n" + "=" * 70)
    print("🌟 Welcome to Autonomous Cognitive Learning System")
    print("=" * 70)
    print("🌍 Interface Language: English")
    print(f"🧠 Vision Core: {i18n.t('vision_loaded')}")
    print("=" * 70)
    
    # 初始化系统协调器
    coordinator = SystemCoordinator()
    
    print(f"\n{i18n.t('system_status')}:")
    print(f"   Available Models: {', '.join(coordinator.perception_manager.get_available_models())}")
    print(f"   Current Model: {coordinator.perception_manager.llm_client.current_model}")
    print()
    
    # 主循环
    while True:
        try:
            # 显示提示符
            command = input(i18n.t('enter_command')).strip()
            
            if not command:
                continue
            
            # 解析命令
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # 命令处理
            if cmd == 'help':
                print(ENGLISH_HELP)
            
            elif cmd == 'lang':
                if args == 'zh':
                    print("🔄 Switching to Chinese...")
                    print("Please restart the program or run: python main.py")
                    break
                elif args == 'en':
                    print("✅ Already in English mode")
                else:
                    print("❌ Invalid language. Use: lang zh or lang en")
            
            elif cmd in ['quit', 'exit']:
                print("\n💾 Saving system state...")
                coordinator.save_system_state()
                print("✅ System state saved")
                print("\n👋 Thank you for using Autonomous Cognitive Learning System!")
                print("   See you next time!")
                break
            
            elif cmd == 'create':
                if args:
                    goal = coordinator.create_learning_goal(args)
                    if goal:
                        # 询问是否生成思维导图
                        gen = input(f"\n{i18n.t('ask_generate')}{i18n.t('yes_no')}").strip().lower()
                        if gen == 'y' or gen == '':
                            coordinator.generate_mindmap_for_goal(goal)
                else:
                    print("❌ Usage: create <description>")
            
            elif cmd == 'list':
                coordinator.list_goals()
            
            elif cmd == 'select':
                if args:
                    coordinator.select_goal(args)
                else:
                    print("❌ Usage: select <ID>")
            
            elif cmd == 'plan':
                if coordinator.current_goal:
                    coordinator.create_learning_plan_for_goal(coordinator.current_goal)
                else:
                    print("❌ Please select a goal first")
            
            elif cmd == 'ask':
                if args:
                    answer = coordinator.qa_system.ask(args)
                    print(f"\n💬 {i18n.t('answer')}:")
                    print("-" * 70)
                    print(answer.get('response', 'No response'))
                    print("-" * 70)
                    print(f"📊 {i18n.t('confidence')}: {answer.get('confidence', 0):.1%}")
                    print(f"⏱️  {i18n.t('processing_time')}: {answer.get('processing_time', 0)}ms")
                else:
                    print("❌ Usage: ask <question>")
            
            elif cmd == 'clear_chat':
                coordinator.qa_system.clear_history()
                print("✅ Chat history cleared")
            
            elif cmd == 'export_chat':
                export_file = coordinator.qa_system.export_conversation()
                if export_file:
                    print(f"✅ Chat history exported: {export_file}")
            
            elif cmd == 'learning_advice':
                if args:
                    advice = coordinator.learning_advisor.provide_learning_advice(args)
                    if advice:
                        print(f"\n📚 {i18n.t('learning_advice')} for '{args}':")
                        print("-" * 70)
                        print(advice)
                        print("-" * 70)
                else:
                    print("❌ Usage: learning_advice <topic>")
            
            elif cmd == 'vision':
                print("\n🌌 Vision Core Status:")
                print("-" * 50)
                print(coordinator.vision_core.get_status())
                print("-" * 50)
            
            elif cmd == 'status':
                coordinator.show_status()
            
            elif cmd == 'save':
                coordinator.save_system_state()
            
            elif cmd == 'stats':
                coordinator.show_statistics()
            
            else:
                print(f"❌ {i18n.t('unknown_command', command=cmd)}")
                print("   Type 'help' to see available commands")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            print("💾 Saving system state...")
            coordinator.save_system_state()
            print("✅ Saved successfully")
            print("👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_english_interface()
