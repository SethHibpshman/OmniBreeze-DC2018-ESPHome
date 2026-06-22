# IR Code Discovery

## The Problem

The OmniBreeze DC2018 came without its original remote. Without a remote, there was no way to capture existing IR codes with a receiver. The fan needed to be brute-forced.

---

## Brute Force Approach

The NEC IR protocol (most common in Chinese appliances) uses an 8-bit address and an 8-bit command - 256 possible commands per address, and up to 256 addresses. That's 65,536 combinations total, but in practice the address space for consumer devices is small.

A MicroPython script was written to systematically send every command in a given address block, one at a time, while watching the fan for a response.

### MicroPython IR Brute Force Script

```python
from machine import Pin, PWM
import time

pwm = PWM(Pin(4), freq=38000, duty=0)

def mark(duration_us):
    pwm.duty(512)
    time.sleep_us(duration_us)

def space(duration_us):
    pwm.duty(0)
    time.sleep_us(duration_us)

def nec_send(address, command):
    mark(9000)
    space(4500)
    for byte in [address, (~address) & 0xFF, command, (~command) & 0xFF]:
        for i in range(8):
            mark(560)
            space(1690 if byte & (1 << i) else 560)
    mark(560)
    space(40000)

def brute_force():
    addresses = [0x00, 0x01, 0x02, 0xFF, 0xFE, 0x10, 0x20]
    for addr in addresses:
        print(f"\n=== STARTING ADDRESS {hex(addr)} ===")
        input("Press Enter to start...")
        for cmd in range(256):
            print(f"addr={hex(addr)} cmd={hex(cmd)}")
            nec_send(addr, cmd)
            time.sleep_ms(300)
        input("\nDone. Press Enter for next address...")

brute_force()
```

The script prints every address/command pair it sends to serial. When the fan responded, the last printed line revealed the working command. All five commands were found within address `0x00`.

---

## Discovered IR Commands

| Function | Address | Command |
|---|---|---|
| Power toggle | `0x00` | `0x1A` |
| Speed cycle | `0x00` | `0x01` |
| Breeze mode cycle | `0x00` | `0x09` |
| Oscillation toggle | `0x00` | `0x03` |
| Timer cycle | `0x00` | `0x07` |

---

## Why ESPHome's `transmit_nec` Didn't Work

After moving to ESPHome, the NEC helper action (`remote_transmitter.transmit_nec`) was tried first. The fan did not respond. The issue was that ESPHome's NEC implementation uses slightly different bit timing or byte ordering than what the fan's receiver expects.

The fix was switching to `transmit_raw` with pulse arrays hand-encoded to exactly match the working MicroPython timing:

- Header: 9000µs mark, 4500µs space
- Bit 1: 560µs mark, 1690µs space  
- Bit 0: 560µs mark, 560µs space
- Stop bit: 560µs mark
- Frame gap: 40000µs space
- Byte order: address, ~address, command, ~command (LSB first)

### Example - Power Command (`0x1A`)

```yaml
- remote_transmitter.transmit_raw:
    carrier_frequency: 38000Hz
    code: [9000, -4500, 560, -560, 560, -560, 560, -560, 560, -560, 560, -560, 560, -560, 560, -560, 560, -560, 560, -1690, 560, -1690, 560, -1690, 560, -1690, 560, -1690, 560, -1690, 560, -1690, 560, -1690, 560, -560, 560, -1690, 560, -560, 560, -1690, 560, -1690, 560, -560, 560, -560, 560, -560, 560, -1690, 560, -560, 560, -1690, 560, -560, 560, -560, 560, -1690, 560, -1690, 560, -1690, 560, -40000]
```

Positive values are marks (IR on), negative values are spaces (IR off), in microseconds.

---

## IR Transmitter Tips

- The carrier frequency must be 50% duty cycle (`carrier_duty_percent: 50%`) - 100% is DC, not modulated, and the fan's receiver won't decode it
- Set `non_blocking: true` on the remote_transmitter component in ESPHome to avoid freezing the main loop during transmission
- Point the module directly at the receiver window on the front of the fan
- Optimal range is 20–50cm - too close can overload the receiver
