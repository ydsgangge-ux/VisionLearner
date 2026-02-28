import json
import re
import math
import random
import heapq
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import statistics

from foundation import (
    MindMapNode, KnowledgeNode, LearningGoal, LearningLevel,
    KnowledgeType, GoalScale, LearningStrategy, MindMapStyle,
    ProgressGranularity, generate_id, FoundationManager,
    TimeEstimationModel
)
from explorer import (
    KnowledgeNetworkBuilder, LearningPathGenerator,
    ExplorerManager
)

from allocator import HierarchicalLearningAllocator
from planner import MindMapDrivenPlanner
from scheduler import AdaptiveScheduler
from monitor import ProgressMonitor


if __name__ == "__main__":
    print("🧪 测试规划模块...")
    print("=" * 70)

    # 创建测试目标
    test_goal = LearningGoal(
        id="test_goal_001",
        description="学习Python编程基础",
        scale=GoalScale.MEDIUM,
        target_knowledge_count=50,
        overall_progress=0.4
    )

    # 创建测试思维导图
    test_mindmap = MindMapNode(
        id="test_mindmap_root",
        title="Python编程基础",
        description="Python编程基础知识体系",
        depth=0
    )

    # 创建一些子节点
    child_nodes = []
    for i in range(5):
        child = MindMapNode(
            id=f"test_child_{i}",
            title=f"Python概念{i+1}",
            description=f"Python编程概念{i+1}",
            depth=1,
            parent_id=test_mindmap.id,
            importance=random.uniform(0.3, 0.9),
            difficulty=random.uniform(0.2, 0.8),
            learning_status="mastered" if i < 2 else "learning"
        )
        child_nodes.append(child)

    # 构建节点映射
    node_map = {test_mindmap.id: test_mindmap}
    for child in child_nodes:
        node_map[child.id] = child
        test_mindmap.children_ids.append(child.id)

    # 测试层次化学习分配器
    print("\n📊 测试层次化学习分配器:")
    print("-" * 50)

    allocator = HierarchicalLearningAllocator()

    allocation_plan = allocator.allocate_by_mindmap(
        goal=test_goal,
        mindmap_root=test_mindmap,
        node_map=node_map,
        strategy="balanced",
        available_time_minutes=600  # 10小时
    )

    print(f"分配计划: {len(allocation_plan.get('learning_sequences', []))}个学习序列")
    print(f"时间分配: {allocation_plan.get('time_allocation', {}).get('total_estimated_minutes', 0)}分钟")

    # 测试思维导图驱动规划器
    print("\n\n📋 测试思维导图驱动规划器:")
    print("-" * 50)

    planner = MindMapDrivenPlanner()

    learning_plan = planner.create_learning_plan(
        goal=test_goal,
        mindmap_root=test_mindmap,
        node_map=node_map,
        allocation_plan=allocation_plan
    )

    print(f"学习计划: {len(learning_plan.get('milestones', []))}个里程碑")
    print(f"时间线: {learning_plan.get('timeline', {}).get('timeline_weeks', 0)}周")

    # 测试自适应调度器
    print("\n\n⏰ 测试自适应调度器:")
    print("-" * 50)

    scheduler = AdaptiveScheduler()

    current_context = {
        "available_minutes": 120,
        "energy_level": 0.7,
        "focus_level": 0.8,
        "distractions": []
    }

    schedule = scheduler.schedule_learning_sessions(
        learning_plan=learning_plan,
        current_context=current_context,
        strategy="adaptive_schedule"
    )

    print(f"调度结果: {len(schedule.get('scheduled_sessions', []))}个学习会话")
    print(f"灵活性分数: {schedule.get('flexibility_score', 0):.2f}")

    # 测试进度监控器
    print("\n\n📈 测试进度监控器:")
    print("-" * 50)

    monitor = ProgressMonitor()

    progress_data = {
        "overall_progress": 0.4,
        "mastery_level": 0.6,
        "engagement_level": 0.7,
        "active_days": 10,
        "daily_progress": {"2024-01-01": 0.1, "2024-01-02": 0.15, "2024-01-03": 0.2}
    }

    monitoring_report = monitor.monitor_goal_progress(
        goal=test_goal,
        progress_data=progress_data,
        monitoring_strategy="adaptive"
    )

    print(f"监控报告: {len(monitoring_report.get('alerts', []))}个预警")
    print(f"进度指标: {monitoring_report.get('progress_metrics', {}).get('overall_score', {}).get('value', 0):.2f}")

    # 测试多目标优化
    print("\n\n⚡ 测试多目标优化:")
    print("-" * 50)

    # 创建多个测试目标
    goals = [
        LearningGoal(
            id=f"goal_{i}",
            description=f"学习目标{i+1}",
            scale=random.choice([GoalScale.SMALL, GoalScale.MEDIUM, GoalScale.LARGE]),
            target_knowledge_count=random.randint(20, 200),
            priority=random.randint(3, 9)
        )
        for i in range(3)
    ]

    available_time = {
        "周一": 2, "周二": 2, "周三": 2, "周四": 2, "周五": 2,
        "周六": 4, "周日": 4
    }

    optimization = scheduler.optimize_schedule_for_goals(
        goals=goals,
        available_time=available_time
    )

    print(f"优化结果: {len(optimization.get('time_allocation', {}))}个时间分配")
    print(f"优化指标: 效率{optimization.get('optimization_metrics', {}).get('efficiency_score', 0):.2f}")

    print("\n✅ 规划模块测试完成")
    print("=" * 70)