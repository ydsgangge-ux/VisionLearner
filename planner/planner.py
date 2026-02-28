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


class MindMapDrivenPlanner:
    """
    思维导图驱动规划器 - 基于思维导图结构制定详细学习计划
    """

    def __init__(self, time_model: Optional[TimeEstimationModel] = None):
        self.time_model = time_model or TimeEstimationModel()
        self.allocation_history = {}

        # 规划模板
        self.planning_templates = {
            "micro_goal": {
                "name": "微目标计划",
                "description": "针对微小学习目标的详细计划",
                "components": ["daily_schedule", "learning_sessions", "review_plan"]
            },
            "small_goal": {
                "name": "小目标计划",
                "description": "针对小型学习目标的周计划",
                "components": ["weekly_schedule", "milestones", "progress_checkpoints"]
            },
            "medium_goal": {
                "name": "中目标计划",
                "description": "针对中型学习目标的月度计划",
                "components": ["monthly_schedule", "phase_planning", "assessment_points"]
            },
            "large_goal": {
                "name": "大目标计划",
                "description": "针对大型学习目标的季度计划",
                "components": ["quarterly_schedule", "module_planning", "evaluation_stages"]
            },
            "massive_goal": {
                "name": "大规模目标计划",
                "description": "针对超大规模学习目标的年度计划",
                "components": ["annual_schedule", "project_planning", "comprehensive_reviews"]
            }
        }

        # 学习阶段配置
        self.learning_phases = {
            "exploration": {
                "name": "探索阶段",
                "duration_ratio": 0.1,
                "activities": ["概览学习", "建立认知", "识别重点"]
            },
            "acquisition": {
                "name": "获取阶段",
                "duration_ratio": 0.4,
                "activities": ["系统学习", "理解概念", "掌握技能"]
            },
            "practice": {
                "name": "实践阶段",
                "duration_ratio": 0.3,
                "activities": ["应用练习", "解决问题", "项目实践"]
            },
            "review": {
                "name": "复习阶段",
                "duration_ratio": 0.1,
                "activities": ["巩固记忆", "查漏补缺", "系统回顾"]
            },
            "integration": {
                "name": "整合阶段",
                "duration_ratio": 0.1,
                "activities": ["知识整合", "创新应用", "体系构建"]
            }
        }

    def create_learning_plan(self,
                           goal: LearningGoal,
                           mindmap_root: Optional[MindMapNode] = None,
                           node_map: Optional[Dict[str, MindMapNode]] = None,
                           allocation_plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建学习计划

        Args:
            goal: 学习目标
            mindmap_root: 思维导图根节点
            node_map: 节点映射
            allocation_plan: 分配计划

        Returns:
            学习计划
        """
        print(f"📋 创建学习计划: {goal.description}")

        learning_plan = {
            "goal_id": goal.id,
            "goal_description": goal.description,
            "created_at": datetime.now().isoformat(),
            "plan_type": "mindmap_driven",
            "plan_components": {},
            "timeline": {},
            "milestones": [],
            "schedules": {},
            "review_plan": {},
            "assessment_plan": {}
        }

        # 确定计划类型
        plan_type = self._determine_plan_type(goal)
        learning_plan["plan_type"] = plan_type

        # 获取模板
        template = self.planning_templates.get(plan_type, self.planning_templates["medium_goal"])
        learning_plan["template_used"] = template

        # 如果提供了分配计划，使用它
        if allocation_plan:
            learning_plan["allocation_plan"] = allocation_plan
            sequences = allocation_plan.get("learning_sequences", [])
            time_allocation = allocation_plan.get("time_allocation", {})
        else:
            # 创建基本分配
            sequences = self._create_basic_sequences(goal, node_map)
            time_allocation = {}

        # 创建时间线
        timeline = self._create_timeline(goal, sequences, time_allocation)
        learning_plan["timeline"] = timeline

        # 创建里程碑
        milestones = self._create_milestones(goal, sequences, timeline)
        learning_plan["milestones"] = milestones

        # 创建详细日程
        schedules = self._create_detailed_schedules(goal, sequences, timeline)
        learning_plan["schedules"] = schedules

        # 创建复习计划
        review_plan = self._create_review_plan(goal, sequences, timeline)
        learning_plan["review_plan"] = review_plan

        # 创建评估计划
        assessment_plan = self._create_assessment_plan(goal, milestones, timeline)
        learning_plan["assessment_plan"] = assessment_plan

        # 整合所有组件
        learning_plan["plan_components"] = self._integrate_plan_components(
            goal, timeline, milestones, schedules, review_plan, assessment_plan
        )

        # 生成计划摘要
        learning_plan["summary"] = self._generate_plan_summary(learning_plan)

        print(f"✅ 学习计划创建完成: {len(milestones)}个里程碑，{len(schedules.get('weekly_schedules', []))}周计划")
        return learning_plan

    def create_adaptive_plan(self,
                           goal: LearningGoal,
                           learning_history: List[Dict[str, Any]],
                           current_progress: Dict[str, Any],
                           available_time_per_week: int = 10) -> Dict[str, Any]:
        """
        创建自适应学习计划

        Args:
            goal: 学习目标
            learning_history: 学习历史
            current_progress: 当前进度
            available_time_per_week: 每周可用时间（小时）

        Returns:
            自适应学习计划
        """
        print(f"🔄 创建自适应学习计划")

        adaptive_plan = {
            "goal_id": goal.id,
            "created_at": datetime.now().isoformat(),
            "plan_type": "adaptive",
            "learning_profile": {},
            "adaptive_strategies": [],
            "flexible_schedule": {},
            "adjustment_rules": [],
            "contingency_plans": []
        }

        # 分析学习历史
        learning_profile = self._analyze_learning_profile(learning_history)
        adaptive_plan["learning_profile"] = learning_profile

        # 确定自适应策略
        strategies = self._determine_adaptive_strategies(learning_profile, current_progress)
        adaptive_plan["adaptive_strategies"] = strategies

        # 创建弹性时间表
        flexible_schedule = self._create_flexible_schedule(
            goal, available_time_per_week, learning_profile
        )
        adaptive_plan["flexible_schedule"] = flexible_schedule

        # 创建调整规则
        adjustment_rules = self._create_adjustment_rules(learning_profile, current_progress)
        adaptive_plan["adjustment_rules"] = adjustment_rules

        # 创建应急计划
        contingency_plans = self._create_contingency_plans(goal, learning_profile)
        adaptive_plan["contingency_plans"] = contingency_plans

        # 生成建议
        adaptive_plan["recommendations"] = self._generate_adaptive_recommendations(
            adaptive_plan, goal, current_progress
        )

        return adaptive_plan

    def adjust_plan_based_on_progress(self,
                                    original_plan: Dict[str, Any],
                                    progress_data: Dict[str, Any],
                                    learning_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        基于进度调整学习计划

        Args:
            original_plan: 原始计划
            progress_data: 进度数据
            learning_history: 学习历史

        Returns:
            调整后的计划
        """
        print(f"🔄 基于进度调整学习计划")

        adjusted_plan = original_plan.copy()
        adjusted_plan["last_adjusted_at"] = datetime.now().isoformat()
        adjusted_plan["adjustments_made"] = []

        # 提取进度信息
        current_progress = progress_data.get("overall_progress", 0)
        expected_progress = self._calculate_expected_progress(original_plan)
        progress_delta = current_progress - expected_progress

        mastered_nodes = progress_data.get("mastered_nodes", [])
        struggling_nodes = progress_data.get("struggling_nodes", [])
        learning_speed = progress_data.get("learning_speed", 1.0)

        # 调整时间线
        if "timeline" in adjusted_plan:
            timeline = adjusted_plan["timeline"]

            # 根据进度差异调整时间线
            if abs(progress_delta) > 0.1:  # 进度偏差超过10%
                if progress_delta > 0:
                    # 进度超前，可以缩短时间或增加内容
                    adjustment = self._adjust_for_ahead_schedule(timeline, progress_delta)
                    adjusted_plan["adjustments_made"].append(adjustment)
                else:
                    # 进度落后，需要延长时间或减少内容
                    adjustment = self._adjust_for_behind_schedule(timeline, abs(progress_delta))
                    adjusted_plan["adjustments_made"].append(adjustment)

            adjusted_plan["timeline"] = timeline

        # 调整里程碑
        if "milestones" in adjusted_plan:
            milestones = adjusted_plan["milestones"]
            adjusted_milestones = []

            for milestone in milestones:
                # 检查里程碑是否已达成
                if milestone.get("achieved", False):
                    adjusted_milestones.append(milestone)
                    continue

                # 调整未达成里程碑
                adjusted_milestone = self._adjust_milestone(
                    milestone, progress_data, learning_history
                )
                adjusted_milestones.append(adjusted_milestone)

            adjusted_plan["milestones"] = adjusted_milestones

        # 调整日程安排
        if "schedules" in adjusted_plan:
            schedules = adjusted_plan["schedules"]

            # 根据学习速度调整
            if learning_speed != 1.0:
                schedules = self._adjust_schedules_for_speed(schedules, learning_speed)
                adjusted_plan["adjustments_made"].append(
                    f"根据学习速度({learning_speed:.2f}x)调整日程"
                )

            # 如果有困难节点，调整日程
            if struggling_nodes:
                schedules = self._adjust_schedules_for_difficulty(schedules, struggling_nodes)
                adjusted_plan["adjustments_made"].append(
                    f"为{len(struggling_nodes)}个困难节点调整日程"
                )

            adjusted_plan["schedules"] = schedules

        # 生成调整摘要
        adjusted_plan["adjustment_summary"] = self._generate_adjustment_summary(
            adjusted_plan, progress_data
        )

        return adjusted_plan

    def _determine_plan_type(self, goal: LearningGoal) -> str:
        """确定计划类型"""
        if goal.scale == GoalScale.MICRO:
            return "micro_goal"
        elif goal.scale == GoalScale.SMALL:
            return "small_goal"
        elif goal.scale == GoalScale.MEDIUM:
            return "medium_goal"
        elif goal.scale == GoalScale.LARGE:
            return "large_goal"
        elif goal.scale == GoalScale.MASSIVE:
            return "massive_goal"
        else:
            return "medium_goal"

    def _create_basic_sequences(self,
                              goal: LearningGoal,
                              node_map: Optional[Dict[str, MindMapNode]]) -> List[Dict[str, Any]]:
        """创建基本学习序列"""
        if not node_map:
            # 如果没有节点映射，创建简单序列
            return [{
                "id": generate_id("basic_sequence_"),
                "name": "基础学习序列",
                "description": f"学习目标: {goal.description}",
                "node_ids": [],
                "node_count": goal.target_knowledge_count,
                "estimated_time_minutes": goal.target_knowledge_count * 30  # 每个知识点30分钟
            }]

        # 如果有节点映射，创建基于节点的序列
        total_nodes = len(node_map)
        if total_nodes <= 10:
            # 节点少，一个序列
            all_nodes = list(node_map.keys())
            return [{
                "id": generate_id("basic_sequence_"),
                "name": "完整学习序列",
                "description": "包含所有知识节点的学习序列",
                "node_ids": all_nodes,
                "node_count": total_nodes,
                "estimated_time_minutes": sum(
                    node.estimated_time_minutes for node in node_map.values()
                )
            }]
        else:
            # 节点多，分成多个序列
            sequence_count = min(4, total_nodes // 5)
            nodes_per_sequence = math.ceil(total_nodes / sequence_count)

            all_nodes = list(node_map.keys())
            sequences = []

            for i in range(sequence_count):
                start_idx = i * nodes_per_sequence
                end_idx = min((i + 1) * nodes_per_sequence, total_nodes)

                sequence_nodes = all_nodes[start_idx:end_idx]
                sequences.append({
                    "id": generate_id(f"basic_seq_{i}_"),
                    "name": f"学习序列 {i+1}",
                    "description": f"第{i+1}部分学习内容",
                    "node_ids": sequence_nodes,
                    "node_count": len(sequence_nodes),
                    "estimated_time_minutes": sum(
                        node_map[nid].estimated_time_minutes for nid in sequence_nodes
                    )
                })

            return sequences

    def _create_timeline(self,
                        goal: LearningGoal,
                        sequences: List[Dict[str, Any]],
                        time_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """创建学习时间线"""
        timeline = {
            "total_estimated_hours": 0,
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "phases": [],
            "weekly_breakdown": []
        }

        # 计算总时间
        total_minutes = sum(seq.get("estimated_time_minutes", 0) for seq in sequences)
        if total_minutes == 0 and goal.target_knowledge_count > 0:
            # 使用时间模型估算
            total_minutes = self.time_model.estimate_for_goal(goal)

        total_hours = total_minutes / 60
        timeline["total_estimated_hours"] = total_hours

        # 计算学习周期
        if total_hours <= 10:
            # 10小时以内：1周
            timeline_days = 7
            timeline_weeks = 1
        elif total_hours <= 40:
            # 10-40小时：2周
            timeline_days = 14
            timeline_weeks = 2
        elif total_hours <= 100:
            # 40-100小时：1个月
            timeline_days = 30
            timeline_weeks = 4
        elif total_hours <= 300:
            # 100-300小时：2个月
            timeline_days = 60
            timeline_weeks = 8
        else:
            # 300小时以上：3个月
            timeline_days = 90
            timeline_weeks = 12

        timeline["timeline_days"] = timeline_days
        timeline["timeline_weeks"] = timeline_weeks

        # 计算结束日期
        start_date = datetime.now()
        end_date = start_date + timedelta(days=timeline_days)
        timeline["end_date"] = end_date.isoformat()

        # 创建学习阶段
        phases = self._create_learning_phases(timeline_weeks, sequences)
        timeline["phases"] = phases

        # 创建每周分解
        weekly_breakdown = self._create_weekly_breakdown(
            timeline_weeks, sequences, total_hours
        )
        timeline["weekly_breakdown"] = weekly_breakdown

        return timeline

    def _create_learning_phases(self,
                               total_weeks: int,
                               sequences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """创建学习阶段"""
        phases = []

        # 确定阶段数量
        if total_weeks <= 2:
            phase_count = 2
        elif total_weeks <= 4:
            phase_count = 3
        elif total_weeks <= 8:
            phase_count = 4
        else:
            phase_count = 5

        # 分配阶段
        weeks_per_phase = math.ceil(total_weeks / phase_count)

        for i in range(phase_count):
            phase_start_week = i * weeks_per_phase + 1
            phase_end_week = min((i + 1) * weeks_per_phase, total_weeks)

            # 选择阶段类型
            phase_types = list(self.learning_phases.keys())
            phase_type = phase_types[i % len(phase_types)]
            phase_config = self.learning_phases[phase_type]

            # 分配序列（如果有）
            sequences_for_phase = []
            if sequences:
                # 简单分配：每个阶段分配一些序列
                seq_per_phase = math.ceil(len(sequences) / phase_count)
                start_seq = i * seq_per_phase
                end_seq = min((i + 1) * seq_per_phase, len(sequences))
                sequences_for_phase = sequences[start_seq:end_seq]

            phase = {
                "id": generate_id(f"phase_{i}_"),
                "name": phase_config["name"],
                "type": phase_type,
                "description": phase_config["description"] if "description" in phase_config else "",
                "start_week": phase_start_week,
                "end_week": phase_end_week,
                "duration_weeks": phase_end_week - phase_start_week + 1,
                "activities": phase_config["activities"],
                "sequences": sequences_for_phase,
                "focus_areas": self._determine_phase_focus(phase_type, sequences_for_phase)
            }

            phases.append(phase)

        return phases

    def _determine_phase_focus(self,
                             phase_type: str,
                             sequences: List[Dict[str, Any]]) -> List[str]:
        """确定阶段重点"""
        focus_areas = []

        if phase_type == "exploration":
            focus_areas = ["整体认知", "建立框架", "识别重点"]
        elif phase_type == "acquisition":
            focus_areas = ["概念理解", "知识获取", "基础建立"]
        elif phase_type == "practice":
            focus_areas = ["应用练习", "技能掌握", "问题解决"]
        elif phase_type == "review":
            focus_areas = ["巩固记忆", "查漏补缺", "系统回顾"]
        elif phase_type == "integration":
            focus_areas = ["知识整合", "创新应用", "体系构建"]

        # 根据序列内容调整
        if sequences:
            if any("高级" in seq.get("name", "") for seq in sequences):
                focus_areas.append("深度理解")
            if any("实践" in seq.get("name", "") for seq in sequences):
                focus_areas.append("实践应用")

        return focus_areas

    def _create_weekly_breakdown(self,
                                total_weeks: int,
                                sequences: List[Dict[str, Any]],
                                total_hours: float) -> List[Dict[str, Any]]:
        """创建每周分解"""
        weekly_breakdown = []

        # 计算每周学习小时数
        hours_per_week = math.ceil(total_hours / total_weeks)

        for week in range(1, total_weeks + 1):
            # 分配序列（如果有）
            sequences_for_week = []
            if sequences:
                # 简单轮转分配
                seq_index = (week - 1) % len(sequences)
                sequences_for_week = [sequences[seq_index]]

            week_plan = {
                "week_number": week,
                "focus": self._determine_weekly_focus(week, total_weeks),
                "estimated_hours": hours_per_week,
                "daily_recommendation": f"每日{math.ceil(hours_per_week / 7)}小时",
                "sequences": sequences_for_week,
                "key_activities": self._get_weekly_activities(week, total_weeks),
                "milestones": []  # 将在后面填充
            }

            weekly_breakdown.append(week_plan)

        return weekly_breakdown

    def _determine_weekly_focus(self, week: int, total_weeks: int) -> str:
        """确定每周重点"""
        if week == 1:
            return "建立学习习惯，熟悉学习内容"
        elif week <= total_weeks // 3:
            return "系统学习，建立知识基础"
        elif week <= total_weeks * 2 // 3:
            return "深化理解，加强实践应用"
        elif week == total_weeks:
            return "总结回顾，整合知识体系"
        else:
            return "巩固提高，准备下一阶段"

    def _get_weekly_activities(self, week: int, total_weeks: int) -> List[str]:
        """获取每周活动"""
        activities = []

        # 每周基础活动
        base_activities = ["学习新知识", "完成练习", "复习巩固"]
        activities.extend(base_activities)

        # 特殊周活动
        if week == 1:
            activities.append("制定详细计划")
        elif week % 2 == 0:
            activities.append("进行小测验")
        elif week % 4 == 0:
            activities.append("进行阶段评估")

        if week == total_weeks:
            activities.append("进行最终总结")

        return activities

    def _create_milestones(self,
                          goal: LearningGoal,
                          sequences: List[Dict[str, Any]],
                          timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建里程碑"""
        milestones = []

        total_weeks = timeline.get("timeline_weeks", 4)
        phases = timeline.get("phases", [])

        # 阶段里程碑
        for phase in phases:
            milestone = {
                "id": generate_id(f"milestone_phase_{phase.get('name', '')}_"),
                "name": f"完成{phase.get('name', '')}",
                "type": "phase_completion",
                "description": f"完成{phase.get('name', '')}的学习",
                "target_week": phase.get("end_week", 0),
                "success_criteria": [
                    f"完成{phase.get('name', '')}的所有学习活动",
                    f"掌握{phase.get('name', '')}的核心概念"
                ],
                "reward": f"庆祝{phase.get('name', '')}完成，短暂休息"
            }
            milestones.append(milestone)

        # 序列里程碑（如果有序列）
        if sequences:
            for i, seq in enumerate(sequences):
                milestone_week = min((i + 1) * total_weeks // len(sequences), total_weeks)
                milestone = {
                    "id": generate_id(f"milestone_seq_{i}_"),
                    "name": f"完成{seq.get('name', f'序列{i+1}')}",
                    "type": "sequence_completion",
                    "description": f"完成{seq.get('name', f'第{i+1}个学习序列')}",
                    "target_week": milestone_week,
                    "success_criteria": [
                        f"完成{seq.get('name', f'序列{i+1}')}的所有学习内容",
                        f"通过{seq.get('name', f'序列{i+1}')}的测试"
                    ],
                    "reward": "继续下一阶段学习"
                }
                milestones.append(milestone)

        # 时间里程碑
        time_milestones = [
            (total_weeks // 4, "完成第一月学习", "检查学习进度，调整计划"),
            (total_weeks // 2, "完成一半学习", "进行中期评估，总结学习成果"),
            (total_weeks * 3 // 4, "完成第三月学习", "加强薄弱环节，准备最后冲刺"),
            (total_weeks, "完成全部学习", "进行最终评估，庆祝学习成果")
        ]

        for week, name, description in time_milestones:
            if week <= total_weeks:
                milestone = {
                    "id": generate_id(f"milestone_time_{week}_"),
                    "name": name,
                    "type": "time_based",
                    "description": description,
                    "target_week": week,
                    "success_criteria": [f"按计划完成第{week}周学习"],
                    "reward": "成就感奖励"
                }
                milestones.append(milestone)

        # 按目标周排序
        milestones.sort(key=lambda x: x.get("target_week", 0))

        return milestones

    def _create_detailed_schedules(self,
                                 goal: LearningGoal,
                                 sequences: List[Dict[str, Any]],
                                 timeline: Dict[str, Any]) -> Dict[str, Any]:
        """创建详细日程"""
        schedules = {
            "weekly_schedules": [],
            "daily_templates": [],
            "time_blocks": []
        }

        total_weeks = timeline.get("timeline_weeks", 4)
        weekly_breakdown = timeline.get("weekly_breakdown", [])

        # 创建每周日程
        for week_plan in weekly_breakdown:
            week_number = week_plan.get("week_number", 1)
            weekly_schedule = self._create_weekly_schedule(week_plan, week_number)
            schedules["weekly_schedules"].append(weekly_schedule)

        # 创建每日模板
        daily_templates = self._create_daily_templates(goal)
        schedules["daily_templates"] = daily_templates

        # 创建时间块
        time_blocks = self._create_time_blocks()
        schedules["time_blocks"] = time_blocks

        return schedules

    def _create_weekly_schedule(self, week_plan: Dict[str, Any], week_number: int) -> Dict[str, Any]:
        """创建周日程"""
        weekly_schedule = {
            "week_number": week_number,
            "focus": week_plan.get("focus", ""),
            "estimated_hours": week_plan.get("estimated_hours", 10),
            "daily_breakdown": []
        }

        # 每日学习时间分配（假设每周学习5天）
        daily_hours = math.ceil(week_plan.get("estimated_hours", 10) / 5)

        # 创建每日计划
        for day in range(1, 6):  # 周一至周五
            daily_plan = {
                "day": day,
                "day_name": ["周一", "周二", "周三", "周四", "周五"][day-1],
                "estimated_hours": daily_hours,
                "focus_areas": self._get_daily_focus_areas(day, week_number),
                "activities": self._get_daily_activities(day, week_number),
                "time_slots": self._create_daily_time_slots(daily_hours)
            }
            weekly_schedule["daily_breakdown"].append(daily_plan)

        # 周末计划
        weekend_plan = {
            "day": 6,
            "day_name": "周末",
            "estimated_hours": 2,  # 周末复习2小时
            "focus_areas": ["复习", "整理", "计划"],
            "activities": ["复习本周内容", "整理学习笔记", "制定下周计划"],
            "time_slots": [{"time": "灵活安排", "activity": "周末复习"}]
        }
        weekly_schedule["daily_breakdown"].append(weekend_plan)

        return weekly_schedule

    def _get_daily_focus_areas(self, day: int, week: int) -> List[str]:
        """获取每日重点领域"""
        focus_pattern = [
            ["新知识学习", "概念理解"],
            ["深化理解", "练习应用"],
            ["技能训练", "实践操作"],
            ["复习巩固", "查漏补缺"],
            ["整合应用", "创新思考"]
        ]

        pattern_index = (day - 1) % len(focus_pattern)
        return focus_pattern[pattern_index]

    def _get_daily_activities(self, day: int, week: int) -> List[str]:
        """获取每日活动"""
        base_activities = ["阅读学习材料", "完成练习", "复习笔记"]

        # 每周第一天添加计划活动
        if day == 1:
            base_activities.append("制定本周计划")

        # 每周最后一天添加总结活动
        if day == 5:
            base_activities.append("本周总结")

        # 特殊活动
        if week % 2 == 0 and day == 3:
            base_activities.append("进行小测验")

        return base_activities

    def _create_daily_time_slots(self, daily_hours: int) -> List[Dict[str, str]]:
        """创建每日时间块"""
        # 假设学习时间分布在多个时间段
        time_slots = []

        if daily_hours >= 3:
            # 长时间学习：分多个时间段
            slots = [
                {"time": "09:00-10:30", "activity": "上午学习", "duration": 90},
                {"time": "14:00-15:30", "activity": "下午学习", "duration": 90},
                {"time": "20:00-21:00", "activity": "晚间复习", "duration": 60}
            ]
        elif daily_hours >= 2:
            # 中等时间学习
            slots = [
                {"time": "19:00-20:30", "activity": "晚间学习", "duration": 90},
                {"time": "21:00-21:30", "activity": "晚间复习", "duration": 30}
            ]
        else:
            # 短时间学习
            slots = [
                {"time": "20:00-21:00", "activity": "集中学习", "duration": 60}
            ]

        return slots

    def _create_daily_templates(self, goal: LearningGoal) -> List[Dict[str, Any]]:
        """创建每日模板"""
        templates = []

        # 高强度学习日模板
        templates.append({
            "name": "高强度学习日",
            "description": "专注深度学习和复杂任务",
            "total_hours": 3,
            "time_blocks": [
                {"time": "09:00-10:30", "activity": "深度学习", "focus": "复杂概念"},
                {"time": "14:00-15:30", "activity": "实践练习", "focus": "技能应用"},
                {"time": "20:00-21:00", "activity": "复习总结", "focus": "知识巩固"}
            ],
            "suitable_for": ["重要概念学习", "技能训练", "项目实践"]
        })

        # 中等强度学习日模板
        templates.append({
            "name": "中等强度学习日",
            "description": "平衡学习和复习",
            "total_hours": 2,
            "time_blocks": [
                {"time": "19:00-20:30", "activity": "系统学习", "focus": "新知识获取"},
                {"time": "21:00-21:30", "activity": "快速复习", "focus": "记忆巩固"}
            ],
            "suitable_for": ["日常学习", "知识积累", "进度维持"]
        })

        # 低强度学习日模板
        templates.append({
            "name": "低强度学习日",
            "description": "轻量学习和复习",
            "total_hours": 1,
            "time_blocks": [
                {"time": "20:00-21:00", "activity": "集中学习", "focus": "重点复习"}
            ],
            "suitable_for": ["忙碌日子", "复习巩固", "保持学习习惯"]
        })

        return templates

    def _create_time_blocks(self) -> List[Dict[str, Any]]:
        """创建时间块"""
        time_blocks = [
            {
                "name": "清晨学习块",
                "time_range": "06:00-08:00",
                "duration_minutes": 120,
                "characteristics": ["头脑清醒", "记忆力好", "干扰少"],
                "suitable_activities": ["记忆性学习", "概念理解", "计划制定"]
            },
            {
                "name": "上午学习块",
                "time_range": "09:00-12:00",
                "duration_minutes": 180,
                "characteristics": ["精力充沛", "专注度高", "效率高"],
                "suitable_activities": ["深度学习", "复杂任务", "项目工作"]
            },
            {
                "name": "下午学习块",
                "time_range": "14:00-17:00",
                "duration_minutes": 180,
                "characteristics": ["稳定发挥", "适合实践", "互动性好"],
                "suitable_activities": ["实践练习", "小组学习", "技能训练"]
            },
            {
                "name": "晚间学习块",
                "time_range": "19:00-22:00",
                "duration_minutes": 180,
                "characteristics": ["安静环境", "适合复习", "总结整理"],
                "suitable_activities": ["复习巩固", "知识整理", "计划反思"]
            }
        ]

        return time_blocks

    def _create_review_plan(self,
                          goal: LearningGoal,
                          sequences: List[Dict[str, Any]],
                          timeline: Dict[str, Any]) -> Dict[str, Any]:
        """创建复习计划"""
        review_plan = {
            "review_strategy": "spaced_repetition",
            "review_schedule": [],
            "review_methods": [],
            "review_checkpoints": []
        }

        total_weeks = timeline.get("timeline_weeks", 4)

        # 复习时间表（基于间隔重复）
        review_intervals = [1, 3, 7, 14, 30]  # 学习后的第几天复习

        for interval in review_intervals:
            review_plan["review_schedule"].append({
                "interval_days": interval,
                "review_type": "spaced_repetition",
                "focus": "记忆巩固",
                "methods": ["快速回顾", "自我测试", "概念复述"]
            })

        # 复习方法
        review_methods = [
            {
                "name": "主动回忆",
                "description": "不看书本，尝试回忆学习内容",
                "effectiveness": "高",
                "time_required": "中"
            },
            {
                "name": "自我测试",
                "description": "通过测试题检查掌握程度",
                "effectiveness": "高",
                "time_required": "中"
            },
            {
                "name": "概念图",
                "description": "绘制概念关系图",
                "effectiveness": "中",
                "time_required": "高"
            },
            {
                "name": "费曼技巧",
                "description": "用简单语言解释复杂概念",
                "effectiveness": "高",
                "time_required": "中"
            }
        ]
        review_plan["review_methods"] = review_methods

        # 复习检查点
        if total_weeks >= 4:
            checkpoints = [
                {"week": 1, "type": "周复习", "focus": "第一周内容"},
                {"week": 2, "type": "双周复习", "focus": "前两周内容"},
                {"week": 4, "type": "月复习", "focus": "整月内容"}
            ]
            if total_weeks >= 8:
                checkpoints.append({"week": 8, "type": "中期复习", "focus": "前半段内容"})
            if total_weeks >= 12:
                checkpoints.append({"week": 12, "type": "最终复习", "focus": "全部内容"})

            review_plan["review_checkpoints"] = checkpoints

        return review_plan

    def _create_assessment_plan(self,
                              goal: LearningGoal,
                              milestones: List[Dict[str, Any]],
                              timeline: Dict[str, Any]) -> Dict[str, Any]:
        """创建评估计划"""
        assessment_plan = {
            "assessment_types": [],
            "assessment_schedule": [],
            "evaluation_criteria": [],
            "feedback_mechanisms": []
        }

        # 评估类型
        assessment_types = [
            {
                "name": "形成性评估",
                "purpose": "学习过程中的持续评估",
                "methods": ["自我测试", "小测验", "学习日记"],
                "frequency": "每周"
            },
            {
                "name": "总结性评估",
                "purpose": "阶段性的综合评估",
                "methods": ["阶段考试", "项目评估", "综合测试"],
                "frequency": "每月"
            },
            {
                "name": "诊断性评估",
                "purpose": "识别学习困难和需求",
                "methods": ["前测", "知识地图", "学习分析"],
                "frequency": "学习开始时和需要时"
            }
        ]
        assessment_plan["assessment_types"] = assessment_types

        # 评估时间表
        total_weeks = timeline.get("timeline_weeks", 4)

        for week in range(1, total_weeks + 1):
            assessments = []

            # 每周小测验
            if week % 2 == 0:  # 每两周一次
                assessments.append({
                    "type": "小测验",
                    "purpose": "检查周学习成果",
                    "estimated_time": "30分钟"
                })

            # 里程碑评估
            for milestone in milestones:
                if milestone.get("target_week") == week:
                    assessments.append({
                        "type": "里程碑评估",
                        "purpose": f"评估{milestone.get('name')}完成情况",
                        "estimated_time": "60分钟"
                    })

            if assessments:
                assessment_plan["assessment_schedule"].append({
                    "week": week,
                    "assessments": assessments
                })

        # 评估标准
        assessment_plan["evaluation_criteria"] = [
            {"criterion": "知识掌握", "weight": 0.4, "description": "对学习内容的掌握程度"},
            {"criterion": "技能应用", "weight": 0.3, "description": "将知识应用于实际问题的能力"},
            {"criterion": "学习进步", "weight": 0.2, "description": "相比之前的学习进步"},
            {"criterion": "学习参与", "weight": 0.1, "description": "学习过程中的参与和投入程度"}
        ]

        # 反馈机制
        assessment_plan["feedback_mechanisms"] = [
            {"mechanism": "自我反馈", "frequency": "每日", "format": "学习日记"},
            {"mechanism": "系统反馈", "frequency": "每次评估后", "format": "评估报告"},
            {"mechanism": "同伴反馈", "frequency": "每周", "format": "学习小组讨论"},
            {"mechanism": "专家反馈", "frequency": "每月", "format": "指导会议"}
        ]

        return assessment_plan

    def _integrate_plan_components(self,
                                 goal: LearningGoal,
                                 timeline: Dict[str, Any],
                                 milestones: List[Dict[str, Any]],
                                 schedules: Dict[str, Any],
                                 review_plan: Dict[str, Any],
                                 assessment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """整合计划组件"""
        integrated_components = {
            "timeline_integration": {
                "total_weeks": timeline.get("timeline_weeks", 0),
                "start_date": timeline.get("start_date"),
                "end_date": timeline.get("end_date"),
                "milestone_count": len(milestones),
                "weekly_schedule_count": len(schedules.get("weekly_schedules", [])),
                "review_checkpoints": len(review_plan.get("review_checkpoints", [])),
                "assessment_schedule": len(assessment_plan.get("assessment_schedule", []))
            },
            "component_links": [],
            "coordination_points": []
        }

        # 创建组件链接
        for milestone in milestones:
            milestone_week = milestone.get("target_week", 0)

            # 链接到周计划
            for weekly_schedule in schedules.get("weekly_schedules", []):
                if weekly_schedule.get("week_number") == milestone_week:
                    integrated_components["component_links"].append({
                        "from": f"milestone_{milestone.get('name')}",
                        "to": f"weekly_schedule_week_{milestone_week}",
                        "relationship": "里程碑对应周计划"
                    })

            # 链接到复习检查点
            for checkpoint in review_plan.get("review_checkpoints", []):
                if checkpoint.get("week") == milestone_week:
                    integrated_components["component_links"].append({
                        "from": f"milestone_{milestone.get('name')}",
                        "to": f"review_checkpoint_week_{milestone_week}",
                        "relationship": "里程碑对应复习点"
                    })

        # 创建协调点
        coordination_points = []

        # 每周协调点
        for week in range(1, timeline.get("timeline_weeks", 0) + 1):
            coordination_points.append({
                "week": week,
                "activities": [
                    "检查周计划完成情况",
                    "调整下周计划",
                    "进行周复习",
                    "记录学习进展"
                ],
                "estimated_time": "60分钟"
            })

        # 里程碑协调点
        for milestone in milestones:
            coordination_points.append({
                "milestone": milestone.get("name"),
                "week": milestone.get("target_week"),
                "activities": [
                    f"评估{milestone.get('name')}完成情况",
                    "庆祝里程碑达成",
                    "调整后续计划",
                    "进行阶段性总结"
                ],
                "estimated_time": "90分钟"
            })

        integrated_components["coordination_points"] = coordination_points

        return integrated_components

    def _generate_plan_summary(self, learning_plan: Dict[str, Any]) -> Dict[str, Any]:
        """生成计划摘要"""
        timeline = learning_plan.get("timeline", {})
        milestones = learning_plan.get("milestones", [])
        schedules = learning_plan.get("schedules", {})

        summary = {
            "overview": {
                "total_weeks": timeline.get("timeline_weeks", 0),
                "total_milestones": len(milestones),
                "weekly_schedules": len(schedules.get("weekly_schedules", [])),
                "estimated_total_hours": timeline.get("total_estimated_hours", 0)
            },
            "key_dates": {
                "start_date": timeline.get("start_date"),
                "end_date": timeline.get("end_date"),
                "key_milestones": [
                    {
                        "name": milestone.get("name"),
                        "week": milestone.get("target_week"),
                        "type": milestone.get("type")
                    }
                    for milestone in milestones[:3]  # 只显示前3个重要里程碑
                ]
            },
            "weekly_commitment": {
                "average_hours_per_week": math.ceil(
                    timeline.get("total_estimated_hours", 0) / timeline.get("timeline_weeks", 1)
                ),
                "learning_days_per_week": 5,
                "daily_average_hours": math.ceil(
                    timeline.get("total_estimated_hours", 0) / (timeline.get("timeline_weeks", 1) * 5)
                )
            },
            "success_factors": [
                "坚持每日学习",
                "定期复习巩固",
                "积极参与评估",
                "及时调整计划"
            ]
        }

        return summary

    def _analyze_learning_profile(self, learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析学习画像"""
        if not learning_history:
            return {"message": "无学习历史数据"}

        profile = {
            "total_sessions": len(learning_history),
            "learning_patterns": {},
            "preferences": {},
            "strengths": [],
            "weaknesses": []
        }

        # 分析学习时间模式
        session_times = []
        session_durations = []

        for session in learning_history:
            # 记录会话时间（假设有timestamp字段）
            if "timestamp" in session:
                session_time = datetime.fromisoformat(session["timestamp"]).hour
                session_times.append(session_time)

            # 记录会话时长（假设有duration_minutes字段）
            if "duration_minutes" in session:
                session_durations.append(session["duration_minutes"])

        if session_times:
            # 分析最佳学习时间
            time_counts = {}
            for hour in session_times:
                time_counts[hour] = time_counts.get(hour, 0) + 1

            if time_counts:
                best_hour = max(time_counts.items(), key=lambda x: x[1])[0]
                profile["learning_patterns"]["preferred_time"] = f"{best_hour}:00-{best_hour+1}:00"

        if session_durations:
            avg_duration = statistics.mean(session_durations)
            profile["learning_patterns"]["average_session_duration"] = avg_duration

        # 分析学习偏好（从历史中提取）
        # 这里简化处理，实际中需要更复杂的分析
        profile["preferences"] = {
            "learning_style": "balanced",  # 可以从历史中分析
            "preferred_content_type": "mixed",
            "interaction_level": "medium"
        }

        return profile

    def _determine_adaptive_strategies(self,
                                     learning_profile: Dict[str, Any],
                                     current_progress: Dict[str, Any]) -> List[Dict[str, Any]]:
        """确定自适应策略"""
        strategies = []

        # 基于学习时间的策略
        if "preferred_time" in learning_profile.get("learning_patterns", {}):
            strategies.append({
                "strategy": "时间优化",
                "description": f"在{learning_profile['learning_patterns']['preferred_time']}进行主要学习",
                "implementation": "安排重要学习任务在最佳时间段"
            })

        # 基于学习时长的策略
        avg_duration = learning_profile.get("learning_patterns", {}).get("average_session_duration", 0)
        if avg_duration > 0:
            if avg_duration < 30:
                strategies.append({
                    "strategy": "短时高效",
                    "description": "学习会话较短，采用高效学习方法",
                    "implementation": "使用番茄工作法，25分钟专注学习"
                })
            elif avg_duration > 90:
                strategies.append({
                    "strategy": "深度专注",
                    "description": "能够长时间专注学习",
                    "implementation": "安排长时间深度学习任务"
                })

        # 基于进度的策略
        progress = current_progress.get("overall_progress", 0)
        if progress < 0.3:
            strategies.append({
                "strategy": "建立基础",
                "description": "学习初期，重点建立基础",
                "implementation": "放慢节奏，确保基础概念掌握"
            })
        elif progress > 0.7:
            strategies.append({
                "strategy": "加速推进",
                "description": "学习后期，可以加速推进",
                "implementation": "增加学习强度，快速完成剩余内容"
            })

        return strategies

    def _create_flexible_schedule(self,
                                goal: LearningGoal,
                                available_time_per_week: int,
                                learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """创建弹性时间表"""
        flexible_schedule = {
            "available_hours_per_week": available_time_per_week,
            "minimum_weekly_hours": max(2, available_time_per_week // 2),
            "maximum_weekly_hours": min(20, available_time_per_week * 2),
            "flexible_days": [],
            "backup_time_slots": []
        }

        # 确定灵活学习日
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        flexible_days = []

        # 基于可用时间确定灵活日
        if available_time_per_week >= 10:
            # 时间充足，工作日学习
            flexible_days = days[:5]
        else:
            # 时间有限，集中在少数几天
            flexible_days = days[:3] + [days[-1]]  # 周一到周三加周日

        flexible_schedule["flexible_days"] = flexible_days

        # 创建备用时间段
        backup_slots = [
            {"day": "周末", "time": "09:00-12:00", "purpose": "补学未完成内容"},
            {"day": "工作日", "time": "20:00-22:00", "purpose": "日常学习"}
        ]

        # 如果有偏好的学习时间，优先使用
        preferred_time = learning_profile.get("learning_patterns", {}).get("preferred_time", "")
        if preferred_time:
            backup_slots.insert(0, {
                "day": "最佳时间",
                "time": preferred_time,
                "purpose": "高效学习时间段"
            })

        flexible_schedule["backup_time_slots"] = backup_slots

        return flexible_schedule

    def _create_adjustment_rules(self,
                               learning_profile: Dict[str, Any],
                               current_progress: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建调整规则"""
        rules = []

        # 进度调整规则
        rules.append({
            "rule_id": "progress_adjustment",
            "condition": "进度落后计划10%以上",
            "action": "增加每周学习时间10%",
            "priority": "high"
        })

        rules.append({
            "rule_id": "progress_ahead",
            "condition": "进度超前计划20%以上",
            "action": "可以提前学习后续内容或增加难度",
            "priority": "medium"
        })

        # 时间调整规则
        rules.append({
            "rule_id": "time_constraint",
            "condition": "连续3天未达到每日学习目标",
            "action": "重新评估时间分配，调整学习计划",
            "priority": "high"
        })

        # 难度调整规则
        rules.append({
            "rule_id": "difficulty_adjustment",
            "condition": "连续3个学习会话遇到困难",
            "action": "降低学习难度，增加基础练习",
            "priority": "medium"
        })

        # 参与度调整规则
        rules.append({
            "rule_id": "engagement_adjustment",
            "condition": "学习参与度连续下降",
            "action": "改变学习方式，增加互动元素",
            "priority": "medium"
        })

        return rules

    def _create_contingency_plans(self,
                                goal: LearningGoal,
                                learning_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建应急计划"""
        contingency_plans = []

        # 时间不足应急计划
        contingency_plans.append({
            "scenario": "时间严重不足",
            "probability": "medium",
            "impact": "high",
            "response": [
                "聚焦核心概念，跳过次要内容",
                "采用高效学习方法（如费曼技巧）",
                "延长学习周期，降低每周强度"
            ],
            "trigger": "可用时间减少50%以上"
        })

        # 学习困难应急计划
        contingency_plans.append({
            "scenario": "遇到学习瓶颈",
            "probability": "high",
            "impact": "medium",
            "response": [
                "寻求外部帮助（导师、学习小组）",
                "改变学习策略",
                "暂时切换学习内容，避免倦怠"
            ],
            "trigger": "连续2周无明显进步"
        })

        # 动力不足应急计划
        contingency_plans.append({
            "scenario": "学习动力下降",
            "probability": "medium",
            "impact": "medium",
            "response": [
                "设置小奖励机制",
                "寻找学习伙伴",
                "回顾学习初衷和目标"
            ],
            "trigger": "连续3天缺乏学习动力"
        })

        return contingency_plans

    def _generate_adaptive_recommendations(self,
                                         adaptive_plan: Dict[str, Any],
                                         goal: LearningGoal,
                                         current_progress: Dict[str, Any]) -> List[str]:
        """生成自适应建议"""
        recommendations = []

        # 基于学习画像的建议
        learning_profile = adaptive_plan.get("learning_profile", {})
        if "preferred_time" in learning_profile.get("learning_patterns", {}):
            recommendations.append(
                f"根据历史数据，建议在{learning_profile['learning_patterns']['preferred_time']}进行主要学习"
            )

        # 基于可用时间的建议
        available_time = adaptive_plan.get("flexible_schedule", {}).get("available_hours_per_week", 0)
        if available_time < 5:
            recommendations.append("每周可用时间有限，建议采用高效学习方法")
        elif available_time > 15:
            recommendations.append("每周可用时间充足，可以安排深度学习和实践")

        # 基于进度的建议
        progress = current_progress.get("overall_progress", 0)
        if progress > 0 and progress < 0.3:
            recommendations.append("学习初期，建议放慢节奏打好基础")
        elif progress > 0.7:
            recommendations.append("学习后期，可以加速完成剩余内容")

        return recommendations

    def _calculate_expected_progress(self, plan: Dict[str, Any]) -> float:
        """计算预期进度"""
        timeline = plan.get("timeline", {})
        created_at = plan.get("created_at")

        if not created_at or "start_date" not in timeline:
            return 0.0

        try:
            start_date = datetime.fromisoformat(timeline["start_date"])
            current_date = datetime.now()

            # 计算已过时间比例
            if "end_date" in timeline:
                end_date = datetime.fromisoformat(timeline["end_date"])
                total_days = (end_date - start_date).days
                elapsed_days = (current_date - start_date).days

                if total_days > 0:
                    return min(max(elapsed_days / total_days, 0.0), 1.0)

            # 如果没有结束日期，使用周数估算
            total_weeks = timeline.get("timeline_weeks", 4)
            if total_weeks > 0:
                # 假设每周进度均匀
                elapsed_days = (current_date - start_date).days
                elapsed_weeks = elapsed_days / 7
                return min(max(elapsed_weeks / total_weeks, 0.0), 1.0)

        except Exception as e:
            print(f"❌ 计算预期进度失败: {str(e)}")

        return 0.0

    def _adjust_for_ahead_schedule(self,
                                 timeline: Dict[str, Any],
                                 progress_delta: float) -> Dict[str, Any]:
        """为进度超前调整时间线"""
        adjustment = {
            "type": "ahead_schedule",
            "progress_delta": progress_delta,
            "actions": []
        }

        # 如果进度超前超过20%，可以考虑提前结束
        if progress_delta > 0.2:
            adjustment["actions"].append("考虑提前完成学习目标")
            adjustment["actions"].append("可以增加学习内容深度")

        # 如果进度超前10-20%，可以保持节奏或增加内容
        elif progress_delta > 0.1:
            adjustment["actions"].append("保持当前学习节奏")
            adjustment["actions"].append("可以考虑增加扩展学习")

        return adjustment

    def _adjust_for_behind_schedule(self,
                                  timeline: Dict[str, Any],
                                  progress_delta: float) -> Dict[str, Any]:
        """为进度落后调整时间线"""
        adjustment = {
            "type": "behind_schedule",
            "progress_delta": progress_delta,
            "actions": []
        }

        # 如果进度落后超过20%，需要大幅调整
        if progress_delta > 0.2:
            adjustment["actions"].append("需要大幅增加学习时间")
            adjustment["actions"].append("考虑延长学习周期")
            adjustment["actions"].append("聚焦核心内容，跳过次要部分")

        # 如果进度落后10-20%，需要适当调整
        elif progress_delta > 0.1:
            adjustment["actions"].append("适当增加每周学习时间")
            adjustment["actions"].append("加强薄弱环节学习")
            adjustment["actions"].append("优化学习方法提高效率")

        return adjustment

    def _adjust_milestone(self,
                         milestone: Dict[str, Any],
                         progress_data: Dict[str, Any],
                         learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """调整里程碑"""
        adjusted_milestone = milestone.copy()

        # 检查里程碑是否应该调整
        current_week = self._get_current_week_from_plan(progress_data)
        target_week = milestone.get("target_week", 0)

        if current_week > target_week and not milestone.get("achieved", False):
            # 里程碑已过期但未达成
            adjusted_milestone["status"] = "overdue"
            adjusted_milestone["adjustment_needed"] = True

            # 重新安排里程碑
            new_target_week = current_week + 1  # 安排到下一周
            adjusted_milestone["target_week"] = new_target_week
            adjusted_milestone["original_target_week"] = target_week
            adjusted_milestone["rescheduled_at"] = datetime.now().isoformat()

        return adjusted_milestone

    def _get_current_week_from_plan(self, progress_data: Dict[str, Any]) -> int:
        """从进度数据获取当前周"""
        # 这里简化处理，实际中需要更复杂的逻辑
        overall_progress = progress_data.get("overall_progress", 0)

        # 假设进度均匀，计算当前周
        if "learning_weeks" in progress_data:
            total_weeks = progress_data["learning_weeks"]
            return min(math.ceil(overall_progress * total_weeks), total_weeks)

        return math.ceil(overall_progress * 12)  # 默认12周

    def _adjust_schedules_for_speed(self,
                                  schedules: Dict[str, Any],
                                  learning_speed: float) -> Dict[str, Any]:
        """根据学习速度调整日程"""
        adjusted_schedules = schedules.copy()

        # 调整每周计划
        if "weekly_schedules" in adjusted_schedules:
            for weekly_schedule in adjusted_schedules["weekly_schedules"]:
                # 调整预估时间
                if "estimated_hours" in weekly_schedule:
                    original_hours = weekly_schedule["estimated_hours"]
                    adjusted_hours = original_hours / learning_speed
                    weekly_schedule["estimated_hours"] = max(1, math.ceil(adjusted_hours))

                # 调整每日计划
                if "daily_breakdown" in weekly_schedule:
                    for daily_plan in weekly_schedule["daily_breakdown"]:
                        if "estimated_hours" in daily_plan:
                            daily_hours = daily_plan["estimated_hours"]
                            adjusted_daily = daily_hours / learning_speed
                            daily_plan["estimated_hours"] = max(0.5, math.ceil(adjusted_daily * 2) / 2)  # 保留0.5小时精度

        return adjusted_schedules

    def _adjust_schedules_for_difficulty(self,
                                       schedules: Dict[str, Any],
                                       struggling_nodes: List[str]) -> Dict[str, Any]:
        """为困难节点调整日程"""
        adjusted_schedules = schedules.copy()

        # 为困难节点增加额外时间
        extra_time_per_node = 0.5  # 每个困难节点额外0.5小时

        if "weekly_schedules" in adjusted_schedules:
            for weekly_schedule in adjusted_schedules["weekly_schedules"]:
                # 检查这周是否有困难节点
                has_struggling_nodes = False

                # 这里简化处理，实际中需要更精确的匹配
                if random.random() < 0.3:  # 30%的概率这周有困难节点
                    has_struggling_nodes = True

                if has_struggling_nodes:
                    # 增加额外时间
                    if "estimated_hours" in weekly_schedule:
                        weekly_schedule["estimated_hours"] += extra_time_per_node * len(struggling_nodes)

                    # 添加说明
                    weekly_schedule["note"] = f"包含{len(struggling_nodes)}个困难节点的额外练习时间"

        return adjusted_schedules

    def _generate_adjustment_summary(self,
                                   adjusted_plan: Dict[str, Any],
                                   progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成调整摘要"""
        summary = {
            "adjustment_count": len(adjusted_plan.get("adjustments_made", [])),
            "adjustment_types": [],
            "current_status": {},
            "next_steps": []
        }

        # 收集调整类型
        adjustments_made = adjusted_plan.get("adjustments_made", [])
        for adjustment in adjustments_made:
            if isinstance(adjustment, dict):
                summary["adjustment_types"].append(adjustment.get("type", "unknown"))
            elif isinstance(adjustment, str):
                summary["adjustment_types"].append(adjustment.split(" ")[0] if " " in adjustment else adjustment)

        # 当前状态
        progress = progress_data.get("overall_progress", 0)
        summary["current_status"] = {
            "progress_percentage": f"{progress*100:.1f}%",
            "adjustment_reason": ", ".join(set(summary["adjustment_types"])),
            "plan_health": "良好" if len(adjustments_made) < 3 else "需要关注"
        }

        # 下一步
        if progress < 0.3:
            summary["next_steps"] = ["继续按计划学习", "建立学习习惯", "定期检查进度"]
        elif progress < 0.7:
            summary["next_steps"] = ["保持学习节奏", "加强薄弱环节", "准备中期评估"]
        else:
            summary["next_steps"] = ["加速完成剩余内容", "进行综合复习", "准备最终评估"]

        return summary