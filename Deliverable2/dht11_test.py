import RPi.GPIO as GPIO
import time
import sys

class DHT11:
    def __init__(self, pin):
        self.pin = pin
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
        except Exception as e:
            print(f"GPIO initialization failed: {str(e)}")
            sys.exit(1)
        
    def read(self):
        try:
            # Initialize variables
            data = []
            
            # Send start signal
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.05)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(0.02)
            
            # Switch to input with pull-up
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Wait for sensor response with timeout
            if not self._wait_for_level(GPIO.HIGH, 0.1):
                print("Timeout waiting for sensor response (HIGH)")
                return None, None
            if not self._wait_for_level(GPIO.LOW, 0.1):
                print("Timeout waiting for sensor response (LOW)")
                return None, None
            if not self._wait_for_level(GPIO.HIGH, 0.1):
                print("Timeout waiting for sensor response (HIGH)")
                return None, None
            
            # Read 40 bits
            for _ in range(40):
                if not self._wait_for_level(GPIO.LOW, 0.1):
                    print("Timeout waiting for bit start")
                    return None, None
                
                start = time.time()
                if not self._wait_for_level(GPIO.HIGH, 0.1):
                    print("Timeout waiting for bit end")
                    return None, None
                duration = time.time() - start
                
                data.append(1 if duration > 0.00005 else 0)
            
            # Parse data
            bytes = []
            for i in range(5):
                byte = 0
                for j in range(8):
                    byte <<= 1
                    byte |= data[i*8 + j]
                bytes.append(byte)
            
            # Verify checksum
            if (bytes[0] + bytes[1] + bytes[2] + bytes[3]) & 0xff != bytes[4]:
                print("Checksum error")
                return None, None
            
            humidity = bytes[0] + bytes[1] * 0.1
            temperature = bytes[2] + bytes[3] * 0.1
            
            return temperature, humidity
            
        except Exception as e:
            print(f"Error during read: {str(e)}")
            return None, None
    
    def _wait_for_level(self, level, timeout):
        start = time.time()
        while GPIO.input(self.pin) != level:
            if time.time() - start > timeout:
                return False
            time.sleep(0.001)
        return True

if __name__ == "__main__":
    try:
        print("DHT11 Temperature/Humidity Test")
        print("Press Ctrl+C to exit")
        
        sensor = DHT11(4)  # Using GPIO4 (pin 7)
        
        while True:
            temp, hum = sensor.read()
            if temp is not None and hum is not None:
                print(f"Temperature: {temp:.1f}°C, Humidity: {hum:.1f}%")
            else:
                print("Read failed - check wiring and try again")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        GPIO.cleanup()