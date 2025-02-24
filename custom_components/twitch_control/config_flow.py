import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class TwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Twitch integration config flow."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Twitch Control", data=user_input)

        schema = vol.Schema({
            vol.Required("twitch_channel"): str,
            vol.Required("twitch_oauth_token"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return TwitchOptionsFlowHandler(entry)

class TwitchOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Twitch integration options."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("twitch_channel", default=self.entry.data["twitch_channel"]): str,
            vol.Required("twitch_oauth_token", default=self.entry.data["twitch_oauth_token"]): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
