"""Command handler for CLI interface."""

import uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mcp import MCPToolManager

from .display import display_welcome, display_history, display_tools_status
from ..config import Commands


class CommandHandler:
    """處理 CLI 命令的類別"""

    def __init__(self, app, mcp_manager: Optional["MCPToolManager"] = None):
        """
        初始化命令處理器

        Args:
            app: Graph 應用實例
            mcp_manager: MCP 工具管理器（可選）
        """
        self.app = app
        self.mcp_manager = mcp_manager
        self.has_tools = mcp_manager is not None and mcp_manager._initialized

    def handle_command(self, user_input: str, config: dict) -> tuple[bool, Optional[dict]]:
        """
        處理使用者命令

        Args:
            user_input: 使用者輸入
            config: 當前的 graph 配置

        Returns:
            (should_exit, new_config) - 是否退出程式和新的配置（如有）
        """
        command = user_input.lower().strip()

        # Quit command
        if command in Commands.QUIT:
            print("\n[系統] 再見！感謝使用！\n")
            return True, None

        # New conversation
        if command == Commands.NEW:
            new_thread_id = str(uuid.uuid4())
            new_config = {"configurable": {"thread_id": new_thread_id}}
            print("\n[系統] 已開始新的對話\n")
            return False, new_config

        # Show history
        if command == Commands.HISTORY:
            display_history(self.app, config)
            return False, None

        # Show tools status
        if command == Commands.TOOLS:
            display_tools_status(self.mcp_manager)
            return False, None

        # Show help
        if command == Commands.HELP:
            display_welcome(self.has_tools)
            return False, None

        # Not a command
        return False, None

    def is_command(self, user_input: str) -> bool:
        """
        檢查輸入是否為命令

        Args:
            user_input: 使用者輸入

        Returns:
            是否為命令
        """
        command = user_input.lower().strip()
        return (
            command in Commands.QUIT or
            command == Commands.NEW or
            command == Commands.HISTORY or
            command == Commands.TOOLS or
            command == Commands.HELP
        )
