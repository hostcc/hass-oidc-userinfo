"""
Pytest configuration and fixtures
"""
import pytest


@pytest.fixture(autouse=True)
# pylint: disable=unused-argument
def auto_enable_custom_integrations(enable_custom_integrations):
    """
    Automatically uses `enable_custom_integrations` Homeassistant fixture,
    since it is required for custom integrations to be loaded during tests.
    """
    yield
