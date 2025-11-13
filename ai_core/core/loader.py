import importlib.util
import os
from typing import Any, Dict, Optional

from .logger import get_logger

logger = get_logger(__name__)


class PluginLoader:
    """Generic plugin loader for strategies, models, and integrations."""

    def load_python_module(self, file_path: str, class_name: Optional[str] = None) -> Optional[Any]:
        if not os.path.exists(file_path):
            logger.error("Plugin file not found: %s", file_path)
            return None
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", file_path)
            module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            assert spec and spec.loader
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            if class_name:
                return getattr(module, class_name, None)
            return module
        except Exception as exc:
            logger.error("Error loading plugin %s: %s", file_path, exc)
            return None

    def load_configured(self, config: Dict[str, Any]) -> Optional[Any]:
        """Load a plugin based on a config dict with keys: type, path, class."""
        if config.get("type") == "python":
            return self.load_python_module(config.get("path", ""), config.get("class"))
        logger.warning("Unsupported plugin type: %s", config.get("type"))
        return None