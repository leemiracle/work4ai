"""配置加载器 - 支持 YAML 配置、环境变量替换"""

from __future__ import annotations

import os
import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_BASE_DIR = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _BASE_DIR / "config"


def _load_dotenv():
    """加载 .env 文件中的环境变量（简单实现，无需 python-dotenv）"""
    env_file = _BASE_DIR / ".env"
    if not env_file.exists():
        return
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


def _resolve_env(value: str) -> str:
    pattern = re.compile(r"\{env:([A-Za-z0-9_]+)(?:\|([^}]*))?\}")

    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default = match.group(2)
        env_value = os.environ.get(var_name)
        if env_value is not None:
            return env_value
        if default is not None:
            return _resolve_env(default)
        return ""

    return pattern.sub(replacer, value)


def _resolve_recursive(obj: Any) -> Any:
    if isinstance(obj, str):
        return _resolve_env(obj)
    if isinstance(obj, dict):
        return {k: _resolve_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_recursive(v) for v in obj]
    return obj


def load_yaml(filename: str) -> dict:
    path = _CONFIG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return _resolve_recursive(raw)


class Config:
    _settings: dict | None = None
    _sources: dict | None = None

    @classmethod
    def settings(cls) -> dict:
        if cls._settings is None:
            cls._settings = load_yaml("settings.yaml")
        return cls._settings

    @classmethod
    def sources(cls) -> dict:
        if cls._sources is None:
            cls._sources = load_yaml("sources.yaml")
        return cls._sources

    @classmethod
    def reload(cls):
        cls._settings = None
        cls._sources = None

    @classmethod
    def base_dir(cls) -> Path:
        return _BASE_DIR

    @classmethod
    def ensure_dirs(cls):
        for path in [
            "data/raw",
            "data/processed",
            "data/graphs",
            "data/reports",
            "data/vectors",
        ]:
            (cls.base_dir() / path).mkdir(parents=True, exist_ok=True)
