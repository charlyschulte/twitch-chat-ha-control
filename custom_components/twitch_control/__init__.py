import logging
import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "twitch_control"

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config):
    """Set up Twitch Control from YAML (if used)."""
    return True  # We use config flow, so setup from YAML does nothing

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Twitch Control from a config entry."""
    from .twitch import TwitchBot

    token = entry.data.get("twitch_oauth_token")
    channel = entry.data.get("twitch_channel")

    if not token or not channel:
        _LOGGER.error("Missing Twitch OAuth token or channel in config entry")
        return False

    bot = TwitchBot(hass, token, channel)
    hass.data[DOMAIN] = bot

    # Register the send_message service
    async def handle_send_message(call):
        """Send a message to Twitch chat."""
        message = call.data.get("message", "Hello from Home Assistant!")
        await bot.send_message(message)

    hass.services.async_register(DOMAIN, "send_message", handle_send_message)

    async def start_bot():
        """Start the Twitch bot."""
        _LOGGER.error("Starting Bot")
        
        try:
            await bot.start()
            _LOGGER.error("Twitch Control integration initialized")
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout occurred while starting Twitch bot.")
        except Exception as e:
            _LOGGER.error(f"Error starting Twitch bot: {e}")

    hass.loop.create_task(start_bot())  # Ensure bot starts after HA is initialized

    # Listen for the twitch_command event
    async def handle_twitch_command(event):
        """Handle the twitch_command event."""
        message = event.data.get("message")
        if message:
            # Add your automation control logic here
            _LOGGER.error(f"Handling Twitch command: {message}")
            # Example: Turn on a light
            await hass.services.async_call("light", "turn_on", {"entity_id": "light.your_light_entity"})

    hass.bus.async_listen("twitch_command", handle_twitch_command)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    bot = hass.data.pop(DOMAIN, None)

    if bot:
        try:
            await bot.close()  # Ensure the bot shuts down properly
            _LOGGER.error("Twitch bot closed successfully")
        except Exception as e:
            _LOGGER.error(f"Error closing Twitch bot: {e}")
            return False  # Return False to indicate an error during unload

    return True
