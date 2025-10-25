import os
import uuid
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from mcp_manager import MCPToolManager


# Load environment variables
load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_chatbot():
    """Create and configure the chatbot with memory and MCP tools."""

    # Initialize the LM Studio chat model
    model = ChatOpenAI(
        base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
        model="gpt-oss:20b",
        temperature=0.7,
        streaming=False,
    )

    # Initialize MCP Tool Manager
    mcp_manager = None
    tools = []
    mcp_enabled = os.getenv("MCP_ENABLED", "true").lower() == "true"

    if mcp_enabled:
        try:
            logger.info("正在初始化 MCP 工具管理器...")
            mcp_config_path = os.getenv("MCP_CONFIG_PATH", "mcp_config.json")
            mcp_manager = MCPToolManager(mcp_config_path)
            tools = await mcp_manager.initialize()
            logger.info(f"成功載入 {len(tools)} 個 MCP 工具")
        except Exception as e:
            logger.warning(f"MCP 初始化失敗，將以純聊天模式運行: {e}")
            logger.warning("如需使用 MCP 工具，請確保：")
            logger.warning("1. Node.js 已安裝且可執行 npx")
            logger.warning("2. 網路可以訪問 https://mcp-api.op.gg/mcp")
            logger.warning("3. mcp_config.json 配置正確")
            mcp_manager = None
            tools = []

    # Get current date information
    current_date = datetime.now()
    date_info = (
        f"當前日期：{current_date.year}年{current_date.month}月{current_date.day}日\n"
        f"星期：{['一', '二', '三', '四', '五', '六', '日'][current_date.weekday()]}\n"
    )

    # Define system prompt
    if tools:
        system_prompt = (
            "你是一個專業的英雄聯盟（League of Legends, LOL）助手，具備記憶功能。\n"
            "你可以使用 OP.GG 的工具來查詢玩家資訊、英雄數據、對局歷史等最新資料。\n\n"
            f"{date_info}\n"
            "可用工具包括：\n"
            "- 召喚師查詢：查詢玩家的基本資訊和統計數據\n"
            "- 對局歷史：獲取玩家最近的對局記錄\n"
            "- 英雄分析：分析英雄的 counter、ban/pick 數據\n"
            "- 英雄 meta 數據：獲取英雄的統計和表現指標\n"
            "- 位置統計：查詢英雄在各位置的數據\n"
            "- 排行榜：獲取英雄排行榜資訊\n"
            "- 造型特價：查詢特價的英雄造型\n"
            "- 更新數據：更新召喚師的最新資料\n\n"
            "當使用者詢問 LOL 相關資訊時，你應該主動使用適當的工具來獲取最新數據。\n"
            "請用繁體中文回答問題，並記住之前的對話內容。"
        )
    else:
        system_prompt = (
            "你是一個友善且樂於助人的 AI 助手。\n"
            f"{date_info}\n"
            "請用繁體中文回答問題，並記住之前的對話內容。\n"
            "注意：目前 MCP 工具未啟用，無法查詢即時的 LOL 資料。"
        )

    # Create the state graph
    workflow = StateGraph(state_schema=MessagesState)

    if tools:
        # Agent mode with tools
        def call_model(state: MessagesState):
            """Process messages and generate AI response with tool support."""
            messages = [SystemMessage(content=system_prompt)] + state["messages"]
            response = model.bind_tools(tools).invoke(messages)
            return {"messages": response}

        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(tools))

        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            tools_condition,  # Automatically routes to tools if needed
        )
        workflow.add_edge("tools", "agent")

    else:
        # Simple chat mode without tools
        def call_model(state: MessagesState):
            """Process messages and generate AI response."""
            messages = [SystemMessage(content=system_prompt)] + state["messages"]
            response = model.invoke(messages)
            return {"messages": response}

        workflow.add_node("model", call_model)
        workflow.add_edge(START, "model")

    # Add memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app, mcp_manager


def display_welcome(has_tools: bool = False):
    """Display welcome message and instructions."""
    print("=" * 60)
    if has_tools:
        print("  LOL Chat Helper - 具備記憶功能和 OP.GG 工具的聊天機器人")
    else:
        print("  LOL Chat Helper - 具備記憶功能的聊天機器人")
    print("=" * 60)
    print("\n可用命令:")
    print("  /quit 或 /exit  - 退出程式")
    print("  /new           - 開始新的對話")
    print("  /history       - 顯示當前對話歷史")
    if has_tools:
        print("  /tools         - 顯示 MCP 工具狀態")
    print("  /help          - 顯示幫助訊息")
    print("\n請確保 LM Studio 已啟動並載入了模型！")
    if has_tools:
        print("OP.GG MCP 工具已啟用，可以查詢 LOL 即時資料！")
    print("-" * 60)


def display_history(app, config):
    """Display conversation history."""
    try:
        state = app.get_state(config)
        messages = state.values.get("messages", [])

        if not messages:
            print("\n[系統] 目前沒有對話歷史\n")
            return

        print("\n" + "=" * 60)
        print("對話歷史:")
        print("=" * 60)

        for msg in messages:
            if hasattr(msg, 'type'):
                if msg.type == 'human':
                    print(f"\n👤 使用者: {msg.content}")
                elif msg.type == 'ai':
                    print(f"🤖 AI: {msg.content}")
                elif msg.type == 'system':
                    print(f"⚙️  系統: {msg.content}")
                elif msg.type == 'tool':
                    print(f"🔧 工具: {msg.name} - {msg.content[:100]}...")

        print("\n" + "=" * 60 + "\n")
    except Exception as e:
        print(f"\n[錯誤] 無法取得對話歷史: {e}\n")


def display_tools_status(mcp_manager):
    """Display MCP tools status."""
    if not mcp_manager:
        print("\n[系統] MCP 工具未啟用\n")
        return

    try:
        status = mcp_manager.get_tools_status()

        print("\n" + "=" * 60)
        print("OP.GG MCP 工具狀態")
        print("=" * 60)
        print(f"\n總計: {status['enabled']}/{status['total']} 工具已啟用")
        print(f"初始化狀態: {'✅ 已初始化' if status['initialized'] else '❌ 未初始化'}")

        # 按伺服器分組顯示
        if 'servers' in status and status['servers']:
            print("\n按伺服器分組:")
            for server_name, server_info in status['servers'].items():
                print(f"\n  📦 {server_name} ({server_info['enabled_count']} 個工具)")
                for tool_name in server_info['enabled_tools']:
                    print(f"     ✅ {tool_name}")

        # 顯示所有工具的詳細狀態
        if status['initialized'] and status['tools']:
            print("\n詳細工具列表:")
            enabled_tools = [t for t in status['tools'] if t['enabled']]
            disabled_tools = [t for t in status['tools'] if not t['enabled']]

            if enabled_tools:
                print("\n  ✅ 已啟用:")
                for tool in enabled_tools:
                    print(f"     • {tool['pure_name']} (伺服器: {tool['server']})")

            if disabled_tools:
                print("\n  ❌ 已停用:")
                for tool in disabled_tools:
                    print(f"     • {tool['pure_name']} (伺服器: {tool['server']})")

        print("\n" + "=" * 60 + "\n")
    except Exception as e:
        print(f"\n[錯誤] 無法取得工具狀態: {e}\n")
        logger.error(f"取得工具狀態時發生錯誤: {e}", exc_info=True)


async def main_async():
    """Main chatbot loop (async version)."""
    display_welcome()

    # Create the chatbot
    try:
        app, mcp_manager = await create_chatbot()
        has_tools = mcp_manager is not None and mcp_manager._initialized

        if has_tools:
            print("\n[系統] 聊天機器人已啟動（含 MCP 工具）！開始對話吧！\n")
        else:
            print("\n[系統] 聊天機器人已啟動（純聊天模式）！開始對話吧！\n")
    except Exception as e:
        print(f"\n[錯誤] 無法啟動聊天機器人: {e}")
        print("請確保:")
        print("1. LM Studio 已啟動")
        print("2. 已載入模型")
        print("3. 本地伺服器正在運行 (預設: http://localhost:1234)\n")
        return

    # Generate a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Main conversation loop
    try:
        while True:
            try:
                # Get user input
                user_input = input("👤 你: ").strip()

                # Handle empty input
                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['/quit', '/exit']:
                    print("\n[系統] 再見！感謝使用！\n")
                    break

                elif user_input.lower() == '/new':
                    thread_id = str(uuid.uuid4())
                    config = {"configurable": {"thread_id": thread_id}}
                    print("\n[系統] 已開始新的對話\n")
                    continue

                elif user_input.lower() == '/history':
                    display_history(app, config)
                    continue

                elif user_input.lower() == '/tools':
                    display_tools_status(mcp_manager)
                    continue

                elif user_input.lower() == '/help':
                    display_welcome(has_tools)
                    continue

                # Process user message
                input_message = HumanMessage(content=user_input)

                # Get AI response
                print("🤖 AI: ", end="", flush=True)
                try:
                    output = app.invoke({"messages": [input_message]}, config)
                    ai_response = output["messages"][-1].content
                    print(ai_response)
                except Exception as e:
                    print(f"\n[錯誤] AI 回應失敗: {e}")
                    print("請檢查 LM Studio 是否正常運作。\n")
                    logger.error(f"AI 回應錯誤: {e}", exc_info=True)

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print("\n\n[系統] 偵測到中斷訊號，正在退出...\n")
                break
            except Exception as e:
                print(f"\n[錯誤] 發生未預期的錯誤: {e}\n")
                logger.error(f"未預期錯誤: {e}", exc_info=True)

    finally:
        # Cleanup MCP resources
        if mcp_manager:
            await mcp_manager.cleanup()


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
