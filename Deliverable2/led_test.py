from gpiozero import LED
from time import sleep

# Initialize LED - change the pin number to match your connection
led = LED(6)  # Using GPIO6 as example

print("Testing LED module")
print("LED will blink 5 times")

try:
    for _ in range(5):
        led.on()
        print("LED ON")
        sleep(1)
        led.off()
        print("LED OFF")
        sleep(1)
        
    print("LED test completed successfully")
except KeyboardInterrupt:
    print("\nTest stopped by user")
finally:
    led.off()  # Ensure LED is turned off