"""
tbd
"""
from __future__ import annotations
from contextlib import suppress

import yarl
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.network import get_url, NoURLAvailableError

DOMAIN = "auth-user"


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """ tbd """
    hass.http.register_view(CurrentUserView)

    return True


class CurrentUserView(HomeAssistantView):
    """ tbd """

    url = "/auth/user"
    name = "api:auth:user"
    requires_auth = True

    @callback
    async def get(self, request):
        """ tbd """
        user = request["hass_user"]
        hass = request.app['hass']

        hass_host = 'homeassistant.local'
        with suppress(NoURLAvailableError):
            hass_host = yarl.URL(get_url(hass, allow_ip=True)).host

        user_name = user.name
        for cred in user.credentials:
            provider = hass.auth.get_auth_provider(
                cred.auth_provider_type, cred.auth_provider_id
            )
            user_meta = await provider.async_user_meta_for_credentials(cred)
            user_name = user_meta.name
            break

        return self.json({
            'name': user.name,
            'email': f'{user_name}@{hass_host}',
            'sub': user.id,
        })
