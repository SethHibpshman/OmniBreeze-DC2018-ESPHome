# Hardware Overview & Wiring

## Components

| Component | Model | Purpose |
|---|---|---|
| Microcontroller | ESP32-S3 dev board | Main controller |
| IR transmitter | 3-pin module (VCC/GND/DATA) | Send IR commands to fan |
| LDRs | GL5528 × 11 | Read fan LED states |
| Resistors | 10kΩ × 11 | Voltage dividers for LDRs |
| Display | SSD1306 128×32 I2C | Status display |
| Fan | OmniBreeze DC2018 | Target hardware |

---

## GPIO Pin Assignments

| GPIO | Function |
|---|---|
| GPIO4 | IR transmitter DATA |
| GPIO1 | LDR - Speed 1 (ultra-quiet) |
| GPIO2 | LDR - Speed 2 (low) |
| GPIO3 | LDR - Speed 3 (med) |
| GPIO8 | LDR - Speed 4 (high) |
| GPIO9 | LDR - Breeze 1 (standard) |
| GPIO10 | LDR - Breeze 2 (natural) |
| GPIO11 | LDR - Breeze 3 (sleep) |
| GPIO12 | LDR - Timer 1h |
| GPIO13 | LDR - Timer 2h |
| GPIO14 | LDR - Timer 4h |
| GPIO17 | LDR - Timer 8h |
| GPIO18 | SSD1306 SCL |
| GPIO21 | SSD1306 SDA |

> **Note:** GPIO3 is a strapping pin on the ESP32-S3. It works fine here but ESPHome will warn about it. It was kept to avoid rewiring.

---

## LDR Voltage Divider Circuit

Each of the 11 LDRs uses the same circuit:

```
3.3V ──[LDR]──┬── GPIO pin
               │
            [10kΩ]
               │
             GND
```

When the LED is **off**: LDR resistance is high (~1MΩ), GPIO reads ~0.05–0.10V

When the LED is **on**: LDR resistance drops (~10–20kΩ), GPIO reads ~0.20–0.40V

The threshold in ESPHome is set to **0.15V** - comfortably above the off-state noise floor and below the on-state minimum.

---

## IR Transmitter

The IR module has three pins: VCC, GND, and DATA. It is a raw LED module with a transistor driver - the 38kHz carrier is generated in software by ESPHome's remote_transmitter component.

```
Module VCC  → 3.3V
Module GND  → GND
Module DATA → GPIO4
```

Point the module at the IR receiver window on the front of the fan. Optimal distance is 20–50cm. Too close can overload the receiver.

---

## SSD1306 OLED

Standard I2C wiring:

```
OLED VCC → 3.3V
OLED GND → GND
OLED SDA → GPIO21
OLED SCL → GPIO18
```

Default I2C address is `0x3C`. If the display is blank after flashing, try `0x3D`.

---

## Power

The ESP32 is powered via USB from a separate wall plug. The fan's internal KP3310DP AC-DC regulator IC was investigated as a potential internal power source (it outputs 5V and is on the control board), but its 138mA current limit cannot sustain the ESP32's WiFi transmit spikes, which caused brownout resets.

For a single-plug solution, a **HLK-PM01** (5V/600mA isolated AC-DC module, ~$3) wired to mains inside the fan would be the correct approach.

---

## Fan PCB Notes

The OmniBreeze DC2018 control board contains:

- **KP3310DP** - offline AC-DC linear regulator (Kiwi Instruments), powers the control logic. Connects directly to mains - do not touch pins 6, 7, 8.
- **Unmarked IC** - the actual fan controller handling buttons, LEDs, and motor speed
- **X2 safety capacitor** - mains EMI suppression, ignore entirely
- All buttons and LEDs are SMD - direct soldering is difficult. The 3D printed LDR frame is used instead of soldering to read LED states.
