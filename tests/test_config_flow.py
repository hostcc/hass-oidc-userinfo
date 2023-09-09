"""
Tests config flow for the custom component.
"""
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.config_entries import ConfigEntry

from custom_components.oidc_userinfo.const import DOMAIN


async def test_config_flow(hass):
    """
    Tests config flow with no options.
    """
    # Initial step
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
    )

    # Verify it results in creating entity of proper type/domain
    assert result['type'] == FlowResultType.CREATE_ENTRY
    assert isinstance(result['result'], ConfigEntry)
    assert result['result'].domain == DOMAIN

    # Attemting to instantiate another entry should be aborted
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
    )

    assert result['type'] == FlowResultType.ABORT
    assert result['reason'] == 'single_instance_allowed'
