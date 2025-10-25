"""Configuration management for LOL Chat Helper."""

import os
import logging
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for the language model."""

    base_url: str
    api_key: str
    model_name: str
    temperature: float
    streaming: bool = False

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create ModelConfig from environment variables."""
        return cls(
            base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
            model_name=os.getenv("MODEL_NAME", "gpt-oss:20b"),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
            streaming=os.getenv("MODEL_STREAMING", "false").lower() == "true",
        )


@dataclass
class MCPConfig:
    """Configuration for MCP (Model Context Protocol) tools."""

    enabled: bool
    config_path: str

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Create MCPConfig from environment variables."""
        return cls(
            enabled=os.getenv("MCP_ENABLED", "true").lower() == "true",
            config_path=os.getenv("MCP_CONFIG_PATH", "mcp_config.json"),
        )


@dataclass
class AppConfig:
    """Main application configuration."""

    model: ModelConfig
    mcp: MCPConfig
    log_level: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create AppConfig from environment variables."""
        return cls(
            model=ModelConfig.from_env(),
            mcp=MCPConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Logging configuration
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


# Global logger instance
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))


# Constants
DEFAULT_THREAD_ID_LENGTH = 36  # UUID4 length
WEEKDAYS_ZH = ['一', '二', '三', '四', '五', '六', '日']


# Command constants
class Commands:
    """CLI command constants."""
    QUIT = ['/quit', '/exit']
    NEW = '/new'
    HISTORY = '/history'
    TOOLS = '/tools'
    HELP = '/help'
