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

while True:
    try:
        addr = input("Address (hex e.g. 0x00): ")
        cmd  = input("Command (hex e.g. 0x01): ")
        
        addr = int(addr, 16)
        cmd  = int(cmd, 16)
        
        print(f"Sending addr={hex(addr)} cmd={hex(cmd)}")
        nec_send(addr, cmd)
        print("Sent!")
        
    except ValueError:
        print("Invalid input, use hex like 0x00")
    except KeyboardInterrupt:
        print("\nExiting")
        pwm.deinit()
        break