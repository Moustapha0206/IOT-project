from gpiozero import Buzzer

buzzer = Buzzer(27)

def buzzer_is_on():
    return buzzer.value == 1
