# OmniBreeze-DC2018-ESPHome

> Retrofitting a dumb tower fan with ESP32, IR control, and LDR state feedback for full Home Assistant integration.

**By [SethHibpshman](https://github.com/SethHibpshman)**

---

## What Is This?

The OmniBreeze DC2018 is a 40" tower fan sold at Costco. Out of the box it has no smart home capability - just a physical remote and a control panel. This project gives it full Home Assistant integration with real-time state feedback, voice control, and a custom OLED display, all without modifying the fan's original electronics.

This is not just a "send an IR command and hope for the best" project. The fan's actual state - speed, breeze mode, timer - is read back in real time using light-dependent resistors (LDRs) placed against the fan's own indicator LEDs. What Home Assistant shows always reflects what the fan is actually doing, regardless of whether it was controlled by HA, the physical buttons, or the original remote.

---

## Demo

> 📹 [Watch the full feature walkthrough video](#) *(link your video here)*

---

## Features

- **Full IR control** - power, speed, breeze mode, oscillation, and timer all sent via IR
- **Real-time state reading** - 11 LDRs read the fan's own LEDs to report actual state back to HA
- **Home Assistant fan entity** - speed, oscillation, breeze mode, and timer all exposed as native HA entities
- **Auto sleep-mode correction** - if the fan cycles into sleep breeze mode, ESPHome detects it and corrects it automatically
- **Custom OLED display** - 128x32 SSD1306 shows speed, breeze mode, and timer status with a logo on the off screen
- **Custom 3D printed mount** - LDR frame and OLED shell designed in Autodesk Fusion, printed in PLA

---

## How It Works

### IR Control
The fan's IR protocol was discovered by brute-forcing NEC address/command combinations with a MicroPython script on the ESP32. Once the five working commands were found, they were re-implemented in ESPHome using raw pulse timing to exactly match the working MicroPython implementation.

### State Feedback via LDRs
Because every button on the fan cycles (power toggles, speed cycles through 4, breeze cycles through 3, timer cycles through 16 steps), there is no way to know the fan's state from commands alone. Eleven LDRs are positioned directly against the fan's indicator LEDs and read by the ESP32's ADC. Binary sensors with threshold detection convert the analog voltage into clean on/off state for each indicator.

### 3D Printed Housing
A two-part 3D printed system was designed from scratch in Autodesk Fusion:
- **LDR frame** - holds all 11 LDRs precisely against their corresponding LEDs on the control panel
- **Top shell** - covers the frame and provides a mount for the SSD1306 OLED display

Both parts were printed in PLA on an Elegoo Neptune 3 Pro.

---

## Hardware

| Component | Details |
|---|---|
| Microcontroller | ESP32-S3 dev board |
| IR transmitter | 3-pin IR LED module (VCC, GND, DATA) |
| LDRs | GL5528 × 11 |
| Resistors | 10kΩ × 11 (voltage dividers) |
| Display | SSD1306 128×32 OLED (I2C) |
| Fan | OmniBreeze DC2018 40" Tower Fan |
| Power | USB (external) |

---

## Photos

> *(Add your photos here - suggested structure below)*

| | |
|---|---|
| ![Fan internals](images/internals.jpg) | ![LDR frame installed](images/ldr_frame.jpg) |
| ![Build progress](images/build_progress.jpg) | ![Finished fan](images/finished.jpg) |
| ![HA dashboard](images/dashboard.jpg) | ![OLED display](images/oled.jpg) |

---

## Repository Structure

```
OmniBreeze-DC2018-ESPHome/
├── esphome/
│   ├── omnibreeze-fan.yaml       # Full ESPHome config
│   └── sh_logo.png               # OLED logo image
├── micropython/
│   └── ir_brute_force.py         # IR discovery script
├── home-assistant/
│   └── dashboard-card.yaml       # Lovelace card config
├── 3d-models/
│   ├── ldr-frame.stl             # LDR holder
│   └── oled-shell.stl            # Top cover with OLED mount
├── images/                       # Project photos
└── README.md
```

---

## What I Learned

**IR protocol reverse engineering is not always clean.** The ESPHome `transmit_nec` helper didn't work with this fan - the bit timing didn't match. The fix was switching to raw pulse arrays hand-encoded from the working MicroPython implementation. Getting the exact 9000µs header, 4500µs gap, and 560/1690µs bit timings right made the difference.

**Analog state detection is harder than it sounds.** Blue LEDs are less sensitive to standard LDRs than green or yellow light. Two physically adjacent LEDs (sleep breeze and the 1h timer) caused crosstalk that made both sensors read identically - indistinguishable in voltage alone. The fix was a software rule: if both are high, assume timer, never sleep.

**ESPHome's feedback loop problem is real.** Syncing a template fan entity's displayed state back from hardware sensors without triggering the send callbacks took several iterations. The final working approach was a 1-second interval writing directly to the entity's internal state variables via `publish_state()`.

**Power supply research matters.** The fan contains a KP3310DP offline AC-DC regulator IC capable of 5V output. After researching the datasheet, it seemed like a clean internal power source for the ESP32 - but the 138mA current limit couldn't handle the ESP32's WiFi transmit spikes, causing brownout resets. The ESP32 ended up on a separate USB power supply.

---

## What I Would Do Differently

The ESP32 is powered by a USB cable that exits the fan, meaning two wall plugs are used total - one for the fan, one for the ESP32. Ideally a small isolated AC-DC module like the HLK-PM01 (5V/600mA, fully isolated from mains) would be wired internally to power everything from a single plug. The KP3310 research showed it wasn't viable for this, but the HLK-PM01 is a $3 drop-in solution that would clean this up completely.

---

## Wiki

Deep-dive documentation is in the [GitHub Wiki](../../wiki):

- [Hardware Overview & Wiring](../../wiki/Hardware-Overview)
- [IR Code Discovery](../../wiki/IR-Code-Discovery)
- [LDR Wiring & Calibration](../../wiki/LDR-Wiring-and-Calibration)
- [3D Model Design & Printing](../../wiki/3D-Models)
- [ESPHome Config Explained](../../wiki/ESPHome-Config)
- [Home Assistant Setup](../../wiki/Home-Assistant-Setup)
- [Troubleshooting](../../wiki/Troubleshooting)

---

## Built With

- [ESPHome](https://esphome.io/)
- [Home Assistant](https://www.home-assistant.io/)
- [Autodesk Fusion](https://www.autodesk.com/products/fusion-360/)
- [Elegoo Neptune 3 Pro](https://www.elegoo.com/)
- MicroPython (for IR discovery)
