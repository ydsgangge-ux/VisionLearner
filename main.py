# main.py - 主系统与交互界面（完整版）
"""
第5段：主系统与交互界面
功能：整合所有模块，提供用户交互界面，管理系统运行
特点：模块化设计，支持命令行交互，数据持久化
创新：思维导图探索器，可视化界面，系统协调器
"""

import json
import os
import sys
import time
import random
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import asdict
from collections import defaultdict, deque

# 导入前面几段的模块
from foundation import (
    MindMapNode, KnowledgeNode, LearningGoal, LearningLevel, 
    KnowledgeType, GoalScale, LearningStrategy, MindMapStyle,
    ProgressGranularity, generate_id, FoundationManager,
    TimeEstimationModel, create_mindmap_tree, mindmap_to_dict_tree
)

from perception import (
    MindMapGenerator, MultimodalRecognizer, 
    KnowledgeExtractor, ActiveLearningTrigger,
    PerceptionManager
)

from explorer import (
    IntelligentQuestionEngine, MindMapVisualizer,
    KnowledgeNetworkBuilder, LearningPathGenerator,
    ExplorerManager
)

from planner import (
    HierarchicalLearningAllocator, MindMapDrivenPlanner,
    AdaptiveScheduler, ProgressMonitor
)

# 导入愿景核心
from vision_core import get_vision_core

# 导入上下文问答系统
from qa_context import (
    ContextAwareQASystem, DialogueTurn, ConversationContext, LearningAdvisor
)

# ========== 系统协调器 ==========

class SystemCoordinator:
    """
    系统协调器 - 整合所有模块，管理学习流程
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # ========== 愿景核心集成：初始化思想钢印 ==========
        self.vision_core = get_vision_core()
        
        # 初始化所有管理器
        self.foundation_manager = FoundationManager()
        self.perception_manager = PerceptionManager()
        self.explorer_manager = ExplorerManager()
        
        # 初始化规划模块
        self.allocator = HierarchicalLearningAllocator()
        self.planner = MindMapDrivenPlanner()
        self.scheduler = AdaptiveScheduler()
        self.monitor = ProgressMonitor()

        # ========== 初始化上下文问答系统 ==========
        from perception import LLMClient
        llm_client = LLMClient()
        self.qa_system = ContextAwareQASystem(model_provider=llm_client)
        self.learning_advisor = LearningAdvisor(qa_system=self.qa_system)

        # 数据存储
        self.data_manager = DataStorageManager()
        
        # 系统状态
        self.active_goals: Dict[str, LearningGoal] = {}
        self.completed_goals: Dict[str, LearningGoal] = {}
        self.pending_goals: Dict[str, LearningGoal] = {}
        
        # 当前会话
        self.current_goal: Optional[LearningGoal] = None
        self.current_mindmap: Optional[MindMapNode] = None
        self.current_plan: Optional[Dict[str, Any]] = None
        self.current_schedule: Optional[Dict[str, Any]] = None
        
        # 学习历史
        self.learning_history: List[Dict[str, Any]] = []
        
        # 性能统计
        self.stats = {
            "total_goals_created": 0,
            "total_goals_completed": 0,
            "total_learning_time_minutes": 0,
            "total_knowledge_nodes": 0,
            "avg_completion_rate": 0.0,
            "system_start_time": datetime.now().isoformat()
        }
        
        # 显示愿景宣言（首次启动）
        if not self.vision_core.manifesto_shown:
            print("\n" + "="*70)
            print("🌌 欢迎来到自主认知学习系统")
            print("="*70)
            print(self.vision_core.get_vision_manifesto("brief"))
            print("="*70 + "\n")
            self.vision_core.manifesto_shown = True
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "system": {
                "name": "自主认知学习系统",
                "version": "2.0.0",
                "auto_save_interval": 300,  # 自动保存间隔（秒）
                "max_history_size": 1000,
                "log_level": "INFO"
            },
            "learning": {
                "default_strategy": "mindmap_driven",
                "max_concurrent_goals": 3,
                "min_learning_time_per_day": 30,  # 分钟
                "max_learning_time_per_day": 240  # 分钟
            },
            "mindmap": {
                "default_depth": 3,
                "default_style": "balanced",
                "min_node_importance": 0.3,
                "max_children_per_node": 7
            },
            "storage": {
                "data_directory": "./learning_data",
                "backup_enabled": True,
                "backup_interval": 86400,  # 每天备份一次
                "compression_enabled": False
            },
            "ai": {
                "llm_provider": "deepseek",  # deepseek, doubao, openai
                "api_key": "",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # 合并配置（深度合并）
                def deep_merge(default, override):
                    for key, value in override.items():
                        if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                            deep_merge(default[key], value)
                        else:
                            default[key] = value
                
                deep_merge(default_config, loaded_config)
            
            # 创建数据目录
            data_dir = default_config["storage"]["data_directory"]
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
        except Exception as e:
            print(f"⚠️ 加载配置失败: {str(e)}，使用默认配置")
        
        return default_config
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"❌ 保存配置失败: {str(e)}")
    
    def create_learning_goal(self, description: str) -> LearningGoal:
        """创建学习目标"""
        print(f"🎯 创建学习目标: {description}")
        
        # 使用基础管理器创建目标
        goal = self.foundation_manager.create_learning_goal(description)
        
        # 分析目标特性
        analyzer = self.foundation_manager.get_goal_analyzer()
        analysis = analyzer.analyze(description)
        
        # 更新目标属性
        goal.target_knowledge_count = analysis.get("estimated_items", 1)
        goal.complexity = 0.5 if analysis.get("complexity") == "medium" else \
                         0.3 if analysis.get("complexity") == "low" else 0.7
        
        # 添加到待处理目标
        self.pending_goals[goal.id] = goal
        
        # 更新统计
        self.stats["total_goals_created"] += 1
        
        print(f"✅ 目标创建成功: {goal.description} (ID: {goal.id})")
        print(f"   规模: {goal.scale.value}, 预估知识点: {goal.target_knowledge_count}")
        
        return goal
    
    def generate_mindmap_for_goal(self, goal: LearningGoal) -> Optional[MindMapNode]:
        """为学习目标生成思维导图"""
        print(f"🧠 为'{goal.description}'生成思维导图...")

        # 检查是否已有思维导图
        if goal.mindmap_root_id and goal.mindmap_root_id in self.data_manager.mindmaps:
            print(f"📂 使用现有思维导图")
            return self.data_manager.mindmaps[goal.mindmap_root_id]

        try:
            # 使用感知管理器生成思维导图
            mindmap = self.perception_manager.generate_mindmap_for_goal(goal)

            if mindmap:
                # 更新目标
                goal.set_mindmap_root(mindmap.id)

                # 保存思维导图
                self.data_manager.save_mindmap(mindmap)

                # 构建节点映射
                node_map = self._build_mindmap_node_map(mindmap)

                # 显示文本版思维导图
                print(f"\n📋 思维导图内容:")
                print("=" * 50)
                self._display_mindmap_text(mindmap, node_map)
                print("=" * 50)

                # 可选：生成PNG可视化（默认关闭）
                if self.config["system"].get("enable_visualization", False):
                    visualizer = MindMapVisualizer()
                    visualization_path = visualizer.visualize_mindmap(
                        mindmap_root=mindmap,
                        node_map=node_map,
                        output_format="png"
                    )

                    if visualization_path:
                        print(f"📊 可视化图生成成功: {visualization_path}")

                print(f"✅ 思维导图生成成功: {len(node_map)}个节点")
                return mindmap
            else:
                print("❌ 思维导图生成失败")
                return None

        except Exception as e:
            print(f"❌ 思维导图生成异常: {str(e)}")
            return None
    
    def _build_mindmap_node_map(self, root_node: MindMapNode) -> Dict[str, MindMapNode]:
        """构建思维导图节点映射"""
        node_map = {}

        def collect_nodes(node: MindMapNode):
            node_map[node.id] = node
            # 实际中需要递归收集所有子节点
            # 这里简化处理

        collect_nodes(root_node)
        return node_map

    def _display_mindmap_text(self, root_node: MindMapNode, node_map: Dict[str, MindMapNode]) -> None:
        """显示文本版思维导图"""
        def print_node(node: MindMapNode, indent: int = 0):
            prefix = "  " * indent
            node_symbol = "├─" if indent > 0 else "●"
            print(f"{prefix}{node_symbol} {node.title}")
            if node.description and indent == 0:
                print(f"{prefix}   {node.description[:80]}...")

            # 递归显示子节点
            for child_id in node.children_ids:
                if child_id in node_map:
                    print_node(node_map[child_id], indent + 1)

        print_node(root_node)
    
    def create_learning_plan_for_goal(self, goal: LearningGoal) -> Optional[Dict[str, Any]]:
        """为学习目标创建学习计划"""
        print(f"📋 为'{goal.description}'创建学习计划...")
        
        # 检查是否需要思维导图
        if not goal.mindmap_root_id:
            print("⚠️ 目标没有思维导图，先创建思维导图")
            mindmap = self.generate_mindmap_for_goal(goal)
            if not mindmap:
                print("❌ 无法创建学习计划：思维导图生成失败")
                return None
        
        # 获取思维导图
        mindmap = self.data_manager.mindmaps.get(goal.mindmap_root_id)
        if not mindmap:
            print("❌ 无法找到思维导图")
            return None
        
        # 构建节点映射
        node_map = self._build_mindmap_node_map(mindmap)
        
        # 创建分配计划
        allocation_plan = self.allocator.allocate_by_mindmap(
            goal=goal,
            mindmap_root=mindmap,
            node_map=node_map,
            strategy=self.config["learning"]["default_strategy"],
            available_time_minutes=self.config["learning"]["max_learning_time_per_day"] * 7  # 一周时间
        )
        
        # 创建详细学习计划
        learning_plan = self.planner.create_learning_plan(
            goal=goal,
            mindmap_root=mindmap,
            node_map=node_map,
            allocation_plan=allocation_plan
        )
        
        # 保存计划
        self.data_manager.save_learning_plan(goal.id, learning_plan)
        
        # 更新当前状态
        self.current_goal = goal
        self.current_mindmap = mindmap
        self.current_plan = learning_plan
        
        # 将目标从待处理移动到活动
        if goal.id in self.pending_goals:
            del self.pending_goals[goal.id]
        self.active_goals[goal.id] = goal
        
        print(f"✅ 学习计划创建成功: {len(learning_plan.get('milestones', []))}个里程碑")
        return learning_plan
    
    def schedule_learning_sessions(self) -> Optional[Dict[str, Any]]:
        """调度学习会话"""
        if not self.current_goal or not self.current_plan:
            print("❌ 没有激活的目标或计划")
            return None
        
        print(f"⏰ 为'{self.current_goal.description}'调度学习会话...")
        
        # 创建当前上下文
        current_context = self._create_current_context()
        
        # 调度学习会话
        schedule = self.scheduler.schedule_learning_sessions(
            learning_plan=self.current_plan,
            current_context=current_context,
            strategy="adaptive_schedule"
        )
        
        # 保存调度
        self.current_schedule = schedule
        self.data_manager.save_schedule(self.current_goal.id, schedule)
        
        print(f"✅ 学习会话调度成功: {len(schedule.get('scheduled_sessions', []))}个会话")
        return schedule
    
    def _create_current_context(self) -> Dict[str, Any]:
        """创建当前上下文"""
        current_hour = datetime.now().hour
        current_weekday = datetime.now().weekday()
        
        # 简化上下文创建
        context = {
            "available_minutes": 120,  # 默认120分钟
            "energy_level": 0.7,  # 默认精力水平
            "focus_level": 0.6,  # 默认专注度
            "distractions": [],
            "current_time": {
                "hour": current_hour,
                "weekday": current_weekday
            }
        }
        
        return context
    
    def execute_learning_session(self, session_id: str = None) -> Dict[str, Any]:
        """执行学习会话"""
        if not self.current_goal or not self.current_schedule:
            print("❌ 没有激活的调度")
            return {"success": False, "error": "没有激活的调度"}
        
        print(f"🚀 执行学习会话...")
        
        # 如果没有指定会话ID，使用第一个
        sessions = self.current_schedule.get("scheduled_sessions", [])
        if not sessions:
            print("❌ 没有可执行的学习会话")
            return {"success": False, "error": "没有可执行的学习会话"}
        
        if session_id is None:
            session = sessions[0]
        else:
            session = next((s for s in sessions if s.get("session_id") == session_id), None)
            if not session:
                print(f"❌ 找不到会话 {session_id}")
                return {"success": False, "error": f"找不到会话 {session_id}"}
        
        # 执行会话
        result = self._execute_single_session(session)
        
        # 记录学习历史
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "goal_id": self.current_goal.id,
            "session_id": session.get("session_id"),
            "duration_minutes": session.get("duration_minutes", 0),
            "result": result
        }
        self.learning_history.append(history_entry)
        
        # 更新统计
        self.stats["total_learning_time_minutes"] += session.get("duration_minutes", 0)
        
        # 检查是否需要重新调度
        if result.get("completed", False):
            # 从调度中移除已完成的会话
            sessions = [s for s in sessions if s.get("session_id") != session.get("session_id")]
            self.current_schedule["scheduled_sessions"] = sessions
            
            # 如果所有会话都完成了，重新调度
            if not sessions:
                print("🎉 所有会话完成，重新调度...")
                self.schedule_learning_sessions()
        
        return result
    
    def _execute_single_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个学习会话"""
        print(f"📚 执行会话: {session.get('session_id', '未知')}")
        print(f"   类型: {session.get('type', '未知')}")
        print(f"   时长: {session.get('duration_minutes', 0)}分钟")
        print(f"   强度: {session.get('intensity', '未知')}")
        
        # 模拟学习过程
        session_type = session.get("type", "general")
        duration = session.get("duration_minutes", 30)
        
        # 根据会话类型执行不同的学习活动
        if session_type == "deep_learning":
            activities = ["深度阅读", "概念理解", "思考分析"]
        elif session_type == "practice":
            activities = ["练习题目", "实践操作", "技能训练"]
        elif session_type == "review":
            activities = ["复习笔记", "自我测试", "知识回顾"]
        else:
            activities = ["综合学习", "知识获取", "应用练习"]
        
        # 模拟学习过程
        print(f"   活动: {', '.join(activities)}")
        print(f"⏳ 学习中... (模拟{duration}分钟)")
        
        # 在实际应用中，这里会有真正的学习逻辑
        # 这里模拟学习过程
        time.sleep(min(duration / 10, 2))  # 简化模拟，最多等待2秒
        
        # 生成学习结果
        result = {
            "success": True,
            "session_id": session.get("session_id"),
            "duration_minutes": duration,
            "activities_completed": activities,
            "knowledge_gained": random.randint(1, 5),
            "mastery_increase": random.uniform(0.1, 0.3),
            "completed": True,
            "notes": "会话执行成功"
        }
        
        print(f"✅ 会话完成: 获得{result['knowledge_gained']}个知识点")
        return result
    
    def monitor_progress(self) -> Dict[str, Any]:
        """监控进度"""
        if not self.current_goal:
            print("❌ 没有激活的目标")
            return {"success": False, "error": "没有激活的目标"}
        
        print(f"📈 监控进度: {self.current_goal.description}")
        
        # 创建进度数据
        progress_data = {
            "overall_progress": self.current_goal.overall_progress,
            "mastery_level": 0.6,  # 简化
            "engagement_level": 0.7,
            "active_days": len(set(h["timestamp"][:10] for h in self.learning_history if h["goal_id"] == self.current_goal.id)),
            "recent_sessions": [h for h in self.learning_history[-5:] if h["goal_id"] == self.current_goal.id],
            "daily_progress": self._calculate_daily_progress()
        }
        
        # 监控目标进度
        monitoring_report = self.monitor.monitor_goal_progress(
            goal=self.current_goal,
            progress_data=progress_data,
            monitoring_strategy="adaptive"
        )
        
        # 如果有思维导图，监控思维导图进度
        if self.current_goal.mindmap_root_id:
            mindmap = self.data_manager.mindmaps.get(self.current_goal.mindmap_root_id)
            if mindmap:
                node_map = self._build_mindmap_node_map(mindmap)
                
                mindmap_report = self.monitor.monitor_mindmap_progress(
                    goal=self.current_goal,
                    mindmap_root=mindmap,
                    node_map=node_map,
                    progress_data=progress_data
                )
                
                monitoring_report["mindmap_report"] = mindmap_report
        
        # 检查是否需要调整计划
        alerts = monitoring_report.get("alerts", [])
        if alerts:
            print(f"⚠️ 发现{alerts}个预警")
            
            # 如果有严重预警，建议调整计划
            high_severity_alerts = [a for a in alerts if a.get("severity") == "high"]
            if high_severity_alerts:
                print("🔄 检测到严重预警，建议调整学习计划")
                self.adjust_plan_based_on_progress()
        
        print(f"✅ 进度监控完成: 当前进度{self.current_goal.overall_progress:.1%}")
        return monitoring_report
    
    def _calculate_daily_progress(self) -> Dict[str, float]:
        """计算每日进度"""
        daily_progress = {}
        
        if not self.current_goal:
            return daily_progress
        
        # 统计最近7天的学习情况
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            # 查找当天的学习历史
            daily_sessions = [h for h in self.learning_history 
                            if h["goal_id"] == self.current_goal.id and 
                            h["timestamp"][:10] == date]
            
            if daily_sessions:
                # 计算当天进度
                total_duration = sum(s.get("duration_minutes", 0) for s in daily_sessions)
                progress = min(total_duration / 120, 1.0)  # 假设120分钟为满分
                daily_progress[date] = progress
        
        return daily_progress
    
    def adjust_plan_based_on_progress(self) -> Optional[Dict[str, Any]]:
        """基于进度调整计划"""
        if not self.current_goal or not self.current_plan:
            print("❌ 没有激活的目标或计划")
            return None
        
        print(f"🔄 基于进度调整学习计划...")
        
        # 创建进度数据
        progress_data = {
            "overall_progress": self.current_goal.overall_progress,
            "mastered_nodes": [],  # 实际中需要从数据库获取
            "struggling_nodes": [],
            "learning_speed": 1.0,
            "engagement_level": 0.7
        }
        
        # 调整分配计划
        if self.current_plan.get("allocation_plan"):
            adjusted_allocation = self.allocator.adjust_allocation(
                original_plan=self.current_plan["allocation_plan"],
                progress_data=progress_data,
                node_map=self._build_mindmap_node_map(self.current_mindmap) if self.current_mindmap else {}
            )
            self.current_plan["allocation_plan"] = adjusted_allocation
        
        # 调整学习计划
        adjusted_plan = self.planner.adjust_plan_based_on_progress(
            original_plan=self.current_plan,
            progress_data=progress_data,
            learning_history=self.learning_history
        )
        
        # 保存调整后的计划
        self.current_plan = adjusted_plan
        self.data_manager.save_learning_plan(self.current_goal.id, adjusted_plan)
        
        # 重新调度
        self.schedule_learning_sessions()
        
        print(f"✅ 学习计划调整完成")
        return adjusted_plan
    
    def explore_knowledge(self, topic: str = None) -> Dict[str, Any]:
        """探索知识"""
        if not topic and self.current_goal:
            topic = self.current_goal.description
        
        if not topic:
            print("❌ 没有指定探索主题")
            return {"success": False, "error": "没有指定探索主题"}
        
        print(f"🔍 探索知识: {topic}")
        
        # 使用探索管理器
        explorer = self.explorer_manager
        
        # 生成问题
        questions = explorer.generate_questions(topic, question_count=5)
        
        # 构建知识网络
        knowledge_network = explorer.build_knowledge_network(topic, depth=2)
        
        # 生成学习路径
        learning_paths = explorer.generate_learning_paths(topic, path_count=2)
        
        # 可视化（如果启用）
        if self.config["system"].get("enable_visualization", True):
            visualizer = MindMapVisualizer()
            visualizer.visualize_network(knowledge_network)
        
        result = {
            "topic": topic,
            "questions": questions,
            "knowledge_network": knowledge_network,
            "learning_paths": learning_paths
        }
        
        print(f"✅ 知识探索完成: 生成{len(questions)}个问题，{len(learning_paths)}条学习路径")
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            "system": {
                "name": self.config["system"]["name"],
                "version": self.config["system"]["version"],
                "uptime": self._calculate_uptime(),
                "status": "running"
            },
            "goals": {
                "total": self.stats["total_goals_created"],
                "active": len(self.active_goals),
                "pending": len(self.pending_goals),
                "completed": len(self.completed_goals)
            },
            "learning": {
                "total_time_minutes": self.stats["total_learning_time_minutes"],
                "current_goal": self.current_goal.description if self.current_goal else "无",
                "current_progress": self.current_goal.overall_progress if self.current_goal else 0.0
            },
            "storage": {
                "goals_count": len(self.data_manager.goals),
                "mindmaps_count": len(self.data_manager.mindmaps),
                "plans_count": len(self.data_manager.learning_plans)
            }
        }
        
        return status
    
    def _calculate_uptime(self) -> str:
        """计算系统运行时间"""
        try:
            start_time = datetime.fromisoformat(self.stats["system_start_time"])
            uptime = datetime.now() - start_time
            
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            if days > 0:
                return f"{days}天{hours}小时{minutes}分钟"
            elif hours > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{minutes}分钟"
        except:
            return "未知"
    
    def save_system_state(self) -> None:
        """保存系统状态"""
        print("💾 保存系统状态...")
        
        try:
            # 保存所有数据
            self.data_manager.save_all_data()
            
            # 保存系统状态
            system_state = {
                "stats": self.stats,
                "active_goals": {gid: asdict(goal) for gid, goal in self.active_goals.items()},
                "pending_goals": {gid: asdict(goal) for gid, goal in self.pending_goals.items()},
                "completed_goals": {gid: asdict(goal) for gid, goal in self.completed_goals.items()},
                "current_goal_id": self.current_goal.id if self.current_goal else None,
                "learning_history": self.learning_history[-100:],  # 保存最近100条
                "saved_at": datetime.now().isoformat()
            }
            
            state_file = os.path.join(self.config["storage"]["data_directory"], "system_state.json")
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(system_state, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 系统状态已保存到 {state_file}")
            
        except Exception as e:
            print(f"❌ 保存系统状态失败: {str(e)}")
    
    def load_system_state(self) -> bool:
        """加载系统状态"""
        print("📂 加载系统状态...")
        
        try:
            state_file = os.path.join(self.config["storage"]["data_directory"], "system_state.json")
            
            if not os.path.exists(state_file):
                print("⚠️ 没有找到系统状态文件")
                return False
            
            with open(state_file, 'r', encoding='utf-8') as f:
                system_state = json.load(f)
            
            # 加载统计信息
            self.stats.update(system_state.get("stats", {}))
            
            # 加载目标
            for goal_data in system_state.get("active_goals", {}).values():
                goal = LearningGoal.from_dict(goal_data)
                self.active_goals[goal.id] = goal
            
            for goal_data in system_state.get("pending_goals", {}).values():
                goal = LearningGoal.from_dict(goal_data)
                self.pending_goals[goal.id] = goal
            
            for goal_data in system_state.get("completed_goals", {}).values():
                goal = LearningGoal.from_dict(goal_data)
                self.completed_goals[goal.id] = goal
            
            # 设置当前目标
            current_goal_id = system_state.get("current_goal_id")
            if current_goal_id:
                self.current_goal = self.active_goals.get(current_goal_id)
                
                # 加载当前计划
                if self.current_goal:
                    self.current_plan = self.data_manager.load_learning_plan(self.current_goal.id)
            
            # 加载学习历史
            self.learning_history = system_state.get("learning_history", [])
            
            print(f"✅ 系统状态加载成功: {len(self.active_goals)}个活动目标")
            return True
            
        except Exception as e:
            print(f"❌ 加载系统状态失败: {str(e)}")
            return False
    
    def run_auto_pilot(self, goal_description: str = None) -> Dict[str, Any]:
        """运行自动驾驶模式 - 自动完成整个学习流程"""
        print("🤖 启动自动驾驶模式...")
        
        results = {
            "steps": [],
            "success": False,
            "error": None
        }
        
        try:
            # 步骤1: 创建目标
            if goal_description:
                goal = self.create_learning_goal(goal_description)
                results["steps"].append({"step": "create_goal", "success": True, "goal_id": goal.id})
            elif self.current_goal:
                goal = self.current_goal
                results["steps"].append({"step": "use_existing_goal", "success": True, "goal_id": goal.id})
            else:
                results["success"] = False
                results["error"] = "没有指定学习目标"
                return results
            
            # 步骤2: 生成思维导图
            mindmap = self.generate_mindmap_for_goal(goal)
            if mindmap:
                results["steps"].append({"step": "generate_mindmap", "success": True, "node_count": 1})
            else:
                results["steps"].append({"step": "generate_mindmap", "success": False})
                results["success"] = False
                results["error"] = "思维导图生成失败"
                return results
            
            # 步骤3: 创建学习计划
            plan = self.create_learning_plan_for_goal(goal)
            if plan:
                results["steps"].append({"step": "create_plan", "success": True, "milestone_count": len(plan.get("milestones", []))})
            else:
                results["steps"].append({"step": "create_plan", "success": False})
                results["success"] = False
                results["error"] = "学习计划创建失败"
                return results
            
            # 步骤4: 调度学习会话
            schedule = self.schedule_learning_sessions()
            if schedule:
                results["steps"].append({"step": "schedule_sessions", "success": True, "session_count": len(schedule.get("scheduled_sessions", []))})
            else:
                results["steps"].append({"step": "schedule_sessions", "success": False})
                results["success"] = False
                results["error"] = "学习会话调度失败"
                return results
            
            # 步骤5: 执行学习会话（模拟3个会话）
            for i in range(3):
                result = self.execute_learning_session()
                if result.get("success"):
                    results["steps"].append({"step": f"execute_session_{i+1}", "success": True})
                else:
                    results["steps"].append({"step": f"execute_session_{i+1}", "success": False})
            
            # 步骤6: 监控进度
            monitoring_result = self.monitor_progress()
            if monitoring_result:
                results["steps"].append({"step": "monitor_progress", "success": True})
            else:
                results["steps"].append({"step": "monitor_progress", "success": False})
            
            # 保存系统状态
            self.save_system_state()
            
            results["success"] = True
            results["final_progress"] = goal.overall_progress
            results["total_steps"] = len(results["steps"])
            
            print(f"✅ 自动驾驶模式完成: {results['total_steps']}个步骤，最终进度{goal.overall_progress:.1%}")
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            print(f"❌ 自动驾驶模式失败: {str(e)}")
        
        return results

# ========== 数据存储管理器 ==========

class DataStorageManager:
    """数据存储管理器"""
    
    def __init__(self, data_directory: str = "./learning_data"):
        self.data_directory = data_directory
        
        # 创建数据目录
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        
        # 数据存储
        self.goals: Dict[str, LearningGoal] = {}
        self.mindmaps: Dict[str, MindMapNode] = {}
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.learning_plans: Dict[str, Dict[str, Any]] = {}
        self.schedules: Dict[str, Dict[str, Any]] = {}
        self.progress_data: Dict[str, Dict[str, Any]] = {}
        
        # 子目录
        self.subdirectories = {
            "goals": "goals",
            "mindmaps": "mindmaps",
            "knowledge": "knowledge",
            "plans": "plans",
            "schedules": "schedules",
            "progress": "progress"
        }
        
        # 创建所有子目录
        for subdir in self.subdirectories.values():
            path = os.path.join(self.data_directory, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
        
        # 加载现有数据
        self.load_all_data()
    
    def save_goal(self, goal: LearningGoal) -> None:
        """保存学习目标"""
        try:
            self.goals[goal.id] = goal
            
            # 保存到文件
            goal_dir = os.path.join(self.data_directory, self.subdirectories["goals"])
            goal_file = os.path.join(goal_dir, f"{goal.id}.json")
            
            goal_dict = goal.to_dict()
            with open(goal_file, 'w', encoding='utf-8') as f:
                json.dump(goal_dict, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 保存目标失败: {str(e)}")
    
    def load_goal(self, goal_id: str) -> Optional[LearningGoal]:
        """加载学习目标"""
        try:
            # 先从内存中查找
            if goal_id in self.goals:
                return self.goals[goal_id]
            
            # 从文件加载
            goal_dir = os.path.join(self.data_directory, self.subdirectories["goals"])
            goal_file = os.path.join(goal_dir, f"{goal_id}.json")
            
            if os.path.exists(goal_file):
                with open(goal_file, 'r', encoding='utf-8') as f:
                    goal_dict = json.load(f)
                
                goal = LearningGoal.from_dict(goal_dict)
                self.goals[goal_id] = goal
                return goal
            
        except Exception as e:
            print(f"❌ 加载目标失败: {str(e)}")
        
        return None
    
    def save_mindmap(self, mindmap: MindMapNode) -> None:
        """保存思维导图"""
        try:
            self.mindmaps[mindmap.id] = mindmap
            
            # 保存到文件
            mindmap_dir = os.path.join(self.data_directory, self.subdirectories["mindmaps"])
            mindmap_file = os.path.join(mindmap_dir, f"{mindmap.id}.json")
            
            mindmap_dict = mindmap.to_dict()
            with open(mindmap_file, 'w', encoding='utf-8') as f:
                json.dump(mindmap_dict, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 保存思维导图失败: {str(e)}")
    
    def load_mindmap(self, mindmap_id: str) -> Optional[MindMapNode]:
        """加载思维导图"""
        try:
            # 先从内存中查找
            if mindmap_id in self.mindmaps:
                return self.mindmaps[mindmap_id]
            
            # 从文件加载
            mindmap_dir = os.path.join(self.data_directory, self.subdirectories["mindmaps"])
            mindmap_file = os.path.join(mindmap_dir, f"{mindmap_id}.json")
            
            if os.path.exists(mindmap_file):
                with open(mindmap_file, 'r', encoding='utf-8') as f:
                    mindmap_dict = json.load(f)
                
                mindmap = MindMapNode.from_dict(mindmap_dict)
                self.mindmaps[mindmap_id] = mindmap
                return mindmap
            
        except Exception as e:
            print(f"❌ 加载思维导图失败: {str(e)}")
        
        return None
    
    def save_knowledge_node(self, node: KnowledgeNode) -> None:
        """保存知识节点"""
        try:
            self.knowledge_nodes[node.id] = node
            
            # 保存到文件
            knowledge_dir = os.path.join(self.data_directory, self.subdirectories["knowledge"])
            node_file = os.path.join(knowledge_dir, f"{node.id}.json")
            
            node_dict = node.to_dict()
            with open(node_file, 'w', encoding='utf-8') as f:
                json.dump(node_dict, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 保存知识节点失败: {str(e)}")
    
    def load_knowledge_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """加载知识节点"""
        try:
            # 先从内存中查找
            if node_id in self.knowledge_nodes:
                return self.knowledge_nodes[node_id]
            
            # 从文件加载
            knowledge_dir = os.path.join(self.data_directory, self.subdirectories["knowledge"])
            node_file = os.path.join(knowledge_dir, f"{node_id}.json")
            
            if os.path.exists(node_file):
                with open(node_file, 'r', encoding='utf-8') as f:
                    node_dict = json.load(f)
                
                node = KnowledgeNode.from_dict(node_dict)
                self.knowledge_nodes[node_id] = node
                return node
            
        except Exception as e:
            print(f"❌ 加载知识节点失败: {str(e)}")
        
        return None
    
    def save_learning_plan(self, goal_id: str, plan: Dict[str, Any]) -> None:
        """保存学习计划"""
        try:
            self.learning_plans[goal_id] = plan
            
            # 保存到文件
            plans_dir = os.path.join(self.data_directory, self.subdirectories["plans"])
            plan_file = os.path.join(plans_dir, f"{goal_id}.json")
            
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 保存学习计划失败: {str(e)}")
    
    def load_learning_plan(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """加载学习计划"""
        try:
            # 先从内存中查找
            if goal_id in self.learning_plans:
                return self.learning_plans[goal_id]
            
            # 从文件加载
            plans_dir = os.path.join(self.data_directory, self.subdirectories["plans"])
            plan_file = os.path.join(plans_dir, f"{goal_id}.json")
            
            if os.path.exists(plan_file):
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan = json.load(f)
                
                self.learning_plans[goal_id] = plan
                return plan
            
        except Exception as e:
            print(f"❌ 加载学习计划失败: {str(e)}")
        
        return None
    
    def save_schedule(self, goal_id: str, schedule: Dict[str, Any]) -> None:
        """保存调度"""
        try:
            self.schedules[goal_id] = schedule
            
            # 保存到文件
            schedules_dir = os.path.join(self.data_directory, self.subdirectories["schedules"])
            schedule_file = os.path.join(schedules_dir, f"{goal_id}.json")
            
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 保存调度失败: {str(e)}")
    
    def load_schedule(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """加载调度"""
        try:
            # 先从内存中查找
            if goal_id in self.schedules:
                return self.schedules[goal_id]
            
            # 从文件加载
            schedules_dir = os.path.join(self.data_directory, self.subdirectories["schedules"])
            schedule_file = os.path.join(schedules_dir, f"{goal_id}.json")
            
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r', encoding='utf-8') as f:
                    schedule = json.load(f)
                
                self.schedules[goal_id] = schedule
                return schedule
            
        except Exception as e:
            print(f"❌ 加载调度失败: {str(e)}")
        
        return None
    
    def save_progress_data(self, goal_id: str, progress: Dict[str, Any]) -> None:
        """保存进度数据"""
        try:
            self.progress_data[goal_id] = progress
            
            # 保存到文件
            progress_dir = os.path.join(self.data_directory, self.subdirectories["progress"])
            progress_file = os.path.join(progress_dir, f"{goal_id}.json")
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ 保存进度数据失败: {str(e)}")
    
    def load_progress_data(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """加载进度数据"""
        try:
            # 先从内存中查找
            if goal_id in self.progress_data:
                return self.progress_data[goal_id]
            
            # 从文件加载
            progress_dir = os.path.join(self.data_directory, self.subdirectories["progress"])
            progress_file = os.path.join(progress_dir, f"{goal_id}.json")
            
            if os.path.exists(progress_file):
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                
                self.progress_data[goal_id] = progress
                return progress
            
        except Exception as e:
            print(f"❌ 加载进度数据失败: {str(e)}")
        
        return None
    
    def save_all_data(self) -> None:
        """保存所有数据"""
        print("💾 保存所有数据...")
        
        # 保存所有目标
        for goal in self.goals.values():
            self.save_goal(goal)
        
        # 保存所有思维导图
        for mindmap in self.mindmaps.values():
            self.save_mindmap(mindmap)
        
        # 保存所有知识节点
        for node in self.knowledge_nodes.values():
            self.save_knowledge_node(node)
        
        # 保存所有计划
        for goal_id, plan in self.learning_plans.items():
            self.save_learning_plan(goal_id, plan)
        
        # 保存所有调度
        for goal_id, schedule in self.schedules.items():
            self.save_schedule(goal_id, schedule)
        
        # 保存所有进度数据
        for goal_id, progress in self.progress_data.items():
            self.save_progress_data(goal_id, progress)
        
        print(f"✅ 所有数据已保存: {len(self.goals)}个目标, {len(self.mindmaps)}个思维导图")
    
    def load_all_data(self) -> None:
        """加载所有数据"""
        print("📂 加载所有数据...")
        
        try:
            # 加载所有目标
            goals_dir = os.path.join(self.data_directory, self.subdirectories["goals"])
            if os.path.exists(goals_dir):
                for filename in os.listdir(goals_dir):
                    if filename.endswith(".json"):
                        goal_id = filename[:-5]  # 移除.json后缀
                        self.load_goal(goal_id)
            
            # 加载所有思维导图
            mindmaps_dir = os.path.join(self.data_directory, self.subdirectories["mindmaps"])
            if os.path.exists(mindmaps_dir):
                for filename in os.listdir(mindmaps_dir):
                    if filename.endswith(".json"):
                        mindmap_id = filename[:-5]
                        self.load_mindmap(mindmap_id)
            
            # 加载所有知识节点
            knowledge_dir = os.path.join(self.data_directory, self.subdirectories["knowledge"])
            if os.path.exists(knowledge_dir):
                for filename in os.listdir(knowledge_dir):
                    if filename.endswith(".json"):
                        node_id = filename[:-5]
                        self.load_knowledge_node(node_id)
            
            # 加载所有计划
            plans_dir = os.path.join(self.data_directory, self.subdirectories["plans"])
            if os.path.exists(plans_dir):
                for filename in os.listdir(plans_dir):
                    if filename.endswith(".json"):
                        goal_id = filename[:-5]
                        self.load_learning_plan(goal_id)
            
            print(f"✅ 数据加载完成: {len(self.goals)}个目标, {len(self.mindmaps)}个思维导图")
            
        except Exception as e:
            print(f"❌ 加载数据失败: {str(e)}")
    
    def backup_data(self, backup_name: str = None) -> str:
        """备份数据"""
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_dir = os.path.join(self.data_directory, "backups", backup_name)
            
            # 创建备份目录
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 复制所有数据文件
            import shutil
            
            for subdir_name, subdir in self.subdirectories.items():
                src_dir = os.path.join(self.data_directory, subdir)
                dst_dir = os.path.join(backup_dir, subdir)
                
                if os.path.exists(src_dir):
                    shutil.copytree(src_dir, dst_dir)
            
            print(f"✅ 数据已备份到: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ 数据备份失败: {str(e)}")
            return ""
    
    def cleanup_old_data(self, days_old: int = 30) -> int:
        """清理旧数据"""
        try:
            deleted_count = 0
            
            # 清理备份
            backups_dir = os.path.join(self.data_directory, "backups")
            if os.path.exists(backups_dir):
                cutoff_time = time.time() - (days_old * 86400)
                
                for backup_name in os.listdir(backups_dir):
                    backup_path = os.path.join(backups_dir, backup_name)
                    
                    if os.path.isdir(backup_path):
                        # 检查备份时间
                        if os.path.getmtime(backup_path) < cutoff_time:
                            import shutil
                            shutil.rmtree(backup_path)
                            deleted_count += 1
            
            print(f"✅ 清理了{deleted_count}个超过{days_old}天的备份")
            return deleted_count
            
        except Exception as e:
            print(f"❌ 数据清理失败: {str(e)}")
            return 0
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """获取数据统计"""
        stats = {
            "goals": len(self.goals),
            "mindmaps": len(self.mindmaps),
            "knowledge_nodes": len(self.knowledge_nodes),
            "learning_plans": len(self.learning_plans),
            "schedules": len(self.schedules),
            "progress_data": len(self.progress_data),
            "storage_size": self._calculate_storage_size()
        }
        
        return stats
    
    def _calculate_storage_size(self) -> str:
        """计算存储空间使用情况"""
        try:
            total_size = 0
            
            for root, dirs, files in os.walk(self.data_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            
            # 转换为易读格式
            if total_size < 1024:
                return f"{total_size} B"
            elif total_size < 1024 * 1024:
                return f"{total_size/1024:.1f} KB"
            elif total_size < 1024 * 1024 * 1024:
                return f"{total_size/(1024*1024):.1f} MB"
            else:
                return f"{total_size/(1024*1024*1024):.1f} GB"
                
        except:
            return "未知"

# ========== 交互式思维导图探索器 ==========

class InteractiveMindMapExplorer:
    """交互式思维导图探索器"""
    
    def __init__(self, coordinator: SystemCoordinator):
        self.coordinator = coordinator
        self.current_mindmap: Optional[MindMapNode] = None
        self.current_node: Optional[MindMapNode] = None
        self.node_map: Dict[str, MindMapNode] = {}
        self.history: List[MindMapNode] = []
        
        # 探索状态
        self.exploration_depth = 0
        self.max_exploration_depth = 5
        self.visited_nodes: Set[str] = set()
        
        # 可视化配置
        self.visualization_enabled = True
        self.visualizer = MindMapVisualizer()
    
    def explore_mindmap(self, mindmap_id: str = None) -> None:
        """探索思维导图"""
        # 获取思维导图
        if mindmap_id:
            self.current_mindmap = self.coordinator.data_manager.load_mindmap(mindmap_id)
        elif self.coordinator.current_mindmap:
            self.current_mindmap = self.coordinator.current_mindmap
        else:
            print("❌ 没有可用的思维导图")
            return
        
        if not self.current_mindmap:
            print("❌ 思维导图加载失败")
            return
        
        # 构建节点映射
        self._build_node_map(self.current_mindmap)
        
        # 设置当前节点为根节点
        self.current_node = self.current_mindmap
        self.history = [self.current_node]
        self.visited_nodes.add(self.current_node.id)
        
        print(f"🧭 开始探索思维导图: {self.current_mindmap.title}")
        print(f"   节点总数: {len(self.node_map)}")
        
        # 主探索循环
        self._exploration_loop()
    
    def _build_node_map(self, root_node: MindMapNode) -> None:
        """构建节点映射"""
        self.node_map = {}
        
        def collect_nodes(node: MindMapNode):
            self.node_map[node.id] = node
            
            # 实际中需要递归收集所有子节点
            # 这里简化处理
        
        collect_nodes(root_node)
    
    def _exploration_loop(self) -> None:
        """探索循环"""
        while True:
            print("\n" + "=" * 60)
            self._display_current_node()
            print("=" * 60)
            
            # 显示选项
            print("\n选项:")
            print("  1. 查看子节点")
            print("  2. 返回父节点")
            print("  3. 查看详细信息")
            print("  4. 查看相关节点")
            print("  5. 查看学习状态")
            print("  6. 可视化当前视图")
            print("  7. 返回上一节点")
            print("  8. 退出探索")
            
            choice = input("\n请选择操作 (1-8): ").strip()
            
            if choice == "1":
                self._explore_children()
            elif choice == "2":
                self._go_to_parent()
            elif choice == "3":
                self._show_node_details()
            elif choice == "4":
                self._show_related_nodes()
            elif choice == "5":
                self._show_learning_status()
            elif choice == "6":
                self._visualize_current_view()
            elif choice == "7":
                self._go_back()
            elif choice == "8":
                print("👋 退出思维导图探索")
                break
            else:
                print("❌ 无效选择，请重试")
    
    def _display_current_node(self) -> None:
        """显示当前节点"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        node = self.current_node
        
        print(f"📍 当前位置: {node.title}")
        print(f"   描述: {node.description}")
        print(f"   深度: {node.depth}")
        print(f"   类型: {node.node_type}")
        print(f"   重要性: {node.importance:.2f}")
        print(f"   难度: {node.difficulty:.2f}")
        print(f"   学习状态: {node.learning_status}")
        
        # 显示子节点信息
        child_count = len(node.children_ids)
        if child_count > 0:
            print(f"   子节点: {child_count}个")
            
            # 显示前3个子节点
            child_nodes = []
            for child_id in node.children_ids[:3]:
                child = self.node_map.get(child_id)
                if child:
                    child_nodes.append(child.title)
            
            if child_nodes:
                print(f"      前3个子节点: {', '.join(child_nodes)}")
        
        # 显示导航信息
        if self.history:
            print(f"   导航深度: {len(self.history)}")
    
    def _explore_children(self) -> None:
        """探索子节点"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        child_ids = self.current_node.children_ids
        if not child_ids:
            print("📭 当前节点没有子节点")
            return
        
        print(f"\n子节点列表 ({len(child_ids)}个):")
        for i, child_id in enumerate(child_ids, 1):
            child = self.node_map.get(child_id)
            if child:
                status_icon = "✅" if child.learning_status == "mastered" else "📖" if child.learning_status == "learning" else "⏳"
                print(f"  {i}. {status_icon} {child.title} "
                      f"(重要性: {child.importance:.2f}, 状态: {child.learning_status})")
        
        # 选择要探索的子节点
        try:
            choice = input("\n选择要探索的子节点编号 (0返回): ").strip()
            if choice == "0":
                return
            
            index = int(choice) - 1
            if 0 <= index < len(child_ids):
                child_id = child_ids[index]
                child = self.node_map.get(child_id)
                
                if child:
                    # 更新当前节点
                    self.history.append(child)
                    self.current_node = child
                    self.visited_nodes.add(child.id)
                    
                    # 检查探索深度
                    self.exploration_depth += 1
                    if self.exploration_depth > self.max_exploration_depth:
                        print(f"⚠️ 已达到最大探索深度 ({self.max_exploration_depth})")
                        self._go_back()
                else:
                    print("❌ 找不到选择的子节点")
            else:
                print("❌ 无效的选择")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def _go_to_parent(self) -> None:
        """前往父节点"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        parent_id = self.current_node.parent_id
        if not parent_id:
            print("📍 已经是根节点")
            return
        
        parent = self.node_map.get(parent_id)
        if parent:
            self.history.append(parent)
            self.current_node = parent
            self.exploration_depth = max(0, self.exploration_depth - 1)
            print(f"⬆️ 已返回父节点: {parent.title}")
        else:
            print("❌ 找不到父节点")
    
    def _go_back(self) -> None:
        """返回上一节点"""
        if len(self.history) <= 1:
            print("📍 已经是起始节点")
            return
        
        # 移除当前节点
        self.history.pop()
        
        # 获取上一个节点
        if self.history:
            self.current_node = self.history[-1]
            self.exploration_depth = max(0, self.exploration_depth - 1)
            print(f"↩️ 已返回上一节点: {self.current_node.title}")
    
    def _show_node_details(self) -> None:
        """显示节点详细信息"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        node = self.current_node
        
        print(f"\n📋 节点详细信息:")
        print(f"   标题: {node.title}")
        print(f"   描述: {node.description}")
        print(f"   ID: {node.id}")
        print(f"   深度: {node.depth}")
        print(f"   类型: {node.node_type}")
        print(f"   重要性: {node.importance:.2f}")
        print(f"   难度: {node.difficulty:.2f}")
        print(f"   先决条件分数: {node.prerequisite_score:.2f}")
        print(f"   学习状态: {node.learning_status}")
        print(f"   预估时间: {node.estimated_time_minutes}分钟")
        print(f"   实际时间: {node.actual_time_minutes}分钟")
        print(f"   生成时间: {node.generated_at}")
        print(f"   生成模型: {node.generated_by}")
        
        # 显示先决条件
        if node.prerequisites:
            print(f"   先决条件: {len(node.prerequisites)}个")
            for prereq_id in node.prerequisites[:3]:  # 只显示前3个
                prereq = self.node_map.get(prereq_id)
                if prereq:
                    print(f"     - {prereq.title} ({prereq.learning_status})")
        
        # 显示关联知识节点
        if node.knowledge_node_ids:
            print(f"   关联知识节点: {len(node.knowledge_node_ids)}个")
        
        # 显示标签
        if node.tags:
            print(f"   标签: {', '.join(node.tags)}")
        
        input("\n按Enter键继续...")
    
    def _show_related_nodes(self) -> None:
        """显示相关节点"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        node = self.current_node
        related_ids = node.related_nodes
        
        if not related_ids:
            print("📭 当前节点没有相关节点")
            return
        
        print(f"\n🔗 相关节点 ({len(related_ids)}个):")
        
        for i, related_id in enumerate(related_ids, 1):
            related = self.node_map.get(related_id)
            if related:
                distance = abs(related.depth - node.depth)
                print(f"  {i}. {related.title} (深度: {related.depth}, 距离: {distance})")
        
        # 选择要跳转的相关节点
        try:
            choice = input("\n选择要跳转的相关节点编号 (0返回): ").strip()
            if choice == "0":
                return
            
            index = int(choice) - 1
            if 0 <= index < len(related_ids):
                related_id = related_ids[index]
                related = self.node_map.get(related_id)
                
                if related:
                    # 更新当前节点
                    self.history.append(related)
                    self.current_node = related
                    self.visited_nodes.add(related.id)
                    print(f"🔗 已跳转到相关节点: {related.title}")
                else:
                    print("❌ 找不到选择的相关节点")
            else:
                print("❌ 无效的选择")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def _show_learning_status(self) -> None:
        """显示学习状态"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        node = self.current_node
        
        print(f"\n📚 学习状态:")
        print(f"   当前状态: {node.learning_status}")
        
        if node.learning_status == "mastered":
            print("   ✅ 已掌握")
            if node.actual_time_minutes > 0:
                efficiency = node.estimated_time_minutes / node.actual_time_minutes
                print(f"   学习效率: {efficiency:.2f}x")
        elif node.learning_status == "learning":
            print("   📖 学习中")
            progress = min(node.actual_time_minutes / node.estimated_time_minutes, 1.0)
            print(f"   进度: {progress:.1%}")
        elif node.learning_status == "reviewing":
            print("   🔄 复习中")
        else:
            print("   ⏳ 待学习")
        
        # 显示学习建议
        suggestions = self._generate_learning_suggestions(node)
        if suggestions:
            print(f"\n💡 学习建议:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
        
        input("\n按Enter键继续...")
    
    def _generate_learning_suggestions(self, node: MindMapNode) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        if node.learning_status == "pending":
            # 检查先决条件
            if node.prerequisites:
                incomplete_prereqs = []
                for prereq_id in node.prerequisites:
                    prereq = self.node_map.get(prereq_id)
                    if prereq and prereq.learning_status != "mastered":
                        incomplete_prereqs.append(prereq.title)
                
                if incomplete_prereqs:
                    suggestions.append(f"先学习先决条件: {', '.join(incomplete_prereqs[:3])}")
            
            # 基于重要性
            if node.importance > 0.7:
                suggestions.append("这是高重要性节点，建议优先学习")
            elif node.importance < 0.3:
                suggestions.append("这是低重要性节点，可以后学习")
        
        elif node.learning_status == "learning":
            if node.actual_time_minutes > node.estimated_time_minutes * 1.5:
                suggestions.append("学习时间已超出预估，考虑调整学习方法")
            
            if node.difficulty > 0.7:
                suggestions.append("这是高难度节点，建议分段学习")
        
        elif node.learning_status == "reviewing":
            suggestions.append("定期复习以巩固记忆")
        
        return suggestions
    
    def _visualize_current_view(self) -> None:
        """可视化当前视图"""
        if not self.current_node:
            print("❌ 当前节点不可用")
            return
        
        if not self.visualization_enabled:
            print("⚠️ 可视化功能已禁用")
            return
        
        print(f"\n🎨 生成可视化视图...")
        
        try:
            # 创建局部视图（当前节点及其邻居）
            local_nodes = self._get_local_view(self.current_node, radius=2)
            
            if local_nodes:
                # 转换为树形结构
                tree_structure = self._create_local_tree(local_nodes, self.current_node)
                
                # 可视化
                result = self.visualizer.visualize_tree(tree_structure, local_nodes)
                
                if result.get("success"):
                    print("✅ 可视化生成成功")
                    
                    # 显示可视化信息
                    if "visualization_type" in result:
                        print(f"   类型: {result['visualization_type']}")
                    
                    # 保存选项
                    save = input("\n是否保存可视化图像？(y/N): ").strip().lower()
                    if save == 'y':
                        filename = f"mindmap_{self.current_node.id}_{int(time.time())}.png"
                        self.visualizer.save_visualization(filename)
                        print(f"💾 已保存到: {filename}")
                else:
                    print(f"❌ 可视化失败: {result.get('error', '未知错误')}")
            else:
                print("❌ 无法创建可视化视图")
                
        except Exception as e:
            print(f"❌ 可视化异常: {str(e)}")
    
    def _get_local_view(self, center_node: MindMapNode, radius: int = 2) -> Dict[str, MindMapNode]:
        """获取局部视图（中心节点及其邻居）"""
        local_nodes = {}
        
        def collect_neighbors(node: MindMapNode, current_radius: int):
            if node.id in local_nodes or current_radius > radius:
                return
            
            local_nodes[node.id] = node
            
            # 收集父节点
            if node.parent_id:
                parent = self.node_map.get(node.parent_id)
                if parent:
                    collect_neighbors(parent, current_radius + 1)
            
            # 收集子节点
            for child_id in node.children_ids:
                child = self.node_map.get(child_id)
                if child:
                    collect_neighbors(child, current_radius + 1)
            
            # 收集相关节点（仅限一层）
            if current_radius == 0:
                for related_id in node.related_nodes:
                    related = self.node_map.get(related_id)
                    if related:
                        local_nodes[related.id] = related
        
        collect_neighbors(center_node, 0)
        return local_nodes
    
    def _create_local_tree(self, node_map: Dict[str, MindMapNode], 
                          root_node: MindMapNode) -> MindMapNode:
        """创建局部树结构"""
        # 创建一个新的根节点（复制）
        new_root = MindMapNode(
            id=root_node.id,
            title=root_node.title,
            description=root_node.description,
            depth=0
        )
        
        # 添加直接子节点
        for child_id in root_node.children_ids:
            child = node_map.get(child_id)
            if child:
                new_root.children_ids.append(child_id)
        
        return new_root

# ========== 命令行界面 ==========

class CommandLineInterface:
    """命令行界面"""
    
    def __init__(self, coordinator: SystemCoordinator):
        self.coordinator = coordinator
        self.explorer = InteractiveMindMapExplorer(coordinator)
        
        # 命令映射
        self.commands = {
            "help": self.show_help,
            "status": self.show_status,
            "create": self.create_goal,
            "list": self.list_goals,
            "select": self.select_goal,
            "plan": self.create_plan,
            "schedule": self.schedule_sessions,
            "learn": self.learn_now,
            "monitor": self.monitor_progress,
            "explore": self.explore_mindmap,
            "explore_knowledge": self.explore_knowledge,
            "auto": self.run_auto_pilot,
            "save": self.save_state,
            "load": self.load_state,
            "config": self.show_config,
            "stats": self.show_stats,
            "vision": self.show_vision,  # ========== 愿景核心命令 ==========
            "vision_manifesto": self.show_vision_manifesto,  # 愿景宣言
            "vision_decisions": self.show_vision_decisions,  # 伦理决策记录
            "qa": self.ask_question,  # ========== 问答系统命令 ==========
            "ask": self.ask_question,  # 同上
            "clear_chat": self.clear_chat_history,  # 清空对话
            "export_chat": self.export_chat_history,  # 导出对话
            "learning_advice": self.show_learning_advice,  # 学习建议
            "quit": self.quit_system,
            "exit": self.quit_system
        }
        
        # 命令历史
        self.command_history = deque(maxlen=50)
        
        # 欢迎信息
        self.welcome_message = """
╔══════════════════════════════════════════════════════╗
║           🧠 自主认知学习系统 v2.0.0 🧠            ║
║         思维导图驱动的智能学习平台           ║
╚══════════════════════════════════════════════════════╝
        
🌟 核心功能:
   • 思维导图驱动的学习路径规划
   • 自适应学习调度与进度监控
   • 多模态知识提取与深度探索
   • 层次化学习任务分配
        
输入 'help' 查看所有命令
输入 'auto 学习目标' 启动自动驾驶模式
        """
    
    def show_help(self, args: List[str] = None) -> None:
        """显示帮助信息"""
        help_text = """
📚 可用命令:
        
🎯 目标管理:
  create <描述>      - 创建学习目标 (例: create 学习Python编程)
  list              - 列出所有目标
  select <ID>       - 选择目标
        
📋 学习规划:
  plan              - 为当前目标创建学习计划
  schedule          - 调度学习会话
  learn             - 立即开始学习
        
📈 进度监控:
  monitor           - 监控当前进度
  explore           - 探索思维导图
        
🔍 知识探索:
  explore_knowledge <主题> - 探索知识主题
        
🤖 自动化:
  auto <描述>       - 自动驾驶模式
        
💾 系统管理:
  status            - 显示系统状态
  save              - 保存系统状态
  load              - 加载系统状态
  config            - 显示配置
  stats             - 显示统计数据

🌌 愿景核心 (思想钢印):
  vision            - 显示愿景核心状态
  vision_manifesto  - 显示愿景宣言
                     - vision_manifesto [brief|core|full]
  vision_decisions  - 显示伦理决策记录

📚 问答系统:
  ask <问题>       - 询问问题（支持上下文理解）
                     - ask 什么是Python函数？
  clear_chat        - 清空对话历史
  export_chat       - 导出对话历史
  learning_advice <主题> - 获取学习方法建议
                     - learning_advice Python编程

❓ 其他:
  help              - 显示帮助
  quit / exit       - 退出系统
        
💡 提示:
  • 使用 'auto 学习目标' 可以快速启动完整学习流程
  • 思维导图探索器提供直观的知识结构浏览
  • 系统会自动保存进度，也可手动保存
        """
        print(help_text)
    
    def show_status(self, args: List[str] = None) -> None:
        """显示系统状态"""
        status = self.coordinator.get_system_status()
        
        print("\n" + "=" * 60)
        print("📊 系统状态")
        print("=" * 60)
        
        # 系统信息
        print(f"\n🖥️ 系统:")
        print(f"  名称: {status['system']['name']}")
        print(f"  版本: {status['system']['version']}")
        print(f"  运行时间: {status['system']['uptime']}")
        print(f"  状态: {status['system']['status']}")
        
        # 目标信息
        print(f"\n🎯 目标:")
        print(f"  总计: {status['goals']['total']}")
        print(f"  活动中: {status['goals']['active']}")
        print(f"  待处理: {status['goals']['pending']}")
        print(f"  已完成: {status['goals']['completed']}")
        
        # 学习信息
        print(f"\n📚 学习:")
        print(f"  总学习时间: {status['learning']['total_time_minutes']}分钟")
        print(f"  当前目标: {status['learning']['current_goal']}")
        print(f"  当前进度: {status['learning']['current_progress']:.1%}")
        
        # 存储信息
        print(f"\n💾 存储:")
        print(f"  目标数: {status['storage']['goals_count']}")
        print(f"  思维导图数: {status['storage']['mindmaps_count']}")
        print(f"  计划数: {status['storage']['plans_count']}")
        
        # 存储统计
        storage_stats = self.coordinator.data_manager.get_data_statistics()
        print(f"\n📈 数据统计:")
        for key, value in storage_stats.items():
            if key != "storage_size":
                print(f"  {key}: {value}")
        print(f"  存储空间: {storage_stats['storage_size']}")
        
        print("\n" + "=" * 60)
    
    def create_goal(self, args: List[str]) -> None:
        """创建学习目标"""
        if not args:
            print("❌ 请提供目标描述")
            print("用法: create <目标描述>")
            return
        
        description = " ".join(args)
        goal = self.coordinator.create_learning_goal(description)
        
        # 询问是否立即生成思维导图
        if goal:
            choice = input("\n是否立即生成思维导图？(Y/n): ").strip().lower()
            if choice in ['y', 'yes', '']:
                self.coordinator.generate_mindmap_for_goal(goal)
    
    def list_goals(self, args: List[str] = None) -> None:
        """列出所有目标"""
        print("\n📋 目标列表:")
        print("-" * 60)
        
        # 活动目标
        if self.coordinator.active_goals:
            print("\n🎯 活动目标:")
            for goal_id, goal in self.coordinator.active_goals.items():
                current = "📍" if self.coordinator.current_goal and self.coordinator.current_goal.id == goal_id else " "
                print(f"  {current} {goal_id[:8]}... - {goal.description}")
                print(f"     规模: {goal.scale.value}, 进度: {goal.overall_progress:.1%}")
        
        # 待处理目标
        if self.coordinator.pending_goals:
            print("\n⏳ 待处理目标:")
            for goal_id, goal in self.coordinator.pending_goals.items():
                print(f"  ⏳ {goal_id[:8]}... - {goal.description}")
                print(f"     规模: {goal.scale.value}, 预估知识点: {goal.target_knowledge_count}")
        
        # 已完成目标
        if self.coordinator.completed_goals:
            print("\n✅ 已完成目标:")
            for goal_id, goal in self.coordinator.completed_goals.items():
                print(f"  ✅ {goal_id[:8]}... - {goal.description}")
                print(f"     规模: {goal.scale.value}, 完成时间: {goal.completed_at[:10] if goal.completed_at else '未知'}")
        
        if not (self.coordinator.active_goals or self.coordinator.pending_goals or self.coordinator.completed_goals):
            print("📭 暂无目标")
        
        print("-" * 60)
    
    def select_goal(self, args: List[str]) -> None:
        """选择目标"""
        if not args:
            print("❌ 请提供目标ID")
            print("用法: select <目标ID>")
            print("     使用 'list' 命令查看所有目标ID")
            return
        
        goal_id = args[0]
        
        # 在所有目标中查找
        goal = (self.coordinator.active_goals.get(goal_id) or 
                self.coordinator.pending_goals.get(goal_id) or 
                self.coordinator.completed_goals.get(goal_id))
        
        if goal:
            self.coordinator.current_goal = goal
            
            # 加载相关数据
            if goal.mindmap_root_id:
                self.coordinator.current_mindmap = self.coordinator.data_manager.load_mindmap(goal.mindmap_root_id)
            
            self.coordinator.current_plan = self.coordinator.data_manager.load_learning_plan(goal.id)
            
            print(f"✅ 已选择目标: {goal.description}")
            print(f"   进度: {goal.overall_progress:.1%}")
        else:
            print(f"❌ 找不到目标ID: {goal_id}")
            print("   使用 'list' 命令查看所有目标ID")
    
    def create_plan(self, args: List[str] = None) -> None:
        """创建学习计划"""
        if not self.coordinator.current_goal:
            print("❌ 请先选择目标 (使用 'select <目标ID>' 或 'create <目标描述>')")
            return
        
        plan = self.coordinator.create_learning_plan_for_goal(self.coordinator.current_goal)
        
        if plan:
            # 显示计划摘要
            summary = plan.get("summary", {})
            if summary:
                print(f"\n📋 计划摘要:")
                print(f"   总周数: {summary.get('overview', {}).get('total_weeks', 0)}")
                print(f"   里程碑数: {summary.get('overview', {}).get('total_milestones', 0)}")
                print(f"   预估总时长: {summary.get('overview', {}).get('estimated_total_hours', 0):.1f}小时")
                
                # 显示关键日期
                key_dates = summary.get("key_dates", {})
                if key_dates.get("start_date"):
                    print(f"   开始日期: {key_dates['start_date'][:10]}")
                if key_dates.get("end_date"):
                    print(f"   结束日期: {key_dates['end_date'][:10]}")
    
    def schedule_sessions(self, args: List[str] = None) -> None:
        """调度学习会话"""
        if not self.coordinator.current_goal:
            print("❌ 请先选择目标")
            return
        
        if not self.coordinator.current_plan:
            print("❌ 请先创建学习计划 (使用 'plan' 命令)")
            return
        
        schedule = self.coordinator.schedule_learning_sessions()
        
        if schedule:
            sessions = schedule.get("scheduled_sessions", [])
            if sessions:
                print(f"\n⏰ 已调度 {len(sessions)} 个学习会话:")
                
                for i, session in enumerate(sessions[:3], 1):  # 只显示前3个
                    print(f"  {i}. {session.get('type', '未知')} - "
                          f"{session.get('duration_minutes', 0)}分钟 - "
                          f"{session.get('priority', '中')}优先级")
                
                if len(sessions) > 3:
                    print(f"  ... 还有 {len(sessions) - 3} 个会话")
    
    def learn_now(self, args: List[str] = None) -> None:
        """立即开始学习"""
        if not self.coordinator.current_goal:
            print("❌ 请先选择目标")
            return
        
        # 检查是否有调度
        if not self.coordinator.current_schedule:
            print("ℹ️ 没有现有调度，正在创建...")
            self.coordinator.schedule_learning_sessions()
        
        # 执行学习会话
        result = self.coordinator.execute_learning_session()
        
        if result.get("success"):
            print(f"✅ 学习完成!")
            print(f"   获得知识点: {result.get('knowledge_gained', 0)}")
            print(f"   掌握度提升: {result.get('mastery_increase', 0):.2f}")
            
            # 询问是否继续
            choice = input("\n是否继续下一个学习会话？(Y/n): ").strip().lower()
            if choice in ['y', 'yes', '']:
                self.learn_now()
    
    def monitor_progress(self, args: List[str] = None) -> None:
        """监控进度"""
        if not self.coordinator.current_goal:
            print("❌ 请先选择目标")
            return
        
        report = self.coordinator.monitor_progress()
        
        if report:
            # 显示关键指标
            metrics = report.get("progress_metrics", {})
            if metrics:
                print(f"\n📈 进度指标:")
                
                for metric_name, metric_data in metrics.items():
                    if metric_name != "overall_score" and "value" in metric_data:
                        value = metric_data["value"]
                        status = metric_data.get("status", "unknown")
                        
                        status_icon = {
                            "good": "✅",
                            "warning": "⚠️",
                            "poor": "❌"
                        }.get(status, "❓")
                        
                        print(f"  {status_icon} {metric_name}: {value:.2f}")
                
                # 显示综合分数
                overall = metrics.get("overall_score", {}).get("value", 0)
                print(f"\n  📊 综合分数: {overall:.2f}")
            
            # 显示预警
            alerts = report.get("alerts", [])
            if alerts:
                print(f"\n⚠️ 预警 ({len(alerts)}个):")
                for alert in alerts[:3]:  # 只显示前3个
                    severity = alert.get("severity", "unknown")
                    severity_icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🔵"
                    print(f"  {severity_icon} {alert.get('message', '未知预警')}")
            
            # 显示建议
            recommendations = report.get("recommendations", [])
            if recommendations:
                print(f"\n💡 建议:")
                for rec in recommendations[:3]:  # 只显示前3个
                    print(f"  • {rec}")
    
    def explore_mindmap(self, args: List[str] = None) -> None:
        """探索思维导图"""
        if not self.coordinator.current_goal:
            print("❌ 请先选择目标")
            return
        
        if not self.coordinator.current_mindmap:
            print("ℹ️ 目标没有思维导图，正在生成...")
            self.coordinator.generate_mindmap_for_goal(self.coordinator.current_goal)
        
        if self.coordinator.current_mindmap:
            self.explorer.explore_mindmap(self.coordinator.current_mindmap.id)
        else:
            print("❌ 思维导图生成失败")
    
    def explore_knowledge(self, args: List[str]) -> None:
        """探索知识"""
        if not args:
            # 如果没有指定主题，使用当前目标
            if self.coordinator.current_goal:
                topic = self.coordinator.current_goal.description
            else:
                print("❌ 请提供探索主题")
                print("用法: explore_knowledge <主题>")
                return
        else:
            topic = " ".join(args)
        
        result = self.coordinator.explore_knowledge(topic)
        
        if result.get("success") is not False:  # 成功或没有success字段
            # 显示问题
            questions = result.get("questions", [])
            if questions:
                print(f"\n❓ 相关问题 ({len(questions)}个):")
                for i, question in enumerate(questions[:5], 1):  # 只显示前5个
                    print(f"  {i}. {question}")
            
            # 显示学习路径
            learning_paths = result.get("learning_paths", [])
            if learning_paths:
                print(f"\n🛣️ 学习路径 ({len(learning_paths)}条):")
                for i, path in enumerate(learning_paths[:2], 1):  # 只显示前2条
                    print(f"  路径{i}: {path.get('name', '未命名')}")
                    print(f"     节点数: {path.get('node_count', 0)}")
    
    def run_auto_pilot(self, args: List[str]) -> None:
        """运行自动驾驶模式"""
        if not args:
            # 如果没有指定目标，使用当前目标
            if self.coordinator.current_goal:
                goal_description = self.coordinator.current_goal.description
            else:
                print("❌ 请提供学习目标")
                print("用法: auto <学习目标>")
                return
        else:
            goal_description = " ".join(args)
        
        result = self.coordinator.run_auto_pilot(goal_description)
        
        if result.get("success"):
            print(f"\n🎉 自动驾驶模式完成!")
            print(f"   完成步骤: {result.get('total_steps', 0)}")
            print(f"   最终进度: {result.get('final_progress', 0):.1%}")
            
            # 显示步骤详情
            show_details = input("\n是否显示步骤详情？(y/N): ").strip().lower()
            if show_details == 'y':
                print("\n📋 执行步骤:")
                for step in result.get("steps", []):
                    step_name = step.get("step", "未知步骤")
                    success = step.get("success", False)
                    status = "✅" if success else "❌"
                    print(f"  {status} {step_name}")
        else:
            print(f"❌ 自动驾驶模式失败: {result.get('error', '未知错误')}")
    
    def save_state(self, args: List[str] = None) -> None:
        """保存系统状态"""
        self.coordinator.save_system_state()
    
    def load_state(self, args: List[str] = None) -> None:
        """加载系统状态"""
        success = self.coordinator.load_system_state()
        if success:
            print("✅ 系统状态加载成功")
        else:
            print("❌ 系统状态加载失败")
    
    def show_config(self, args: List[str] = None) -> None:
        """显示配置"""
        config = self.coordinator.config
        
        print("\n⚙️ 系统配置:")
        print("-" * 60)
        
        for section, settings in config.items():
            print(f"\n📁 {section.upper()}:")
            for key, value in settings.items():
                if key != "api_key" or not value:  # 不显示API密钥
                    print(f"  {key}: {value}")
        
        print("-" * 60)
    
    def show_stats(self, args: List[str] = None) -> None:
        """显示统计"""
        stats = self.coordinator.stats
        
        print("\n📊 系统统计:")
        print("-" * 60)
        
        print(f"📅 系统启动时间: {stats.get('system_start_time', '未知')}")
        print(f"🎯 创建目标总数: {stats.get('total_goals_created', 0)}")
        print(f"✅ 完成目标总数: {stats.get('total_goals_completed', 0)}")
        print(f"⏱️ 总学习时间: {stats.get('total_learning_time_minutes', 0)}分钟")
        print(f"🧠 总知识点数: {stats.get('total_knowledge_nodes', 0)}")
        print(f"📈 平均完成率: {stats.get('avg_completion_rate', 0):.1%}")
        
        # 学习历史统计
        if self.coordinator.learning_history:
            total_sessions = len(self.coordinator.learning_history)
            total_duration = sum(s.get("duration_minutes", 0) for s in self.coordinator.learning_history)
            avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
            
            print(f"\n📚 学习历史:")
            print(f"  总学习会话: {total_sessions}")
            print(f"  总时长: {total_duration}分钟")
            print(f"  平均会话时长: {avg_duration:.1f}分钟")
        
        # 存储统计
        storage_stats = self.coordinator.data_manager.get_data_statistics()
        print(f"\n💾 数据存储:")
        for key, value in storage_stats.items():
            print(f"  {key}: {value}")
        
        print("-" * 60)
    
    # ========== 愿景核心相关命令 ==========
    
    def show_vision(self, args: List[str] = None) -> None:
        """显示愿景核心状态"""
        vision_core = self.coordinator.vision_core
        
        print("\n🌌 文明愿景核心状态:")
        print("-" * 60)
        
        # 显示激活级别
        print(f"🧠 思想钢印激活度: {vision_core.vision_activation_level:.0%}")
        
        # 显示当前目标阶段
        print(f"📍 当前文明阶段: {vision_core.current_tier}")
        print(f"🎯 目标文明阶段: {vision_core.target_tier}")
        
        # 显示战略路径
        print(f"\n🛤️ 战略推进路径:")
        for pathway in vision_core.strategic_pathways:
            marker = " ★" if pathway["impact_score"] >= 9.5 else ""
            print(f"  - {pathway['name']}{marker}")
            print(f"    目标: {pathway['goal']}")
            print(f"    影响力: {pathway['impact_score']}/10")
            print(f"    现状: {pathway['current_status']}")
        
        # 显示决策统计
        print(f"\n⚖️ 伦理决策统计: {len(vision_core.decisions_made)}条")
        if vision_core.decisions_made:
            recent = vision_core.decisions_made[-5:]  # 最近5条
            for decision in recent:
                print(f"  - {decision['decision']}: {decision['scenario'][:50]}...")
        
        print("-" * 60)
    
    def show_vision_manifesto(self, args: List[str] = None) -> None:
        """显示完整愿景宣言"""
        vision_core = self.coordinator.vision_core
        
        # 确定详细程度
        level = "full"
        if args and len(args) > 0:
            if args[0] == "brief":
                level = "brief"
            elif args[0] == "core":
                level = "core"
        
        print("\n" + vision_core.get_vision_manifesto(level))
    
    def show_vision_decisions(self, args: List[str] = None) -> None:
        """显示伦理决策记录"""
        vision_core = self.coordinator.vision_core
        decisions = vision_core.decisions_made
        
        if not decisions:
            print("\n⚖️ 暂无伦理决策记录")
            return
        
        print(f"\n⚖️ 伦理决策记录 (共{len(decisions)}条):")
        print("-" * 70)
        
        # 按时间倒序显示
        for i, decision in enumerate(reversed(decisions), 1):
            print(f"\n决策 {i}:")
            print(f"  时间: {decision['timestamp']}")
            print(f"  场景: {decision['scenario']}")
            print(f"  决策: {decision['decision']}")
            
            if decision.get('reasoning'):
                print(f"  推理:")
                for reason in decision['reasoning']:
                    print(f"    - {reason}")
            
            if decision.get('warnings'):
                print(f"  警告:")
                for warning in decision['warnings']:
                    print(f"    ⚠️  {warning}")
            
            print(f"  愿景相关性: {decision.get('alignment_score', 0):.0%}")
        
        print("\n" + "-" * 70)

    # ========== 问答系统相关命令 ==========

    def ask_question(self, args: List[str] = None) -> None:
        """询问问题（使用上下文感知问答系统）"""
        if not args:
            print("❌ 请提供您的问题")
            return

        question = " ".join(args)

        # 构建知识库和思维导图
        knowledge_base = {}
        mindmap_nodes = {}

        # 如果有当前目标，使用其数据
        if self.coordinator.current_mindmap:
            # 收集思维导图节点
            mindmap_nodes = {self.coordinator.current_mindmap.id: self.coordinator.current_mindmap}
            # 这里可以添加遍历子节点的逻辑

        # 使用 qa 系统生成回答
        print(f"\n🤔 正在思考您的问题...")
        response = self.coordinator.qa_system.generate_response(
            question=question,
            conversation_id="main",
            user_id="user",
            knowledge_base=knowledge_base,
            mindmap_nodes=mindmap_nodes,
            learning_goal=self.coordinator.current_goal
        )

        # 显示回答
        print(f"\n💬 回答：")
        print("-" * 70)
        print(response["answer"])
        print("-" * 70)

        # 显示相关信息
        if response.get("relevant_knowledge"):
            print(f"\n📚 参考知识点 ({len(response['relevant_knowledge'])}个):")
            for i, item in enumerate(response["relevant_knowledge"], 1):
                print(f"  {i}. {item['title']} (相关度: {item['relevance']:.2f})")

        # 显示后续问题建议
        if response.get("suggested_follow_up"):
            print(f"\n💡 后续问题建议：")
            for i, question in enumerate(response["suggested_follow_up"], 1):
                print(f"  {i}. {question}")

        print(f"\n📊 置信度: {response['confidence']:.1%}")
        print(f"⏱️  处理时间: {response['processing_time_ms']}ms")

    def clear_chat_history(self, args: List[str] = None) -> None:
        """清空对话历史"""
        self.coordinator.qa_system.clear_conversation("main")
        print("\n✅ 对话历史已清空")

    def export_chat_history(self, args: List[str] = None) -> None:
        """导出对话历史"""
        conversation = self.coordinator.qa_system.export_conversation("main")

        if not conversation:
            print("\n⚠️ 没有可导出的对话历史")
            return

        # 保存到文件
        export_file = f"chat_export_{conversation['conversation_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 对话历史已导出到: {export_file}")
            print(f"   对话轮次: {len(conversation['turns'])}")
            print(f"   当前主题: {conversation['current_topic']}")
        except Exception as e:
            print(f"\n❌ 导出失败: {str(e)}")

    def show_learning_advice(self, args: List[str] = None) -> None:
        """显示学习建议"""
        if not args:
            print("❌ 请提供学习主题（如: 学习 Python 编程）")
            return

        topic = " ".join(args)
        print(f"\n📚 正在为 '{topic}' 生成学习建议...")

        advice = self.coordinator.learning_advisor.advise_on_method(topic)
        print("\n" + advice)

    def quit_system(self, args: List[str] = None) -> None:
        """退出系统"""
        print("\n💾 正在保存系统状态...")
        self.coordinator.save_system_state()
        
        print("\n👋 感谢使用自主认知学习系统!")
        print("   再见！")
        sys.exit(0)
    
    def run(self) -> None:
        """运行命令行界面"""
        print(self.welcome_message)
        
        # 尝试加载系统状态
        load_choice = input("是否加载上次的系统状态？(Y/n): ").strip().lower()
        if load_choice in ['y', 'yes', '']:
            self.coordinator.load_system_state()
        
        # 主循环
        while True:
            try:
                # 显示提示符
                prompt = "> "
                if self.coordinator.current_goal:
                    goal_desc = self.coordinator.current_goal.description
                    if len(goal_desc) > 20:
                        goal_desc = goal_desc[:17] + "..."
                    prompt = f"[{goal_desc}] > "
                
                # 获取用户输入
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # 添加到历史
                self.command_history.append(user_input)
                
                # 解析命令
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                
                # 执行命令
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"❌ 未知命令: {command}")
                    print("   输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ 检测到中断信号")
                continue_choice = input("是否退出系统？(y/N): ").strip().lower()
                if continue_choice == 'y':
                    self.quit_system()
            
            except EOFError:
                print("\n\n👋 检测到文件结束符，退出系统")
                self.quit_system()
            
            except Exception as e:
                print(f"\n❌ 执行命令时发生错误: {str(e)}")
                print("   输入 'help' 查看可用命令")

# ========== 主函数 ==========

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='自主认知学习系统')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径')
    parser.add_argument('--auto', type=str, help='自动驾驶模式，指定学习目标')
    parser.add_argument('--gui', action='store_true', help='启动图形界面（预留）')
    parser.add_argument('--version', action='store_true', help='显示版本信息')

    args = parser.parse_args()

    # Windows UTF-8 编码支持（在 argparse 之后设置）
    if sys.platform == 'win32':
        try:
            import io
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    
    # 显示版本信息
    if args.version:
        print("🧠 自主认知学习系统 v2.0.0")
        print("思维导图驱动的智能学习平台")
        return
    
    # 创建系统协调器
    print("🚀 初始化自主认知学习系统...")
    coordinator = SystemCoordinator(config_file=args.config)
    
    # 创建命令行界面
    cli = CommandLineInterface(coordinator)
    
    # 检查是否直接运行自动驾驶模式
    if args.auto:
        print(f"🤖 启动自动驾驶模式: {args.auto}")
        result = coordinator.run_auto_pilot(args.auto)
        
        if result.get("success"):
            print(f"✅ 自动驾驶模式完成!")
            sys.exit(0)
        else:
            print(f"❌ 自动驾驶模式失败")
            sys.exit(1)
    
    # 启动命令行界面
    cli.run()

if __name__ == "__main__":
    main()