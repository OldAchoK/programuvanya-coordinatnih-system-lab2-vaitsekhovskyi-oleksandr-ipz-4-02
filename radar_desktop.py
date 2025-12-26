import json
import threading
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import websocket
import requests
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

history_r = deque(maxlen=1)
history_theta = deque(maxlen=1)
history_sizes = deque(maxlen=1)


def on_message(ws, message):
    try:
        data = json.loads(message)
        angle_rad = np.deg2rad(data['scanAngle'])
        echoes = data.get('echoResponses', [])

        r_list, t_list, s_list = [], [], []
        if echoes:
            for echo in echoes:
                dist = (300000 * echo['time']) / 2
                r_list.append(dist)
                t_list.append(angle_rad)
                s_list.append(echo['power'] * 800)

            history_r.append(r_list)
            history_theta.append(t_list)
            history_sizes.append(s_list)
            print(f"{r_list[0]:.2f} km", flush=True)
    except Exception:
        pass


def run_ws():
    ws = websocket.WebSocketApp("ws://localhost:4000", on_message=on_message)
    ws.run_forever()


def update_config():
    url = "http://localhost:4000/config"
    try:
        zone_size = int(entries["emulationZoneSize"].get())
        ax.set_ylim(0, zone_size)

        payload = {
            "measurementsPerRotation": int(entries["measurementsPerRotation"].get()),
            "rotationSpeed": int(entries["rotationSpeed"].get()),
            "beamWidth": float(entries["beamWidth"].get()),
            "pulseDuration": float(entries["pulseDuration"].get()),
            "sensitivity": float(entries["sensitivity"].get()),
            "numberOfTargets": int(entries["numberOfTargets"].get()),
            "targetSpeed": int(entries["targetSpeed"].get()),
            "emulationZoneSize": zone_size,
            "transmitPower": float(entries["transmitPower"].get()),
            "antennaGain": float(entries["antennaGain"].get())
        }
        requests.put(url, json=payload, timeout=2)
    except Exception as e:
        print(f"Error: {e}")


root = tk.Tk()
root.title("Radar Monitor")

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.grid(True, color='gray', alpha=0.3)
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_ylim(0, 200)

scatter = ax.scatter([0], [0], c='black', s=[0], edgecolors='none', zorder=10)

canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(main_frame, padding="10")
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

params = [
    ("Measurements", "measurementsPerRotation", "360"),
    ("Rotation Speed", "rotationSpeed", "60"),
    ("Beam Width", "beamWidth", "1"),
    ("Pulse Duration", "pulseDuration", "1"),
    ("Sensitivity", "sensitivity", "-70"),
    ("Targets Count", "numberOfTargets", "1"),
    ("Target Speed", "targetSpeed", "500"),
    ("Zone Size", "emulationZoneSize", "200"),
    ("Transmit Power", "transmitPower", "1"),
    ("Antenna Gain", "antennaGain", "33")
]

entries = {}
for label_text, key, default in params:
    ttk.Label(control_frame, text=label_text).pack(fill=tk.X)
    ent = ttk.Entry(control_frame)
    ent.insert(0, default)
    ent.pack(fill=tk.X, pady=(0, 5))
    entries[key] = ent

ttk.Button(control_frame, text="Update Config", command=update_config).pack(fill=tk.X, pady=10)


def animate():
    if history_r and len(history_r[0]) > 0:
        coords = np.column_stack((history_theta[0], history_r[0]))
        scatter.set_offsets(coords)
        scatter.set_sizes(history_sizes[0])
    else:
        scatter.set_offsets(np.empty((0, 2)))

    canvas.draw_idle()
    root.after(20, animate)


threading.Thread(target=run_ws, daemon=True).start()
animate()
root.mainloop()