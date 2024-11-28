"""
Tests for HTTP view for current user information
"""
from unittest.mock import Mock
import json
from http import HTTPStatus

import pytest

from aiohttp.web_exceptions import HTTPUnauthorized
from homeassistant.components.http.view import request_handler_factory

from custom_components.oidc_userinfo import CurrentUserView


class MockWebRequest(Mock, dict):
    """
    Mocked aiohttp.web.Request
    """
    def __init__(self, *args, **kwargs):
        # The mocked class inherits from `dict` and `Mock` so call both
        # constructors
        dict.__init__(self, *args, **kwargs)
        Mock.__init__(self, *args, **kwargs)
        # `match_info` member is used by HASS so initialize it with sane
        # defaults
        self.match_info = {}


async def test_auth_user_not_authenticated(hass):
    """
    Tests for HTTP Unathorized when view is called by non-authenticated client.
    """
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


@pytest.mark.parametrize('hass_config_urls,expected_user_domain', [
    # Both external and internal URLs are provided, external one should be
    # selected
    (
        {
            'external_url': 'https://test.url',
            'internal_url': 'http://localhost'
        },
        'test.url'
    ),
    # Only external URL is provided, should be selecte
    ({'external_url': 'https://test.url'}, 'test.url'),
    # Same but for internal one
    ({'internal_url': 'http://localhost'}, 'localhost'),
    # None of URLs are configured in HASS, should fall back to
    # `homeassistant.local`
    ({}, 'homeassistant.local'),
])
async def test_auth_user(
    hass, hass_admin_credential, hass_admin_user, hass_config_urls,
    expected_user_domain
):
    """
    Tests for correct response from the view when client is authenticated
    """
    hass.config.external_url = hass_config_urls.get('external_url', None)
    hass.config.internal_url = hass_config_urls.get('internal_url', None)
    # Link admin user and its credentials (both mocked) together
    await hass.auth.async_link_user(hass_admin_user, hass_admin_credential)
    request = MockWebRequest(
        # Pretend admin user has been authenticated
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
    # Retrieve user name for admin credentials from the authentication provider
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
        # The domain should fallback to `homeassistant.local` since no real
        # networking is available
        'email': f'{user_name}@{expected_user_domain}',
        'sub': hass_admin_user.id,
        'name': hass_admin_user.name,
    }
