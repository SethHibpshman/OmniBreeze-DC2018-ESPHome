# ESPHome Config Explained

The full config file is at `esphome/omnibreeze-fan.yaml`. This page explains the key decisions and non-obvious parts.

---

## ADC Sensors

```yaml
sensor:
  - platform: adc
    pin: GPIO1
    id: ldr_speed1
    name: "LDR Speed 1 Raw"
    update_interval: 100ms
    attenuation: 12db
    filters:
      - sliding_window_moving_average:
          window_size: 5
          send_every: 1
```

- `attenuation: 12db` - sets ADC range to 0–3.3V. Previously `11db` (deprecated in ESPHome 2026.x, functionally identical)
- `window_size: 5` - averages 5 readings before publishing. Filters single-sample noise spikes without adding meaningful lag
- `send_every: 1` - publish after every averaged sample, giving ~100ms effective update rate
- `name` exposed for calibration - add `internal: true` once thresholds are tuned

---

## Binary Sensors

```yaml
binary_sensor:
  - platform: analog_threshold
    sensor_id: ldr_speed1
    id: led_speed1
    threshold: 0.15
    internal: true
```

Converts the analog ADC reading into a clean boolean. Threshold of 0.15V is above the ~0.10V off-state and below the ~0.20V+ on-state. `internal: true` keeps these out of HA - only the derived text sensors are exposed.

---

## IR Transmission

```yaml
remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%
  non_blocking: true
```

- `carrier_duty_percent: 50%` - essential. 100% is DC, the receiver won't decode it
- `non_blocking: true` - sends IR in the background, doesn't freeze the main loop

Each command uses `transmit_raw` with hand-encoded pulse arrays rather than `transmit_nec`, because ESPHome's NEC helper timing didn't match what this fan's receiver expects. See [IR Code Discovery](IR-Code-Discovery) for full explanation.

---

## Cyclic Command Scripts

Since the fan's buttons all cycle through states, ESPHome needs to know where the fan currently is and calculate how many presses to reach the target.

```yaml
script:
  - id: cycle_speed_to
    parameters:
      target: int
    then:
      - lambda: |-
          int current = 0;
          if (id(led_speed1).state) current = 1;
          else if (id(led_speed2).state) current = 2;
          else if (id(led_speed3).state) current = 3;
          else if (id(led_speed4).state) current = 4;
          if (current == 0 || current == target) return;
          int presses = (target - current + 4) % 4;
          for (int i = 0; i < presses; i++) {
            id(send_speed).execute();
            delay(300);
          }
```

The modulo math `(target - current + N) % N` handles wraparound correctly. For example, going from speed 4 to speed 1 is 1 press (not 3 backward).

The 300ms delay between presses gives the fan time to process each IR command and update its LEDs before the next press.

---

## Sleep Breeze Auto-Correction

The fan has three breeze modes (standard, natural, sleep) but sleep is never used intentionally. When sleep is detected via led_breeze3, the text sensor fires one more IR command to cycle the fan past sleep back to standard:

```yaml
  - platform: template
    name: "Fan Breeze Mode"
    id: fan_breeze
    lambda: |-
      if (id(led_breeze1).state) return std::string("standard");
      if (id(led_breeze2).state) return std::string("natural");
      if (id(led_breeze3).state) {
        id(send_breeze).execute();
        return std::string("standard");
      }
      return std::string("off");
    update_interval: 500ms
```

This fires within 500ms of sleep being detected. The breeze select in HA is also kept to only two options (standard, natural) so sleep can never be selected from HA either.

---

## Select Entity Sync

The breeze mode and timer select entities use `optimistic: true` so they update immediately in HA when selected. A 1-second interval then syncs them back from the actual LDR state, so physical button presses on the fan also update the dropdowns:

```yaml
interval:
  - interval: 1s
    then:
      - lambda: |-
          std::string breeze = "standard";
          if (id(led_breeze2).state) breeze = "natural";
          id(breeze_mode).publish_state(breeze);

          int hours = (id(led_timer1).state ? 1 : 0)
                    + (id(led_timer2).state ? 2 : 0)
                    + (id(led_timer3).state ? 4 : 0)
                    + (id(led_timer4).state ? 8 : 0);
          // ... string conversion ...
          id(fan_timer_select).publish_state(timer);
```

`publish_state()` on a select updates the displayed value without triggering `set_action`, so no IR commands are fired by the sync.

---

## Oscillation State

There is no LED for oscillation on this fan. Oscillation state is tracked in a global boolean that resets to `false` on reboot:

```yaml
globals:
  - id: oscillation_state
    type: bool
    restore_value: no
    initial_value: 'false'
```

If the fan is physically toggled while ESPHome is running, oscillation state will drift. The only fix would be a hardware modification to add a sensor.

---

## OLED Display

Font is Roboto Mono at size 9 - monospace prevents uneven character spacing, and size 9 fits three lines within the 32px display height with lines at y=0, 11, 22.

```yaml
display:
  - platform: ssd1306_i2c
    model: SSD1306_128X32
    address: 0x3c
    lambda: |-
      bool any_on = id(led_speed1).state || ...

      if (!any_on) {
        it.print(0, 0, id(font_main), "OmniBreeze");
        it.print(0, 11, id(font_main), "OFF");
        it.image(96, 0, id(fan_logo));
        return;
      }

      it.printf(0,  0, id(font_main), "Speed:  %s", speed.c_str());
      it.printf(0, 11, id(font_main), "Breeze: %s", breeze.c_str());
      it.printf(0, 22, id(font_main), "Timer:  %s", timer_str.c_str());
```

The logo image is placed at x=96 on the 128px wide display, sitting flush right with the 32px image.
