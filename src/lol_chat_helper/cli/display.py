"""Display functions for CLI interface."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mcp import MCPToolManager

from ..config import logger


def display_welcome(has_tools: bool = False):
    """
    顯示歡迎訊息和使用說明

    Args:
        has_tools: 是否啟用 MCP 工具
    """
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
    """
    顯示對話歷史

    Args:
        app: Graph 應用實例
        config: Graph 配置
    """
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
        logger.error(f"取得對話歷史時發生錯誤: {e}", exc_info=True)


def display_tools_status(mcp_manager: Optional["MCPToolManager"]):
    """
    顯示 MCP 工具狀態

    Args:
        mcp_manager: MCP 工具管理器實例
    """
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
