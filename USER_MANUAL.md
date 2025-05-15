# 🧊 BBQ Cooler Monitoring System – User Manual

---

## 📦 1. What This System Does

This system monitors your cooler and helps you enjoy your drinks in your preferred conditions.

It tracks:
- Temperature
- Humidity
- Whether the lid is open or closed

It also gives alerts using lights and sound, and sends the data to the cloud (AWS).

---

## ⚙️ 2. How to Start the App

### On the Raspberry Pi:
1. Connect all sensors and actuators **based on the pin mappings** shown in the code (`main.py`).
2. Open a terminal.
3. Run:
   ```bash
   python3 main.py
   ```
4. The app window will open with live data.

### Optional: View from another device
Use **RealVNC Viewer** on your laptop to connect to the Pi’s desktop.

---

## 🔍 3. What You See on Screen

| Display Item         | Meaning                                  |
|----------------------|------------------------------------------|
| **Temperature**      | Current cooler temperature (°C)          |
| **Humidity**         | Current air moisture (%)                 |
| **Door Status**      | "OPEN" if lid is open, "CLOSED" if shut  |
| **Red Alert Box**    | Warning if temperature is too high/low   |
| **Lid Status Message** | Extra message for lid open/closed       |

---

## 🛠️ 4. How to Set Temperature & Humidity Limits

1. Click the **"Set Thresholds"** button.
2. A popup will appear.
3. Change:
   - Max / Min Temperature
   - Max / Min Humidity
4. Click **Apply**.
5. The app will now use your new limits to trigger alerts.

---

## ❄️ 5. Manual Cool Mode

> 🚧 **Note:** This feature is **not yet implemented**.

The button is present for future use. Eventually, it will let you simulate or trigger the cooling manually.

---

## 🔔 6. Alerts and Warnings

| Condition                        | What Happens                  |
|----------------------------------|-------------------------------|
| Temp too high / low              | Red alert box appears         |
| Lid opened                       | Bell icon + buzzer beeps      |
| Data changes                     | Sent to AWS cloud automatically |

---

## ☁️ 7. Cloud Integration (AWS)

Every 2 seconds, the system sends this data to the cloud:
- Temperature
- Humidity
- Lid status (open or closed)
- Whether LED or buzzer is active

Data is stored in **AWS DynamoDB** under topic:
```
twahidi/device/37/data
```

---

## 🔐 8. Security Sequence (Coming Soon)

A special button combo or passcode can be added to lock settings or access logs. Not implemented yet.

---

## 🛠️ 9. Troubleshooting

| Issue                              | Fix                                   |
|------------------------------------|----------------------------------------|
| "Humidity error" or "--%"          | Wait or restart – sensor may retry     |
| No window appears                  | Make sure you're running on desktop Pi |
| Black screen in VNC                | Use HDMI or enable fake display mode   |