import json
import logging
from pathlib import Path
from typing import Optional

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
import dotenv

# 載入環境變數
dotenv.load_dotenv()

# 設定日誌
logging_level = logging.DEBUG  if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)


class MCPToolManager:
    """
    MCP 工具管理器

    負責管理 MCP 伺服器連線、工具載入和過濾。
    """

    def __init__(self, config_path: str = "mcp_config.json"):
        """
        初始化 MCP 工具管理器

        Args:
            config_path: MCP 配置檔案路徑
        """
        self.servers = []
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.client: Optional[MultiServerMCPClient] = None
        self.all_tools: list[BaseTool] = []
        self.enabled_tools: list[BaseTool] = []
        self._initialized = False

    def _load_config(self) -> dict:
        """載入 MCP 配置檔案"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info(f"成功載入 MCP 配置: {self.config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"找不到 MCP 配置檔案: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"MCP 配置檔案格式錯誤: {e}")
            raise

    async def initialize(self) -> list[BaseTool]:
        """
        初始化 MCP 客戶端並載入工具

        Returns:
            啟用的工具列表

        Raises:
            Exception: 初始化失敗時拋出
        """
        if self._initialized:
            logger.info("MCP 已初始化，返回已載入的工具")
            return self.enabled_tools

        try:
            logger.info("開始初始化 MCP 客戶端...")

            # 建立 MultiServerMCPClient
            mcp_servers = self.config.get("mcpServers", {})
            if not mcp_servers:
                raise ValueError("MCP 配置中沒有定義任何伺服器")

            self.client = MultiServerMCPClient(mcp_servers)

            # 紀錄連線的伺服器
            self.servers = list(mcp_servers.keys())
            logger.info(f"已連線到 MCP 伺服器: {self.servers}")

            # 載入所有工具
            logger.info("正在從 MCP 伺服器載入工具...")
            self.all_tools = await self.client.get_tools()
            logger.info(f"成功載入 {len(self.all_tools)} 個工具")

            # 過濾啟用的工具
            self.enabled_tools = self._filter_enabled_tools()
            logger.info(f"啟用 {len(self.enabled_tools)}/{len(self.all_tools)} 個工具")

            self._initialized = True
            return self.enabled_tools

        except Exception as e:
            logger.error(f"MCP 初始化失敗: {e}")
            raise

    def _parse_tool_name(self, tool_name: str) -> tuple[str, str]:
        """
        從工具的完整名稱中提取伺服器名稱和純工具名稱

        Args:
            tool_name: 工具的完整名稱，例如 "opgg-mcp_lol-summoner-search"

        Returns:
            (伺服器名稱, 純工具名稱) 例如 ("opgg-mcp", "lol-summoner-search")
        """
        # 工具名稱格式通常是：server-name_tool-name
        self.servers = self.servers or []
        for server in self.servers:
            prefix = f"{server}_"
            if tool_name.startswith(prefix):
                return server, tool_name[len(prefix):]
        return "", tool_name

    def _filter_enabled_tools(self) -> list[BaseTool]:
        """
        根據配置過濾啟用的工具

        新格式：toolsConfig 按伺服器分組，enabled 是工具名稱陣列
        例如：
        {
          "toolsConfig": {
            "opgg-mcp": {
              "enabled": ["lol_summoner_search", "lol_champion_analysis", ...]
            }
          }
        }

        Returns:
            啟用的工具列表
        """
        tools_config = self.config.get("toolsConfig", {})
        enabled_tools = []

        # DEBUG: Log all tool names to understand format
        logger.info("=" * 60)
        logger.info("工具過濾診斷資訊")
        logger.info("=" * 60)
        logger.info(f"從 MCP 伺服器載入的工具列表 (共 {len(self.all_tools)} 個):")
        for i, tool in enumerate(self.all_tools, 1):
            logger.info(f"  {i}. 名稱: {tool.name}")
            logger.info(f"     描述: {getattr(tool, 'description', 'N/A')[:100]}")

        logger.info(f"\n配置檔案中的 toolsConfig:")
        for srv_name, srv_config in tools_config.items():
            enabled_list = srv_config.get("enabled", [])
            logger.info(f"  伺服器: {srv_name}")
            logger.info(f"  啟用列表 (共 {len(enabled_list)} 個): {enabled_list}")

        logger.info("\n開始匹配工具...")
        logger.info("=" * 60)

        for tool in self.all_tools:
            # 解析工具名稱，提取伺服器名稱和純工具名稱
            server_name, pure_tool_name = self._parse_tool_name(tool.name)
            logger.debug(f"處理工具: {tool.name}")
            logger.debug(f"  解析結果 -> 伺服器: '{server_name}', 純名稱: '{pure_tool_name}'")
            is_enabled = False

            # 檢查該伺服器的 enabled 陣列
            if server_name in tools_config:
                enabled_list = tools_config[server_name].get("enabled", [])
                logger.debug(f"  找到伺服器配置 '{server_name}'，enabled 列表: {enabled_list}")

                if pure_tool_name in enabled_list:
                    is_enabled = True
                    logger.info(f"✅ 啟用: {tool.name} (匹配到: {pure_tool_name})")
                else:
                    logger.debug(f"  '{pure_tool_name}' 不在 enabled 列表中")
            else:
                logger.debug(f"  伺服器 '{server_name}' 不在 toolsConfig 中")
                # 如果找不到對應的伺服器配置，嘗試在所有伺服器的 enabled 陣列中查找
                for srv_name, srv_config in tools_config.items():
                    enabled_list = srv_config.get("enabled", [])
                    logger.debug(f"  備用檢查 - 伺服器 {srv_name} 的 enabled 列表: {enabled_list}")

                    # 檢查純工具名稱或完整名稱是否在 enabled 陣列中
                    if pure_tool_name in enabled_list or tool.name in enabled_list:
                        is_enabled = True
                        logger.info(f"✅ 啟用: {tool.name} (從伺服器 {srv_name} 配置中找到)")
                        break

            if is_enabled:
                enabled_tools.append(tool)
            else:
                logger.debug(f"❌ 停用: {tool.name}")

        logger.info("=" * 60)
        logger.info(f"過濾完成：啟用 {len(enabled_tools)}/{len(self.all_tools)} 個工具")
        logger.info("=" * 60)

        return enabled_tools

    def get_enabled_tools(self) -> list[BaseTool]:
        """
        獲取啟用的工具列表

        Returns:
            啟用的工具列表
        """
        if not self._initialized:
            logger.warning("MCP 尚未初始化，返回空列表")
            return []
        return self.enabled_tools

    def is_tool_enabled(self, tool_name: str) -> bool:
        """
        檢查指定工具是否啟用

        Args:
            tool_name: 工具名稱

        Returns:
            工具是否啟用
        """
        return any(tool.name == tool_name for tool in self.enabled_tools)

    def get_tools_status(self) -> dict:
        """
        獲取工具狀態統計

        新格式：按伺服器分組顯示啟用的工具列表

        Returns:
            包含工具狀態的字典，格式：
            {
                "total": 總工具數,
                "enabled": 啟用工具數,
                "disabled": 停用工具數,
                "initialized": 是否已初始化,
                "servers": {
                    "server-name": {
                        "enabled_tools": ["tool1", "tool2", ...],
                        "enabled_count": 數量
                    }
                },
                "tools": [所有工具的詳細狀態列表]
            }
        """
        tools_config = self.config.get("toolsConfig", {})

        enabled_count = len(self.enabled_tools)
        total_count = len(self.all_tools) if self._initialized else 0

        # 按伺服器分組統計
        servers_info = {}
        for server_name, server_config in tools_config.items():
            enabled_list = server_config.get("enabled", [])
            servers_info[server_name] = {
                "enabled_tools": enabled_list,
                "enabled_count": len(enabled_list)
            }

        # 建立所有工具的詳細狀態列表
        tools_list = []
        if self._initialized:
            for tool in self.all_tools:
                server_name, pure_tool_name = self._parse_tool_name(tool.name)
                is_enabled = tool in self.enabled_tools

                tools_list.append({
                    "name": tool.name,
                    "pure_name": pure_tool_name,
                    "server": server_name,
                    "enabled": is_enabled,
                    "description": getattr(tool, "description", "")
                })
        else:
            # 未初始化時，從配置中生成工具列表
            for server_name, server_config in tools_config.items():
                enabled_list = server_config.get("enabled", [])
                for tool_name in enabled_list:
                    tools_list.append({
                        "name": f"{server_name}_{tool_name}",
                        "pure_name": tool_name,
                        "server": server_name,
                        "enabled": True,
                        "description": ""
                    })

        return {
            "total": total_count,
            "enabled": enabled_count,
            "disabled": total_count - enabled_count,
            "initialized": self._initialized,
            "servers": servers_info,
            "tools": tools_list
        }

    async def cleanup(self):
        """清理資源，關閉 MCP 連線"""
        if self.client:
            logger.info("清理 MCP 資源...")
            # MultiServerMCPClient 會自動管理連線
            self.client = None
            self._initialized = False

    def __repr__(self) -> str:
        status = self.get_tools_status()
        return (
            f"MCPToolManager(initialized={status['initialized']}, "
            f"enabled={status['enabled']}/{status['total']})"
        )
