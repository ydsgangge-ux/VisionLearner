# 多语言使用指南 / Multilingual Usage Guide

## 🌍 Supported Languages / 支持的语言

- ✅ 中文 (Chinese - zh)
- ✅ English (英语 - en)

---

## 🚀 快速启动 / Quick Start

### 中文用户 / Chinese Users

**方式1：双击启动**
```
双击 start_zh.bat
```

**方式2：命令行运行**
```bash
python main.py
```

**方式3：从语言菜单选择**
```
双击 start.bat
选择 2 (中文)
```

---

### English Users

**Method 1: Double-click to start**
```
Double-click start_en.bat
```

**Method 2: Run from command line**
```bash
python main_en.py
```

**Method 3: Select from language menu**
```
Double-click start.bat
Select 1 (English)
```

---

## 📋 命令对照 / Command Reference

### 目标管理 / Goal Management

| 中文命令 | English Command | 说明 / Description |
|---------|-----------------|------------------|
| `create <描述>` | `create <description>` | 创建学习目标 / Create learning goal |
| `list` | `list` | 列出所有目标 / List all goals |
| `select <ID>` | `select <ID>` | 选择目标 / Select goal |

### 学习规划 / Learning Planning

| 中文命令 | English Command | 说明 / Description |
|---------|-----------------|------------------|
| `plan` | `plan` | 创建学习计划 / Create learning plan |
| `schedule` | `schedule` | 调度学习会话 / Schedule learning session |
| `learn` | `learn` | 开始学习 / Start learning |

### 进度监控 / Progress Monitoring

| 中文命令 | English Command | 说明 / Description |
|---------|-----------------|------------------|
| `monitor` | `monitor` | 监控进度 / Monitor progress |
| `explore` | `explore` | 探索思维导图 / Explore mindmap |

### 问答系统 / Q&A System

| 中文命令 | English Command | 说明 / Description |
|---------|-----------------|------------------|
| `ask <问题>` | `ask <question>` | 询问问题 / Ask question |
| `clear_chat` | `clear_chat` | 清空对话历史 / Clear chat history |
| `export_chat` | `export_chat` | 导出对话历史 / Export chat |
| `learning_advice <主题>` | `learning_advice <topic>` | 获取学习方法建议 / Get learning advice |

### 系统管理 / System Management

| 中文命令 | English Command | 说明 / Description |
|---------|-----------------|------------------|
| `status` | `status` | 显示系统状态 / Show system status |
| `save` | `save` | 保存系统状态 / Save system state |
| `help` | `help` | 显示帮助 / Show help |
| `quit` / `exit` | `quit` / `exit` | 退出系统 / Exit system |

### 语言切换 / Language Switching

| 命令 / Command | 说明 / Description |
|---------|------------------|
| `lang zh` | 切换到中文 / Switch to Chinese |
| `lang en` | Switch to English | 切换到英语 |

---

## 💡 使用示例 / Usage Examples

### 中文示例

```
# 创建学习目标
> create 学习Python编程

# 生成思维导图
是否立即生成思维导图？: Y

# 询问问题
> ask 什么是Python函数？

# 获取学习方法建议
> learning_advice Python编程

# 查看系统状态
> status

# 退出系统
> quit
```

### English Example

```
# Create learning goal
> create Learn Python programming

# Generate mindmap
Generate mindmap now?: Y

# Ask question
> ask What is a Python function?

# Get learning advice
> learning_advice Python programming

# Show system status
> status

# Exit system
> quit
```

---

## ⚙️ 配置 / Configuration

### 切换默认语言 / Change Default Language

编辑 `main.py` 或 `main_en.py`，或者在环境变量中设置：

```bash
# Set to Chinese
export APP_LANGUAGE=zh

# Set to English
set APP_LANGUAGE=en
```

---

## 🌐 国际化开发 / Internationalization Development

### 添加新翻译 / Adding New Translations

1. 在 `i18n.py` 中添加翻译键值对
2. 更新 `ZH` 字典（中文翻译）
3. 更新 `EN` 字典（英文翻译）
4. 使用 `t()` 函数获取翻译文本

### 示例 / Example

```python
from i18n import t

# 使用翻译
print(t('goal_created'))  # 会根据当前语言显示对应的文本
```

---

## 📝 技术说明 / Technical Notes

### 字符编码 / Character Encoding

- 中文版本：使用 UTF-8 编码
- 英文版本：使用 UTF-8 编码
- Windows 启动脚本自动设置编码为 UTF-8 (chcp 65001)

### 字体支持 / Font Support

- 中文版本：自动检测系统中的中文字体（微软雅黑、黑体等）
- 英文版本：使用系统默认字体

---

## ❓ 常见问题 / FAQ

**Q: Can I switch language during runtime?**
A: Yes! Use `lang zh` or `lang en` command to switch.

**Q: How do I add a new language?**
A: Edit `i18n.py` to add new translation dictionaries and implement language detection logic.

**Q: Are all features available in both languages?**
A: Yes! All features are fully supported in both Chinese and English.

---

## 📞 获取帮助 / Getting Help

如需更多帮助或反馈问题，请联系开发团队。
For more help or to report issues, please contact the development team.
