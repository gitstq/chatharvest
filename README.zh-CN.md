<div align="center">

# 🌾 ChatHarvest

### AI 编程对话收割与智能分析引擎

**提取、分析、搜索并释放你的 AI 编程助手对话价值**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![零核心依赖](https://img.shields.io/badge/零核心依赖-✅-orange.svg)]()
[![测试](https://img.shields.io/badge/测试-33%20通过-brightgreen.svg)]()

简体中文 | [繁體中文](README.zh-TW.md) | [English](README.md)

</div>

---

## 🎉 项目介绍

ChatHarvest 是一款功能强大、零依赖的 Python 工具，能够**跨平台收割和分析你的 AI 编程助手对话**。无论你使用 Claude Code、Cursor、Windsurf、Aider、Cline、ChatGPT 还是 Gemini——ChatHarvest 都能将所有对话统一整合为一个可搜索、可分析的知识库。

### 💡 为什么选择 ChatHarvest？

每天，开发者都会与 AI 助手进行数百次有价值的对话——调试会话、架构决策、代码审查、学习时刻。但这些对话**被锁在各个工具内部**，分散且无法搜索。ChatHarvest 改变了这一切：

- 🔓 **解锁**你的对话数据，打破工具孤岛
- 🔍 **搜索**跨平台内容，基于 TF-IDF 全文检索
- 📊 **分析**Token 使用量、费用、编码模式和任务分布
- 🧠 **提取**代码片段、待办事项、决策记录、命令和错误模式
- 📦 **导出**为 Markdown、JSON、HTML、PDF，或通过内置 Web UI 浏览

### 🌟 灵感来源

源于这样一个观察：当开发者切换工具或清除聊天记录时，会丢失价值数千美元的 AI 生成知识。ChatHarvest 确保你的 AI 协作历史成为一项**永久、可搜索的资产**。

---

## ✨ 核心特性

### 🔌 多平台提取
- **支持 7+ 平台**：Claude Code、Cursor、Windsurf、Aider、Cline/Roo Code、ChatGPT、Google Gemini
- **自动检测**各平台的默认数据路径
- **智能去重**基于内容哈希——杜绝重复对话
- **增量提取**——仅处理新增数据

### 🔍 智能搜索
- **TF-IDF 全文搜索**覆盖所有对话和代码片段
- **来源过滤**——按平台缩小结果范围
- **日期范围过滤**——查找特定时间段的对话
- **相关性评分**配合匹配词高亮
- **零外部依赖**——纯 Python 倒排索引

### 📊 深度分析
- **全局统计**：对话总数、消息数、Token 数、预估费用
- **按平台细分**：查看你最常使用哪些工具
- **语言使用追踪**：哪些编程语言出现在你的对话中
- **任务分类**：自动识别 Bug 修复、功能开发、重构、测试、部署、安全
- **常见错误模式**：识别跨对话的重复问题
- **最活跃时段**：你最常编码的时间（按天和小时）
- **可执行建议**：数据驱动的工作流改进建议

### 🧠 知识提取
- **代码片段提取**附带语言检测和分类（代码/配置/命令/查询）
- **TODO/FIXME 检测**——永不错过待办任务
- **决策提取**——捕获架构和技术决策
- **命令收集**——汇总有用的 Shell 命令
- **错误模式挖掘**——构建个人错误知识库
- **关键词提取**——识别主导技术主题

### 📦 多格式导出
- **Markdown**：合并归档或按对话分文件
- **JSON**：带完整元数据的结构化数据
- **JSONL**：行分隔格式，适用于大数据管道
- **HTML**：独立可搜索归档，内嵌查看器
- **PDF**：可打印文档（可选 `reportlab` 依赖）

### 🌐 内置 Web 界面
- **零配置仪表盘**展示统计概览
- **可搜索对话浏览器**带分页
- **完整对话查看器**带语法高亮消息
- **来源过滤和排序**
- **本地运行**——你的数据永不出本机

### 🛡️ 隐私优先
- **100% 本地处理**——无数据发送到外部服务器
- **零核心依赖**——仅使用 Python 标准库
- **开源**——可审计每一行代码
- **MIT 协议**——个人和商业项目均可自由使用

---

## 🚀 快速开始

### 📋 环境要求

- **Python**：3.8 或更高版本
- **操作系统**：Windows、macOS 或 Linux
- **核心功能无需外部依赖**

### ⚙️ 安装

```bash
# 从源码安装（推荐）
git clone https://github.com/gitstq/chatharvest.git
cd chatharvest
pip install -e .

# 或安装带 PDF 支持的版本
pip install -e ".[full]"

# 验证安装
chatharvest --version
```

### 🏃 一键工作流

```bash
# 1. 从 Claude Code 提取对话
chatharvest extract claude-code -o my_conversations.json

# 2. 分析你的对话
chatharvest analyze -i my_conversations.json

# 3. 搜索特定主题
chatharvest search -i my_conversations.json "docker compose"

# 4. 导出为可搜索的 HTML 归档
chatharvest export -i my_conversations.json -o archive.html --format html

# 5. 启动 Web UI 仪表盘
chatharvest web -i my_conversations.json --port 8080
```

### 🎯 从所有平台提取

```bash
# Claude Code（默认：~/.claude/projects）
chatharvest extract claude-code -o claude.json

# Cursor（默认：~/.cursor）
chatharvest extract cursor -o cursor.json

# Windsurf（默认：~/.windsurf）
chatharvest extract windsurf -o windsurf.json

# Aider（默认：当前目录）
chatharvest extract aider --path ~/projects/myapp -o aider.json

# Cline / Roo Code（默认：~/.vscode）
chatharvest extract cline -o cline.json

# ChatGPT（导出的 conversations.json）
chatharvest extract chatgpt --path ~/Downloads/conversations.json -o chatgpt.json

# Google Gemini（Takeout 导出）
chatharvest extract gemini --path ~/Downloads/Takeout -o gemini.json
```

---

## 📖 详细使用指南

### 🔧 CLI 命令参考

#### `extract` — 提取对话

```bash
chatharvest extract <source> [--path PATH] [--output FILE] [--format FORMAT]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `source` | 平台类型（claude-code, cursor, windsurf, aider, cline, chatgpt, gemini） | 必填 |
| `--path, -p` | 数据目录/文件路径 | 平台默认路径 |
| `--output, -o` | 输出文件路径 | 标准输出摘要 |
| `--format, -f` | 输出格式：json, jsonl, markdown, html, pdf | json |

#### `analyze` — 分析对话

```bash
chatharvest analyze --input FILE [--output REPORT]
```

生成综合分析报告，包括：
- 全局统计（对话数、消息数、Token 数、费用）
- 按平台和模型细分
- 语言使用分布
- 任务类型分类
- 常见错误模式
- 最活跃编码时段
- 可执行建议

#### `search` — 搜索对话

```bash
chatharvest search --input FILE <query> [--limit N] [--source SOURCE]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 搜索关键词 | 必填 |
| `--limit, -n` | 最大结果数 | 20 |
| `--source, -s` | 按平台过滤 | 所有平台 |

#### `export` — 导出对话

```bash
chatharvest export --input FILE --output PATH --format FORMAT [--split]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--format, -f` | json, jsonl, markdown, html, pdf | markdown |
| `--split` | Markdown 按对话拆分为独立文件 | false |

#### `knowledge` — 提取知识

```bash
chatharvest knowledge --input FILE [--output FILE]
```

提取结构化知识：代码片段、待办事项、决策记录、命令、错误、关键词。

#### `web` — 启动 Web 界面

```bash
chatharvest web [--input FILE] [--host HOST] [--port PORT]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | 绑定地址 | 127.0.0.1 |
| `--port, -p` | 端口号 | 8765 |

#### `list` — 列出提取器

```bash
chatharvest list
```

### 📁 数据格式

ChatHarvest 使用统一的对话格式：

```json
{
  "id": "unique-id",
  "source": "claude-code",
  "title": "对话标题",
  "created_at": "2026-08-15T10:30:00Z",
  "model": "claude-sonnet-4",
  "messages": [
    {
      "role": "user",
      "content": "我该如何...",
      "tokens_input": 25,
      "tokens_output": null,
      "code_snippets": []
    }
  ],
  "stats": {
    "message_count": 10,
    "total_tokens": 855,
    "estimated_cost_usd": 0.0119,
    "languages_used": ["python", "yaml"]
  }
}
```

### 🖼️ Web 界面截图

Web 界面提供现代化深色主题仪表盘：

- **统计卡片**一览关键指标
- **搜索栏**即时过滤
- **对话表格**带来源标签、消息数、Token 使用量
- **详情弹窗**完整对话视图
- **响应式设计**适配桌面和移动端

---

## 💡 设计理念与迭代规划

### 🏗️ 设计原则

1. **零核心依赖**：核心引擎仅使用 Python 标准库。基础功能无需 pip 安装。
2. **隐私优先**：所有处理在本地完成。你的对话数据永远不会接触互联网。
3. **统一格式**：每个平台的数据都归一化为单一一致的模式。
4. **可扩展架构**：新提取器是继承 `BaseExtractor` 的简单类。
5. **开发者友好**：清晰的 CLI、明确的输出、有意义的错误信息。

### 🛠️ 技术栈

| 组件 | 技术 | 选型原因 |
|------|------|----------|
| **语言** | Python 3.8+ | 普及度高，数据处理能力强 |
| **核心引擎** | Python 标准库 | 零依赖，最大兼容性 |
| **搜索** | 自定义 TF-IDF | 轻量级，无需外部搜索引擎 |
| **Web UI** | 标准库 HTTP + 原生 JS | 无构建步骤，随处可运行 |
| **测试** | pytest | 行业标准，易于扩展 |
| **打包** | setuptools + pyproject.toml | 现代 Python 打包方式 |

### 🗺️ 迭代规划

#### ✅ v1.0.0（当前版本）
- [x] 7+ 平台提取器
- [x] TF-IDF 全文搜索
- [x] 综合分析引擎
- [x] 知识提取（片段、待办、决策、命令、错误）
- [x] 多格式导出（JSON、JSONL、Markdown、HTML、PDF）
- [x] 内置 Web UI 仪表盘
- [x] 智能去重
- [x] 33 个单元测试，全部通过
- [x] 零核心依赖

#### 🔜 v1.1.0（计划中）
- [ ] 对话增量提取（从上次检查点恢复）
- [ ] 对话标签和分类
- [ ] 跨平台费用对比
- [ ] 跨对话代码片段去重
- [ ] Anki 卡片导出用于间隔重复
- [ ] 更多平台支持（Zed、Continue.dev、Codeium）

#### 🔮 v2.0.0（未来）
- [ ] 本地 LLM 驱动的对话摘要
- [ ] 语义搜索（基于向量嵌入）
- [ ] 知识图谱生成
- [ ] 多用户团队知识库
- [ ] 自定义提取器和分析器插件系统

### 🤝 社区贡献方向

我们欢迎以下领域的贡献：
- **新提取器**：支持更多 AI 编程工具
- **更好的分析**：新指标、可视化、洞察
- **文档**：教程、示例、翻译
- **测试**：更多测试覆盖、边界情况
- **性能**：针对大型对话数据集的优化

---

## 📦 打包与部署指南

### 🐍 Python 包

```bash
# 构建包
python -m build

# 本地安装
pip install dist/chatharvest-1.0.0-py3-none-any.whl

# 运行
chatharvest --help
```

### 📦 独立可执行文件（可选）

使用 PyInstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --name chatharvest chatharvest/__main__.py
# 输出：dist/chatharvest（Windows 上为 chatharvest.exe）
```

### 🐳 Docker（可选）

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
VOLUME /data
EXPOSE 8765
ENTRYPOINT ["chatharvest"]
```

```bash
docker build -t chatharvest .
docker run -v ~/.claude:/root/.claude -p 8765:8765 chatharvest web --host 0.0.0.0
```

### 🔧 兼容环境

| 环境 | 状态 | 说明 |
|------|------|------|
| **Python 3.8-3.12** | ✅ 完全支持 | 核心功能 |
| **Windows 10/11** | ✅ 支持 | 路径自动适配 |
| **macOS 12+** | ✅ 支持 | 默认路径已配置 |
| **Linux（全发行版）** | ✅ 支持 | 主要开发平台 |
| **Docker** | ✅ 支持 | 通过可选 Dockerfile |
| **PDF 导出** | ⚠️ 可选 | 需要 `pip install reportlab` |

---

## 🤝 贡献指南

我们欢迎所有人的贡献！详细指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

**快速步骤：**
1. Fork 本仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

### 📐 Pull Request 格式

使用 Conventional Commits 作为 PR 标题：
- `feat: 新增 X 提取器`
- `fix: 修复 Token 计数 Bug`
- `docs: 更新安装指南`
- `refactor: 优化搜索性能`

---

## 📄 开源协议说明

本项目采用 **MIT 许可证**——详见 [LICENSE](LICENSE) 文件。

```
MIT 许可证

版权所有 (c) 2026 ChatHarvest 贡献者

特此免费授予任何获得本软件副本和相关文档文件（下称"软件"）的人不受限制地
处置本软件的权利，包括但不限于使用、复制、修改、合并、出版、分发、再许可
和/或销售软件副本，以及允许向其提供软件的人这样做，符合以下条件：

上述版权声明和本许可声明应包含在软件的所有副本或主要部分中。
```

---

<div align="center">

**由开发者用 🌾 打造，为开发者服务**

[⭐ 点星收藏](https://github.com/gitstq/chatharvest) · [🐛 反馈问题](https://github.com/gitstq/chatharvest/issues) · [🤝 参与贡献](CONTRIBUTING.md)

</div>
