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


class AdaptiveScheduler:
    """
    自适应调度器 - 根据学习情况动态调整学习调度
    """

    def __init__(self):
        self.scheduling_strategies = {
            "fixed_schedule": {
                "name": "固定日程",
                "description": "按固定时间表学习",
                "flexibility": "低",
                "suitable_for": ["规律生活", "初学者", "建立习惯"]
            },
            "flexible_schedule": {
                "name": "弹性日程",
                "description": "在时间窗口内灵活安排",
                "flexibility": "中",
                "suitable_for": ["工作繁忙", "时间不定", "中级学习者"]
            },
            "dynamic_schedule": {
                "name": "动态日程",
                "description": "根据状态和进度实时调整",
                "flexibility": "高",
                "suitable_for": ["高级学习者", "自适应学习", "个性化需求"]
            },
            "adaptive_schedule": {
                "name": "自适应日程",
                "description": "基于多因素智能调整",
                "flexibility": "最高",
                "suitable_for": ["复杂目标", "多任务学习", "优化学习体验"]
            }
        }

        # 调度因素权重
        self.scheduling_factors = {
            "time_availability": {"weight": 0.3, "description": "时间可用性"},
            "energy_level": {"weight": 0.2, "description": "精力水平"},
            "learning_progress": {"weight": 0.25, "description": "学习进度"},
            "task_difficulty": {"weight": 0.15, "description": "任务难度"},
            "personal_preference": {"weight": 0.1, "description": "个人偏好"}
        }

        # 调度历史
        self.scheduling_history = defaultdict(list)

    def schedule_learning_sessions(self,
                                  learning_plan: Dict[str, Any],
                                  current_context: Dict[str, Any],
                                  strategy: str = "adaptive_schedule") -> Dict[str, Any]:
        """
        调度学习会话

        Args:
            learning_plan: 学习计划
            current_context: 当前上下文（时间、精力等）
            strategy: 调度策略

        Returns:
            调度结果
        """
        print(f"⏰ 调度学习会话 (策略: {strategy})")

        schedule = {
            "scheduled_at": datetime.now().isoformat(),
            "strategy": strategy,
            "context_analysis": {},
            "scheduled_sessions": [],
            "recommendations": [],
            "flexibility_score": 0.0
        }

        # 分析当前上下文
        context_analysis = self._analyze_current_context(current_context)
        schedule["context_analysis"] = context_analysis

        # 根据策略调度
        if strategy == "fixed_schedule":
            sessions = self._create_fixed_schedule(learning_plan, context_analysis)
        elif strategy == "flexible_schedule":
            sessions = self._create_flexible_schedule(learning_plan, context_analysis)
        elif strategy == "dynamic_schedule":
            sessions = self._create_dynamic_schedule(learning_plan, context_analysis)
        else:  # adaptive_schedule
            sessions = self._create_adaptive_schedule(learning_plan, context_analysis)

        schedule["scheduled_sessions"] = sessions

        # 计算灵活性分数
        flexibility_score = self._calculate_flexibility_score(sessions, context_analysis)
        schedule["flexibility_score"] = flexibility_score

        # 生成调度建议
        recommendations = self._generate_scheduling_recommendations(
            schedule, learning_plan, context_analysis
        )
        schedule["recommendations"] = recommendations

        # 记录调度历史
        self._record_scheduling_history(learning_plan.get("goal_id", "unknown"), schedule)

        print(f"✅ 学习会话调度完成: {len(sessions)}个会话，灵活性分数: {flexibility_score:.2f}")
        return schedule

    def reschedule_based_on_feedback(self,
                                   original_schedule: Dict[str, Any],
                                   session_feedback: Dict[str, Any],
                                   current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于反馈重新调度

        Args:
            original_schedule: 原始调度
            session_feedback: 会话反馈
            current_context: 当前上下文

        Returns:
            重新调度结果
        """
        print(f"🔄 基于反馈重新调度")

        reschedule = original_schedule.copy()
        reschedule["rescheduled_at"] = datetime.now().isoformat()
        reschedule["original_schedule_id"] = original_schedule.get("scheduled_at", "")

        # 分析反馈
        feedback_analysis = self._analyze_session_feedback(session_feedback)
        reschedule["feedback_analysis"] = feedback_analysis

        # 提取需要调整的信息
        completed_sessions = session_feedback.get("completed_sessions", [])
        canceled_sessions = session_feedback.get("canceled_sessions", [])
        session_ratings = session_feedback.get("session_ratings", {})

        # 调整会话
        original_sessions = original_schedule.get("scheduled_sessions", [])
        adjusted_sessions = []

        for session in original_sessions:
            session_id = session.get("session_id", "")

            # 如果会话已完成或取消，跳过
            if session_id in completed_sessions or session_id in canceled_sessions:
                continue

            # 如果有评分，根据评分调整
            if session_id in session_ratings:
                rating = session_ratings[session_id]
                adjusted_session = self._adjust_session_based_on_rating(session, rating)
                adjusted_sessions.append(adjusted_session)
            else:
                # 没有评分，保持原样或轻微调整
                adjusted_sessions.append(session)

        # 添加新会话（如果需要）
        if feedback_analysis.get("need_more_sessions", False):
            additional_sessions = self._create_additional_sessions(
                feedback_analysis, current_context, len(adjusted_sessions)
            )
            adjusted_sessions.extend(additional_sessions)

        reschedule["scheduled_sessions"] = adjusted_sessions
        reschedule["adjustments_made"] = len(original_sessions) - len(adjusted_sessions) + len(additional_sessions)

        # 更新上下文分析
        reschedule["context_analysis"] = self._analyze_current_context(current_context)

        print(f"✅ 重新调度完成: {reschedule['adjustments_made']}项调整")
        return reschedule

    def optimize_schedule_for_goals(self,
                                  goals: List[LearningGoal],
                                  available_time: Dict[str, int],  # 每周可用时间（小时）
                                  priority_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        为多个目标优化调度

        Args:
            goals: 学习目标列表
            available_time: 可用时间
            priority_weights: 优先级权重

        Returns:
            优化调度
        """
        print(f"⚡ 为{len(goals)}个目标优化调度")

        optimization = {
            "optimized_at": datetime.now().isoformat(),
            "goals_count": len(goals),
            "available_time": available_time,
            "time_allocation": {},
            "conflict_resolution": [],
            "optimized_schedule": {}
        }

        if not goals:
            optimization["message"] = "没有需要优化的目标"
            return optimization

        # 如果没有提供优先级权重，自动计算
        if priority_weights is None:
            priority_weights = self._calculate_priority_weights(goals)

        optimization["priority_weights"] = priority_weights

        # 计算每个目标的时间分配
        time_allocation = self._allocate_time_to_goals(goals, available_time, priority_weights)
        optimization["time_allocation"] = time_allocation

        # 解决时间冲突
        conflicts = self._identify_scheduling_conflicts(goals, time_allocation)
        optimization["conflict_resolution"] = conflicts

        # 创建优化后的日程
        optimized_schedule = self._create_optimized_schedule(goals, time_allocation, conflicts)
        optimization["optimized_schedule"] = optimized_schedule

        # 计算优化效果
        optimization["optimization_metrics"] = self._calculate_optimization_metrics(
            goals, time_allocation, optimized_schedule
        )

        print(f"✅ 多目标优化完成: {len(time_allocation)}个时间分配，解决{len(conflicts)}个冲突")
        return optimization

    def _analyze_current_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析当前上下文"""
        analysis = {
            "time_analysis": {},
            "energy_analysis": {},
            "focus_analysis": {},
            "readiness_score": 0.0
        }

        # 时间分析
        current_hour = datetime.now().hour
        current_weekday = datetime.now().weekday()  # 0=周一, 6=周日

        time_analysis = {
            "current_hour": current_hour,
            "current_weekday": current_weekday,
            "time_category": self._categorize_time(current_hour, current_weekday),
            "available_minutes": context.get("available_minutes", 60)
        }
        analysis["time_analysis"] = time_analysis

        # 精力分析
        energy_level = context.get("energy_level", 0.5)
        energy_trend = context.get("energy_trend", "stable")

        energy_analysis = {
            "energy_level": energy_level,
            "energy_trend": energy_trend,
            "suggested_activity_intensity": self._suggest_activity_intensity(energy_level)
        }
        analysis["energy_analysis"] = energy_analysis

        # 专注度分析
        focus_level = context.get("focus_level", 0.5)
        distractions = context.get("distractions", [])

        focus_analysis = {
            "focus_level": focus_level,
            "distraction_count": len(distractions),
            "distraction_types": list(set(distractions)),
            "suggested_focus_duration": self._suggest_focus_duration(focus_level)
        }
        analysis["focus_analysis"] = focus_analysis

        # 准备度分数
        readiness_score = self._calculate_readiness_score(
            time_analysis, energy_analysis, focus_analysis
        )
        analysis["readiness_score"] = readiness_score

        return analysis

    def _categorize_time(self, hour: int, weekday: int) -> str:
        """分类时间"""
        if 6 <= hour < 9:
            return "清晨"
        elif 9 <= hour < 12:
            return "上午"
        elif 12 <= hour < 14:
            return "午间"
        elif 14 <= hour < 18:
            return "下午"
        elif 18 <= hour < 22:
            return "晚间"
        else:
            return "深夜"

    def _suggest_activity_intensity(self, energy_level: float) -> str:
        """建议活动强度"""
        if energy_level > 0.7:
            return "高强度"
        elif energy_level > 0.4:
            return "中等强度"
        else:
            return "低强度"

    def _suggest_focus_duration(self, focus_level: float) -> int:
        """建议专注时长（分钟）"""
        if focus_level > 0.7:
            return 60
        elif focus_level > 0.4:
            return 45
        else:
            return 25

    def _calculate_readiness_score(self,
                                 time_analysis: Dict[str, Any],
                                 energy_analysis: Dict[str, Any],
                                 focus_analysis: Dict[str, Any]) -> float:
        """计算准备度分数"""
        factors = []

        # 时间因子
        time_category = time_analysis.get("time_category", "")
        time_factors = {
            "清晨": 0.8,
            "上午": 0.9,
            "午间": 0.6,
            "下午": 0.7,
            "晚间": 0.8,
            "深夜": 0.4
        }
        factors.append(time_factors.get(time_category, 0.5))

        # 精力因子
        energy_level = energy_analysis.get("energy_level", 0.5)
        factors.append(energy_level)

        # 专注因子
        focus_level = focus_analysis.get("focus_level", 0.5)
        factors.append(focus_level)

        # 可用时间因子
        available_minutes = time_analysis.get("available_minutes", 60)
        time_factor = min(available_minutes / 120, 1.0)  # 120分钟为理想值
        factors.append(time_factor)

        # 计算平均分
        if factors:
            return sum(factors) / len(factors)
        else:
            return 0.5

    def _create_fixed_schedule(self,
                              learning_plan: Dict[str, Any],
                              context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建固定日程"""
        sessions = []

        # 固定日程：每天固定时间学习
        daily_templates = learning_plan.get("schedules", {}).get("daily_templates", [])

        if not daily_templates:
            # 如果没有模板，创建基本会话
            base_session = {
                "session_id": generate_id("fixed_session_"),
                "type": "fixed",
                "scheduled_time": "19:00-20:00",
                "duration_minutes": 60,
                "flexibility": "low",
                "recommended_activities": ["系统学习", "完成练习"],
                "priority": "medium"
            }
            sessions.append(base_session)
        else:
            # 使用模板创建会话
            for i, template in enumerate(daily_templates[:3]):  # 最多3个模板
                session = {
                    "session_id": generate_id(f"fixed_session_{i}_"),
                    "type": "fixed",
                    "template_name": template.get("name", ""),
                    "scheduled_time": template.get("time_blocks", [{}])[0].get("time", "19:00-20:00"),
                    "duration_minutes": template.get("total_hours", 1) * 60,
                    "flexibility": "low",
                    "recommended_activities": template.get("suitable_for", ["通用学习"]),
                    "priority": "medium"
                }
                sessions.append(session)

        return sessions

    def _create_flexible_schedule(self,
                                learning_plan: Dict[str, Any],
                                context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建弹性日程"""
        sessions = []

        # 弹性日程：在时间窗口内灵活安排
        time_windows = [
            {"window": "09:00-12:00", "duration_minutes": 90, "priority": "high"},
            {"window": "14:00-17:00", "duration_minutes": 90, "priority": "medium"},
            {"window": "19:00-22:00", "duration_minutes": 60, "priority": "medium"}
        ]

        for i, window in enumerate(time_windows):
            session = {
                "session_id": generate_id(f"flexible_session_{i}_"),
                "type": "flexible",
                "time_window": window["window"],
                "duration_minutes": window["duration_minutes"],
                "flexibility": "medium",
                "suggested_time": self._suggest_time_in_window(window["window"]),
                "priority": window["priority"],
                "conditions": [
                    "在时间窗口内完成",
                    "根据精力选择具体时间",
                    "可以调整时长±30分钟"
                ]
            }
            sessions.append(session)

        return sessions

    def _create_dynamic_schedule(self,
                               learning_plan: Dict[str, Any],
                               context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建动态日程"""
        sessions = []

        # 动态日程：根据当前状态实时调整
        readiness_score = context_analysis.get("readiness_score", 0.5)
        available_minutes = context_analysis.get("time_analysis", {}).get("available_minutes", 60)

        # 确定会话类型和参数
        if readiness_score > 0.7 and available_minutes >= 90:
            # 状态好，时间长：深度学习会话
            session_type = "deep_learning"
            duration = 90
            intensity = "high"
        elif readiness_score > 0.5 and available_minutes >= 60:
            # 状态中等，时间中等：常规学习会话
            session_type = "regular_learning"
            duration = 60
            intensity = "medium"
        elif readiness_score > 0.3 and available_minutes >= 30:
            # 状态一般，时间短：复习或轻量学习
            session_type = "light_review"
            duration = 30
            intensity = "low"
        else:
            # 状态差或时间少：微学习
            session_type = "micro_learning"
            duration = 15
            intensity = "very_low"

        # 创建会话
        session = {
            "session_id": generate_id("dynamic_session_"),
            "type": "dynamic",
            "session_type": session_type,
            "duration_minutes": duration,
            "intensity": intensity,
            "flexibility": "high",
            "suggested_time": "立即开始",
            "priority": "high" if session_type == "deep_learning" else "medium",
            "adaptation_rules": [
                f"根据准备度分数({readiness_score:.2f})调整",
                f"根据可用时间({available_minutes}分钟)调整",
                "可以随时中断和恢复"
            ]
        }

        sessions.append(session)

        # 如果状态和时间允许，安排第二个会话
        if readiness_score > 0.6 and available_minutes >= duration + 30:
            # 安排一个补充会话
            supplemental_session = {
                "session_id": generate_id("dynamic_supplemental_"),
                "type": "dynamic",
                "session_type": "supplemental_practice",
                "duration_minutes": 30,
                "intensity": "medium",
                "flexibility": "high",
                "suggested_time": f"{duration}分钟后",
                "priority": "medium",
                "conditions": ["完成主会话后执行", "根据剩余精力调整"]
            }
            sessions.append(supplemental_session)

        return sessions

    def _create_adaptive_schedule(self,
                                learning_plan: Dict[str, Any],
                                context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建自适应日程"""
        sessions = []

        # 自适应日程：基于多因素智能调整
        readiness_score = context_analysis.get("readiness_score", 0.5)
        energy_level = context_analysis.get("energy_analysis", {}).get("energy_level", 0.5)
        focus_level = context_analysis.get("focus_analysis", {}).get("focus_level", 0.5)
        available_minutes = context_analysis.get("time_analysis", {}).get("available_minutes", 60)

        # 计算多因素综合分数
        factor_scores = [
            readiness_score * 0.4,
            energy_level * 0.3,
            focus_level * 0.2,
            min(available_minutes / 120, 1.0) * 0.1
        ]
        composite_score = sum(factor_scores)

        # 确定最佳学习类型
        learning_types = self._determine_optimal_learning_types(
            composite_score, energy_level, focus_level, available_minutes
        )

        # 创建自适应会话
        for i, learning_type in enumerate(learning_types[:2]):  # 最多2种类型
            # 为每种类型计算最佳参数
            session_params = self._calculate_session_parameters(
                learning_type, composite_score, available_minutes
            )

            session = {
                "session_id": generate_id(f"adaptive_session_{i}_"),
                "type": "adaptive",
                "learning_type": learning_type,
                "composite_score": composite_score,
                "duration_minutes": session_params["duration"],
                "intensity": session_params["intensity"],
                "flexibility": "highest",
                "suggested_time": session_params["suggested_time"],
                "priority": session_params["priority"],
                "adaptation_factors": {
                    "readiness_score": readiness_score,
                    "energy_level": energy_level,
                    "focus_level": focus_level,
                    "available_minutes": available_minutes
                },
                "adjustment_rules": [
                    "根据实时状态动态调整",
                    "可以随时切换学习类型",
                    "支持中断和继续"
                ]
            }
            sessions.append(session)

        return sessions

    def _determine_optimal_learning_types(self,
                                        composite_score: float,
                                        energy_level: float,
                                        focus_level: float,
                                        available_minutes: int) -> List[str]:
        """确定最佳学习类型"""
        learning_types = []

        # 基于综合分数
        if composite_score > 0.8:
            learning_types.extend(["深度学习", "复杂问题解决", "创新思考"])
        elif composite_score > 0.6:
            learning_types.extend(["系统学习", "实践练习", "技能训练"])
        elif composite_score > 0.4:
            learning_types.extend(["知识复习", "概念理解", "基础练习"])
        else:
            learning_types.extend(["微学习", "记忆巩固", "轻量阅读"])

        # 基于精力水平调整
        if energy_level < 0.4:
            # 精力低，优先轻量学习
            learning_types = [lt for lt in learning_types if lt not in ["深度学习", "复杂问题解决"]]
            learning_types.insert(0, "轻量学习")

        # 基于专注度调整
        if focus_level < 0.4:
            # 专注度低，优先简单任务
            learning_types = [lt for lt in learning_types if lt not in ["系统学习", "创新思考"]]
            learning_types.insert(0, "简单任务")

        # 基于可用时间调整
        if available_minutes < 30:
            # 时间短，优先高效学习
            learning_types = [lt for lt in learning_types if lt in ["微学习", "记忆巩固", "轻量阅读"]]

        return list(set(learning_types))  # 去重

    def _calculate_session_parameters(self,
                                    learning_type: str,
                                    composite_score: float,
                                    available_minutes: int) -> Dict[str, Any]:
        """计算会话参数"""
        # 默认参数
        params = {
            "duration": 45,
            "intensity": "medium",
            "suggested_time": "尽快开始",
            "priority": "medium"
        }

        # 根据学习类型调整
        type_configs = {
            "深度学习": {"duration": 90, "intensity": "high", "priority": "high"},
            "系统学习": {"duration": 60, "intensity": "medium", "priority": "high"},
            "实践练习": {"duration": 45, "intensity": "medium", "priority": "medium"},
            "知识复习": {"duration": 30, "intensity": "low", "priority": "medium"},
            "微学习": {"duration": 15, "intensity": "very_low", "priority": "low"}
        }

        for key, config in type_configs.items():
            if key in learning_type:
                params.update(config)
                break

        # 根据综合分数调整
        if composite_score > 0.8:
            params["duration"] = min(params["duration"] + 30, available_minutes)
        elif composite_score < 0.4:
            params["duration"] = max(15, params["duration"] - 15)

        # 确保不超过可用时间
        params["duration"] = min(params["duration"], available_minutes)

        # 建议时间
        if params["duration"] >= 60:
            params["suggested_time"] = "安排专门时间段"
        elif params["duration"] >= 30:
            params["suggested_time"] = "利用碎片时间"
        else:
            params["suggested_time"] = "随时可以开始"

        return params

    def _suggest_time_in_window(self, time_window: str) -> str:
        """在时间窗口内建议具体时间"""
        # 简单实现：建议窗口中间时间
        if "-" in time_window:
            start_str, end_str = time_window.split("-")

            # 转换为分钟
            try:
                start_hour, start_minute = map(int, start_str.split(":"))
                end_hour, end_minute = map(int, end_str.split(":"))

                start_total = start_hour * 60 + start_minute
                end_total = end_hour * 60 + end_minute

                # 计算中间时间
                middle_total = (start_total + end_total) // 2
                middle_hour = middle_total // 60
                middle_minute = middle_total % 60

                return f"{middle_hour:02d}:{middle_minute:02d}"
            except:
                pass

        return time_window.split("-")[0]  # 返回开始时间

    def _calculate_flexibility_score(self,
                                   sessions: List[Dict[str, Any]],
                                   context_analysis: Dict[str, Any]) -> float:
        """计算灵活性分数"""
        if not sessions:
            return 0.0

        flexibility_scores = []

        for session in sessions:
            flexibility = session.get("flexibility", "medium")

            if flexibility == "low":
                flexibility_scores.append(0.3)
            elif flexibility == "medium":
                flexibility_scores.append(0.6)
            elif flexibility == "high":
                flexibility_scores.append(0.8)
            elif flexibility == "highest":
                flexibility_scores.append(1.0)
            else:
                flexibility_scores.append(0.5)

        # 考虑上下文灵活性
        readiness_score = context_analysis.get("readiness_score", 0.5)
        context_flexibility = readiness_score * 0.3 + 0.7  # 准备度越高，灵活性越高

        # 综合分数
        if flexibility_scores:
            avg_session_flexibility = sum(flexibility_scores) / len(flexibility_scores)
            return (avg_session_flexibility * 0.7 + context_flexibility * 0.3)
        else:
            return context_flexibility

    def _generate_scheduling_recommendations(self,
                                           schedule: Dict[str, Any],
                                           learning_plan: Dict[str, Any],
                                           context_analysis: Dict[str, Any]) -> List[str]:
        """生成调度建议"""
        recommendations = []

        strategy = schedule.get("strategy", "")
        flexibility_score = schedule.get("flexibility_score", 0.5)
        session_count = len(schedule.get("scheduled_sessions", []))
        readiness_score = context_analysis.get("readiness_score", 0.5)

        # 基于策略的建议
        if strategy == "fixed_schedule":
            recommendations.append("固定日程适合建立学习习惯，请严格遵守时间")
        elif strategy == "flexible_schedule":
            recommendations.append("弹性日程提供了灵活性，请在时间窗口内完成学习")
        elif strategy == "dynamic_schedule":
            recommendations.append("动态日程根据状态调整，请关注自身状态变化")
        elif strategy == "adaptive_schedule":
            recommendations.append("自适应日程智能优化，系统会自动调整最佳学习安排")

        # 基于灵活性分数的建议
        if flexibility_score < 0.4:
            recommendations.append("当前日程灵活性较低，请确保按计划执行")
        elif flexibility_score > 0.7:
            recommendations.append("当前日程灵活性高，可以根据状态调整学习安排")

        # 基于会话数量的建议
        if session_count > 3:
            recommendations.append(f"安排了{session_count}个学习会话，建议合理分配精力")
        elif session_count == 1:
            recommendations.append("安排了一个主要学习会话，请专注于完成它")

        # 基于准备度的建议
        if readiness_score < 0.4:
            recommendations.append("当前准备度较低，建议从简单任务开始")
        elif readiness_score > 0.8:
            recommendations.append("当前准备度很高，适合进行深度学习和复杂任务")

        return recommendations

    def _analyze_session_feedback(self, session_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """分析会话反馈"""
        analysis = {
            "completion_rate": 0.0,
            "average_rating": 0.0,
            "common_issues": [],
            "success_factors": [],
            "need_more_sessions": False
        }

        completed_sessions = session_feedback.get("completed_sessions", [])
        total_sessions = session_feedback.get("total_sessions", 0)
        session_ratings = session_feedback.get("session_ratings", {})
        issues = session_feedback.get("issues", [])

        # 完成率
        if total_sessions > 0:
            analysis["completion_rate"] = len(completed_sessions) / total_sessions

        # 平均评分
        if session_ratings:
            ratings = list(session_ratings.values())
            if ratings:
                analysis["average_rating"] = statistics.mean(ratings)

        # 常见问题
        if issues:
            issue_counts = {}
            for issue in issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

            common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            analysis["common_issues"] = [issue for issue, count in common_issues]

        # 成功因素（从正面反馈中提取）
        positive_feedback = session_feedback.get("positive_feedback", [])
        if positive_feedback:
            analysis["success_factors"] = positive_feedback[:3]

        # 是否需要更多会话
        if analysis["completion_rate"] < 0.5 or analysis["average_rating"] < 0.6:
            analysis["need_more_sessions"] = True

        return analysis

    def _adjust_session_based_on_rating(self,
                                      session: Dict[str, Any],
                                      rating: float) -> Dict[str, Any]:
        """基于评分调整会话"""
        adjusted_session = session.copy()

        # 根据评分调整参数
        if rating < 0.4:
            # 评分低：简化会话
            original_duration = adjusted_session.get("duration_minutes", 60)
            adjusted_session["duration_minutes"] = max(15, original_duration * 0.5)
            adjusted_session["intensity"] = "low"
            adjusted_session["note"] = "根据低评分简化了会话"
        elif rating > 0.8:
            # 评分高：保持或加强
            original_duration = adjusted_session.get("duration_minutes", 60)
            adjusted_session["duration_minutes"] = min(120, original_duration * 1.2)
            adjusted_session["intensity"] = "high" if session.get("intensity") != "very_low" else "medium"
            adjusted_session["note"] = "根据高评分加强了会话"

        return adjusted_session

    def _create_additional_sessions(self,
                                  feedback_analysis: Dict[str, Any],
                                  current_context: Dict[str, Any],
                                  existing_session_count: int) -> List[Dict[str, Any]]:
        """创建额外会话"""
        additional_sessions = []

        # 根据反馈分析确定需要多少额外会话
        completion_rate = feedback_analysis.get("completion_rate", 0.0)
        need_more = feedback_analysis.get("need_more_sessions", False)

        if not need_more:
            return additional_sessions

        # 计算需要补充的会话数量
        if completion_rate < 0.3:
            additional_count = 3
        elif completion_rate < 0.6:
            additional_count = 2
        else:
            additional_count = 1

        # 限制总会话数量
        max_total_sessions = 5
        additional_count = min(additional_count, max_total_sessions - existing_session_count)

        if additional_count <= 0:
            return additional_sessions

        # 创建补充会话
        for i in range(additional_count):
            session = {
                "session_id": generate_id(f"additional_session_{i}_"),
                "type": "supplemental",
                "purpose": "补充学习",
                "duration_minutes": 30,
                "intensity": "medium",
                "flexibility": "high",
                "suggested_time": "利用碎片时间",
                "priority": "low",
                "conditions": ["在主要会话完成后进行", "根据时间灵活安排"]
            }
            additional_sessions.append(session)

        return additional_sessions

    def _calculate_priority_weights(self, goals: List[LearningGoal]) -> Dict[str, float]:
        """计算优先级权重"""
        if not goals:
            return {}

        # 基于目标属性计算权重
        weights = {}
        total_weight = 0.0

        for goal in goals:
            weight = 0.0

            # 基于规模
            scale_weights = {
                GoalScale.MICRO: 1.0,
                GoalScale.SMALL: 2.0,
                GoalScale.MEDIUM: 3.0,
                GoalScale.LARGE: 4.0,
                GoalScale.MASSIVE: 5.0
            }
            weight += scale_weights.get(goal.scale, 2.0)

            # 基于优先级
            weight += goal.priority / 2.0  # 优先级1-10，转换为0.5-5

            # 基于复杂度
            weight += goal.complexity * 2.0

            # 基于时间紧迫性
            if goal.deadline:
                try:
                    deadline_date = datetime.fromisoformat(goal.deadline)
                    days_until_deadline = (deadline_date - datetime.now()).days
                    if days_until_deadline > 0:
                        time_factor = 10.0 / days_until_deadline  # 越近权重越高
                        weight += min(time_factor, 5.0)
                except:
                    pass

            weights[goal.id] = weight
            total_weight += weight

        # 归一化
        if total_weight > 0:
            for goal_id in weights:
                weights[goal_id] = weights[goal_id] / total_weight

        return weights

    def _allocate_time_to_goals(self,
                              goals: List[LearningGoal],
                              available_time: Dict[str, int],
                              priority_weights: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """分配时间给各个目标"""
        time_allocation = {}

        # 总可用时间
        total_available = sum(available_time.values())

        if total_available <= 0:
            return time_allocation

        # 为每个目标分配时间
        for goal in goals:
            goal_id = goal.id
            weight = priority_weights.get(goal_id, 0.0)

            # 基于权重分配时间
            allocated_hours = total_available * weight

            # 考虑目标自身的时间需求
            estimated_time = self._estimate_goal_time(goal)
            if estimated_time > 0:
                # 如果预估时间小于分配时间，使用预估时间
                allocated_hours = min(allocated_hours, estimated_time)

            # 分配到具体时间（简化处理）
            weekly_allocation = {}
            days = list(available_time.keys())

            if days:
                # 平均分配到每天
                hours_per_day = allocated_hours / len(days)
                for day in days:
                    weekly_allocation[day] = hours_per_day

            time_allocation[goal_id] = {
                "goal_name": goal.description,
                "priority_weight": weight,
                "allocated_hours_per_week": allocated_hours,
                "weekly_allocation": weekly_allocation,
                "estimated_completion_weeks": self._estimate_completion_weeks(goal, allocated_hours)
            }

        return time_allocation

    def _estimate_goal_time(self, goal: LearningGoal) -> float:
        """估算目标所需时间（小时）"""
        # 使用时间模型估算
        try:
            time_model = TimeEstimationModel()
            minutes = time_model.estimate_for_goal(goal)
            return minutes / 60
        except:
            # 备用估算
            return goal.target_knowledge_count * 0.5  # 每个知识点0.5小时

    def _estimate_completion_weeks(self, goal: LearningGoal, weekly_hours: float) -> float:
        """估算完成周数"""
        if weekly_hours <= 0:
            return float('inf')

        total_hours = self._estimate_goal_time(goal)
        return math.ceil(total_hours / weekly_hours)

    def _identify_scheduling_conflicts(self,
                                     goals: List[LearningGoal],
                                     time_allocation: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别调度冲突"""
        conflicts = []

        # 简化冲突检测：检查总时间分配是否合理
        total_allocated = 0
        for allocation in time_allocation.values():
            total_allocated += allocation.get("allocated_hours_per_week", 0)

        # 假设每周最多学习40小时
        max_reasonable_hours = 40

        if total_allocated > max_reasonable_hours:
            conflicts.append({
                "type": "overtime",
                "description": f"总分配时间({total_allocated:.1f}小时)超过合理上限({max_reasonable_hours}小时)",
                "severity": "high",
                "solutions": [
                    "减少某些目标的时间分配",
                    "延长学习周期",
                    "调整目标优先级"
                ]
            })

        # 检查目标间的时间冲突（简化）
        if len(goals) > 3:
            # 如果目标太多，可能存在时间冲突
            avg_hours_per_goal = total_allocated / len(goals)
            if avg_hours_per_goal < 2:
                conflicts.append({
                    "type": "insufficient_time_per_goal",
                    "description": f"每个目标平均只有{avg_hours_per_goal:.1f}小时，可能不足",
                    "severity": "medium",
                    "solutions": [
                        "聚焦少数重要目标",
                        "增加总学习时间",
                        "提高学习效率"
                    ]
                })

        return conflicts

    def _create_optimized_schedule(self,
                                 goals: List[LearningGoal],
                                 time_allocation: Dict[str, Dict[str, Any]],
                                 conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建优化后的日程"""
        # 创建每日计划模板
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        daily_plans = {}
        
        for day in days:
            daily_plan = {
                "total_hours": 0,
                "goal_sessions": [],
                "recommended_time_slots": [],
                "flexibility": "medium"
            }
            
            # 为每个目标分配当天的学习时间
            for goal_id, allocation in time_allocation.items():
                daily_hours = allocation.get("weekly_allocation", {}).get(day, 0)
                if daily_hours > 0:
                    goal_session = {
                        "goal_id": goal_id,
                        "goal_name": allocation.get("goal_name", ""),
                        "allocated_hours": daily_hours,
                        "priority_weight": allocation.get("priority_weight", 0.0),
                        "suggested_time": self._suggest_goal_time(day, goal_id, allocation)
                    }
                    daily_plan["goal_sessions"].append(goal_session)
                    daily_plan["total_hours"] += daily_hours
            
            # 推荐时间段
            if daily_plan["total_hours"] > 0:
                if daily_plan["total_hours"] <= 2:
                    daily_plan["recommended_time_slots"] = [
                        {"time": "19:00-21:00", "intensity": "medium"}
                    ]
                elif daily_plan["total_hours"] <= 4:
                    daily_plan["recommended_time_slots"] = [
                        {"time": "09:00-11:00", "intensity": "high"},
                        {"time": "19:00-21:00", "intensity": "medium"}
                    ]
                else:
                    daily_plan["recommended_time_slots"] = [
                        {"time": "09:00-12:00", "intensity": "high"},
                        {"time": "14:00-16:00", "intensity": "medium"},
                        {"time": "19:00-21:00", "intensity": "low"}
                    ]
            
            daily_plans[day] = daily_plan
        
        optimized_schedule = {
            "daily_schedule": daily_plans
        }
        
        # 创建周度概览
        weekly_overview = {
            "total_goals": len(goals),
            "total_weekly_hours": sum(alloc.get("allocated_hours_per_week", 0) for alloc in time_allocation.values()),
            "goal_distribution": {alloc.get("goal_name", ""): alloc.get("allocated_hours_per_week", 0) 
                                 for alloc in time_allocation.values()},
            "daily_breakdown": {day: daily_plans[day]["total_hours"] for day in days if day in daily_plans},
            "busiest_day": max(daily_plans.items(), key=lambda x: x[1]["total_hours"])[0] if daily_plans else "无"
        }
        optimized_schedule["weekly_overview"] = weekly_overview
        
        # 记录应用的冲突解决方案
        for conflict in conflicts:
            if conflict.get("solutions_applied"):
                optimized_schedule["conflict_resolutions_applied"] = optimized_schedule.get("conflict_resolutions_applied", [])
                optimized_schedule["conflict_resolutions_applied"].extend(conflict["solutions_applied"])
        
        return optimized_schedule
    
    def _suggest_goal_time(self, day: str, goal_id: str, allocation: Dict[str, Any]) -> str:
        """为目标推荐学习时间"""
        # 基于优先级和目标特性推荐时间
        priority = allocation.get("priority_weight", 0.0)
        
        if priority > 0.7:
            return "上午高效时段"
        elif priority > 0.4:
            return "下午专注时段"
        else:
            return "晚间灵活时段"
    
    def _apply_overtime_solution(self, time_allocation: Dict[str, Dict[str, Any]]) -> None:
        """应用超时解决方案"""
        # 减少所有目标的时间分配，优先保护高优先级目标
        total_allocated = sum(alloc.get("allocated_hours_per_week", 0) for alloc in time_allocation.values())
        max_hours = 40  # 每周最多40小时
        
        if total_allocated <= max_hours:
            return
        
        # 计算需要减少的比例
        reduction_factor = max_hours / total_allocated
        
        # 按优先级调整：低优先级目标减少更多
        for goal_id, allocation in time_allocation.items():
            original_hours = allocation.get("allocated_hours_per_week", 0)
            priority = allocation.get("priority_weight", 0.5)
            
            # 高优先级目标减少较少
            if priority > 0.7:
                adjustment_factor = 0.9  # 只减少10%
            elif priority > 0.4:
                adjustment_factor = 0.8  # 减少20%
            else:
                adjustment_factor = 0.6  # 减少40%
            
            # 应用调整
            new_hours = original_hours * reduction_factor * adjustment_factor
            allocation["allocated_hours_per_week"] = max(1, new_hours)  # 至少1小时
        
    def _calculate_optimization_metrics(self,
                                      goals: List[LearningGoal],
                                      time_allocation: Dict[str, Dict[str, Any]],
                                      optimized_schedule: Dict[str, Any]) -> Dict[str, Any]:
        """计算优化指标"""
        metrics = {
            "efficiency_score": 0.0,
            "balance_score": 0.0,
            "feasibility_score": 0.0,
            "satisfaction_score": 0.0,
            "improvements": []
        }
        
        # 计算效率分数（时间分配与优先级匹配度）
        priority_alignment = 0.0
        for goal_id, allocation in time_allocation.items():
            priority = allocation.get("priority_weight", 0.0)
            time_ratio = allocation.get("allocated_hours_per_week", 0) / 40  # 假设40小时为上限
            
            # 理想情况：时间分配与优先级成正比
            alignment = 1.0 - abs(priority - time_ratio)
            priority_alignment += alignment * priority
        
        if time_allocation:
            priority_alignment /= len(time_allocation)
        
        metrics["efficiency_score"] = priority_alignment
        
        # 计算平衡分数（每日时间分布均衡）
        daily_schedule = optimized_schedule.get("daily_schedule", {})
        daily_hours = [plan.get("total_hours", 0) for plan in daily_schedule.values()]
        
        if daily_hours:
            avg_hours = sum(daily_hours) / len(daily_hours)
            variance = sum((h - avg_hours) ** 2 for h in daily_hours) / len(daily_hours)
            balance_score = 1.0 / (1.0 + variance)  # 方差越小，分数越高
            metrics["balance_score"] = min(balance_score, 1.0)
        
        # 计算可行性分数（每日不超过合理上限）
        feasible_days = 0
        for day, plan in daily_schedule.items():
            total_hours = plan.get("total_hours", 0)
            if total_hours <= 8:  # 假设每天最多8小时学习
                feasible_days += 1
        
        if daily_schedule:
            metrics["feasibility_score"] = feasible_days / len(daily_schedule)
        
        # 计算满意度分数（综合指标）
        metrics["satisfaction_score"] = (
            metrics["efficiency_score"] * 0.4 +
            metrics["balance_score"] * 0.3 +
            metrics["feasibility_score"] * 0.3
        )
        
        # 改进建议
        if metrics["efficiency_score"] < 0.7:
            metrics["improvements"].append("优化时间分配以更好地匹配目标优先级")
        
        if metrics["balance_score"] < 0.6:
            metrics["improvements"].append("调整日程以使每日学习时间更均衡")
        
        if metrics["feasibility_score"] < 0.8:
            metrics["improvements"].append("减少某些日的学习量以提高可行性")
        
        return metrics
    
    def _record_scheduling_history(self, goal_id: str, schedule: Dict[str, Any]) -> None:
        """记录调度历史"""
        history_entry = {
            "scheduled_at": schedule.get("scheduled_at", datetime.now().isoformat()),
            "strategy": schedule.get("strategy", ""),
            "session_count": len(schedule.get("scheduled_sessions", [])),
            "flexibility_score": schedule.get("flexibility_score", 0.0)
        }
        
        self.scheduling_history[goal_id].append(history_entry)
        
        # 限制历史记录长度
        if len(self.scheduling_history[goal_id]) > 20:
            self.scheduling_history[goal_id] = self.scheduling_history[goal_id][-20:]