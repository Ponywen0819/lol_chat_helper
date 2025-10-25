"""Graph node functions for LOL Chat Helper."""

import time
from typing import Callable, Any
from langchain_core.messages import SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from lol_chat_helper.config import logger


def create_agent_node(
    model: BaseChatModel,
    system_prompt: str,
    tools: list[BaseTool]
) -> Callable[[MessagesState], dict]:
    """
    建立帶有工具的 agent 節點

    Args:
        model: 語言模型實例
        system_prompt: System prompt 內容
        tools: 可用工具列表

    Returns:
        Agent 節點函數
    """
    def agent_node(state: MessagesState) -> dict:
        """
        處理訊息並生成 AI 回應（支援工具調用）

        Args:
            state: 當前的訊息狀態

        Returns:
            包含新訊息的字典
        """
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = model.bind_tools(tools).invoke(messages)
        return {"messages": response}

    return agent_node


def create_chat_node(
    model: BaseChatModel,
    system_prompt: str
) -> Callable[[MessagesState], dict]:
    """
    建立純聊天節點（不帶工具）

    Args:
        model: 語言模型實例
        system_prompt: System prompt 內容

    Returns:
        Chat 節點函數
    """
    def chat_node(state: MessagesState) -> dict:
        """
        處理訊息並生成 AI 回應（不使用工具）

        Args:
            state: 當前的訊息狀態

        Returns:
            包含新訊息的字典
        """
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = model.invoke(messages)
        return {"messages": response}

    return chat_node


class LoggingToolNode(ToolNode):
    """
    ToolNode with debug logging capabilities.

    Extends ToolNode to add detailed logging for:
    - Tool calls before execution
    - Execution time
    - Tool results after execution
    - Errors and exceptions

    All logs use DEBUG level for development debugging.
    """

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:
        """
        Execute tool calls with detailed logging.

        Args:
            input: Input state containing messages with tool calls
            config: Optional configuration
            **kwargs: Additional arguments

        Returns:
            Tool execution results
        """
        # Extract messages from input
        messages = input.get("messages", [])

        # Find messages with tool calls
        tool_call_messages = [
            msg for msg in messages
            if hasattr(msg, "tool_calls") and msg.tool_calls
        ]

        if tool_call_messages:
            # Log tool calls before execution
            for msg in tool_call_messages:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id", "unknown")

                    logger.debug(
                        f"[ToolNode] Calling tool: {tool_name} "
                        f"(id: {tool_id}) with args: {tool_args}"
                    )

        # Start timing
        start_time = time.time()

        try:
            # Execute tool calls via parent class
            result = super().invoke(input, config, **kwargs)

            # Calculate execution time
            elapsed_time = time.time() - start_time

            # Log results
            if tool_call_messages:
                tool_count = sum(
                    len(msg.tool_calls)
                    for msg in tool_call_messages
                )

                logger.debug(
                    f"[ToolNode] Executed {tool_count} tool(s) "
                    f"in {elapsed_time:.3f}s"
                )

                # Log individual tool results
                result_messages = result.get("messages", [])
                for msg in result_messages:
                    if hasattr(msg, "name") and hasattr(msg, "content"):
                        content_preview = (
                            str(msg.content)[:100] + "..."
                            if len(str(msg.content)) > 100
                            else str(msg.content)
                        )
                        logger.debug(
                            f"[ToolNode] Tool '{msg.name}' returned: "
                            f"{content_preview}"
                        )

            return result

        except Exception as e:
            # Log error with execution time
            elapsed_time = time.time() - start_time
            logger.debug(
                f"[ToolNode] Tool execution failed after {elapsed_time:.3f}s: "
                f"{type(e).__name__}: {str(e)}"
            )
            logger.exception("[ToolNode] Full traceback:")
            raise


# Future: Add more specialized node types
# Example:
# def create_routing_node(...) -> Callable:
#     """建立路由節點，可以根據使用者輸入路由到不同的 agent"""
#     pass
#
# def create_memory_node(...) -> Callable:
#     """建立記憶節點，處理長期記憶的儲存和檢索"""
#     pass
#
# def create_validation_node(...) -> Callable:
#     """建立驗證節點，驗證工具輸出或使用者輸入"""
#     pass
