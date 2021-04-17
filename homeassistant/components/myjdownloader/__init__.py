"""MyJDownloader integration."""

from datetime import timedelta
import logging

import myjdapi
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_EMAIL, CONF_NAME, CONF_PASSWORD
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

from .sensor import MyJDSensor

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MyJDownloader Sensor."""
    email = config.get(CONF_EMAIL)
    password = config.get(CONF_PASSWORD)
    name = config.get(CONF_NAME)

    myjd = myjdapi.Myjdapi()
    try:
        myjd.connect(email, password)
    except myjdapi.myjdapi.MYJDException:
        _LOGGER.error(
            "Failed to connect to MyJDownloader, please check email and password"
        )
        raise PlatformNotReady

    entities = []
    if name:
        entities.append(MyJDSensor(hass, myjd, name))
    else:
        for device in myjd.list_devices():
            entities.append(MyJDSensor(hass, myjd, device["name"]))
    if not entities:
        _LOGGER.warning("Failed to setup MyJDownloader sensor, no device found.")
        raise PlatformNotReady

    add_entities(entities, True)
