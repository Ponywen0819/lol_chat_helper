"""LOL Chat Helper - A chatbot with memory and MCP tools support."""

from lol_chat_helper.config import AppConfig, ModelConfig, MCPConfig, logger
from lol_chat_helper.mcp import MCPToolManager
from lol_chat_helper.prompts import get_system_prompt, get_lol_agent_prompt, PromptTemplates
from lol_chat_helper.nodes import create_agent_node, create_chat_node
from lol_chat_helper.graph import GraphBuilder, build_lol_agent, build_general_agent, build_custom_agent
from lol_chat_helper.cli import ChatApp

__version__ = "0.2.0"

__all__ = [
    # Config
    "AppConfig",
    "ModelConfig",
    "MCPConfig",
    "logger",

    # MCP
    "MCPToolManager",

    # Prompts
    "get_system_prompt",
    "get_lol_agent_prompt",
    "PromptTemplates",

    # Nodes
    "create_agent_node",
    "create_chat_node",

    # Graph
    "GraphBuilder",
    "build_lol_agent",
    "build_general_agent",
    "build_custom_agent",

    # CLI
    "ChatApp",
]
