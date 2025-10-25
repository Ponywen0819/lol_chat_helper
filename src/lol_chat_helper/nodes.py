"""Graph node functions for LOL Chat Helper."""

from typing import Callable
from langchain_core.messages import SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import MessagesState


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
