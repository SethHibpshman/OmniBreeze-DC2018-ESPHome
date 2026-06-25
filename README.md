# OmniBreeze-DC2018-ESPHome

> Retrofitting a tower fan with ESP32, IR control, and LDR state feedback for full Home Assistant integration.

---

## What Is This?

The OmniBreeze DC2018 is a 40" tower fan. Out of the box it has no smart home capability, only a physical remote and control panel. This project adds full Home Assistant integration with real-time state feedback, voice control, and a custom OLED display without modifying the fan's original electronics.

Unlike most IR integrations, this project reads the fan's actual state and reports it back to Home Assistant. Speed, breeze mode, and timer status are monitored in real time using light-dependent resistors (LDRs) positioned over the fan's indicator LEDs. Home Assistant always reflects the fan's current state, whether it was changed from Home Assistant, the physical control panel, or the original remote.

## Features

- **Full IR control:** power, speed, breeze mode, oscillation, and timer
- **Real-time state reading:** 11 LDRs monitor the fan's LEDs and report actual state back to Home Assistant
- **Home Assistant fan entity:** speed, oscillation, breeze mode, and timer exposed as native entities
- **Auto sleep-mode correction:** ESPHome detects unintended sleep-mode transitions and automatically restores the selected mode
- **Custom OLED display:** 128×32 SSD1306 display showing speed, breeze mode, and timer status, plus a logo when the fan is off
- **Custom 3D printed mount:** LDR frame and OLED enclosure designed in Autodesk Fusion and printed in PLA

---

## How It Works

### IR Control
The fan's IR protocol was discovered by brute-forcing NEC address and command combinations with a MicroPython script running on the ESP32. Once the five valid commands were identified, they were recreated in ESPHome using raw pulse timing that matched the working MicroPython implementation.

### State Feedback via LDRs
Every button on the fan cycles through multiple states, so command tracking alone cannot reliably determine the current operating mode. Eleven LDRs sit directly over the fan's indicator LEDs and are monitored by the ESP32's ADC. Threshold-based binary sensors convert the analog readings into clean on/off states for each indicator.

### 3D Printed Housing
A two-part enclosure was designed in Autodesk Fusion:
- **LDR frame:** positions all 11 LDRs directly over their corresponding LEDs
- **Top shell:** covers the frame and provides a mounting point for the SSD1306 OLED display
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

<table>
<tr>
<td align="center">
<img src="../../wiki/assets/smart_fan_shroud_bottom.jpg" width="320"><br>
LDR Frame Interior
</td>
<td align="center">
<img src="../../wiki/assets/front_panel_insides.jpg" width="320"><br>
Front Panel Interior
</td>
</tr>

<tr>
<td align="center">
<img src="../../wiki/assets/smart_fan_shroud_top_fusion.png" width="320"><br>
Fusion 360 Top Cover Design
</td>
<td align="center">
<img src="../../wiki/assets/front_cover.jpg" width="320"><br>
Printed Front Cover
</td>
</tr>

<tr>
<td align="center">
<img src="../../wiki/assets/fan_overview.jpg" width="320"><br>
Fan Internals
</td>
<td align="center">
<img src="../../wiki/assets/fan_wiring.jpg" width="320"><br>
Voltage Dividers & ESP Wiring
</td>
</tr>

<tr>
<td colspan="2" align="center">
<img src="../../wiki/assets/ha_card.png" width="560" alt="Home Assistant Dashboard"><br>
Home Assistant Dashboard Card
</td>
</tr>
</table>

---

## Repository Structure

```
OmniBreeze-DC2018-ESPHome/
├── firmware/
│   ├── esphome/omnibreeze-fan.yaml       # Full ESPHome config
│   └── micropython_ir_scraping/          # Micropython tools used to scrape IR commands
├── hardware/
│   ├── 3d_models/                 # 3D models of all printed parts
│   └── esp32-s3_n16r8/            # ESP module specific files
├── reference material/            # Datasheets for fan & linear power regulator on board
└── README.md
```

---

## What I Learned

**IR protocol reverse engineering is not always clean.** The ESPHome transmit_nec helper did not work with this fan because the generated timing differed from what the receiver expected. Switching to raw pulse arrays solved the issue. Matching the 9000µs header, 4500µs gap, and 560/1690µs bit timing produced reliable operation.

**Analog state detection is harder than it sounds.** Blue LEDs produced weaker responses from the LDRs than green or yellow LEDs. Two adjacent indicators, sleep breeze mode and the 1-hour timer LED, also created enough light leakage to generate nearly identical readings. A software rule resolves the ambiguity: when both sensors read high, the state is treated as a timer indicator rather than sleep mode.

**ESPHome's feedback loop problem is real.** Synchronizing the template fan entity with hardware sensor feedback without triggering command callbacks required several iterations. The final solution uses a one-second interval that updates the entity's internal state through publish_state().

**Power supply research matters.** The fan contains a KP3310DP offline AC-DC regulator capable of providing 5V output. Datasheet review suggested it could power the ESP32 internally, but testing showed the 138mA current limit could not handle Wi-Fi transmission spikes. Brownout resets occurred regularly, so the ESP32 was moved to a dedicated USB power supply.

---

## What I Would Do Differently

The ESP32 is currently powered through a USB cable routed outside the fan, requiring a second wall outlet. A small isolated AC-DC module such as the HLK-PM01 could be installed internally and power both the fan controller and ESP32 from a single plug. Testing showed the KP3310DP was not suitable for this role, but the HLK-PM01 would provide a straightforward solution.

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


## Author

**Seth Hibpshman**  
Student of Electrical Engineering, Eastern Washington University

## AI Disclosure
_AI (LLM) tools were used for quality assurance review of the firmware and in the drafting and editing of this README and wiki documentation; all code was written by hand._

## License

[GNU General Public License v3.0](LICENSE)
