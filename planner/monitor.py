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


class ProgressMonitor:
    """
    进度监控器 - 实时监控学习进度并提供反馈
    """

    def __init__(self):
        self.monitoring_strategies = {
            "continuous": {
                "name": "持续监控",
                "description": "实时监控学习进度",
                "update_frequency": "real_time",
                "granularity": "fine"
            },
            "periodic": {
                "name": "定期监控",
                "description": "按固定时间间隔监控",
                "update_frequency": "daily",
                "granularity": "medium"
            },
            "milestone": {
                "name": "里程碑监控",
                "description": "在关键里程碑检查进度",
                "update_frequency": "milestone_based",
                "granularity": "coarse"
            },
            "adaptive": {
                "name": "自适应监控",
                "description": "根据学习情况调整监控频率",
                "update_frequency": "adaptive",
                "granularity": "variable"
            }
        }

        # 进度指标配置
        self.progress_metrics = {
            "completion_rate": {
                "name": "完成率",
                "description": "已完成项目的比例",
                "weight": 0.3,
                "target": 1.0
            },
            "learning_speed": {
                "name": "学习速度",
                "description": "单位时间内学习的项目数",
                "weight": 0.2,
                "target": "dynamic"
            },
            "mastery_level": {
                "name": "掌握程度",
                "description": "知识的掌握深度",
                "weight": 0.25,
                "target": 0.8
            },
            "consistency": {
                "name": "一致性",
                "description": "学习过程的稳定程度",
                "weight": 0.15,
                "target": 0.9
            },
            "engagement": {
                "name": "参与度",
                "description": "学习过程的投入程度",
                "weight": 0.1,
                "target": 0.8
            }
        }

        # 监控历史
        self.monitoring_history = defaultdict(list)

    def monitor_goal_progress(self,
                             goal: LearningGoal,
                             progress_data: Dict[str, Any],
                             monitoring_strategy: str = "adaptive") -> Dict[str, Any]:
        """
        监控目标进度

        Args:
            goal: 学习目标
            progress_data: 进度数据
            monitoring_strategy: 监控策略

        Returns:
            监控报告
        """
        print(f"📈 监控目标进度: {goal.description}")

        monitoring_report = {
            "goal_id": goal.id,
            "monitored_at": datetime.now().isoformat(),
            "strategy": monitoring_strategy,
            "current_progress": {},
            "progress_metrics": {},
            "trend_analysis": {},
            "alerts": [],
            "recommendations": []
        }

        # 验证策略
        if monitoring_strategy not in self.monitoring_strategies:
            print(f"⚠️ 未知监控策略 {monitoring_strategy}，使用自适应策略")
            monitoring_strategy = "adaptive"

        monitoring_report["strategy"] = monitoring_strategy

        # 分析当前进度
        current_progress = self._analyze_current_progress(goal, progress_data)
        monitoring_report["current_progress"] = current_progress

        # 计算进度指标
        progress_metrics = self._calculate_progress_metrics(goal, progress_data)
        monitoring_report["progress_metrics"] = progress_metrics

        # 分析趋势
        trend_analysis = self._analyze_progress_trends(goal, progress_data, current_progress)
        monitoring_report["trend_analysis"] = trend_analysis

        # 检查预警
        alerts = self._check_progress_alerts(goal, current_progress, progress_metrics, trend_analysis)
        monitoring_report["alerts"] = alerts

        # 生成建议
        recommendations = self._generate_progress_recommendations(
            goal, current_progress, progress_metrics, trend_analysis, alerts
        )
        monitoring_report["recommendations"] = recommendations

        # 记录监控历史
        self._record_monitoring_history(goal.id, monitoring_report)

        print(f"✅ 进度监控完成: {len(alerts)}个预警，{len(recommendations)}条建议")
        return monitoring_report

    def monitor_mindmap_progress(self,
                                goal: LearningGoal,
                                mindmap_root: MindMapNode,
                                node_map: Dict[str, MindMapNode],
                                progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        监控思维导图进度

        Args:
            goal: 学习目标
            mindmap_root: 思维导图根节点
            node_map: 节点映射
            progress_data: 进度数据

        Returns:
            思维导图进度报告
        """
        print(f"🧠 监控思维导图进度")

        mindmap_report = {
            "goal_id": goal.id,
            "mindmap_id": mindmap_root.id,
            "monitored_at": datetime.now().isoformat(),
            "node_progress": {},
            "layer_progress": {},
            "structural_analysis": {},
            "weak_areas": [],
            "strong_areas": []
        }

        # 分析节点进度
        node_progress = self._analyze_node_progress(node_map, progress_data)
        mindmap_report["node_progress"] = node_progress

        # 分析层级进度
        layer_progress = self._analyze_layer_progress(node_map, progress_data)
        mindmap_report["layer_progress"] = layer_progress

        # 结构分析
        structural_analysis = self._analyze_mindmap_structure_progress(node_map, progress_data)
        mindmap_report["structural_analysis"] = structural_analysis

        # 识别薄弱区域
        weak_areas = self._identify_weak_areas(node_map, progress_data)
        mindmap_report["weak_areas"] = weak_areas

        # 识别优势区域
        strong_areas = self._identify_strong_areas(node_map, progress_data)
        mindmap_report["strong_areas"] = strong_areas

        # 生成思维导图学习建议
        mindmap_report["mindmap_recommendations"] = self._generate_mindmap_recommendations(
            node_map, progress_data, weak_areas, strong_areas
        )

        return mindmap_report

    def generate_progress_visualization(self,
                                      goal: LearningGoal,
                                      progress_data: Dict[str, Any],
                                      mindmap_node_map: Optional[Dict[str, MindMapNode]] = None) -> Dict[str, Any]:
        """
        生成进度可视化数据

        Args:
            goal: 学习目标
            progress_data: 进度数据
            mindmap_node_map: 思维导图节点映射

        Returns:
            可视化数据
        """
        print(f"📊 生成进度可视化")

        visualization = {
            "goal_id": goal.id,
            "generated_at": datetime.now().isoformat(),
            "progress_charts": {},
            "trend_visualizations": {},
            "mindmap_visualizations": {}
        }

        # 进度图表数据
        progress_charts = self._create_progress_charts(goal, progress_data)
        visualization["progress_charts"] = progress_charts

        # 趋势可视化
        trend_visualizations = self._create_trend_visualizations(goal, progress_data)
        visualization["trend_visualizations"] = trend_visualizations

        # 思维导图可视化（如果有思维导图）
        if mindmap_node_map:
            mindmap_visualizations = self._create_mindmap_visualizations(
                goal, mindmap_node_map, progress_data
            )
            visualization["mindmap_visualizations"] = mindmap_visualizations

        return visualization

    def predict_completion_time(self,
                               goal: LearningGoal,
                               progress_data: Dict[str, Any],
                               learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        预测完成时间

        Args:
            goal: 学习目标
            progress_data: 进度数据
            learning_history: 学习历史

        Returns:
            完成时间预测
        """
        print(f"⏱️ 预测完成时间: {goal.description}")

        prediction = {
            "goal_id": goal.id,
            "predicted_at": datetime.now().isoformat(),
            "current_progress": progress_data.get("overall_progress", 0),
            "prediction_models": {},
            "confidence_scores": {},
            "recommended_actions": []
        }

        # 使用多种模型预测
        prediction_models = {}

        # 1. 线性外推模型
        linear_prediction = self._predict_with_linear_model(goal, progress_data, learning_history)
        prediction_models["linear"] = linear_prediction

        # 2. 学习曲线模型
        learning_curve_prediction = self._predict_with_learning_curve(goal, progress_data, learning_history)
        prediction_models["learning_curve"] = learning_curve_prediction

        # 3. 时间序列模型
        time_series_prediction = self._predict_with_time_series(goal, progress_data, learning_history)
        prediction_models["time_series"] = time_series_prediction

        # 4. 自适应模型
        adaptive_prediction = self._predict_with_adaptive_model(goal, progress_data, learning_history)
        prediction_models["adaptive"] = adaptive_prediction

        prediction["prediction_models"] = prediction_models

        # 计算置信度
        confidence_scores = self._calculate_prediction_confidence(prediction_models)
        prediction["confidence_scores"] = confidence_scores

        # 综合预测（加权平均）
        weighted_prediction = self._calculate_weighted_prediction(prediction_models, confidence_scores)
        prediction["weighted_prediction"] = weighted_prediction

        # 生成建议
        if weighted_prediction["on_track"] == "behind":
            prediction["recommended_actions"].append("增加每日学习时间")
            prediction["recommended_actions"].append("优化学习方法")
        elif weighted_prediction["on_track"] == "ahead":
            prediction["recommended_actions"].append("可以提前完成或增加学习深度")

        return prediction

    def _analyze_current_progress(self,
                                 goal: LearningGoal,
                                 progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析当前进度"""
        current_progress = {
            "overall_progress": goal.overall_progress,
            "progress_details": {},
            "milestone_status": {},
            "recent_activity": {}
        }

        # 详细进度
        if goal.batch_progress:
            current_progress["progress_details"]["batch_progress"] = goal.batch_progress

        if goal.item_progress:
            current_progress["progress_details"]["item_progress"] = goal.item_progress

        if goal.subgoal_progress:
            current_progress["progress_details"]["subgoal_progress"] = goal.subgoal_progress

        if goal.mindmap_layer_progress:
            current_progress["progress_details"]["mindmap_layer_progress"] = goal.mindmap_layer_progress

        # 里程碑状态
        if "milestones" in progress_data:
            for milestone in progress_data["milestones"]:
                milestone_id = milestone.get("id", "")
                status = milestone.get("status", "pending")
                current_progress["milestone_status"][milestone_id] = status

        # 最近活动
        recent_days = 7
        current_progress["recent_activity"] = {
            "learning_sessions": progress_data.get("recent_sessions", []),
            "daily_progress": progress_data.get("daily_progress", {}),
            "active_days": progress_data.get("active_days", 0)
        }

        return current_progress

    def _calculate_progress_metrics(self,
                                  goal: LearningGoal,
                                  progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算进度指标"""
        metrics = {}

        # 完成率
        completion_rate = goal.overall_progress
        metrics["completion_rate"] = {
            "value": completion_rate,
            "status": "good" if completion_rate >= 0.7 else 
                     "warning" if completion_rate >= 0.3 else "poor"
        }

        # 学习速度（项目/天）
        total_items = goal.target_knowledge_count
        completed_items = sum(1 for p in goal.item_progress.values() if p >= 0.8) if goal.item_progress else 0
        days_elapsed = self._calculate_days_elapsed(goal)

        if days_elapsed > 0:
            learning_speed = completed_items / days_elapsed
        else:
            learning_speed = 0

        metrics["learning_speed"] = {
            "value": learning_speed,
            "status": "good" if learning_speed >= 5 else 
                     "warning" if learning_speed >= 2 else "poor"
        }

        # 掌握程度（基于测试成绩）
        mastery_level = progress_data.get("mastery_level", 0.0)
        metrics["mastery_level"] = {
            "value": mastery_level,
            "status": "good" if mastery_level >= 0.8 else 
                     "warning" if mastery_level >= 0.6 else "poor"
        }

        # 一致性（学习天数比例）
        total_days = self._calculate_total_days(goal)
        if total_days > 0:
            consistency = progress_data.get("active_days", 0) / total_days
        else:
            consistency = 0

        metrics["consistency"] = {
            "value": consistency,
            "status": "good" if consistency >= 0.7 else 
                     "warning" if consistency >= 0.4 else "poor"
        }

        # 参与度（基于学习时长和专注度）
        engagement = progress_data.get("engagement_level", 0.5)
        metrics["engagement"] = {
            "value": engagement,
            "status": "good" if engagement >= 0.7 else 
                     "warning" if engagement >= 0.5 else "poor"
        }

        # 综合进度分数
        weights = {
            "completion_rate": 0.3,
            "learning_speed": 0.2,
            "mastery_level": 0.25,
            "consistency": 0.15,
            "engagement": 0.1
        }

        weighted_score = 0
        for metric_name, metric_data in metrics.items():
            weight = weights.get(metric_name, 0)
            score = metric_data["value"]
            weighted_score += score * weight

        metrics["overall_score"] = {
            "value": weighted_score,
            "status": "good" if weighted_score >= 0.7 else 
                     "warning" if weighted_score >= 0.5 else "poor"
        }

        return metrics

    def _calculate_days_elapsed(self, goal: LearningGoal) -> int:
        """计算已过天数"""
        try:
            if goal.started_at:
                start_date = datetime.fromisoformat(goal.started_at)
                current_date = datetime.now()
                days_elapsed = (current_date - start_date).days
                return max(days_elapsed, 0)
        except:
            pass

        return 0

    def _calculate_total_days(self, goal: LearningGoal) -> int:
        """计算总天数（从开始到预计完成）"""
        try:
            if goal.started_at and goal.estimated_completion:
                start_date = datetime.fromisoformat(goal.started_at)
                end_date = datetime.fromisoformat(goal.estimated_completion)
                total_days = (end_date - start_date).days
                return max(total_days, 1)
        except:
            pass

        # 如果没有预估完成时间，使用默认值
        return 30  # 默认30天

    def _analyze_progress_trends(self,
                                goal: LearningGoal,
                                progress_data: Dict[str, Any],
                                current_progress: Dict[str, Any]) -> Dict[str, Any]:
        """分析进度趋势"""
        trends = {
            "progress_trend": "stable",
            "velocity_trend": "stable",
            "consistency_trend": "stable",
            "predicted_completion": None,
            "risk_factors": []
        }

        # 分析历史进度趋势
        if "progress_history" in progress_data:
            history = progress_data["progress_history"]

            if len(history) >= 3:
                # 计算近期进度变化
                recent_changes = []
                for i in range(1, min(4, len(history))):
                    if i < len(history):
                        change = history[-i].get("progress", 0) - history[-i-1].get("progress", 0)
                        recent_changes.append(change)

                if recent_changes:
                    avg_change = sum(recent_changes) / len(recent_changes)

                    if avg_change > 0.05:  # 每周进度增加超过5%
                        trends["progress_trend"] = "accelerating"
                    elif avg_change < -0.02:  # 每周进度减少超过2%
                        trends["progress_trend"] = "decelerating"
                        trends["risk_factors"].append("学习进度在下降")
                    else:
                        trends["progress_trend"] = "stable"

        # 分析学习速度趋势
        if "learning_velocity" in progress_data:
            velocity_history = progress_data["learning_velocity"]

            if len(velocity_history) >= 3:
                recent_velocity = velocity_history[-3:]
                avg_velocity = sum(recent_velocity) / len(recent_velocity)

                # 与早期速度比较
                if len(velocity_history) >= 6:
                    early_velocity = velocity_history[-6:-3]
                    avg_early_velocity = sum(early_velocity) / len(early_velocity) if early_velocity else 0

                    if avg_velocity > avg_early_velocity * 1.2:
                        trends["velocity_trend"] = "increasing"
                    elif avg_velocity < avg_early_velocity * 0.8:
                        trends["velocity_trend"] = "decreasing"
                        trends["risk_factors"].append("学习速度在下降")

        # 预测完成时间
        days_elapsed = self._calculate_days_elapsed(goal)
        current_progress_value = current_progress.get("overall_progress", 0)

        if days_elapsed > 0 and current_progress_value > 0:
            # 线性预测
            if current_progress_value > 0:
                estimated_total_days = days_elapsed / current_progress_value
                days_remaining = estimated_total_days - days_elapsed

                try:
                    predicted_date = datetime.now() + timedelta(days=days_remaining)
                    trends["predicted_completion"] = predicted_date.isoformat()

                    # 检查是否按时
                    if goal.estimated_completion:
                        estimated_date = datetime.fromisoformat(goal.estimated_completion)
                        days_until_deadline = (estimated_date - datetime.now()).days

                        if days_remaining > days_until_deadline * 1.2:
                            trends["risk_factors"].append(f"预计将延期{int(days_remaining - days_until_deadline)}天")
                except:
                    pass

        return trends

    def _check_progress_alerts(self,
                              goal: LearningGoal,
                              current_progress: Dict[str, Any],
                              progress_metrics: Dict[str, Any],
                              trend_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查进度预警"""
        alerts = []

        # 进度过慢预警
        current_progress_value = current_progress.get("overall_progress", 0)
        days_elapsed = self._calculate_days_elapsed(goal)

        if days_elapsed > 7 and current_progress_value < 0.2:
            alerts.append({
                "type": "slow_progress",
                "severity": "high",
                "message": f"学习7天后进度仅{current_progress_value:.1%}，可能过慢",
                "suggested_action": "检查学习方法或增加学习时间"
            })

        # 学习速度下降预警
        if trend_analysis.get("velocity_trend") == "decreasing":
            alerts.append({
                "type": "decreasing_velocity",
                "severity": "medium",
                "message": "学习速度在下降",
                "suggested_action": "分析原因并调整学习策略"
            })

        # 一致性预警
        consistency = progress_metrics.get("consistency", {}).get("value", 0)
        if consistency < 0.3:
            alerts.append({
                "type": "low_consistency",
                "severity": "medium",
                "message": f"学习一致性较低({consistency:.1%})",
                "suggested_action": "建立更规律的学习习惯"
            })

        # 参与度预警
        engagement = progress_metrics.get("engagement", {}).get("value", 0)
        if engagement < 0.4:
            alerts.append({
                "type": "low_engagement",
                "severity": "medium",
                "message": f"学习参与度较低({engagement:.1%})",
                "suggested_action": "增加学习互动性或调整内容"
            })

        # 进度停滞预警
        if "progress_history" in goal.metadata:
            history = goal.metadata["progress_history"]
            if len(history) >= 3:
                recent_progress = [h.get("progress", 0) for h in history[-3:]]
                if max(recent_progress) - min(recent_progress) < 0.02:  # 几乎无变化
                    alerts.append({
                        "type": "progress_stagnation",
                        "severity": "high",
                        "message": "最近3次检查进度几乎无变化",
                        "suggested_action": "突破学习瓶颈，尝试新方法"
                    })

        # 思维导图进度不均衡预警
        if "mindmap_layer_progress" in current_progress.get("progress_details", {}):
            layer_progress = current_progress["progress_details"]["mindmap_layer_progress"]
            if layer_progress:
                progress_values = list(layer_progress.values())
                if len(progress_values) >= 2:
                    progress_range = max(progress_values) - min(progress_values)
                    if progress_range > 0.5:  # 不同层级进度差异过大
                        alerts.append({
                            "type": "unbalanced_mindmap_progress",
                            "severity": "medium",
                            "message": "思维导图不同层级学习进度不均衡",
                            "suggested_action": "调整学习重点，加强薄弱层级"
                        })

        return alerts

    def _generate_progress_recommendations(self,
                                         goal: LearningGoal,
                                         current_progress: Dict[str, Any],
                                         progress_metrics: Dict[str, Any],
                                         trend_analysis: Dict[str, Any],
                                         alerts: List[Dict[str, Any]]) -> List[str]:
        """生成进度建议"""
        recommendations = []

        # 基于进度状态
        current_progress_value = current_progress.get("overall_progress", 0)

        if current_progress_value < 0.3:
            recommendations.append("学习初期，建议打好基础，不要急于求成")
        elif current_progress_value < 0.7:
            recommendations.append("学习中期，建议加强练习和复习")
        else:
            recommendations.append("学习后期，建议进行综合应用和总结")

        # 基于学习速度
        learning_speed = progress_metrics.get("learning_speed", {}).get("value", 0)
        if learning_speed < 2:
            recommendations.append(f"当前学习速度较低({learning_speed:.1f}项目/天)，建议提高学习效率")
        elif learning_speed > 10:
            recommendations.append(f"学习速度很快({learning_speed:.1f}项目/天)，可以考虑增加学习深度")

        # 基于趋势
        progress_trend = trend_analysis.get("progress_trend", "stable")
        if progress_trend == "decelerating":
            recommendations.append("检测到学习进度在减慢，建议分析原因并调整")
        elif progress_trend == "accelerating":
            recommendations.append("学习进度在加速，继续保持当前节奏")

        # 基于风险因素
        if trend_analysis.get("risk_factors"):
            for risk in trend_analysis["risk_factors"]:
                if "延期" in risk:
                    recommendations.append("预计将延期完成，建议增加学习时间或调整目标")

        # 基于整体分数
        overall_score = progress_metrics.get("overall_score", {}).get("value", 0)
        if overall_score < 0.5:
            recommendations.append("整体学习状况有待改善，建议全面检查学习计划")
        elif overall_score > 0.8:
            recommendations.append("学习状况良好，可以继续保持或挑战更高目标")

        return recommendations

    def _analyze_node_progress(self,
                              node_map: Dict[str, MindMapNode],
                              progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析节点进度"""
        node_progress = {
            "total_nodes": len(node_map),
            "completed_nodes": 0,
            "learning_nodes": 0,
            "pending_nodes": 0,
            "node_status_distribution": {},
            "node_progress_by_type": {},
            "node_progress_by_depth": {}
        }

        # 统计节点状态
        for node_id, node in node_map.items():
            status = node.learning_status

            if status not in node_progress["node_status_distribution"]:
                node_progress["node_status_distribution"][status] = 0
            node_progress["node_status_distribution"][status] += 1

            if status == "mastered":
                node_progress["completed_nodes"] += 1
            elif status == "learning":
                node_progress["learning_nodes"] += 1
            else:
                node_progress["pending_nodes"] += 1

            # 按类型统计
            node_type = node.node_type
            if node_type not in node_progress["node_progress_by_type"]:
                node_progress["node_progress_by_type"][node_type] = {
                    "total": 0,
                    "completed": 0,
                    "progress": 0.0
                }

            node_progress["node_progress_by_type"][node_type]["total"] += 1
            if status == "mastered":
                node_progress["node_progress_by_type"][node_type]["completed"] += 1

            # 按深度统计
            depth = node.depth
            if depth not in node_progress["node_progress_by_depth"]:
                node_progress["node_progress_by_depth"][depth] = {
                    "total": 0,
                    "completed": 0,
                    "progress": 0.0
                }

            node_progress["node_progress_by_depth"][depth]["total"] += 1
            if status == "mastered":
                node_progress["node_progress_by_depth"][depth]["completed"] += 1

        # 计算进度百分比
        for node_type, stats in node_progress["node_progress_by_type"].items():
            if stats["total"] > 0:
                stats["progress"] = stats["completed"] / stats["total"]

        for depth, stats in node_progress["node_progress_by_depth"].items():
            if stats["total"] > 0:
                stats["progress"] = stats["completed"] / stats["total"]

        return node_progress

    def _analyze_layer_progress(self,
                               node_map: Dict[str, MindMapNode],
                               progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析层级进度"""
        layer_progress = {}

        # 按深度分组
        depth_groups = defaultdict(list)
        for node_id, node in node_map.items():
            depth_groups[node.depth].append(node)

        # 计算每层进度
        for depth, nodes in depth_groups.items():
            total_nodes = len(nodes)
            mastered_nodes = sum(1 for node in nodes if node.learning_status == "mastered")
            progress = mastered_nodes / total_nodes if total_nodes > 0 else 0.0

            layer_progress[depth] = {
                "total_nodes": total_nodes,
                "mastered_nodes": mastered_nodes,
                "progress": progress,
                "status": "completed" if progress >= 0.8 else
                          "in_progress" if progress >= 0.3 else "pending"
            }

        return layer_progress

    def _analyze_mindmap_structure_progress(self,
                                          node_map: Dict[str, MindMapNode],
                                          progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析思维导图结构进度"""
        structure_progress = {
            "branch_completion": {},
            "prerequisite_chains": {},
            "structural_integrity": 0.0
        }

        # 分析分支完成情况
        branch_roots = [node for node in node_map.values() if node.depth == 1]

        for branch_root in branch_roots:
            # 获取分支所有节点
            branch_nodes = self._get_branch_nodes(branch_root.id, node_map)
            total_nodes = len(branch_nodes)
            mastered_nodes = sum(1 for node_id in branch_nodes 
                                if node_map.get(node_id, MindMapNode("", "", learning_status="pending")).learning_status == "mastered")

            if total_nodes > 0:
                branch_progress = mastered_nodes / total_nodes
                structure_progress["branch_completion"][branch_root.title] = {
                    "total_nodes": total_nodes,
                    "mastered_nodes": mastered_nodes,
                    "progress": branch_progress
                }

        # 分析先决条件链
        prerequisite_chains = self._identify_prerequisite_chains(node_map)
        structure_progress["prerequisite_chains"] = prerequisite_chains

        # 计算结构完整性
        if node_map:
            # 结构完整性 = 已完成节点的重要性加权平均
            total_importance = 0
            completed_importance = 0

            for node in node_map.values():
                total_importance += node.importance
                if node.learning_status == "mastered":
                    completed_importance += node.importance

            if total_importance > 0:
                structure_progress["structural_integrity"] = completed_importance / total_importance

        return structure_progress

    def _get_branch_nodes(self, root_id: str, node_map: Dict[str, MindMapNode]) -> List[str]:
        """获取分支所有节点"""
        branch_nodes = []

        def collect_nodes(node_id: str):
            node = node_map.get(node_id)
            if not node:
                return

            branch_nodes.append(node_id)
            for child_id in node.children_ids:
                collect_nodes(child_id)

        collect_nodes(root_id)
        return branch_nodes

    def _identify_prerequisite_chains(self, node_map: Dict[str, MindMapNode]) -> Dict[str, Any]:
        """识别先决条件链"""
        chains = {
            "completed_chains": [],
            "incomplete_chains": [],
            "blocking_nodes": []
        }

        # 查找有先决条件的节点
        for node_id, node in node_map.items():
            if node.prerequisites:
                # 检查先决条件是否满足
                prerequisites_completed = all(
                    node_map.get(prereq_id, MindMapNode("", "", learning_status="pending")).learning_status == "mastered"
                    for prereq_id in node.prerequisites
                )

                chain = {
                    "node_id": node_id,
                    "node_title": node.title,
                    "prerequisites": node.prerequisites,
                    "all_completed": prerequisites_completed,
                    "blocked": not prerequisites_completed and node.learning_status != "mastered"
                }

                if prerequisites_completed:
                    chains["completed_chains"].append(chain)
                else:
                    chains["incomplete_chains"].append(chain)

                    # 识别阻塞节点
                    if chain["blocked"]:
                        chains["blocking_nodes"].append(node_id)

        return chains

    def _identify_weak_areas(self,
                            node_map: Dict[str, MindMapNode],
                            progress_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别薄弱区域"""
        weak_areas = []

        # 识别学习困难的节点
        for node_id, node in node_map.items():
            if node.learning_status == "learning":
                # 检查学习时间是否过长
                if node.actual_time_minutes > node.estimated_time_minutes * 2:
                    weak_areas.append({
                        "node_id": node_id,
                        "node_title": node.title,
                        "reason": "学习时间远超预估",
                        "actual_time": node.actual_time_minutes,
                        "estimated_time": node.estimated_time_minutes
                    })

        # 识别重要性高但未掌握的节点
        for node_id, node in node_map.items():
            if node.learning_status != "mastered" and node.importance > 0.7:
                weak_areas.append({
                    "node_id": node_id,
                    "node_title": node.title,
                    "reason": "高重要性节点尚未掌握",
                    "importance": node.importance,
                    "status": node.learning_status
                })

        # 识别先决条件未满足的阻塞节点
        for node_id, node in node_map.items():
            if node.prerequisites and node.learning_status != "mastered":
                incomplete_prereqs = []
                for prereq_id in node.prerequisites:
                    prereq_node = node_map.get(prereq_id)
                    if prereq_node and prereq_node.learning_status != "mastered":
                        incomplete_prereqs.append(prereq_id)

                if incomplete_prereqs:
                    weak_areas.append({
                        "node_id": node_id,
                        "node_title": node.title,
                        "reason": "先决条件未满足",
                        "incomplete_prerequisites": incomplete_prereqs
                    })

        return weak_areas

    def _identify_strong_areas(self,
                              node_map: Dict[str, MindMapNode],
                              progress_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别优势区域"""
        strong_areas = []

        # 识别快速掌握的节点
        for node_id, node in node_map.items():
            if node.learning_status == "mastered":
                # 检查是否快速掌握
                if node.actual_time_minutes > 0 and node.actual_time_minutes < node.estimated_time_minutes * 0.5:
                    strong_areas.append({
                        "node_id": node_id,
                        "node_title": node.title,
                        "reason": "快速掌握",
                        "actual_time": node.actual_time_minutes,
                        "estimated_time": node.estimated_time_minutes,
                        "efficiency_ratio": node.estimated_time_minutes / node.actual_time_minutes
                    })

        # 识别重要性高且已掌握的节点
        for node_id, node in node_map.items():
            if node.learning_status == "mastered" and node.importance > 0.8:
                strong_areas.append({
                    "node_id": node_id,
                    "node_title": node.title,
                    "reason": "高重要性节点已掌握",
                    "importance": node.importance,
                    "mastery_level": "excellent"
                })

        # 识别完整掌握的分支
        branch_roots = [node for node in node_map.values() if node.depth == 1]

        for branch_root in branch_roots:
            branch_nodes = self._get_branch_nodes(branch_root.id, node_map)
            mastered_count = sum(1 for node_id in branch_nodes 
                               if node_map.get(node_id, MindMapNode("", "", learning_status="pending")).learning_status == "mastered")

            if mastered_count == len(branch_nodes) and len(branch_nodes) > 3:
                strong_areas.append({
                    "branch_root_id": branch_root.id,
                    "branch_title": branch_root.title,
                    "reason": "完整分支掌握",
                    "total_nodes": len(branch_nodes),
                    "mastered_nodes": mastered_count
                })

        return strong_areas

    def _generate_mindmap_recommendations(self,
                                        node_map: Dict[str, MindMapNode],
                                        progress_data: Dict[str, Any],
                                        weak_areas: List[Dict[str, Any]],
                                        strong_areas: List[Dict[str, Any]]) -> List[str]:
        """生成思维导图学习建议"""
        recommendations = []

        # 针对薄弱区域的建议
        if weak_areas:
            weak_count = len(weak_areas)
            recommendations.append(f"发现{weak_count}个薄弱区域，建议优先加强")

            # 具体建议
            for weak_area in weak_areas[:3]:  # 最多显示3个
                reason = weak_area.get("reason", "")
                if "学习时间远超预估" in reason:
                    recommendations.append(f"节点'{weak_area['node_title']}'学习时间过长，建议简化学习内容或寻求帮助")
                elif "高重要性节点尚未掌握" in reason:
                    recommendations.append(f"高重要性节点'{weak_area['node_title']}'尚未掌握，建议优先学习")
                elif "先决条件未满足" in reason:
                    recommendations.append(f"节点'{weak_area['node_title']}'的先决条件未满足，建议先学习先决节点")

        # 利用优势区域的建议
        if strong_areas:
            strong_count = len(strong_areas)
            recommendations.append(f"识别出{strong_count}个优势区域，可以在此基础上深化学习")

        # 结构优化建议
        branch_completion = progress_data.get("branch_completion", {})
        if branch_completion:
            incomplete_branches = [branch for branch, stats in branch_completion.items() 
                                 if stats.get("progress", 0) < 0.5]

            if incomplete_branches:
                recommendations.append(f"发现{len(incomplete_branches)}个完成度较低的分支，建议集中学习")

        # 进度均衡建议
        layer_progress = progress_data.get("layer_progress", {})
        if layer_progress and len(layer_progress) >= 2:
            progress_values = [stats.get("progress", 0) for stats in layer_progress.values()]
            if max(progress_values) - min(progress_values) > 0.4:
                recommendations.append("不同层级学习进度不均衡，建议加强薄弱层级")

        return recommendations

    def _create_progress_charts(self,
                               goal: LearningGoal,
                               progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建进度图表数据"""
        charts = {
            "progress_over_time": {
                "labels": [],
                "datasets": [
                    {
                        "label": "整体进度",
                        "data": [],
                        "borderColor": "#4CAF50",
                        "backgroundColor": "rgba(76, 175, 80, 0.1)"
                    }
                ]
            },
            "learning_velocity": {
                "labels": [],
                "datasets": [
                    {
                        "label": "学习速度(项目/天)",
                        "data": [],
                        "borderColor": "#2196F3",
                        "backgroundColor": "rgba(33, 150, 243, 0.1)"
                    }
                ]
            },
            "progress_by_category": {
                "labels": [],
                "datasets": [
                    {
                        "label": "完成率",
                        "data": [],
                        "backgroundColor": ["#4CAF50", "#FFC107", "#F44336", "#9C27B0", "#03A9F4"]
                    }
                ]
            }
        }

        # 进度随时间变化
        if "progress_history" in progress_data:
            history = progress_data["progress_history"]
            for entry in history[-10:]:  # 最近10次记录
                if "date" in entry and "progress" in entry:
                    charts["progress_over_time"]["labels"].append(entry["date"])
                    charts["progress_over_time"]["datasets"][0]["data"].append(entry["progress"])

        # 学习速度
        if "learning_velocity_history" in progress_data:
            velocity_history = progress_data["learning_velocity_history"]
            for i, velocity in enumerate(velocity_history[-10:]):
                charts["learning_velocity"]["labels"].append(f"第{i+1}周")
                charts["learning_velocity"]["datasets"][0]["data"].append(velocity)

        # 按类别进度
        if "category_progress" in progress_data:
            category_progress = progress_data["category_progress"]
            for category, progress in category_progress.items():
                charts["progress_by_category"]["labels"].append(category)
                charts["progress_by_category"]["datasets"][0]["data"].append(progress)

        return charts

    def _create_trend_visualizations(self,
                                   goal: LearningGoal,
                                   progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建趋势可视化"""
        visualizations = {
            "trend_indicators": [],
            "comparison_charts": [],
            "forecast_visualization": {}
        }

        # 趋势指标
        current_progress = goal.overall_progress
        days_elapsed = self._calculate_days_elapsed(goal)

        if days_elapsed > 0:
            daily_progress_rate = current_progress / days_elapsed if current_progress > 0 else 0

            visualizations["trend_indicators"] = [
                {
                    "name": "当前进度",
                    "value": f"{current_progress:.1%}",
                    "trend": "up" if current_progress > 0 else "stable"
                },
                {
                    "name": "日均进度",
                    "value": f"{daily_progress_rate:.2%}",
                    "trend": "up" if daily_progress_rate > 0.01 else "stable"
                },
                {
                    "name": "预计完成天数",
                    "value": f"{int((1 - current_progress) / daily_progress_rate) if daily_progress_rate > 0 else '未知'}",
                    "trend": "down" if daily_progress_rate > 0.02 else "stable"
                }
            ]

        # 对比图表（目标 vs 实际）
        if "planned_progress" in progress_data and "actual_progress" in progress_data:
            planned = progress_data["planned_progress"]
            actual = progress_data["actual_progress"]

            if len(planned) == len(actual):
                comparison_data = {
                    "labels": [f"第{i+1}周" for i in range(len(planned))],
                    "datasets": [
                        {
                            "label": "计划进度",
                            "data": planned,
                            "borderColor": "#FF9800",
                            "backgroundColor": "transparent"
                        },
                        {
                            "label": "实际进度",
                            "data": actual,
                            "borderColor": "#4CAF50",
                            "backgroundColor": "transparent"
                        }
                    ]
                }
                visualizations["comparison_charts"].append(comparison_data)

        # 预测可视化
        prediction = self.predict_completion_time(goal, progress_data, [])
        if "weighted_prediction" in prediction:
            forecast = prediction["weighted_prediction"]
            visualizations["forecast_visualization"] = {
                "predicted_completion": forecast.get("predicted_date"),
                "confidence": forecast.get("confidence", 0),
                "on_track": forecast.get("on_track", "unknown")
            }

        return visualizations

    def _create_mindmap_visualizations(self,
                                     goal: LearningGoal,
                                     node_map: Dict[str, MindMapNode],
                                     progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建思维导图可视化"""
        visualizations = {
            "node_status_heatmap": {},
            "progress_by_depth": {},
            "learning_path_visualization": {}
        }

        # 节点状态热图数据
        node_status_data = []
        for node_id, node in node_map.items():
            status_color = {
                "mastered": "#4CAF50",
                "learning": "#FFC107",
                "reviewing": "#2196F3",
                "pending": "#9E9E9E"
            }.get(node.learning_status, "#9E9E9E")

            node_status_data.append({
                "id": node_id,
                "title": node.title,
                "depth": node.depth,
                "status": node.learning_status,
                "color": status_color,
                "importance": node.importance,
                "difficulty": node.difficulty
            })

        visualizations["node_status_heatmap"] = {
            "nodes": node_status_data,
            "color_scheme": {
                "mastered": "#4CAF50",
                "learning": "#FFC107",
                "reviewing": "#2196F3",
                "pending": "#9E9E9E"
            }
        }

        # 按深度进度数据
        depth_progress = {}
        depth_groups = defaultdict(list)

        for node in node_map.values():
            depth_groups[node.depth].append(node)

        for depth, nodes in depth_groups.items():
            total = len(nodes)
            mastered = sum(1 for node in nodes if node.learning_status == "mastered")
            progress = mastered / total if total > 0 else 0

            depth_progress[depth] = {
                "total": total,
                "mastered": mastered,
                "progress": progress
            }

        visualizations["progress_by_depth"] = depth_progress

        # 学习路径可视化
        learning_path = self._extract_learning_path(node_map, progress_data)
        visualizations["learning_path_visualization"] = {
            "path_nodes": learning_path["nodes"],
            "path_connections": learning_path["connections"],
            "current_position": learning_path["current_position"]
        }

        return visualizations

    def _extract_learning_path(self,
                              node_map: Dict[str, MindMapNode],
                              progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取学习路径"""
        path_nodes = []
        path_connections = []

        # 从根节点开始
        root_nodes = [node for node in node_map.values() if node.depth == 0]

        if root_nodes:
            root = root_nodes[0]
            path_nodes.append({
                "id": root.id,
                "title": root.title,
                "status": root.learning_status,
                "type": "root"
            })

        # 添加已掌握的节点
        mastered_nodes = [node for node in node_map.values() if node.learning_status == "mastered"]
        for node in mastered_nodes:
            if node.depth > 0:  # 排除根节点
                path_nodes.append({
                    "id": node.id,
                    "title": node.title,
                    "status": node.learning_status,
                    "type": "mastered",
                    "depth": node.depth
                })

        # 添加正在学习的节点
        learning_nodes = [node for node in node_map.values() if node.learning_status == "learning"]
        current_position = None

        for node in learning_nodes:
            path_nodes.append({
                "id": node.id,
                "title": node.title,
                "status": node.learning_status,
                "type": "current",
                "depth": node.depth
            })

            # 设置当前位置
            if not current_position or node.importance > 0.7:
                current_position = node.id

        # 创建连接关系
        for node in node_map.values():
            for child_id in node.children_ids:
                if (node.id in [n["id"] for n in path_nodes] and 
                    child_id in [n["id"] for n in path_nodes]):
                    path_connections.append({
                        "from": node.id,
                        "to": child_id,
                        "type": "parent_child"
                    })

        return {
            "nodes": path_nodes,
            "connections": path_connections,
            "current_position": current_position
        }

    def _predict_with_linear_model(self,
                                  goal: LearningGoal,
                                  progress_data: Dict[str, Any],
                                  learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用线性模型预测"""
        current_progress = goal.overall_progress
        days_elapsed = self._calculate_days_elapsed(goal)

        if days_elapsed <= 0 or current_progress <= 0:
            return {
                "method": "linear",
                "predicted_date": None,
                "days_remaining": None,
                "confidence": 0.0,
                "on_track": "unknown"
            }

        # 线性外推
        total_days_needed = days_elapsed / current_progress
        days_remaining = total_days_needed - days_elapsed

        try:
            predicted_date = datetime.now() + timedelta(days=days_remaining)

            # 检查是否按时
            on_track = "on_time"
            if goal.estimated_completion:
                estimated_date = datetime.fromisoformat(goal.estimated_completion)
                days_until_deadline = (estimated_date - datetime.now()).days

                if days_remaining > days_until_deadline * 1.1:
                    on_track = "behind"
                elif days_remaining < days_until_deadline * 0.9:
                    on_track = "ahead"

            # 置信度基于数据点数量
            confidence = min(days_elapsed / 7, 0.9)  # 每过一周增加置信度，最高0.9

            return {
                "method": "linear",
                "predicted_date": predicted_date.isoformat(),
                "days_remaining": max(0, int(days_remaining)),
                "confidence": confidence,
                "on_track": on_track
            }
        except:
            return {
                "method": "linear",
                "predicted_date": None,
                "days_remaining": None,
                "confidence": 0.0,
                "on_track": "unknown"
            }

    def _predict_with_learning_curve(self,
                                    goal: LearningGoal,
                                    progress_data: Dict[str, Any],
                                    learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用学习曲线模型预测"""
        # 学习曲线模型考虑了学习效率随时间的变化
        current_progress = goal.overall_progress
        days_elapsed = self._calculate_days_elapsed(goal)

        if days_elapsed <= 0 or current_progress <= 0:
            return {
                "method": "learning_curve",
                "predicted_date": None,
                "days_remaining": None,
                "confidence": 0.0,
                "on_track": "unknown"
            }

        # 获取历史学习速度
        if learning_history and len(learning_history) >= 3:
            # 计算平均学习速度
            daily_progress_rates = []
            for i in range(1, min(4, len(learning_history))):
                if i < len(learning_history):
                    session = learning_history[-i]
                    if "progress_gain" in session and "duration_days" in session:
                        rate = session["progress_gain"] / session["duration_days"]
                        daily_progress_rates.append(rate)

            if daily_progress_rates:
                avg_daily_rate = sum(daily_progress_rates) / len(daily_progress_rates)

                # 应用学习曲线效应：后期学习可能变慢或变快
                remaining_progress = 1.0 - current_progress

                # 简单模型：剩余进度除以平均速度
                days_remaining = remaining_progress / avg_daily_rate if avg_daily_rate > 0 else 0

                # 调整因子：基于学习曲线
                curve_factor = 1.0
                if current_progress > 0.7:
                    # 后期可能遇到困难，学习变慢
                    curve_factor = 1.2
                elif current_progress < 0.3:
                    # 初期可能较慢，但建立基础后可能加速
                    curve_factor = 0.9

                days_remaining *= curve_factor

                try:
                    predicted_date = datetime.now() + timedelta(days=days_remaining)

                    return {
                        "method": "learning_curve",
                        "predicted_date": predicted_date.isoformat(),
                        "days_remaining": max(0, int(days_remaining)),
                        "confidence": 0.7,
                        "on_track": "on_time"  # 简化处理
                    }
                except:
                    pass

        # 回退到线性模型
        return self._predict_with_linear_model(goal, progress_data, learning_history)

    def _predict_with_time_series(self,
                                 goal: LearningGoal,
                                 progress_data: Dict[str, Any],
                                 learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用时间序列模型预测"""
        # 简化版时间序列预测
        if learning_history and len(learning_history) >= 5:
            # 提取时间序列数据
            dates = []
            progress_values = []

            for session in learning_history[-5:]:
                if "date" in session and "progress" in session:
                    dates.append(session["date"])
                    progress_values.append(session["progress"])

            if len(progress_values) >= 3:
                # 简单趋势分析
                recent_trend = progress_values[-1] - progress_values[-3]

                # 预测剩余时间
                current_progress = progress_values[-1] if progress_values else 0
                remaining_progress = 1.0 - current_progress

                if recent_trend > 0:
                    # 有进展趋势
                    estimated_daily_rate = recent_trend / 3  # 最近3天的平均日进展
                    if estimated_daily_rate > 0:
                        days_remaining = remaining_progress / estimated_daily_rate

                        try:
                            predicted_date = datetime.now() + timedelta(days=days_remaining)

                            return {
                                "method": "time_series",
                                "predicted_date": predicted_date.isoformat(),
                                "days_remaining": max(0, int(days_remaining)),
                                "confidence": 0.6,
                                "on_track": "on_time"
                            }
                        except:
                            pass

        # 回退到线性模型
        return self._predict_with_linear_model(goal, progress_data, learning_history)

    def _predict_with_adaptive_model(self,
                                    goal: LearningGoal,
                                    progress_data: Dict[str, Any],
                                    learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用自适应模型预测"""
        # 自适应模型考虑多个因素
        factors = []

        # 1. 当前进度因素
        current_progress = goal.overall_progress
        if current_progress > 0.8:
            factors.append(0.9)  # 接近完成，预测较准确
        elif current_progress > 0.5:
            factors.append(0.7)
        elif current_progress > 0.2:
            factors.append(0.5)
        else:
            factors.append(0.3)  # 初期不确定性高

        # 2. 历史数据量因素
        if learning_history:
            data_points = len(learning_history)
            data_factor = min(data_points / 10, 1.0)  # 10个数据点为充分
            factors.append(data_factor)
        else:
            factors.append(0.1)

        # 3. 进度稳定性因素
        if "progress_history" in progress_data:
            history = progress_data["progress_history"]
            if len(history) >= 3:
                recent_changes = []
                for i in range(1, min(4, len(history))):
                    if i < len(history):
                        change = abs(history[-i].get("progress", 0) - history[-i-1].get("progress", 0))
                        recent_changes.append(change)

                if recent_changes:
                    avg_change = sum(recent_changes) / len(recent_changes)
                    stability_factor = 1.0 - min(avg_change * 5, 0.8)  # 变化越小越稳定
                    factors.append(stability_factor)

        # 计算综合置信度
        if factors:
            confidence = sum(factors) / len(factors)
        else:
            confidence = 0.5

        # 使用线性模型作为基础
        linear_prediction = self._predict_with_linear_model(goal, progress_data, learning_history)

        # 调整置信度
        linear_prediction["confidence"] = confidence
        linear_prediction["method"] = "adaptive"

        return linear_prediction

    def _calculate_prediction_confidence(self,
                                       prediction_models: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """计算预测置信度"""
        confidences = {}

        for model_name, prediction in prediction_models.items():
            confidences[model_name] = prediction.get("confidence", 0.5)

        # 综合置信度（加权平均）
        if confidences:
            weights = {
                "linear": 0.3,
                "learning_curve": 0.3,
                "time_series": 0.2,
                "adaptive": 0.2
            }

            weighted_sum = 0
            weight_sum = 0

            for model_name, confidence in confidences.items():
                weight = weights.get(model_name, 0.1)
                weighted_sum += confidence * weight
                weight_sum += weight

            if weight_sum > 0:
                confidences["overall"] = weighted_sum / weight_sum
            else:
                confidences["overall"] = 0.5

        return confidences

    def _calculate_weighted_prediction(self,
                                     prediction_models: Dict[str, Dict[str, Any]],
                                     confidence_scores: Dict[str, float]) -> Dict[str, Any]:
        """计算加权预测"""
        # 收集所有预测日期
        predictions = []

        for model_name, prediction in prediction_models.items():
            predicted_date = prediction.get("predicted_date")
            confidence = confidence_scores.get(model_name, 0.5)

            if predicted_date:
                try:
                    date_obj = datetime.fromisoformat(predicted_date)
                    predictions.append({
                        "date": date_obj,
                        "confidence": confidence,
                        "model": model_name
                    })
                except:
                    continue

        if not predictions:
            return {
                "predicted_date": None,
                "confidence": 0.0,
                "on_track": "unknown"
            }

        # 加权平均日期
        total_weight = sum(p["confidence"] for p in predictions)
        weighted_date = datetime.now()

        if total_weight > 0:
            # 计算加权平均的天数偏移
            weighted_days = 0

            for pred in predictions:
                days_offset = (pred["date"] - datetime.now()).days
                weight = pred["confidence"] / total_weight
                weighted_days += days_offset * weight

            weighted_date = datetime.now() + timedelta(days=weighted_days)

        # 判断是否按时
        on_track = "on_time"

        # 检查不同模型的一致性
        if len(predictions) >= 2:
            dates = [p["date"] for p in predictions]
            min_date = min(dates)
            max_date = max(dates)
            date_range = (max_date - min_date).days

            if date_range > 14:  # 预测差异超过14天
                on_track = "uncertain"

        return {
            "predicted_date": weighted_date.isoformat(),
            "confidence": confidence_scores.get("overall", 0.5),
            "on_track": on_track
        }

    def _record_monitoring_history(self, goal_id: str, monitoring_report: Dict[str, Any]) -> None:
        """记录监控历史"""
        history_entry = {
            "monitored_at": monitoring_report.get("monitored_at", datetime.now().isoformat()),
            "strategy": monitoring_report.get("strategy", ""),
            "progress": monitoring_report.get("current_progress", {}).get("overall_progress", 0),
            "alerts_count": len(monitoring_report.get("alerts", [])),
            "metrics_score": monitoring_report.get("progress_metrics", {}).get("overall_score", {}).get("value", 0)
        }

        self.monitoring_history[goal_id].append(history_entry)

        # 限制历史记录长度
        if len(self.monitoring_history[goal_id]) > 50:
            self.monitoring_history[goal_id] = self.monitoring_history[goal_id][-50:]