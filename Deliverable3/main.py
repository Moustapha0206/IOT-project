from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder

# Set fixed window size for the GUI
Window.size = (450, 550)

# Load KV layout file
Builder.load_file("gui.kv")

# Main layout for the app screen
class CoolerMonitorScreen(BoxLayout):
    pass

# Entry point for the Kivy application
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

# Set fixed window size again for consistency
Window.size = (450, 550)

# Load UI layout from KV file
Builder.load_file("gui.kv")

# Setup for DS18B20 temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# DHT11 sensor initialized on GPIO17
dht_device = adafruit_dht.DHT11(board.D17)

# Ultrasonic sensor for lid status detection (trigger: GPIO20, echo: GPIO21)
lid_sensor = DistanceSensor(echo=21, trigger=20, max_distance=1, queue_len=1)

# Output actuators
status_led = LED(18)
buzzer = Buzzer(22)

# Function to read and return temperature from DS18B20
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
        print("Temperature read error:", e)
    return 0

# Main app logic and screen controller
class CoolerMonitorScreen(BoxLayout):
    # UI-bound properties for dynamic updates
    temp_label_text = StringProperty("--°C")
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

    # Threshold values
    max_temp_threshold = NumericProperty(30)
    min_temp_threshold = NumericProperty(20)
    max_humidity_threshold = NumericProperty(70)
    min_humidity_threshold = NumericProperty(40)

    # Manual cooling state
    manual_cool_active = BooleanProperty(False)

    # Translations for multilingual UI
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
            "temp_normal": "Température normale.",
            "temp_high": "TEMPÉRATURE TROP ÉLEVÉE",
            "temp_low": "TEMPÉRATURE TROP BASSE",
            "lid_closed": "Couvercle fermé",
            "lid_open": "Couvercle ouvert",
            "lid_unknown": "État du couvercle inconnu",
            "manual_cool": "Mode Refroidissement Manuel Actif",
            "language_button": "Langue : EN / FR",
            "header": "Système de surveillance du réfrigérateur",
            "set_thresholds": "Définir les seuils",
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

    # Background loop to continuously read lid distance
    def lid_distance_loop(self):
        while True:
            try:
                dist = lid_sensor.distance * 100
                self.lid_distance = round(dist, 2)
            except DistanceSensorNoEcho:
                self.lid_distance = None
            except Exception as e:
                print(" Distance thread error:", e)
                self.lid_distance = None
            time.sleep(1)

    # Update text labels based on selected language
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

    # Toggle between English and French
    def toggle_language(self):
        self.language = "fr" if self.language == "en" else "en"
        self.update_translations()

    # Periodic update of temperature, humidity, lid status, and LED
    def update_sensors(self, dt):
        t = self.translations[self.language]
        temperature = read_temp()
        self.temp_label_text = f"{temperature:.2f}°C"
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

        # Read humidity from DHT11 sensor
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
            print("Humidity error:", e)
            self.humidity_label_text = "--%"

        # Check cooler lid status using distance reading
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
            print("Lid logic error:", e)
            self.door_status_text = "UNKNOWN"
            self.lid_status_message = t["lid_unknown"]

        # Control LED based on ideal conditions or manual override
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
            print("LED control error:", e)
            status_led.off()

    # Activate or deactivate manual cool mode
    def toggle_manual_cool(self):
        t = self.translations[self.language]
        if not self.manual_cool_active:
            self.manual_cool_active = True
            self.manual_cool_message = t["manual_cool"]
            status_led.on()
            Clock.schedule_once(self.deactivate_manual_cool, 5)
        else:
            self.deactivate_manual_cool()

    # Turn off manual cool mode after timeout or toggle
    def deactivate_manual_cool(self, *args):
        self.manual_cool_active = False
        self.manual_cool_message = ""
        status_led.off()

    # Popup window to change temperature/humidity thresholds
    def open_threshold_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Helper to create label input unit row
        def labeled_input(label_text, default_value, unit):
            row = BoxLayout(orientation='horizontal', spacing=5)
            input_field = TextInput(text=str(default_value), input_filter='float', multiline=False)
            row.add_widget(Label(text=label_text))
            row.add_widget(input_field)
            row.add_widget(Label(text=unit))
            return row, input_field

        # Create labeled input rows
        tmax_row, temp_max_input = labeled_input("Max Temp", self.max_temp_threshold, "°C")
        tmin_row, temp_min_input = labeled_input("Min Temp", self.min_temp_threshold, "°C")
        hmax_row, humidity_max_input = labeled_input("Max Humidity", self.max_humidity_threshold, "%")
        hmin_row, humidity_min_input = labeled_input("Min Humidity", self.min_humidity_threshold, "%")

        # Apply button logic to validate and save thresholds
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

        # Assemble popup layout
        layout.add_widget(Label(text="Set Thresholds", bold=True))
        layout.add_widget(tmax_row)
        layout.add_widget(tmin_row)
        layout.add_widget(hmax_row)
        layout.add_widget(hmin_row)
        layout.add_widget(Button(text="Apply", on_release=apply_changes))

        popup = Popup(title="Set Alert Thresholds", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    # Load threshold values from configuration file
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

# Application entry point
class CoolerApp(App):
    def build(self):
        return CoolerMonitorScreen()

# Start the application
if __name__ == '__main__':
    CoolerApp().run()


