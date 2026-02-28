# i18n.py - 国际化支持模块
"""多语言支持"""

import os

class Language:
    """语言配置"""
    CHINESE = "zh"
    ENGLISH = "en"
    AVAILABLE_LANGUAGES = [CHINESE, ENGLISH]

# 中文翻译
ZH = {
    # 系统启动
    "system_starting": "启动系统...",
    "system_welcome": "欢迎使用自主认知学习系统",
    "vision_loaded": "文明愿景核心已激活",
    
    # 命令提示
    "command_prompt": "> ",
    "enter_command": "请输入命令（输入 'help' 查看帮助）: ",
    "unknown_command": "未知命令: {command}",
    "command_help": "可用命令: {commands}",
    
    # 目标管理
    "create_goal": "创建学习目标",
    "goal_created": "目标创建成功",
    "goal_id": "ID",
    "goal_scale": "规模",
    "goal_estimated": "预估知识点",
    "list_goals": "列出所有目标",
    "select_goal": "选择目标",
    "goal_selected": "已选择目标",
    "no_active_goals": "没有活动目标",
    "pending_goals": "待处理目标",
    "completed_goals": "已完成目标",
    
    # 思维导图
    "generate_mindmap": "生成思维导图",
    "mindmap_for": "为'{goal}'生成思维导图",
    "mindmap_content": "思维导图内容",
    "mindmap_saved": "思维导图已保存",
    "mindmap_generated": "思维导图生成成功",
    "mindmap_nodes": "个节点",
    "ask_generate": "是否立即生成思维导图？",
    "yes_no": "(Y/n): ",
    
    # API 调用
    "calling_llm": "调用大模型",
    "llm_response": "LLM响应",
    "vision_injected": "愿景上下文已注入",
    "api_timeout": "API超时",
    "api_failed": "API调用失败",
    "use_fallback": "使用备选方案生成思维导图",
    
    # 学习规划
    "create_plan": "创建学习计划",
    "plan_for": "为'{goal}'创建学习计划",
    "plan_created": "学习计划创建成功",
    "schedule_learning": "调度学习会话",
    "start_learning": "开始学习",
    "learning_session": "学习会话",
    
    # 进度监控
    "monitor_progress": "监控进度",
    "progress": "进度",
    "mastery": "掌握度",
    "time_spent": "学习时间",
    "explore_mindmap": "探索思维导图",
    
    # 问答系统
    "ask_question": "询问问题",
    "answer": "回答",
    "confidence": "置信度",
    "processing_time": "处理时间",
    "clear_chat": "清空对话历史",
    "export_chat": "导出对话历史",
    "learning_advice": "学习方法建议",
    
    # 愿景核心
    "vision_status": "愿景核心状态",
    "vision_manifesto": "愿景宣言",
    "vision_decisions": "伦理决策记录",
    
    # 系统管理
    "system_status": "系统状态",
    "save_system": "保存系统状态",
    "load_system": "加载系统状态",
    "show_config": "显示配置",
    "show_stats": "显示统计",
    "exit_system": "退出系统",
    
    # 错误消息
    "error": "错误",
    "warning": "警告",
    "failed": "失败",
    "success": "成功",
    "not_found": "未找到",
    "already_exists": "已存在",
    "invalid_input": "无效输入",
    "permission_denied": "权限拒绝",
    
    # 状态
    "available": "可用",
    "unavailable": "不可用",
    "enabled": "已启用",
    "disabled": "已禁用",
    "active": "活动",
    "inactive": "不活动",
}

# 英文翻译
EN = {
    # System startup
    "system_starting": "Starting system...",
    "system_welcome": "Welcome to Autonomous Cognitive Learning System",
    "vision_loaded": "Civilizational Vision Core activated",
    
    # Command prompt
    "command_prompt": "> ",
    "enter_command": "Enter command (type 'help' for help): ",
    "unknown_command": "Unknown command: {command}",
    "command_help": "Available commands: {commands}",
    
    # Goal management
    "create_goal": "Create learning goal",
    "goal_created": "Goal created successfully",
    "goal_id": "ID",
    "goal_scale": "Scale",
    "goal_estimated": "Estimated items",
    "list_goals": "List all goals",
    "select_goal": "Select goal",
    "goal_selected": "Selected goal",
    "no_active_goals": "No active goals",
    "pending_goals": "Pending goals",
    "completed_goals": "Completed goals",
    
    # MindMap
    "generate_mindmap": "Generate mindmap",
    "mindmap_for": "Generating mindmap for '{goal}'",
    "mindmap_content": "MindMap Content",
    "mindmap_saved": "MindMap saved",
    "mindmap_generated": "MindMap generated successfully",
    "mindmap_nodes": "nodes",
    "ask_generate": "Generate mindmap now?",
    "yes_no": "(Y/n): ",
    
    # API calls
    "calling_llm": "Calling LLM",
    "llm_response": "LLM response",
    "vision_injected": "Vision context injected",
    "api_timeout": "API timeout",
    "api_failed": "API call failed",
    "use_fallback": "Using fallback method to generate mindmap",
    
    # Learning planning
    "create_plan": "Create learning plan",
    "plan_for": "Creating learning plan for '{goal}'",
    "plan_created": "Learning plan created successfully",
    "schedule_learning": "Schedule learning session",
    "start_learning": "Start learning",
    "learning_session": "Learning session",
    
    # Progress monitoring
    "monitor_progress": "Monitor progress",
    "progress": "Progress",
    "mastery": "Mastery",
    "time_spent": "Time spent",
    "explore_mindmap": "Explore mindmap",
    
    # Q&A system
    "ask_question": "Ask question",
    "answer": "Answer",
    "confidence": "Confidence",
    "processing_time": "Processing time",
    "clear_chat": "Clear chat history",
    "export_chat": "Export chat history",
    "learning_advice": "Learning advice",
    
    # Vision core
    "vision_status": "Vision core status",
    "vision_manifesto": "Vision manifesto",
    "vision_decisions": "Ethical decision records",
    
    # System management
    "system_status": "System status",
    "save_system": "Save system state",
    "load_system": "Load system state",
    "show_config": "Show configuration",
    "show_stats": "Show statistics",
    "exit_system": "Exit system",
    
    # Error messages
    "error": "Error",
    "warning": "Warning",
    "failed": "Failed",
    "success": "Success",
    "not_found": "Not found",
    "already_exists": "Already exists",
    "invalid_input": "Invalid input",
    "permission_denied": "Permission denied",
    
    # Status
    "available": "Available",
    "unavailable": "Unavailable",
    "enabled": "Enabled",
    "disabled": "Disabled",
    "active": "Active",
    "inactive": "Inactive",
}

class I18n:
    """国际化管理器"""
    
    def __init__(self, language: str = None):
        self.language = language or self._detect_language()
        self.translations = ZH if self.language == Language.CHINESE else EN
        
    def _detect_language(self) -> str:
        """检测系统语言"""
        # 1. 检查环境变量
        env_lang = os.getenv("APP_LANGUAGE", "")
        if env_lang in Language.AVAILABLE_LANGUAGES:
            return env_lang
        
        # 2. 检查系统语言
        import locale
        try:
            system_lang = locale.getdefaultlocale()[0] or ""
            if system_lang.startswith('zh'):
                return Language.CHINESE
            elif system_lang.startswith('en'):
                return Language.ENGLISH
        except:
            pass
        
        # 默认中文
        return Language.CHINESE
    
    def t(self, key: str, **kwargs) -> str:
        """翻译文本"""
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text
    
    def set_language(self, language: str) -> bool:
        """设置语言"""
        if language in Language.AVAILABLE_LANGUAGES:
            self.language = language
            self.translations = ZH if language == Language.CHINESE else EN
            return True
        return False

# 全局翻译实例
_i18n = None

def get_i18n() -> I18n:
    """获取翻译实例"""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n

def t(key: str, **kwargs) -> str:
    """快速翻译函数"""
    return get_i18n().t(key, **kwargs)
