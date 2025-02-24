import logging
import twitchio
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from twitchio.ext import commands

DOMAIN = "twitch_control"

_LOGGER = logging.getLogger(__name__)

class TwitchBot(commands.Bot):
    def __init__(self, hass: HomeAssistant, token: str, channel: str):
        """Initialize the bot with the given token and channel."""
        super().__init__(token=token, prefix="!", initial_channels=[channel])
        self.hass = hass  # Store the Home Assistant instance
        self.channel = channel  # Store the channel
        self._client = self  # Fix TwitchIO 2.x changes
    async def event_ready(self):
        """When the bot is connected and ready."""
        _LOGGER.error(f"Twitch bot attributes: {dir(self)}")  # Log available attributes
        _LOGGER.error(f"Twitch bot connected as {self.nick}")
    async def event_disconnect(self):
        """Handle bot disconnection."""
        _LOGGER.error("Twitch bot disconnected!")
    async def event_command_error(self, ctx, error):
        """Log any command errors."""
        _LOGGER.error(f"Twitch command error: {error}")
    async def event_disconnect(self):
        """Handle bot disconnection."""
        _LOGGER.error("Twitch bot disconnected! Attempting to restart...")
        await asyncio.sleep(5)  # Wait a bit before restarting
        await self.start()
    async def event_message(self, message):
        """Handle incoming messages from the Twitch chat."""
        if message.echo or message.author.name.lower() == self.nick.lower():
            return  # Ignore own messages

        _LOGGER.error(f"Twitch command received: {message.content}")  # Log the received message

        if message.content.startswith("!lights"):
            args = message.content.split()
            color = args[1] if len(args) > 1 else "default"

            # Trigger Home Assistant automation
            await self.hass.services.async_call(
                "automation", "trigger",
                {"entity_id": "automation.twitch_lights", "variables": {"color": color}}
            )


    async def send_message(self, message: str):
        """Send a message to the Twitch channel."""
        if not self.connected_channels:
            _LOGGER.error("Twitch bot is not connected to any channels.")
            return
        
        try:
            channel = self.connected_channels[0]  # Get the first connected channel
            await channel.send(message)
        except Exception as e:
            _LOGGER.error(f"Failed to send message: {e}")

    async def close(self):
        """Gracefully shut down the bot."""
        try:
            await super().close()
            _LOGGER.error("Twitch bot closed.")
        except Exception as e:
            _LOGGER.error(f"Error closing Twitch bot: {e}")

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the Twitch integration."""
    token = config[DOMAIN]["twitch_oauth_token"]
    channel = config[DOMAIN]["twitch_channel"]
    
    _LOGGER.error("Starting Bot with credentials: ")
    
    _LOGGER.error(token)
    _LOGGER.error(channel)
    bot = TwitchBot(hass, token, channel)
    hass.data[DOMAIN] = bot

    # Listen for Home Assistant stop to gracefully close the bot
    async def on_shutdown(event):
        await bot.close()
    hass.bus.async_listen_once("homeassistant_stop", on_shutdown)

    # Register the service
    async def handle_send_message(call):
        """Handle sending a message to Twitch chat."""
        message = call.data.get("message", "Hello from Home Assistant!")
        await bot.send_message(message)

    hass.services.async_register(DOMAIN, "send_message", handle_send_message)

    # Start the bot in an async task
    try:
        await bot.start()
    except Exception as e:
        _LOGGER.error(f"Failed to start Twitch bot: {e}")
        return False  

    return True
