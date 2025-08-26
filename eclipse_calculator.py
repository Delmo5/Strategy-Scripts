import tkinter as tk
from tkinter import ttk

# --- Car parameters ---
m = 240       # kg
cr = 0.006    # rolling resistance coefficient
af = 0.914    # frontal area (m^2)
cd = 0.12     # drag coefficient
rho = 1.2     # air density (kg/m^3)

def ploss(v_kmh: float) -> float:
    v_ms = v_kmh / 3.6
    rolling = cr * m * 9.81 * v_ms
    drag = 0.5 * rho * v_ms**2 * af * cd * v_ms
    return rolling + drag  # Watts

def time_to_hours(hours_entry, minutes_entry):
    """Convert hours + minutes entries to decimal hours."""
    try:
        hours = float(hours_entry.get())
    except ValueError:
        hours = 0
    try:
        minutes = float(minutes_entry.get())
    except ValueError:
        minutes = 0
    return hours + minutes / 60

def calculate_time(event=None):
    try:
        dist = float(dist_entry1.get())
        target_speed = float(speed_entry.get())
        current_soc = float(soc_entry1.get())
        solar_power = float(solar_entry1.get())

        time_h = dist / target_speed
        total_loss = ploss(target_speed)
        total_gain = solar_power
        net = total_gain - total_loss
        arrival_soc = current_soc + time_h * net

        hours = int(time_h)
        minutes = int((time_h - hours) * 60)

        results1.set(
            f"Total loss: -{total_loss:.1f} W\n"
            f"Total gain: {total_gain:.1f} W\n"
            f"Net gain/loss: {net:.1f} W\n"
            f"Time to arrival: {hours}h {minutes}m\n"
            f"SOC at arrival: {arrival_soc:.2f} Wh"
        )
    except ValueError:
        results1.set("Please enter valid numbers.")

def calculate_speed(event=None):
    try:
        dist = float(dist_entry2.get())
        arrival_time_h = time_to_hours(hours_entry2, minutes_entry2)
        current_soc = float(soc_entry2.get())
        solar_power = float(solar_entry2.get())

        if arrival_time_h <= 0:
            results2.set("Arrival time must be positive.")
            return

        req_speed = dist / arrival_time_h
        total_loss = ploss(req_speed)
        total_gain = solar_power
        net = total_gain - total_loss
        arrival_soc = current_soc + arrival_time_h * net

        results2.set(
            f"Total loss: -{total_loss:.1f} W\n"
            f"Total gain: {total_gain:.1f} W\n"
            f"Net gain/loss: {net:.1f} W\n"
            f"Required speed: {req_speed:.2f} km/h\n"
            f"SOC at arrival: {arrival_soc:.2f} Wh"
        )
    except ValueError:
        results2.set("Please enter valid numbers.")

def calculate_distance(event=None):
    try:
        speed = float(speed_entry3.get())
        travel_time_h = time_to_hours(hours_entry3, minutes_entry3)
        current_soc = float(soc_entry3.get())
        solar_power = float(solar_entry3.get())

        distance = speed * travel_time_h
        total_loss = ploss(speed)
        total_gain = solar_power
        net = total_gain - total_loss
        arrival_soc = current_soc + travel_time_h * net

        results3.set(
            f"Total loss: -{total_loss:.1f} W\n"
            f"Total gain: {total_gain:.1f} W\n"
            f"Distance traveled: {distance:.2f} km\n"
            f"SOC at arrival: {arrival_soc:.2f} Wh"
        )
    except ValueError:
        results3.set("Please enter valid numbers.")

def calculate_required_speed(event=None):
    try:
        target_soc = float(target_soc_entry.get())
        current_soc = float(current_soc_entry.get())
        solar_power = float(solar_entry4.get())
        distance = float(dist_entry4.get())

        distance_m = distance * 1000
        energy_to_use = current_soc - target_soc  # Wh

        required_speed = None
        required_time = None
        total_loss = None
        total_gain = None

        for speed in range(5, 150):  # search 5–150 km/h
            v_ms = speed / 3.6
            time_h = distance / speed  # h

            loss = ploss(speed) * time_h
            gain = solar_power * time_h
            net_used = loss - gain

            if abs(net_used - energy_to_use) < 50:  # within 50 Wh
                required_speed = speed
                required_time = time_h
                total_loss = loss
                total_gain = gain
                break

        if required_speed:
            hours = int(required_time)
            minutes = int((required_time - hours) * 60)
            results4.set(
                f"Total loss: -{total_loss:.0f} Wh\n"
                f"Total gain: {total_gain:.0f} Wh\n"
                f"Net gain/loss: {total_loss - total_gain:.0f} Wh\n"
                f"Required speed: {required_speed:.1f} km/h\n"
                f"Time to arrival: {hours}h {minutes}m"
            )
        else:
            results4.set("No feasible speed found in range")
    except ValueError:
        results4.set("Please enter valid numbers.")

# --- UI ---
root = tk.Tk()
root.title("Solar Car Energy Calculator")

notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

# --- Calculator 1: Time from speed ---
frame1 = ttk.Frame(notebook, padding="12")
notebook.add(frame1, text="Arrival Time from Speed")

ttk.Label(frame1, text="Distance to travel (km):").grid(column=0, row=0, sticky=tk.W)
dist_entry1 = ttk.Entry(frame1); dist_entry1.grid(column=1, row=0); dist_entry1.insert(0, "100")

ttk.Label(frame1, text="Target speed (km/h):").grid(column=0, row=1, sticky=tk.W)
speed_entry = ttk.Entry(frame1); speed_entry.grid(column=1, row=1); speed_entry.insert(0, "100")

ttk.Label(frame1, text="Current SOC (Wh):").grid(column=0, row=2, sticky=tk.W)
soc_entry1 = ttk.Entry(frame1); soc_entry1.grid(column=1, row=2); soc_entry1.insert(0, "3000")

ttk.Label(frame1, text="Mean solar power (W):").grid(column=0, row=3, sticky=tk.W)
solar_entry1 = ttk.Entry(frame1); solar_entry1.grid(column=1, row=3); solar_entry1.insert(0, "500")

ttk.Button(frame1, text="Calculate", command=calculate_time).grid(column=0, row=4, columnspan=2, pady=8)
results1 = tk.StringVar()
ttk.Label(frame1, textvariable=results1, justify="left").grid(column=0, row=5, columnspan=2, sticky=tk.W)

# --- Calculator 2: Speed from arrival time ---
frame2 = ttk.Frame(notebook, padding="12")
notebook.add(frame2, text="Required Speed from Time")

ttk.Label(frame2, text="Distance to travel (km):").grid(column=0, row=0, sticky=tk.W)
dist_entry2 = ttk.Entry(frame2); dist_entry2.grid(column=1, row=0); dist_entry2.insert(0, "100")

ttk.Label(frame2, text="Arrival time (hours):").grid(column=0, row=1, sticky=tk.W)
hours_entry2 = ttk.Entry(frame2, width=5); hours_entry2.grid(column=1, row=1, sticky=tk.W); hours_entry2.insert(0, "1")
ttk.Label(frame2, text="minutes:").grid(column=1, row=1, padx=(50,0), sticky=tk.W)
minutes_entry2 = ttk.Entry(frame2, width=5); minutes_entry2.grid(column=1, row=1, padx=(100,0), sticky=tk.W); minutes_entry2.insert(0, "0")

ttk.Label(frame2, text="Current SOC (Wh):").grid(column=0, row=2, sticky=tk.W)
soc_entry2 = ttk.Entry(frame2); soc_entry2.grid(column=1, row=2); soc_entry2.insert(0, "3000")

ttk.Label(frame2, text="Mean solar power (W):").grid(column=0, row=3, sticky=tk.W)
solar_entry2 = ttk.Entry(frame2); solar_entry2.grid(column=1, row=3); solar_entry2.insert(0, "500")

ttk.Button(frame2, text="Calculate", command=calculate_speed).grid(column=0, row=4, columnspan=2, pady=8)
results2 = tk.StringVar()
ttk.Label(frame2, textvariable=results2, justify="left").grid(column=0, row=5, columnspan=2, sticky=tk.W)

# --- Calculator 3: Distance from speed and time ---
frame3 = ttk.Frame(notebook, padding="12")
notebook.add(frame3, text="Distance from Speed & Time")

ttk.Label(frame3, text="Speed (km/h):").grid(column=0, row=0, sticky=tk.W)
speed_entry3 = ttk.Entry(frame3); speed_entry3.grid(column=1, row=0); speed_entry3.insert(0, "100")

ttk.Label(frame3, text="Travel time (hours):").grid(column=0, row=1, sticky=tk.W)
hours_entry3 = ttk.Entry(frame3, width=5); hours_entry3.grid(column=1, row=1, sticky=tk.W); hours_entry3.insert(0, "1")
ttk.Label(frame3, text="minutes:").grid(column=1, row=1, padx=(50,0), sticky=tk.W)
minutes_entry3 = ttk.Entry(frame3, width=5); minutes_entry3.grid(column=1, row=1, padx=(100,0), sticky=tk.W); minutes_entry3.insert(0, "0")

ttk.Label(frame3, text="Current SOC (Wh):").grid(column=0, row=2, sticky=tk.W)
soc_entry3 = ttk.Entry(frame3); soc_entry3.grid(column=1, row=2); soc_entry3.insert(0, "3000")

ttk.Label(frame3, text="Mean solar power (W):").grid(column=0, row=3, sticky=tk.W)
solar_entry3 = ttk.Entry(frame3); solar_entry3.grid(column=1, row=3); solar_entry3.insert(0, "500")

ttk.Button(frame3, text="Calculate", command=calculate_distance).grid(column=0, row=4, columnspan=2, pady=8)
results3 = tk.StringVar()
ttk.Label(frame3, textvariable=results3, justify="left").grid(column=0, row=5, columnspan=2, sticky=tk.W)

# --- Calculator 4: Required speed from target SOC ---
frame4 = ttk.Frame(notebook, padding="12")
notebook.add(frame4, text="Required Speed from Target SOC")

ttk.Label(frame4, text="Distance to travel (km):").grid(column=0, row=0, sticky=tk.W)
dist_entry4 = ttk.Entry(frame4); dist_entry4.grid(column=1, row=0); dist_entry4.insert(0, "100")

ttk.Label(frame4, text="Current SOC (Wh):").grid(column=0, row=1, sticky=tk.W)
current_soc_entry = ttk.Entry(frame4); current_soc_entry.grid(column=1, row=1); current_soc_entry.insert(0, "3000")

ttk.Label(frame4, text="Target SOC at arrival (Wh):").grid(column=0, row=2, sticky=tk.W)
target_soc_entry = ttk.Entry(frame4); target_soc_entry.grid(column=1, row=2); target_soc_entry.insert(0, "2000")

ttk.Label(frame4, text="Mean solar power (W):").grid(column=0, row=3, sticky=tk.W)
solar_entry4 = ttk.Entry(frame4); solar_entry4.grid(column=1, row=3); solar_entry4.insert(0, "500")

ttk.Button(frame4, text="Calculate", command=calculate_required_speed).grid(column=0, row=4, columnspan=2, pady=8)
results4 = tk.StringVar()
ttk.Label(frame4, textvariable=results4, justify="left").grid(column=0, row=5, columnspan=2, sticky=tk.W)

root.mainloop()
