# LDR Wiring & Calibration

## Why LDRs?

All five buttons on the OmniBreeze DC2018 are cyclic - power toggles, speed cycles through 4 states, breeze mode cycles through 3, timer cycles through 16. Sending IR commands alone gives no feedback about what state the fan is actually in.

The fan's control panel has 11 indicator LEDs that show the current state. Rather than soldering to the SMD PCB (difficult and risky), LDRs are physically placed against each LED and read by the ESP32's ADC. This gives accurate real-time state without touching the fan's electronics.

---

## LED Map

| LED | State it represents |
|---|---|
| Speed 1 | Ultra-quiet |
| Speed 2 | Low |
| Speed 3 | Med |
| Speed 4 | High |
| Breeze 1 | Standard |
| Breeze 2 | Natural |
| Breeze 3 | Sleep |
| Timer 1h | Binary bit 1 |
| Timer 2h | Binary bit 2 |
| Timer 4h | Binary bit 3 |
| Timer 8h | Binary bit 4 |

### Timer Binary Encoding

The four timer LEDs combine as binary to represent values 1–15:

| Hours | 8h LED | 4h LED | 2h LED | 1h LED |
|---|---|---|---|---|
| 1h | off | off | off | on |
| 2h | off | off | on | off |
| 3h | off | off | on | on |
| 4h | off | on | off | off |
| ... | | | | |
| 15h | on | on | on | on |
| off | off | off | off | off |

---

## Wiring Each LDR

```
3.3V ──[LDR]──┬── GPIO pin
               │
            [10kΩ]
               │
             GND
```

The LDR and 10kΩ resistor form a voltage divider. As light increases, LDR resistance drops, and the GPIO voltage rises.

---

## Measured Voltage Values

| State | Voltage |
|---|---|
| LED off (all) | 0.05 – 0.10V |
| LED on (most) | >0.20V |
| Breeze 1 (weakest) | 0.21 – 0.22V |

**Threshold used: 0.15V** - safely above the off noise floor and below the minimum on value.

---

## ESPHome ADC Config

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

- `attenuation: 12db` sets the ADC input range to 0–3.3V
- `window_size: 5` averages 5 samples to filter electrical noise - fast enough for LED detection, smooth enough to prevent false triggers
- Removing `internal: true` temporarily exposes raw values in HA for calibration

```yaml
binary_sensor:
  - platform: analog_threshold
    sensor_id: ldr_speed1
    id: led_speed1
    threshold: 0.15
    internal: true
```

---

## Calibration Process

1. Remove `internal: true` from the sensor you want to calibrate
2. Flash the device
3. In HA → Developer Tools → States, watch the raw ADC value
4. Record the voltage with the LED **off** and **on**
5. Set threshold to halfway between the two values
6. Re-add `internal: true` when done

---

## Blue LED Challenge

The fan's indicator LEDs are blue. Standard GL5528 LDRs are most sensitive to green/yellow light (~560nm peak) and significantly less responsive to blue (~470nm). This means the on-state voltage is lower than it would be with a green LED, leaving less margin above the noise floor.

The fix is:
- Position the LDR flush against the LED with no gap
- Use heatshrink tubing over each LDR to block ambient light and prevent crosstalk from neighboring LEDs
- Use a lower threshold (0.15V rather than the typical 0.5V default)

---

## Crosstalk: Sleep Breeze vs Timer 1h

The sleep breeze LED (Breeze 3) and the 1h timer LED are physically adjacent on the control panel. Both LDRs read nearly identical voltages regardless of which LED is actually lit - the light from one bleeds into the other's LDR.

**Measured voltages in each scenario:**

| Scenario | Breeze 3 LDR | Timer 1h LDR |
|---|---|---|
| Sleep breeze on, no timer | 0.35–0.40V | 0.35–0.40V |
| Timer 1h on, no sleep breeze | 0.21–0.29V | 0.21–0.30V |
| Both on | 0.51–0.58V | 0.51–0.58V |

The voltages are indistinguishable - a hardware fix (physical separation or light baffle) is the proper solution.

**Software workaround:** Since sleep breeze mode is never intentionally used, Breeze 3's threshold is kept enabled (at 0.15V), but the `fan_breeze` text sensor fires an auto-corrective IR command whenever sleep is detected, cycling the fan past sleep back to standard. The `interval` sync block ignores Breeze 3 entirely when reporting breeze state to HA.

---

## 3D Printed LDR Frame

Rather than hot-gluing LDRs directly to the PCB or the panel surface, a custom two-part 3D printed system was designed:

- **LDR frame** - slots that hold each LDR at the correct position and angle to sit flush against its LED
- **Top shell** - snaps over the frame, covers the wiring, and provides a mount for the SSD1306 OLED

See [3D Model Design & Printing](3D-Models) for full details.
