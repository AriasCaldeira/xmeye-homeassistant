config_flow.py

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from .const import DOMAIN

class XmeyeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for XMeye."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME] or user_input[CONF_HOST],
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=34567): int,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_NAME, default="XMeye Camera"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)