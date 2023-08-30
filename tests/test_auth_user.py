""" tbd """
from unittest.mock import Mock
import json
from http import HTTPStatus

import pytest

from aiohttp.web_exceptions import HTTPUnauthorized
from homeassistant.components.http.view import request_handler_factory

from custom_components.oidc_userinfo import CurrentUserView


class MockWebRequest(Mock, dict):
    """ tbd """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        Mock.__init__(self, *args, **kwargs)
        self.match_info = {}


async def test_auth_user_not_authenticated(hass):
    """ tbd """
    request = MockWebRequest(
        {'ha_authenticated': False},
        path='/dummy',
        remote='local-test',
    )

    with pytest.raises(HTTPUnauthorized):
        await request_handler_factory(
            hass,
            CurrentUserView,
            CurrentUserView().get
        )(request)


async def test_auth_user(hass, hass_admin_credential, hass_admin_user):
    """ tbd """
    await hass.auth.async_link_user(hass_admin_user, hass_admin_credential)
    request = MockWebRequest(
        {
            'hass_user': hass_admin_user,
            'ha_authenticated': True,
        },
        app={'hass': hass},
        path='/dummy',
        remote='local-test',
    )

    response = await request_handler_factory(
        hass,
        CurrentUserView,
        CurrentUserView().get
    )(request)

    assert response.status == HTTPStatus.OK
    user_name = (
        await hass.auth.get_auth_provider(
            hass_admin_credential.auth_provider_type,
            hass_admin_credential.auth_provider_id
        ).async_user_meta_for_credentials(
            hass_admin_credential
        )
    ).name
    response_obj = json.loads(response.text)
    assert response_obj == {
        'email': f'{user_name}@homeassistant.local',
        'sub': hass_admin_user.id,
        'name': hass_admin_user.name,
    }
