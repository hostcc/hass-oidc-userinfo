"""
ConfigFlow support for the custom component.
"""
from __future__ import annotations
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, TITLE


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handles the config flow for the integration.
    """
    VERSION = 1

    async def async_step_user(
        self, _user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handles adding single entry upon user confirmation.
        """
        # Only single entry allowed
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title=TITLE, data={})
