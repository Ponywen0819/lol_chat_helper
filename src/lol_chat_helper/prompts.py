"""Prompt templates and generators for LOL Chat Helper."""

from datetime import datetime
from typing import Optional

from lol_chat_helper.config import WEEKDAYS_ZH


def get_date_info() -> str:
    """
    生成當前日期資訊

    Returns:
        格式化的日期資訊字串
    """
    current_date = datetime.now()
    weekday = WEEKDAYS_ZH[current_date.weekday()]

    return (
        f"當前日期：{current_date.year}年{current_date.month}月{current_date.day}日\n"
        f"星期：{weekday}\n"
    )


def get_lol_agent_prompt(with_tools: bool = True) -> str:
    """
    生成 LOL 助手的 system prompt

    Args:
        with_tools: 是否包含工具說明

    Returns:
        System prompt 字串
    """
    date_info = get_date_info()

    if with_tools:
        return (
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
        return (
            "你是一個友善且樂於助人的 AI 助手。\n"
            f"{date_info}\n"
            "請用繁體中文回答問題，並記住之前的對話內容。\n"
            "注意：目前 MCP 工具未啟用，無法查詢即時的 LOL 資料。"
        )


def get_system_prompt(
    agent_type: str = "lol",
    with_tools: bool = True,
    custom_prompt: Optional[str] = None
) -> str:
    """
    根據 agent 類型獲取 system prompt

    Args:
        agent_type: Agent 類型 ("lol", "general", "custom")
        with_tools: 是否包含工具說明
        custom_prompt: 自訂 prompt（當 agent_type="custom" 時使用）

    Returns:
        System prompt 字串
    """
    if agent_type == "custom" and custom_prompt:
        return custom_prompt

    if agent_type == "lol":
        return get_lol_agent_prompt(with_tools)

    # Default: general chat agent
    date_info = get_date_info()
    return (
        "你是一個友善且樂於助人的 AI 助手。\n"
        f"{date_info}\n"
        "請用繁體中文回答問題，並記住之前的對話內容。"
    )


# Prompt templates for future agent types
class PromptTemplates:
    """Collection of prompt templates for different agent types."""

    LOL_AGENT = "lol"
    GENERAL_AGENT = "general"
    CUSTOM_AGENT = "custom"

    @staticmethod
    def get_template(template_name: str, **kwargs) -> str:
        """
        獲取指定模板

        Args:
            template_name: 模板名稱
            **kwargs: 模板參數

        Returns:
            格式化的 prompt
        """
        if template_name == PromptTemplates.LOL_AGENT:
            return get_lol_agent_prompt(kwargs.get("with_tools", True))
        elif template_name == PromptTemplates.GENERAL_AGENT:
            return get_system_prompt("general", kwargs.get("with_tools", False))
        elif template_name == PromptTemplates.CUSTOM_AGENT:
            return kwargs.get("custom_prompt", "")
        else:
            raise ValueError(f"Unknown template: {template_name}")
