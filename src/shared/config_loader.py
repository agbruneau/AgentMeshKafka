"""
Configuration Loader
====================
Centralized configuration management with YAML file support
and environment variable overrides.
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml


# Default config path relative to project root
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config.yaml"


def load_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """
    Load configuration from YAML file with environment variable overrides.
    
    Environment variables follow the pattern: SECTION__KEY__SUBKEY
    Example: AGENTS__RISK_AGENT__MODEL overrides agents.risk_agent.model
    
    Args:
        config_path: Optional path to config file. Defaults to project root config.yaml
        
    Returns:
        Configuration dictionary
    """
    path = config_path or DEFAULT_CONFIG_PATH
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Apply environment variable overrides
    config = _apply_env_overrides(config)
    
    return config


def _apply_env_overrides(config: dict, prefix: str = "") -> dict:
    """
    Recursively apply environment variable overrides.
    
    Pattern: PREFIX__KEY becomes nested config key.
    """
    for key, value in config.items():
        env_key = f"{prefix}{key}".upper() if prefix else key.upper()
        
        if isinstance(value, dict):
            config[key] = _apply_env_overrides(value, f"{env_key}__")
        else:
            env_value = os.getenv(env_key)
            if env_value is not None:
                # Type conversion based on original type
                if isinstance(value, bool):
                    config[key] = env_value.lower() in ("true", "1", "yes")
                elif isinstance(value, int):
                    config[key] = int(env_value)
                elif isinstance(value, float):
                    config[key] = float(env_value)
                else:
                    config[key] = env_value
    
    return config


def get_agent_config(agent_name: str, config: Optional[dict] = None) -> dict[str, Any]:
    """
    Get configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., "risk_agent", "decision_agent")
        config: Optional pre-loaded config. Will load if not provided.
        
    Returns:
        Agent-specific configuration
    """
    if config is None:
        config = load_config()
    
    return config.get("agents", {}).get(agent_name, {})


def get_thresholds(config: Optional[dict] = None) -> dict[str, Any]:
    """
    Get decision thresholds configuration.
    
    Args:
        config: Optional pre-loaded config. Will load if not provided.
        
    Returns:
        Thresholds configuration
    """
    if config is None:
        config = load_config()
    
    return config.get("thresholds", {
        "auto_approve_score": 20,
        "auto_reject_score": 80,
        "high_value_amount": 100000,
    })


def get_kafka_config(config: Optional[dict] = None) -> dict[str, Any]:
    """
    Get Kafka configuration.
    
    Args:
        config: Optional pre-loaded config. Will load if not provided.
        
    Returns:
        Kafka configuration
    """
    if config is None:
        config = load_config()
    
    return config.get("kafka", {})
