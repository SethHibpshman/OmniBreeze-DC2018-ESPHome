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
            print(f"addr={hex(addr)} cmd={hex(cmd)}")  # newline each time = full history
            nec_send(addr, cmd)
            time.sleep_ms(1000)
        
        print(f"=== FINISHED ADDRESS {hex(addr)} ===")
        input("Note any hits, then press Enter for next address...")

brute_force()