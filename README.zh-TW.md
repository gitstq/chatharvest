<div align="center">

# 🌾 ChatHarvest

### AI 編程對話收割與智慧分析引擎

**提取、分析、搜尋並釋放你的 AI 編程助手對話價值**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![零核心依賴](https://img.shields.io/badge/零核心依賴-✅-orange.svg)]()
[![測試](https://img.shields.io/badge/測試-33%20通過-brightgreen.svg)]()

[简体中文](README.zh-CN.md) | 繁體中文 | [English](README.md)

</div>

---

## 🎉 專案介紹

ChatHarvest 是一款功能強大、零依賴的 Python 工具，能夠**跨平台收割和分析你的 AI 編程助手對話**。無論你使用 Claude Code、Cursor、Windsurf、Aider、Cline、ChatGPT 還是 Gemini——ChatHarvest 都能將所有對話統一整合為一個可搜尋、可分析的知識庫。

### 💡 為什麼選擇 ChatHarvest？

每天，開發者都會與 AI 助手進行數百次有價值的對話——除錯會話、架構決策、程式碼審查、學習時刻。但這些對話**被鎖在各個工具內部**，分散且無法搜尋。ChatHarvest 改變了這一切：

- 🔓 **解鎖**你的對話資料，打破工具孤島
- 🔍 **搜尋**跨平台內容，基於 TF-IDF 全文檢索
- 📊 **分析**Token 使用量、費用、編碼模式和任務分佈
- 🧠 **提取**程式碼片段、待辦事項、決策記錄、指令和錯誤模式
- 📦 **匯出**為 Markdown、JSON、HTML、PDF，或透過內建 Web UI 瀏覽

### 🌟 靈感來源

源於這樣一個觀察：當開發者切換工具或清除聊天記錄時，會遺失價值數千美元的 AI 生成知識。ChatHarvest 確保你的 AI 協作歷史成為一項**永久、可搜尋的資產**。

---

## ✨ 核心特性

### 🔌 多平台提取
- **支援 7+ 平台**：Claude Code、Cursor、Windsurf、Aider、Cline/Roo Code、ChatGPT、Google Gemini
- **自動偵測**各平台的預設資料路徑
- **智慧去重**基於內容雜湊——杜絕重複對話
- **增量提取**——僅處理新增資料

### 🔍 智慧搜尋
- **TF-IDF 全文搜尋**涵蓋所有對話和程式碼片段
- **來源過濾**——按平台縮小結果範圍
- **日期範圍過濾**——查找特定時間段的對話
- **相關性評分**配合匹配詞高亮
- **零外部依賴**——純 Python 倒排索引

### 📊 深度分析
- **全域統計**：對話總數、訊息數、Token 數、預估費用
- **按平台細分**：查看你最常使用哪些工具
- **語言使用追蹤**：哪些程式語言出現在你的對話中
- **任務分類**：自動識別 Bug 修復、功能開發、重構、測試、部署、安全
- **常見錯誤模式**：識別跨對話的重複問題
- **最活躍時段**：你最常編碼的時間（按天和小時）
- **可執行建議**：資料驅動的工作流程改進建議

### 🧠 知識提取
- **程式碼片段提取**附帶語言偵測和分類（程式碼/設定/指令/查詢）
- **TODO/FIXME 偵測**——永不錯過待辦任務
- **決策提取**——擷取架構和技術決策
- **指令收集**——彙整有用的 Shell 指令
- **錯誤模式挖掘**——建構個人錯誤知識庫
- **關鍵詞提取**——識別主導技術主題

### 📦 多格式匯出
- **Markdown**：合併歸檔或按對話分檔案
- **JSON**：帶完整元資料的結構化資料
- **JSONL**：行分隔格式，適用於大資料管道
- **HTML**：獨立可搜尋歸檔，內嵌檢視器
- **PDF**：可列印文件（可選 `reportlab` 依賴）

### 🌐 內建 Web 介面
- **零設定儀表板**展示統計概覽
- **可搜尋對話瀏覽器**帶分頁
- **完整對話檢視器**帶語法高亮訊息
- **來源過濾和排序**
- **本機執行**——你的資料永不出本機

### 🛡️ 隱私優先
- **100% 本機處理**——無資料發送到外部伺服器
- **零核心依賴**——僅使用 Python 標準函式庫
- **開源**——可審計每一行程式碼
- **MIT 協議**——個人和商業專案均可自由使用

---

## 🚀 快速開始

### 📋 環境需求

- **Python**：3.8 或更高版本
- **作業系統**：Windows、macOS 或 Linux
- **核心功能無需外部依賴**

### ⚙️ 安裝

```bash
# 從原始碼安裝（推薦）
git clone https://github.com/gitstq/chatharvest.git
cd chatharvest
pip install -e .

# 或安裝帶 PDF 支援的版本
pip install -e ".[full]"

# 驗證安裝
chatharvest --version
```

### 🏃 一鍵工作流程

```bash
# 1. 從 Claude Code 提取對話
chatharvest extract claude-code -o my_conversations.json

# 2. 分析你的對話
chatharvest analyze -i my_conversations.json

# 3. 搜尋特定主題
chatharvest search -i my_conversations.json "docker compose"

# 4. 匯出為可搜尋的 HTML 歸檔
chatharvest export -i my_conversations.json -o archive.html --format html

# 5. 啟動 Web UI 儀表板
chatharvest web -i my_conversations.json --port 8080
```

### 🎯 從所有平台提取

```bash
# Claude Code（預設：~/.claude/projects）
chatharvest extract claude-code -o claude.json

# Cursor（預設：~/.cursor）
chatharvest extract cursor -o cursor.json

# Windsurf（預設：~/.windsurf）
chatharvest extract windsurf -o windsurf.json

# Aider（預設：目前目錄）
chatharvest extract aider --path ~/projects/myapp -o aider.json

# Cline / Roo Code（預設：~/.vscode）
chatharvest extract cline -o cline.json

# ChatGPT（匯出的 conversations.json）
chatharvest extract chatgpt --path ~/Downloads/conversations.json -o chatgpt.json

# Google Gemini（Takeout 匯出）
chatharvest extract gemini --path ~/Downloads/Takeout -o gemini.json
```

---

## 📖 詳細使用指南

### 🔧 CLI 指令參考

#### `extract` — 提取對話

```bash
chatharvest extract <source> [--path PATH] [--output FILE] [--format FORMAT]
```

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `source` | 平台類型（claude-code, cursor, windsurf, aider, cline, chatgpt, gemini） | 必填 |
| `--path, -p` | 資料目錄/檔案路徑 | 平台預設路徑 |
| `--output, -o` | 輸出檔案路徑 | 標準輸出摘要 |
| `--format, -f` | 輸出格式：json, jsonl, markdown, html, pdf | json |

#### `analyze` — 分析對話

```bash
chatharvest analyze --input FILE [--output REPORT]
```

生成綜合分析報告，包括：
- 全域統計（對話數、訊息數、Token 數、費用）
- 按平台和模型細分
- 語言使用分佈
- 任務類型分類
- 常見錯誤模式
- 最活躍編碼時段
- 可執行建議

#### `search` — 搜尋對話

```bash
chatharvest search --input FILE <query> [--limit N] [--source SOURCE]
```

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `query` | 搜尋關鍵詞 | 必填 |
| `--limit, -n` | 最大結果數 | 20 |
| `--source, -s` | 按平台過濾 | 所有平台 |

#### `export` — 匯出對話

```bash
chatharvest export --input FILE --output PATH --format FORMAT [--split]
```

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--format, -f` | json, jsonl, markdown, html, pdf | markdown |
| `--split` | Markdown 按對話拆分為獨立檔案 | false |

#### `knowledge` — 提取知識

```bash
chatharvest knowledge --input FILE [--output FILE]
```

提取結構化知識：程式碼片段、待辦事項、決策記錄、指令、錯誤、關鍵詞。

#### `web` — 啟動 Web 介面

```bash
chatharvest web [--input FILE] [--host HOST] [--port PORT]
```

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--host` | 綁定位址 | 127.0.0.1 |
| `--port, -p` | 連接埠號 | 8765 |

#### `list` — 列出提取器

```bash
chatharvest list
```

### 📁 資料格式

ChatHarvest 使用統一的對話格式：

```json
{
  "id": "unique-id",
  "source": "claude-code",
  "title": "對話標題",
  "created_at": "2026-08-15T10:30:00Z",
  "model": "claude-sonnet-4",
  "messages": [
    {
      "role": "user",
      "content": "我該如何...",
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

### 🖼️ Web 介面截圖

Web 介面提供現代化深色主題儀表板：

- **統計卡片**一覽關鍵指標
- **搜尋欄**即時過濾
- **對話表格**帶來源標籤、訊息數、Token 使用量
- **詳情彈窗**完整對話檢視
- **響應式設計**適配桌面和行動裝置

---

## 💡 設計理念與迭代規劃

### 🏗️ 設計原則

1. **零核心依賴**：核心引擎僅使用 Python 標準函式庫。基礎功能無需 pip 安裝。
2. **隱私優先**：所有處理在本機完成。你的對話資料永遠不會接觸網際網路。
3. **統一格式**：每個平台的資料都正規化為單一一致的模式。
4. **可擴充架構**：新提取器是繼承 `BaseExtractor` 的簡單類別。
5. **開發者友善**：清晰的 CLI、明確的輸出、有意義的錯誤訊息。

### 🛠️ 技術棧

| 元件 | 技術 | 選型原因 |
|------|------|----------|
| **語言** | Python 3.8+ | 普及度高，資料處理能力強 |
| **核心引擎** | Python 標準函式庫 | 零依賴，最大相容性 |
| **搜尋** | 自訂 TF-IDF | 輕量級，無需外部搜尋引擎 |
| **Web UI** | 標準函式庫 HTTP + 原生 JS | 無建構步驟，隨處可執行 |
| **測試** | pytest | 業界標準，易於擴充 |
| **打包** | setuptools + pyproject.toml | 現代 Python 打包方式 |

### 🗺️ 迭代規劃

#### ✅ v1.0.0（目前版本）
- [x] 7+ 平台提取器
- [x] TF-IDF 全文搜尋
- [x] 綜合分析引擎
- [x] 知識提取（片段、待辦、決策、指令、錯誤）
- [x] 多格式匯出（JSON、JSONL、Markdown、HTML、PDF）
- [x] 內建 Web UI 儀表板
- [x] 智慧去重
- [x] 33 個單元測試，全部通過
- [x] 零核心依賴

#### 🔜 v1.1.0（計劃中）
- [ ] 對話增量提取（從上次檢查點恢復）
- [ ] 對話標籤和分類
- [ ] 跨平台費用比較
- [ ] 跨對話程式碼片段去重
- [ ] Anki 卡片匯出用於間隔重複
- [ ] 更多平台支援（Zed、Continue.dev、Codeium）

#### 🔮 v2.0.0（未來）
- [ ] 本機 LLM 驅動的對話摘要
- [ ] 語意搜尋（基於向量嵌入）
- [ ] 知識圖譜生成
- [ ] 多用戶團隊知識庫
- [ ] 自訂提取器和分析器外掛系統

### 🤝 社群貢獻方向

我們歡迎以下領域的貢獻：
- **新提取器**：支援更多 AI 編程工具
- **更好的分析**：新指標、視覺化、洞察
- **文件**：教學、範例、翻譯
- **測試**：更多測試覆蓋、邊界情況
- **效能**：針對大型對話資料集的最佳化

---

## 📦 打包與部署指南

### 🐍 Python 套件

```bash
# 建構套件
python -m build

# 本機安裝
pip install dist/chatharvest-1.0.0-py3-none-any.whl

# 執行
chatharvest --help
```

### 📦 獨立可執行檔（可選）

使用 PyInstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --name chatharvest chatharvest/__main__.py
# 輸出：dist/chatharvest（Windows 上為 chatharvest.exe）
```

### 🐳 Docker（可選）

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

### 🔧 相容環境

| 環境 | 狀態 | 說明 |
|------|------|------|
| **Python 3.8-3.12** | ✅ 完全支援 | 核心功能 |
| **Windows 10/11** | ✅ 支援 | 路徑自動適配 |
| **macOS 12+** | ✅ 支援 | 預設路徑已設定 |
| **Linux（全發行版）** | ✅ 支援 | 主要開發平台 |
| **Docker** | ✅ 支援 | 透過可選 Dockerfile |
| **PDF 匯出** | ⚠️ 可選 | 需要 `pip install reportlab` |

---

## 🤝 貢獻指南

我們歡迎所有人的貢獻！詳細指南請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

**快速步驟：**
1. Fork 本倉庫
2. 建立功能分支
3. 編寫程式碼和測試
4. 提交 Pull Request

### 📐 Pull Request 格式

使用 Conventional Commits 作為 PR 標題：
- `feat: 新增 X 提取器`
- `fix: 修復 Token 計數 Bug`
- `docs: 更新安裝指南`
- `refactor: 最佳化搜尋效能`

---

## 📄 開源協議說明

本專案採用 **MIT 許可證**——詳見 [LICENSE](LICENSE) 檔案。

```
MIT 許可證

版權所有 (c) 2026 ChatHarvest 貢獻者

特此免費授予任何獲得本軟體副本和相關文件檔案（下稱「軟體」）的人不受限制地
處置本軟體的權利，包括但不限於使用、複製、修改、合併、出版、分發、再許可
和/或銷售軟體副本，以及允許向其提供軟體的人這樣做，符合以下條件：

上述版權聲明和本許可聲明應包含在軟體的所有副本或主要部分中。
```

---

<div align="center">

**由開發者用 🌾 打造，為開發者服務**

[⭐ 點星收藏](https://github.com/gitstq/chatharvest) · [🐛 回報問題](https://github.com/gitstq/chatharvest/issues) · [🤝 參與貢獻](CONTRIBUTING.md)

</div>
