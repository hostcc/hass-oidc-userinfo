"""
Custom HASS component to provide minimal OIDC endpoint for information about
current user.
"""
from __future__ import annotations
from contextlib import suppress

import yarl
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.network import get_url, NoURLAvailableError
from homeassistant.helpers import config_validation as cv
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

# Required for any integration, provide empty schema since component doesn't
# use it
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(
    hass: HomeAssistant, _config: ConfigType
) -> bool:
    """
    Register the HTTP view when component is configured manually via YAML.
    """
    hass.http.register_view(CurrentUserView)

    return True


async def async_setup_entry(
    hass: HomeAssistant, _config_entry: ConfigEntry
) -> bool:
    """
    Register the HTTP view when component is configured via UI.
    """
    # Invoke `async_setup` to avoid code duplication
    return await async_setup(hass, None)


class CurrentUserView(HomeAssistantView):
    """
    HTTP view to provide minimal OIDC endpoint for current user.
    """

    url = "/auth/userinfo"
    name = "api:auth:userinfo"
    requires_auth = True

    @callback
    async def get(self, request):
        """
        Handles GET requests.
        """
        user = request["hass_user"]
        hass = request.app['hass']

        # Default host if more specific one is not available, will be used in
        # user's email (HomeAssistant doesn't have such property for users)
        hass_host = 'homeassistant.local'
        # Attempt to determine the host from HomeAssistant URL
        with suppress(NoURLAvailableError):
            hass_host = yarl.URL(get_url(hass, allow_ip=True)).host

        # Determine user name from authentication provider(s)
        user_name = user.name
        for cred in user.credentials:
            provider = hass.auth.get_auth_provider(
                cred.auth_provider_type, cred.auth_provider_id
            )
            user_meta = await provider.async_user_meta_for_credentials(cred)
            user_name = user_meta.name
            # Exit on first found
            break

        # Provide minimal set of OIDC claims UserInfo,
        # https://openid.net/specs/openid-connect-core-1_0.html#UserInfoResponse.
        # Since the authentication token in HASS doesn't have a notion of
        # claims the set of those is constructed statically (as if
        # 'profile+email' has been requested)
        return self.json({
            'name': user.name,
            'email': f'{user_name}@{hass_host}',
            'sub': user.id,
        })
