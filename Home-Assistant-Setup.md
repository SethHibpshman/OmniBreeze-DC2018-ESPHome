# Home Assistant Setup

## Adding the Device

1. Flash `omnibreeze-fan.yaml` to the ESP32 via USB first time
2. In Home Assistant go to **Settings → Devices & Services → ESPHome**
3. The device should appear automatically - click **Configure** and enter the API encryption key from your config
4. All entities will be imported automatically

---

## Entities Created

| Entity type | Name | Purpose |
|---|---|---|
| Text sensor | Fan Power | on/off state from LDRs |
| Text sensor | Fan Speed | ultra-quiet/low/med/high from LDRs |
| Text sensor | Fan Breeze Mode | standard/natural from LDRs |
| Text sensor | Fan Timer | current timer value from LDRs |
| Select | Breeze Mode | set breeze mode (cycles IR to target) |
| Select | Fan Timer | set timer (cycles IR to target) |
| Button | Fan Power Toggle | sends power IR command |
| Button | Fan Speed Cycle | sends one speed IR command |
| Button | Fan Breeze Mode Cycle | sends one breeze IR command |
| Button | Fan Oscillation Toggle | sends oscillation IR command |
| Button | Fan Timer Cycle | sends one timer IR command |

---

## Dashboard Card

Requires: **Mushroom Cards**, **Stack-in-Card**, **Card Mod** (all from HACS Frontend)

```yaml
type: custom:stack-in-card
mode: vertical
card_mod:
  style: |
    ha-card {
      padding: 12px;
      gap: 8px;
    }
cards:
  - type: custom:mushroom-title-card
    title: OmniBreeze Fan
    subtitle: >
      {{ states('sensor.omnibreeze_fan_fan_speed') | title }}
      {%- if states('sensor.omnibreeze_fan_fan_breeze_mode') != 'off' %} · {{
      states('sensor.omnibreeze_fan_fan_breeze_mode') | title }}{% endif %}
      {%- if states('sensor.omnibreeze_fan_fan_timer') != 'off' %} · {{
      states('sensor.omnibreeze_fan_fan_timer') }}{% endif %}
    card_mod:
      style: |
        ha-card { padding: 0 4px; }

  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: select.seth_s_bedroom_omnibreeze_fan_breeze_mode
        name: Breeze
        icon: mdi:weather-windy
        fill_container: true
        card_mod:
          style: |
            ha-card {
              border-radius: 12px !important;
              margin-right: 4px;
            }
      - type: custom:mushroom-entity-card
        entity: select.seth_s_bedroom_omnibreeze_fan_fan_timer
        name: Timer
        icon: mdi:timer-sand-empty
        fill_container: true
        card_mod:
          style: |
            ha-card {
              border-radius: 12px !important;
              margin-left: 4px;
            }

  - type: custom:mushroom-chips-card
    alignment: center
    card_mod:
      style: |
        ha-card { padding: 4px 0 0 0; }
    chips:
      - type: template
        icon: mdi:power
        icon_color: >-
          {{ 'red' if states('sensor.omnibreeze_fan_fan_power') == 'on' else 'grey' }}
        content: Power
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.omnibreeze_fan_fan_power_toggle
      - type: template
        icon: mdi:speedometer
        content: Speed
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.omnibreeze_fan_fan_speed_cycle
      - type: template
        icon: mdi:arrow-oscillating
        content: Oscillate
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.omnibreeze_fan_fan_oscillation_toggle
```

> **Note:** Replace entity IDs with your own. Check yours in HA under Settings → Devices → OmniBreeze Fan.

---

## Automations

Because there is no fan entity (removed due to feedback loop issues), automations use the button and select entities directly.

### Turn fan off at midnight

```yaml
alias: Turn OmniBreeze off at midnight
trigger:
  - platform: time
    at: "00:00:00"
condition:
  - condition: state
    entity_id: sensor.omnibreeze_fan_fan_power
    state: "on"
action:
  - service: button.press
    target:
      entity_id: button.omnibreeze_fan_fan_power_toggle
```

### Set fan to low speed at bedtime

```yaml
alias: OmniBreeze bedtime mode
trigger:
  - platform: time
    at: "22:30:00"
action:
  - service: select.select_option
    target:
      entity_id: select.seth_s_bedroom_omnibreeze_fan_breeze_mode
    data:
      option: natural
  - service: select.select_option
    target:
      entity_id: select.seth_s_bedroom_omnibreeze_fan_fan_timer
    data:
      option: "8h"
```

---

## Notes

- **Speed** cannot be set directly to a specific value from HA automations without knowing the current speed. Use the cycle button entity in a script that reads the current speed text sensor and calculates presses - or just press Speed until HA reports the desired value
- **Oscillation** state can drift if toggled physically while HA is not watching. It resets to off on ESP32 reboot
- **Timer** counts down on the fan itself - ESPHome reads the LED state, not a countdown. The select shows what the fan is currently set to, not time remaining
