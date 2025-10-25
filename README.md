# LOL Chat Helper

一個使用 LangChain 和 LM Studio 建構的英雄聯盟聊天助手，具備對話記憶功能和 OP.GG MCP 工具整合。

## 功能特色

- ✅ **對話記憶**: 機器人會記住整個對話過程中的所有訊息
- ✅ **Session 管理**: 支援多個獨立的對話 session
- ✅ **本地運行**: 使用 LM Studio，無需外部 API key
- ✅ **OP.GG 工具整合**: 透過 MCP 協議整合 8 個 LOL 資料查詢工具
- ✅ **AI 自動調用工具**: Agent 模式自動判斷並調用適當的工具
- ✅ **繁體中文支援**: 預設使用繁體中文進行對話
- ✅ **簡單 CLI 介面**: 直接在終端機開始對話

## OP.GG MCP 工具

本專案整合了 OP.GG 提供的 MCP (Model Context Protocol) 工具，可以查詢即時的 LOL 資料：

### 可用工具列表

1. **lol-summoner-search** - 召喚師查詢
   - 查詢玩家的基本資訊和統計數據
   - 範例：「幫我查詢 Faker 的資料」

2. **lol-summoner-game-history** - 對局歷史
   - 獲取召喚師最近的對局記錄
   - 範例：「Faker 最近的戰績如何？」

3. **lol-champion-analysis** - 英雄分析
   - 分析英雄的 counter、ban/pick 數據
   - 範例：「哪些英雄 counter Yasuo？」

4. **lol-champion-meta-data** - 英雄 Meta 數據
   - 獲取英雄的統計和表現指標
   - 範例：「Ahri 目前的勝率是多少？」

5. **lol-champion-positions-data** - 位置統計
   - 查詢英雄在各位置的數據
   - 範例：「Yasuo 在中路的勝率如何？」

6. **lol-champion-leader-board** - 英雄排行榜
   - 獲取英雄排行榜資訊
   - 範例：「目前 meta 最強的英雄有哪些？」

7. **lol-champion-skin-sale** - 造型特價
   - 查詢目前特價的英雄造型
   - 範例：「現在有哪些造型在特價？」

8. **lol-summoner-renewal** - 更新召喚師資料
   - 更新召喚師的最新對局資料
   - 範例：「更新 Faker 的資料」

## 系統需求

- Python 3.12 或更高版本
- [LM Studio](https://lmstudio.ai/) 已安裝並運行
- **Node.js 和 npm** (用於執行 MCP 工具)
- 已下載並載入至少一個支援 function calling 的語言模型
  - 推薦：Llama 3.1+, Mistral 7B+, Qwen 2.5+ 等

## 安裝步驟

### 1. 安裝依賴

使用 `uv` 套件管理器（推薦）：

```bash
uv sync
```

或使用傳統的 pip：

```bash
pip install -e .
```

### 2. 設定 LM Studio

1. 啟動 LM Studio 應用程式
2. 下載並載入一個支援 function calling 的語言模型
   - 推薦模型：
     - `Llama-3.2-3B-Instruct` (輕量級)
     - `Mistral-7B-Instruct` (效能均衡)
     - `Qwen2.5-7B-Instruct` (中文表現佳)
3. 在 LM Studio 中啟動本地伺服器：
   - 點擊左側的 "Local Server" 或 "本地伺服器"
   - 選擇已載入的模型
   - 點擊 "Start Server" 或 "啟動伺服器"
   - 預設端口為 `1234`

### 3. 驗證 Node.js 環境

確保 Node.js 已安裝（MCP 工具需要）：

```bash
node --version
npm --version
```

如果未安裝，請參考 [Node.js 官網](https://nodejs.org/) 安裝。

### 4. 配置環境變數（選擇性）

如果需要自訂配置，可以編輯 `.env` 檔案：

```bash
# LM Studio 配置
LM_STUDIO_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio

# MCP 配置
MCP_ENABLED=true
MCP_CONFIG_PATH=mcp_config.json
MCP_TIMEOUT=30
```

## 使用方法

### 啟動聊天機器人

```bash
uv run python main.py
```

或

```bash
python main.py
```

### 可用命令

在對話過程中，你可以使用以下命令：

- `/quit` 或 `/exit` - 退出程式
- `/new` - 開始新的對話 session（清除記憶）
- `/history` - 顯示當前對話的完整歷史
- `/tools` - 顯示 MCP 工具狀態
- `/help` - 顯示幫助訊息

### 使用範例

#### 基本對話

```
============================================================
  LOL Chat Helper - 具備記憶功能和 OP.GG 工具的聊天機器人
============================================================

可用命令:
  /quit 或 /exit  - 退出程式
  /new           - 開始新的對話
  /history       - 顯示當前對話歷史
  /tools         - 顯示 MCP 工具狀態
  /help          - 顯示幫助訊息

請確保 LM Studio 已啟動並載入了模型！
OP.GG MCP 工具已啟用，可以查詢 LOL 即時資料！
------------------------------------------------------------

[系統] 聊天機器人已啟動（含 MCP 工具）！開始對話吧！

👤 你: 你好！
🤖 AI: 你好！我是你的英雄聯盟助手。我可以幫你查詢召喚師資料、英雄數據、對局歷史等資訊。有什麼我可以幫你的嗎？

👤 你: Faker 最近戰績如何？
🤖 AI: [自動調用 lol-summoner-search 和 lol-summoner-game-history]
根據 OP.GG 的資料，Faker（Hide on bush）最近 20 場的戰績是...
```

#### 使用工具查詢

```
👤 你: 哪些英雄 counter Yasuo？
🤖 AI: [自動調用 lol-champion-analysis]
根據目前的 meta 數據，以下英雄能有效 counter Yasuo：
1. Malzahar - 可以用 R 鎖定他
2. Annie - 爆發傷害高，控制能力強
3. Pantheon - Q 可以穿透風牆...

👤 你: Ahri 目前勝率如何？
🤖 AI: [自動調用 lol-champion-meta-data]
Ahri 目前的統計數據如下：
- 整體勝率: 51.2%
- 選取率: 8.7%
- 禁用率: 3.1%...
```

#### 查看工具狀態

```
👤 你: /tools

============================================================
OP.GG MCP 工具狀態
============================================================

總計: 8/8 工具已啟用
初始化狀態: ✅ 已初始化

工具列表:
  ✅ opgg_lol-summoner-search
     查詢 LOL 召喚師資訊和統計數據
  ✅ opgg_lol-summoner-game-history
     獲取召喚師最近的對局歷史
  ✅ opgg_lol-champion-analysis
     分析英雄的 counter、ban/pick 數據
  ✅ opgg_lol-champion-meta-data
     獲取英雄的 meta 數據和表現指標
  ✅ opgg_lol-champion-positions-data
     查詢英雄在各位置的統計數據
  ✅ opgg_lol-champion-leader-board
     獲取英雄排行榜資訊
  ✅ opgg_lol-champion-skin-sale
     查詢目前特價的英雄造型
  ✅ opgg_lol-summoner-renewal
     更新召喚師的對局資料

============================================================
```

## MCP 工具配置

### 工具配置檔案

工具的啟用/停用狀態在 `mcp_config.json` 中管理：

```json
{
  "mcpServers": {
    "opgg": {
      "command": "npx",
      "args": ["-y", "supergateway", "--streamableHttp", "https://mcp-api.op.gg/mcp"],
      "transport": "stdio"
    }
  },
  "toolsConfig": {
    "opgg_lol-summoner-search": {
      "enabled": true,
      "description": "查詢 LOL 召喚師資訊和統計數據"
    },
    ...
  }
}
```

### 自訂工具配置

如果你想停用某些工具，只需將 `enabled` 設為 `false`：

```json
{
  "opgg_lol-champion-skin-sale": {
    "enabled": false,
    "description": "查詢目前特價的英雄造型"
  }
}
```

重新啟動聊天機器人後，該工具就不會被載入。

## 技術架構

### 核心技術

- **LangChain**: 用於建構 LLM 應用程式的框架
- **LangGraph**: 提供狀態管理和記憶功能，建構 Agent 工作流程
- **LangChain MCP Adapters**: 連接 MCP 伺服器的適配器
- **ChatOpenAI**: 使用 OpenAI 相容的 API 介面連接 LM Studio
- **MemorySaver**: 內建記憶體儲存，保存對話歷史
- **MultiServerMCPClient**: 管理多個 MCP 伺服器連線

### Agent 工作流程

```
使用者輸入
    ↓
Agent 節點（判斷是否需要工具）
    ↓
需要工具？ → 否 → 直接生成回應
    ↓ 是
ToolNode（調用 MCP 工具）
    ↓
處理工具結果/錯誤
    ↓
Agent 節點（整合結果生成回應）
    ↓
返回給使用者
```

### 檔案結構

```
lol_chat_helper/
├── .env                    # 環境變數配置
├── .gitignore             # Git 忽略檔案
├── .python-version        # Python 版本
├── README.md              # 使用文檔（本檔案）
├── pyproject.toml         # 專案依賴管理
├── mcp_config.json        # MCP 伺服器和工具配置
├── mcp_manager.py         # MCP 工具管理類別
└── main.py                # 主程式
```

## 常見問題

### Q: 為什麼 AI 沒有回應？

確保：
1. LM Studio 已啟動並載入支援 function calling 的模型
2. 本地伺服器正在運行（預設: http://localhost:1234）
3. 檢查 `.env` 檔案中的 `LM_STUDIO_BASE_URL` 設定是否正確

### Q: MCP 工具無法使用怎麼辦？

檢查以下幾點：
1. **Node.js 環境**: 執行 `node --version` 確認已安裝
2. **網路連線**: 確保可以訪問 `https://mcp-api.op.gg/mcp`
3. **配置檔案**: 檢查 `mcp_config.json` 格式是否正確
4. 查看啟動時的日誌訊息，了解具體錯誤

如果 MCP 初始化失敗，程式會自動降級為純聊天模式（不使用工具）。

### Q: 如何更改 AI 的回應語言或風格？

編輯 [main.py](main.py:59-74) 中的 `system_prompt`。

### Q: 記憶功能如何運作？

使用 LangGraph 的 `MemorySaver`，每個對話 session 都有唯一的 `thread_id`。所有訊息都會儲存在記憶體中，直到：
- 使用 `/new` 命令開始新對話
- 程式重新啟動

### Q: 如何使用不同的模型？

在 LM Studio 中載入不同的模型，然後重新啟動本地伺服器即可。程式會自動使用當前載入的模型。

**重要**：確保模型支援 function calling 功能，否則工具調用可能無法正常運作。

### Q: 可以調整 AI 回應的隨機性嗎？

可以！編輯 [main.py](main.py:30-35) 中的 `temperature` 參數：

```python
model = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
    temperature=0.7,  # 0.0 = 更確定性, 1.0 = 更隨機
    streaming=False,
)
```

### Q: 如何停用 MCP 工具？

在 `.env` 檔案中設定：

```bash
MCP_ENABLED=false
```

重新啟動後，聊天機器人會以純聊天模式運行（不使用 OP.GG 工具）。

### Q: 工具調用會增加多少延遲？

- 首次初始化 MCP 連線：5-10 秒
- 單次工具調用：1-3 秒（視網路速度和 OP.GG API 回應時間）
- 不調用工具時：與原本的純聊天模式相同

### Q: 可以新增其他 MCP 伺服器嗎？

可以！在 `mcp_config.json` 的 `mcpServers` 區塊新增其他伺服器：

```json
{
  "mcpServers": {
    "opgg": { ... },
    "另一個伺服器": {
      "command": "...",
      "args": [...],
      "transport": "stdio"
    }
  }
}
```

## 擴展功能建議

這個專案可以輕鬆擴展以下功能：

- 🔧 **更多 MCP 工具**: 整合其他 MCP 伺服器（天氣、股票、新聞等）
- 📚 **RAG 功能**: 整合向量資料庫，查詢本地文檔
- 💾 **持久化儲存**: 使用資料庫儲存對話歷史
- 🌐 **Web 介面**: 建立 FastAPI 或 Streamlit 介面
- 📊 **數據視覺化**: 將 OP.GG 數據以圖表呈現
- 🎮 **遊戲內整合**: 透過 Riot API 獲取更多資料

## 授權

MIT License

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 相關連結

- [LangChain 官方文檔](https://python.langchain.com/)
- [LangGraph 文檔](https://langchain-ai.github.io/langgraph/)
- [LM Studio 官網](https://lmstudio.ai/)
- [OP.GG MCP Server](https://github.com/opgginc/opgg-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
