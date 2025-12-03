import yaml
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for Pixiv crawler"""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_file):
            return self._get_default_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            return config
        except Exception as e:
            print(f"Error loading config file: {e}. Using default config.")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'download': {
                'output_dir': './downloads',
                'max_pages': 10,
                'timeout': 30,
                'retry_times': 3,
                'delay': 1.0
            },
            'proxy': {
                'enabled': False,
                'http': None,
                'https': None
            },
            'headers': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
        }

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            print(f"Config saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
