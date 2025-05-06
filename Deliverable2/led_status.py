from gpiozero import LED

led = LED(6)

def led_is_on():
    return led.value == 1
