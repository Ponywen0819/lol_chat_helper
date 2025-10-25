"""Main chat application."""

import uuid
import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..config import AppConfig, logger
from ..mcp import MCPToolManager
from ..graph import build_lol_agent
from .display import display_welcome
from .commands import CommandHandler


class ChatApp:
    """主要的聊天應用程式"""

    def __init__(self, config: Optional[AppConfig] = None):
        """
        初始化聊天應用程式

        Args:
            config: 應用程式配置（如未提供則從環境變數載入）
        """
        self.config = config or AppConfig.from_env()
        self.app = None
        self.mcp_manager: Optional[MCPToolManager] = None
        self.command_handler: Optional[CommandHandler] = None
        self.has_tools = False

    async def initialize(self):
        """初始化應用程式（非同步）"""
        # 初始化模型
        logger.info("正在初始化語言模型...")
        model = ChatOpenAI(
            base_url=self.config.model.base_url,
            api_key=self.config.model.api_key,
            model=self.config.model.model_name,
            temperature=self.config.model.temperature,
            streaming=self.config.model.streaming,
        )

        # 初始化 MCP 工具
        tools = []
        if self.config.mcp.enabled:
            try:
                logger.info("正在初始化 MCP 工具管理器...")
                self.mcp_manager = MCPToolManager(self.config.mcp.config_path)
                tools = await self.mcp_manager.initialize()
                self.has_tools = True
                logger.info(f"成功載入 {len(tools)} 個 MCP 工具")
            except Exception as e:
                logger.warning(f"MCP 初始化失敗，將以純聊天模式運行: {e}")
                logger.warning("如需使用 MCP 工具，請確保：")
                logger.warning("1. Node.js 已安裝且可執行 npx")
                logger.warning("2. 網路可以訪問 https://mcp-api.op.gg/mcp")
                logger.warning("3. mcp_config.json 配置正確")
                self.mcp_manager = None
                tools = []
                self.has_tools = False

        # 建構 graph
        logger.info("正在建構 agent graph...")
        self.app = build_lol_agent(model=model, tools=tools, enable_memory=True)

        # 初始化命令處理器
        self.command_handler = CommandHandler(self.app, self.mcp_manager)

        if self.has_tools:
            logger.info("聊天機器人已啟動（含 MCP 工具）")
        else:
            logger.info("聊天機器人已啟動（純聊天模式）")

    async def run_async(self):
        """執行聊天應用程式（非同步版本）"""
        # 顯示歡迎訊息
        display_welcome(self.has_tools)

        # 初始化應用程式
        try:
            await self.initialize()
            if self.has_tools:
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

        # 生成對話執行緒 ID
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # 主要對話循環
        try:
            while True:
                try:
                    # 取得使用者輸入
                    user_input = input("👤 你: ").strip()

                    # 處理空輸入
                    if not user_input:
                        continue

                    # 處理命令
                    if self.command_handler.is_command(user_input):
                        should_exit, new_config = self.command_handler.handle_command(
                            user_input, config
                        )
                        if should_exit:
                            break
                        if new_config:
                            config = new_config
                        continue

                    # 處理使用者訊息
                    input_message = HumanMessage(content=user_input)

                    # 取得 AI 回應
                    print("🤖 AI: ", end="", flush=True)
                    try:
                        output = await self.app.ainvoke({"messages": [input_message]}, config)
                        ai_response = output["messages"][-1].content
                        print(ai_response)
                    except Exception as e:
                        print(f"\n[錯誤] AI 回應失敗: {e}")
                        print("請檢查 LM Studio 是否正常運作。\n")
                        logger.error(f"AI 回應錯誤: {e}", exc_info=True)

                    print()  # 空行增加可讀性

                except KeyboardInterrupt:
                    print("\n\n[系統] 偵測到中斷訊號，正在退出...\n")
                    break
                except Exception as e:
                    print(f"\n[錯誤] 發生未預期的錯誤: {e}\n")
                    logger.error(f"未預期錯誤: {e}", exc_info=True)

        finally:
            # 清理資源
            if self.mcp_manager:
                await self.mcp_manager.cleanup()

    def run(self):
        """執行聊天應用程式（同步入口點）"""
        asyncio.run(self.run_async())
