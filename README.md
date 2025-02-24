Twitch Control

Control your Home Assistant automations using Twitch chat commands.
Installation

    Open HACS → Go to "Custom Repositories" → Add your repository.
    Install the Twitch Control integration.
    Configure your Twitch OAuth token and channel name.
        Get your token here: Twitch Token Generator.
        Important: Copy the Twitch access_token and prefix it with oauth: (e.g., oauth:your_token_here).

Now you're ready to automate Home Assistant via Twitch chat! 🎮🚀


Example Automation: Twitch Lights Control

This automation allows Twitch chat commands to change the color of your lights and send a confirmation message back to the chat.
Setup

    Add the following automation to your Home Assistant automations:
```
alias: Twitch Lights Control
description: "Control lights via Twitch chat"
trigger:
  - event_type: call_service
    event_data:
      domain: automation
      service: trigger
      service_data:
        entity_id: automation.twitch_lights
    platform: event
action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.service_data.variables.color == 'red' }}"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.your_light
            data:
              color_name: red
          - service: twitch_control.send_message
            data:
              message: "🔥 The lights are now RED!"
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.service_data.variables.color == 'blue' }}"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.your_light
            data:
              color_name: blue
          - service: twitch_control.send_message
            data:
              message: "💙 The lights are now BLUE!"
      - conditions: []
        sequence:
          - service: twitch_control.send_message
            data:
              message: "⚠️ Currently not supported"
```
    Replace light.your_light with your actual light entity ID.
    Now, when a Twitch chat command triggers the event, the light will change accordingly! 💡