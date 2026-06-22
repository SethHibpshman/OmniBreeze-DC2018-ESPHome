# 3D Model Design & Printing

## Overview

Rather than hot-gluing components to the fan or running wires loosely inside, a two-part 3D printed system was designed from scratch to give the build a clean, intentional finish.

**Software:** Autodesk Fusion  
**Printer:** Elegoo Neptune 3 Pro  
**Material:** PLA

---

## Part 1 - LDR Frame

The LDR frame solves the problem of positioning 11 LDRs accurately against 11 SMD LEDs on the fan's control panel PCB.

**Design goals:**
- Hold each LDR at the exact position of its corresponding LED
- Keep each LDR flush against the LED surface with no gap (important for blue LEDs which have lower output)
- Prevent LDRs from shifting or rotating over time
- Allow wiring to route cleanly out of the back

**Design approach:**
- The control panel was measured and the LED positions mapped
- Individual slots were modeled for each LDR so they press-fit in and stay in place
- The frame sits on top of the control panel PCB and is held in place by the top shell

---

## Part 2 - Top Shell

The top shell snaps over the LDR frame and serves two purposes:

1. **Covers the LDR wiring** - keeps the inside of the fan tidy and prevents wires from catching on anything
2. **Mounts the SSD1306 OLED** - a cutout and mounting boss positions the display flush so it can be seen through the top of the fan housing

**Design goals:**
- Snap fit onto the LDR frame without screws
- OLED sits flush and square
- Wiring channel routes the OLED ribbon and LDR wires cleanly to the ESP32

---

## Print Settings

| Setting | Value |
|---|---|
| Material | PLA |
| Layer height | 0.2mm |
| Infill | 20% |
| Supports | No (designed to print without) |
| Printer | Elegoo Neptune 3 Pro |

---

## STL Files

STL files are in the `/3d-models/` directory of this repository:

- `ldr-frame.stl` - LDR holder frame
- `oled-shell.stl` - top cover with OLED mount

---

## Tips

- Print the LDR frame with the slot openings facing up to avoid support material inside the slots
- Test fit before gluing anything - the slots should grip the LDR legs with light press-fit pressure
- The top shell snap fit is designed with ~0.3mm clearance - if your printer runs tight, lightly sand the mating surfaces
