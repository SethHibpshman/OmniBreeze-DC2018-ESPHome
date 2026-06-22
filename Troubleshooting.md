# Troubleshooting

## IR Commands Not Working

**Fan doesn't respond to any IR command**
- Check `carrier_duty_percent: 50%` is set - 100% produces DC, not a modulated signal
- Check `non_blocking: true` is set on the remote_transmitter
- Point the IR module directly at the receiver window on the front panel
- Try 30–50cm distance - too close can overload the receiver
- Confirm the IR module is a raw LED type, not a modulated receiver module (they look similar)

**Some commands work, some don't**
- The raw pulse arrays are command-specific - double check the correct code block is assigned to each script
- Verify `carrier_frequency: 38000Hz` is set on each `transmit_raw` action

---

## LDR States Flickering

**Binary sensor toggling rapidly**
- Threshold may be too close to the actual reading - check raw ADC values in HA Developer Tools → States
- Increase `window_size` in the sliding average filter to smooth more
- Check the LDR is flush against the LED with no gap - a loose LDR will pick up ambient light inconsistently
- Add hysteresis by using separate `upper` and `lower` threshold values:

```yaml
binary_sensor:
  - platform: analog_threshold
    sensor_id: ldr_speed1
    id: led_speed1
    threshold:
      upper: 0.18
      lower: 0.12
    internal: true
```

**All LDRs reading low even when LEDs are on**
- Blue LEDs produce less response from standard LDRs - lower threshold to 0.12 or 0.10
- Check wiring: 3.3V → LDR → GPIO + 10kΩ to GND (not reversed)
- Verify `attenuation: 12db` is set

---

## Two LEDs Showing Wrong State Together

This is LED crosstalk - a physically adjacent LDR is picking up light from a neighboring LED.

**Diagnosis:** Remove `internal: true` from both sensors and watch raw ADC values in HA. If both sensors rise when only one LED should be on, it's crosstalk.

**Fix options:**
1. Physical - wrap each LDR in black heatshrink tubing to limit its field of view
2. Software - add a mutual exclusion rule in the affected binary sensor or text sensor lambda
3. Disable one - if one state is never intentionally used, set its threshold to `99` so it can never trigger

---

## OLED Display Blank

- Try I2C address `0x3D` instead of `0x3C` - some SSD1306 modules ship with the alternate address
- Check SDA/SCL wiring (GPIO21/GPIO18)
- Verify 3.3V power to the display
- Add an I2C scan to your config temporarily to confirm the device is detected:

```yaml
i2c:
  sda: GPIO21
  scl: GPIO18
  scan: true
```

ESPHome will log all detected I2C addresses on boot.

---

## ESP32 Brownout Reset Loop

**Symptoms:** LEDs flash briefly then device resets, repeatedly

**Cause:** Boot current spike exceeds power supply limit

**Fixes:**
- Use a separate USB power supply with at least 500mA capacity - the fan's internal KP3310 regulator maxes at 138mA which is insufficient
- If you want internal power, use an HLK-PM01 (5V/600mA isolated AC-DC module) wired to mains inside the fan
- Add a 1000µF electrolytic capacitor across the 5V rail to absorb boot spikes

---

## OTA Upload Failing

**`No route to host` error**
- The device is likely in a reset loop and not staying online - flash via USB instead
- Check your router's DHCP table for the device's actual IP address - it may have changed
- Try pinging the device: `ping omnibreeze-fan.local`

**Device online but OTA still fails**
- Check firewall rules on your HA host aren't blocking port 3232
- Try from the ESPHome dashboard instead of the CLI

---

## Breeze Select Not Syncing After Physical Button Press

The interval sync runs every 1 second and reads the LDR binary sensors. If the select isn't updating:

- Confirm `led_breeze1` and `led_breeze2` thresholds are correct and the binary sensors are actually changing state
- Check the interval block is present in your config and not commented out
- Temporarily remove `internal: true` from the breeze sensors to verify they're reading correctly in HA

---

## Sleep Mode Keeps Activating

If the fan keeps cycling into sleep breeze mode when pressing the breeze button:

- Confirm `led_breeze3` threshold is `0.15` (not `99`) - it needs to detect sleep to trigger the auto-correction
- The `fan_breeze` text sensor lambda fires `send_breeze` when sleep is detected, cycling past it to standard - check this code is present and not overwritten
- There is a 500ms detection window - if the fan cycles through sleep very quickly, the correction may miss it and require a second cycle
