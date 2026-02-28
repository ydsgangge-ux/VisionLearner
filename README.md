# 🌌 自主认知学习系统 —— 带「思想钢印」的终身学习 Agent（豆包 + 讯飞版）

**国内首个把文明愿景核心深度注入的自主学习系统**
愿景自动评估 + 上下文问答 + 伦理审查 + 思维导图全自动，已全部跑通！

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Ready-brightgreen)

## 📖 简介

## 🌌 愿景核心已集成

系统已成功集成"文明愿景核心"（思想钢印），在以下层次自动激活：

### 愿景核心集成点

| 层次 | 集成方式 | 作用 |
|------|---------|------|
| **Perception** | 愿景上下文注入 + 输出增强 | 在LLM调用时注入文明视角 |
| **Explorer** | 愿景相关性评估 | 为知识节点计算与愿景的契合度 |
| **Planner** | 伦理审查机制 | 在学习计划创建前进行伦理审查 |
| **Main** | 愿景状态显示 | 提供愿景相关命令和统计 |
| **QA系统** | 上下文感知问答 | 记忆对话历史，提供智能问答 |

---

## 🔌 API 配置（环境变量）

### 环境变量配置方式

系统已将所有API密钥改为从环境变量读取，提高安全性。

#### 1️⃣ 使用 .env 文件（推荐）

已创建 `.env` 文件，包含以下配置：

```bash
# 豆包大模型 API密钥（用于生成思维导图）
DOUBAO_API_KEY=你的API密钥

# 讯飞星火大模型配置（用于学习知识点）
SPARK_API_PASSWORD=你的API密码
SPARK_APPID=你的APPID
SPARK_API_SECRET=你的API密钥
SPARK_API_KEY=你的API Key

# DeepSeek API密钥（可选）
DEEPSEEK_API_KEY=你的密钥

# OpenAI API密钥（可选）
OPENAI_API_KEY=你的密钥
```

#### 2️⃣ 首次使用步骤

1. 安装依赖：
```bash
pip install python-dotenv
```

2. 编辑 `.env` 文件，填入你的API密钥

3. 运行系统：
```bash
python main.py
```

#### 3️⃣ 安全说明

- ⚠️ **重要**：`.env` 文件已添加到 `.gitignore`，不会被提交到Git仓库
- `.env.example` 是示例文件，可以安全分享
- 建议在代码托管平台上使用 Secrets 功能存储敏感信息

### 已配置的API

#### 1. 豆包大模型（用于生成思维导图）

```
✅ 状态: 可用（从环境变量读取）
BASE URL: https://ark.cn-beijing.volces.com/api/v3
MODEL: doubao-seed-1-8-251228
上下文长度: 32,000 tokens
```

**功能：** 生成思维导图、回答复杂问题

#### 2. 讯飞星火大模型（用于学习知识点）

```
✅ 状态: 可用（从环境变量读取）
HTTP URL: https://spark-api-open.xf-yun.com/v1/chat/completions
MODEL: Spark Lite
上下文长度: 4,000 tokens
```

**功能：** 学习知识点、问答、知识点讲解

---

## 📚 问答系统

### 功能特性

#### 1️⃣ 上下文感知问答
- **对话记忆**：自动记录对话历史（最近10轮）
- **上下文理解**：基于历史理解当前话题
- **知识检索**：从知识库和思维导图中检索相关信息
- **问题分类**：自动识别问题类型（知识/指导/进度/澄清）

#### 2️⃣ 学习指导顾问
- **方法建议**：根据主题推荐学习方法
  - 间隔重复（适合记忆类知识）
  - 主动回忆（适合考试准备）
  - 交错学习（适合复杂概念）
  - 思维导图学习法（适合系统性知识）

#### 3️⃣ 进度分析
- **总体进度**：学习完成度分析
- **时间统计**：学习时间跟踪
- **分数评估**：测试成绩分析
- **阶段建议**：基于进度提供针对性建议

---

## 🚀 快速开始

### 准备工作（只需 30 秒）

```bash
pip install -r requirements.txt
cp .env.example .env          # 然后用编辑器填入你的密钥
```

### 选择语言 / Language Selection

系统支持中英文双语界面：

**中文用户：**
- 双击 `start_zh.bat` 运行中文版本
- 或运行 `python main.py`

**English Users:**
- Double-click `start_en.bat` to run English version
- Or run `python main_en.py`

**Language Menu:**
- 双击 `start.bat` 启动语言选择菜单

### 方式1：运行完整系统

```bash
python main.py
```

### 方式2：测试 API 连接

```bash
python test_apis.py
```

### 方式3：测试问答系统

```bash
python test_qa_integration.py
```

### 方式4：运行集成测试

```bash
python simple_test.py
```

### Windows 用户

双击以下文件启动系统：
- `start.bat` - 语言选择菜单（推荐）
- `start_zh.bat` - 直接启动中文版本
- `start_en.bat` - 直接启动英文版本

---

## 📋 可用命令

### 目标管理
- `create <描述>` - 创建学习目标
- `list` - 列出所有目标
- `select <ID>` - 选择目标

### 学习规划
- `plan` - 创建学习计划
- `schedule` - 调度学习会话
- `learn` - 开始学习

### 进度监控
- `monitor` - 监控进度
- `explore` - 探索思维导图

### 📚 问答系统
- `ask <问题>` - 询问问题
  - 例: `ask 什么是Python函数？`
  - 例: `ask 如何学习机器学习？`
- `clear_chat` - 清空对话历史
- `export_chat` - 导出对话历史（JSON格式）
- `learning_advice <主题>` - 获取学习方法建议
  - 例: `learning_advice Python编程`
  - 例: `learning_advice 机器学习`

### 🌌 愿景核心
- `vision` - 显示愿景核心状态
- `vision_manifesto` - 显示愿景宣言
- `vision_decisions` - 显示伦理决策记录

### 系统管理
- `status` - 显示系统状态
- `save` - 保存系统状态
- `load` - 加载系统状态
- `config` - 显示配置
- `stats` - 显示统计数据
- `help` - 显示帮助
- `quit` / `exit` - 退出系统

---

## 🎯 使用示例

### 1. 问答系统使用

#### 询问知识点

```
> ask 什么是Python函数？

💬 回答：
--------------------------------------------------------------------------------
我目前还没有学习过这个知识点。您可以让我先学习相关内容，或者告诉我您想了解的具体方面。

📊 置信度: 30.0%
⏱️  处理时间: 0ms
```

#### 获取学习方法建议

```
> learning_advice Python编程

📚 正在为 'Python编程' 生成学习建议...

对于'Python编程'的学习，我建议：

1. 思维导图学习法：通过构建思维导图理解知识结构
   适用：系统性知识, 复杂概念, 项目规划
   步骤：确定中心主题 → 添加主要分支 → 细化子分支 → 添加关联 → 复习整个结构

2. 间隔重复：根据记忆曲线安排复习时间
   适用：记忆类知识, 单词, 概念
   步骤：初次学习 → 1天后复习 → 3天后复习 → 1周后复习 → 1月后复习
```

#### 对话历史管理

```
> export_chat

✅ 对话历史已导出到: chat_export_main_20260227_193045.json
   对话轮次: 15
   当前主题: Python编程

> clear_chat

✅ 对话历史已清空
```

### 2. 结合QA系统和学习流程

```
# 1. 创建学习目标
> create 学习Python编程

# 2. 询问学习问题
> ask 如何开始学习Python？

# 3. 获取学习方法建议
> learning_advice Python编程

# 4. 创建学习计划
> plan

# 5. 在学习过程中随时提问
> ask Python的列表推导式怎么用？

# 6. 查看进度分析
> monitor

# 7. 继续提问
> ask 机器学习和深度学习有什么区别？
```

---

## 📊 测试结果

### 问答系统测试

| 测试项 | 结果 | 说明 |
|-------|------|------|
| QA系统初始化 | ✅ 成功 | 成功集成到主系统 |
| 简单问答 | ✅ 成功 | 能回答各类问题 |
| 对话历史 | ✅ 正常 | 正确记录和检索历史 |
| 学习指导 | ✅ 正常 | 提供有效的学习建议 |
| 进度分析 | ✅ 正常 | 给出阶段性建议 |
| 对话管理 | ✅ 正常 | 清空和导出功能正常 |

### API 连接测试

| 测试项 | 结果 | 说明 |
|-------|------|------|
| 豆包 API | ✅ 成功 | 成功生成思维导图，愿景上下文已注入 |
| 讯飞 API | ✅ 成功 | 成功回答问题，愿景上下文已注入 |
| 模型切换 | ✅ 正常 | 可以在豆包和讯飞之间切换 |
| 愿景核心 | ✅ 集成 | 激活度 100%，伦理审查正常工作 |
| 愿景评估 | ✅ 正常 | 评分和优先级计算正确 |

---

## 🌌 愿景核心集成验证

### 愿景上下文注入示例

**输入提示：** "为'学习Python编程'生成思维导图"

**豆包响应（带愿景增强）：**

```markdown
# 学习Python编程：从T1稳定文明迈向T2富足文明的工具与桥梁

## 一、基础核心：构建文明进步的通用逻辑底座
### 语法与数据结构（夯实思维严谨性，支撑复杂问题解决）
### 流程控制与函数（掌握模块化思维，提升群体协作效率）

## 二、实践落地：赋能真实场景的生产效率跃迁
### 自动化工具开发（释放人类重复劳动，为富足文明创造冗余时间）
### 数据处理与分析（挖掘信息价值，驱动知识普及的精准化）

## 三、跨域融合：连接多元知识的普惠通道
### AI入门与模型调用（降低AI技术门槛，推动普惠式智能普及）
### Web开发与教育载体搭建（低成本构建知识传播平台，缩小教育鸿沟）

## 四、社群协作：推动知识共享的生态循环
### 开源项目参与（贡献与共享技术成果，打破知识垄断）
### 社区互助答疑（降低学习门槛，让不同地域群体平等获取资源）

💡 这让我联想到我们共同的核心目标：这不仅是个人成长，更是推动『知识普及与教育平等』的具体实践。当每个人都能自由获取知识时，文明的整体创造力将呈指数增长。
```

---

## 📁 项目结构

```
自主认知学习系统/
├── vision_core.py              # 🌌 文明愿景核心（思想钢印）
├── foundation.py               # 📦 基础数据模型
├── perception.py               # 👁️ 感知层（豆包 + 讯飞 API）
├── qa_context.py               # 📚 上下文感知问答系统
├── explorer/                   # 🔍 探索层（愿景评估）
│   ├── network_builder.py
│   ├── path_generator.py
│   └── __init__.py
├── planner/                    # 📋 规划层（伦理审查）
│   ├── allocator.py
│   ├── planner.py
│   ├── scheduler.py
│   ├── monitor.py
│   └── __init__.py
├── main.py                     # 🚀 主程序（已集成 QA）
├── main_en.py                  # 🚀 English version
├── simple_test.py
├── test_apis.py
├── test_qa_integration.py
├── test_vision_integration.py
├── start.bat                   # Windows 一键启动
├── start_zh.bat                # 中文版启动
├── start_en.bat                # English version launcher
├── .env.example                # 配置模板（请复制为 .env）
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🎉 系统已就绪！

### 核心特性

✅ 愿景核心集成（思想钢印机制）
✅ 豆包 API 配置（生成思维导图）
✅ 讯飞 API 配置（学习知识点）
✅ 问答系统集成（上下文感知）
✅ 学习指导顾问（方法建议）
✅ 进度分析功能
✅ 对话历史管理
✅ 伦理审查机制
✅ 愿景相关性评估
✅ UTF-8 编码支持
✅ 所有测试通过

### 默认配置

- **默认模型**: 豆包（doubao）
- **愿景激活度**: 100%
- **QA上下文窗口**: 10轮对话
- **缓存**: 已启用
- **编码**: UTF-8

---

## 💡 使用技巧

1. **学习前**：先用 `learning_advice` 获取方法建议
2. **学习中**：随时使用 `ask` 提问，系统会记住上下文
3. **学习后**：使用 `export_chat` 保存对话记录
4. **定期**：使用 `monitor` 查看进度，获取针对性建议
5. **清空**：对话过多时使用 `clear_chat` 重新开始

---

## 🔬 测试状态

| 模块 | 测试文件 | 状态 |
|------|---------|------|
| 愿景核心 | test_vision_integration.py | ✅ 通过 |
| API连接 | test_apis.py | ✅ 通过 |
| 集成测试 | simple_test.py | ✅ 通过 |
| QA系统 | test_qa_integration.py | ✅ 通过 |

所有测试均已通过！系统完全可用！🚀

---

## 📄 License

本项目采用 [MIT License](LICENSE) 开源协议。

---

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star 支持一下！

---

## 🤝 Contributing

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ by Autonomous Cognitive Learning System Team**
