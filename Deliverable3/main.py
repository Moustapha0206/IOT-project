
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder

Window.size = (450, 550)

Builder.load_file("gui.kv")

class CoolerMonitorScreen(BoxLayout):
    pass

class CoolerApp(App):
    def build(self):
        return CoolerMonitorScreen()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import os
import glob
import time
import board
import adafruit_dht
from gpiozero import DistanceSensor, LED, Buzzer
from gpiozero.exc import DistanceSensorNoEcho
from threading import Thread

# Set window size
Window.size = (450, 550)

# Load KV layout
Builder.load_file("gui.kv")

# DS18B20 Setup
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# DHT11 on GPIO17
dht_device = adafruit_dht.DHT11(board.D17)

# Ultrasonic Sensor Setup
lid_sensor = DistanceSensor(echo=21, trigger=20, max_distance=1, queue_len=1)

# Actuators
status_led = LED(18)
buzzer = Buzzer(22)

def read_temp():
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            with open(device_file, 'r') as f:
                lines = f.readlines()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            return float(lines[1][equals_pos + 2:]) / 1000.0
    except Exception as e:
        print("âŒ Temperature read error:", e)
    return 0

class CoolerMonitorScreen(BoxLayout):
    temp_label_text = StringProperty("--Â°C")
    humidity_label_text = StringProperty("--%")
    temp_label_color = ListProperty([1, 1, 1, 1])
    temp_high_alert_visible = BooleanProperty(0)
    temp_message = StringProperty("")
    door_status_text = StringProperty("UNKNOWN")
    lid_status_message = StringProperty("")
    manual_cool_message = StringProperty("")
    header_text = StringProperty("")
    button_threshold_text = StringProperty("")
    button_manual_cool_text = StringProperty("")

    max_temp_threshold = NumericProperty(30)
    min_temp_threshold = NumericProperty(20)
    max_humidity_threshold = NumericProperty(70)
    min_humidity_threshold = NumericProperty(40)

    manual_cool_active = BooleanProperty(False)

    translations = {
        "en": {
            "temp_normal": "Temperature is normal.",
            "temp_high": "TEMPERATURE TOO HIGH",
            "temp_low": "TEMPERATURE TOO LOW",
            "lid_closed": "Cooler lid is closed",
            "lid_open": "Cooler lid is open",
            "lid_unknown": "Cooler lid status unknown",
            "manual_cool": "Manual Cool Mode Active",
            "language_button": "Language: FR / EN",
            "header": "BBQ Cooler Monitoring System",
            "set_thresholds": "Set Thresholds",
            "manual_cool_btn": "Manual Cool Mode"
        },
        "fr": {
            "temp_normal": "TempÃ©rature normale.",
            "temp_high": "TEMPÃ‰RATURE TROP Ã‰LEVÃ‰E",
            "temp_low": "TEMPÃ‰RATURE TROP BASSE",
            "lid_closed": "Couvercle fermÃ©",
            "lid_open": "Couvercle ouvert",
            "lid_unknown": "Ã‰tat du couvercle inconnu",
            "manual_cool": "Mode Refroidissement Manuel Actif",
            "language_button": "Langue : EN / FR",
            "header": "SystÃ¨me de surveillance du rÃ©frigÃ©rateur",
            "set_thresholds": "DÃ©finir les seuils",
            "manual_cool_btn": "Mode de refroidissement manuel"
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = "en"
        self.prev_lid_status = None
        self.lid_distance = None
        self.load_thresholds()
        self.update_translations()
        Clock.schedule_interval(self.update_sensors, 2)
        Thread(target=self.lid_distance_loop, daemon=True).start()

    def lid_distance_loop(self):
        while True:
            try:
                dist = lid_sensor.distance * 100
                self.lid_distance = round(dist, 2)
            except DistanceSensorNoEcho:
                self.lid_distance = None
            except Exception as e:
                print("âŒ Distance thread error:", e)
                self.lid_distance = None
            time.sleep(1)

    def update_translations(self):
        t = self.translations[self.language]
        self.temp_message = t["temp_normal"]
        self.lid_status_message = t["lid_unknown"]
        self.manual_cool_message = ""
        self.header_text = t["header"]
        self.button_threshold_text = t["set_thresholds"]
        self.button_manual_cool_text = t["manual_cool_btn"]
        if hasattr(self, "ids") and "language_btn" in self.ids:
            self.ids.language_btn.text = t["language_button"]

    def toggle_language(self):
        self.language = "fr" if self.language == "en" else "en"
        self.update_translations()

    def update_sensors(self, dt):
        t = self.translations[self.language]
        temperature = read_temp()
        self.temp_label_text = f"{temperature:.2f}Â°C"
        if temperature > self.max_temp_threshold:
            self.temp_label_color = [1, 0, 0, 1]
            self.temp_high_alert_visible = True
            self.temp_message = t["temp_high"]
        elif temperature < self.min_temp_threshold:
            self.temp_label_color = [0, 0, 1, 1]
            self.temp_high_alert_visible = True
            self.temp_message = t["temp_low"]
        else:
            self.temp_label_color = [1, 1, 1, 1]
            self.temp_high_alert_visible = False
            self.temp_message = t["temp_normal"]

        humidity = None
        try:
            humidity = dht_device.humidity
            if humidity is not None:
                self.humidity_label_text = f"{humidity:.0f}%"
            else:
                self.humidity_label_text = "--%"
        except RuntimeError:
            self.humidity_label_text = "--%"
        except Exception as e:
            print("âŒ Humidity error:", e)
            self.humidity_label_text = "--%"

        try:
            distance = self.lid_distance
            if distance is None:
                self.door_status_text = "UNKNOWN"
                self.lid_status_message = t["lid_unknown"]
            else:
                new_status = "CLOSED" if distance < 10 else "OPEN"
                if new_status != self.prev_lid_status:
                    buzzer.on()
                    Clock.schedule_once(lambda dt: buzzer.off(), 0.1)
                    self.prev_lid_status = new_status
                self.door_status_text = new_status
                self.lid_status_message = (
                    t["lid_closed"] if new_status == "CLOSED" else t["lid_open"]
                )
        except Exception as e:
            print("âŒ Lid logic error:", e)
            self.door_status_text = "UNKNOWN"
            self.lid_status_message = t["lid_unknown"]

        try:
            if self.manual_cool_active:
                status_led.on()
                return
            ideal_temp = self.min_temp_threshold <= temperature <= self.max_temp_threshold
            ideal_humidity = humidity is not None and self.min_humidity_threshold <= humidity <= self.max_humidity_threshold
            if ideal_temp and ideal_humidity:
                status_led.on()
            else:
                status_led.off()
        except Exception as e:
            print("âŒ LED control error:", e)
            status_led.off()

    def toggle_manual_cool(self):
        t = self.translations[self.language]
        if not self.manual_cool_active:
            self.manual_cool_active = True
            self.manual_cool_message = t["manual_cool"]
            status_led.on()
            Clock.schedule_once(self.deactivate_manual_cool, 5)
        else:
            self.deactivate_manual_cool()

    def deactivate_manual_cool(self, *args):
        self.manual_cool_active = False
        self.manual_cool_message = ""
        status_led.off()

    def open_threshold_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        def labeled_input(label_text, default_value, unit):
            row = BoxLayout(orientation='horizontal', spacing=5)
            input_field = TextInput(text=str(default_value), input_filter='float', multiline=False)
            row.add_widget(Label(text=label_text))
            row.add_widget(input_field)
            row.add_widget(Label(text=unit))
            return row, input_field

        tmax_row, temp_max_input = labeled_input("Max Temp", self.max_temp_threshold, "Â°C")
        tmin_row, temp_min_input = labeled_input("Min Temp", self.min_temp_threshold, "Â°C")
        hmax_row, humidity_max_input = labeled_input("Max Humidity", self.max_humidity_threshold, "%")
        hmin_row, humidity_min_input = labeled_input("Min Humidity", self.min_humidity_threshold, "%")

        def apply_changes(instance):
            try:
                t_max = float(temp_max_input.text)
                t_min = float(temp_min_input.text)
                h_max = float(humidity_max_input.text)
                h_min = float(humidity_min_input.text)

                if t_min > t_max or h_min > h_max:
                    Popup(title="Error", content=Label(text="Min must be less than Max"), size_hint=(0.7, 0.3)).open()
                    return

                self.max_temp_threshold = t_max
                self.min_temp_threshold = t_min
                self.max_humidity_threshold = h_max
                self.min_humidity_threshold = h_min

                with open("thresholds.cfg", "w") as f:
                    f.write(f"min_temp={t_min}\nmax_temp={t_max}\nmin_humidity={h_min}\nmax_humidity={h_max}\n")

                popup.dismiss()
            except ValueError:
                Popup(title="Error", content=Label(text="Enter valid numbers"), size_hint=(0.7, 0.3)).open()

        layout.add_widget(Label(text="Set Thresholds", bold=True))
        layout.add_widget(tmax_row)
        layout.add_widget(tmin_row)
        layout.add_widget(hmax_row)
        layout.add_widget(hmin_row)
        layout.add_widget(Button(text="Apply", on_release=apply_changes))

        popup = Popup(title="Set Alert Thresholds", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def load_thresholds(self):
        try:
            if os.path.exists("thresholds.cfg"):
                with open("thresholds.cfg", "r") as f:
                    for line in f:
                        if "=" in line:
                            key, val = line.strip().split("=")
                            if key == "min_temp": self.min_temp_threshold = float(val)
                            elif key == "max_temp": self.max_temp_threshold = float(val)
                            elif key == "min_humidity": self.min_humidity_threshold = float(val)
                            elif key == "max_humidity": self.max_humidity_threshold = float(val)
        except Exception as e:
            print("Could not load thresholds:", e)

class CoolerApp(App):
    def build(self):
        return CoolerMonitorScreen()

if __name__ == '__main__':
    CoolerApp().run()


if __name__ == '__main__':
    CoolerApp().run()
