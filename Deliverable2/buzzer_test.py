from gpiozero import Buzzer
from time import sleep

# Initialize buzzer - change the pin number to match your connection
buzzer = Buzzer(27)  # Using GPIO18 as example

print("Testing Active Buzzer module")
print("Buzzer will beep 3 times")

try:
    for _ in range(3):
        buzzer.on()
        print("Buzzer ON")
        sleep(0.5)
        buzzer.off()
        print("Buzzer OFF")
        sleep(0.5)
        
    print("Buzzer test completed successfully")
except KeyboardInterrupt:
    print("\nTest stopped by user")
finally:
    buzzer.off()  # Ensure buzzer is turned off