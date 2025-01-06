import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import threading
import time

# Configure serial connection
serial_port = 'COM6'  # Replace with your serial port
baud_rate = 9600  # Match the baud rate
timeout = 1  # Timeout for serial reading
running = False

# Data lists for plotting
acc_x_data, acc_y_data, acc_z_data, vib_data = [], [], [], []

# Initialize serial object
ser = None

# Function to read serial data
def read_serial():
    global running, acc_x_data, acc_y_data, acc_z_data, vib_data
    try:
        ser = serial.Serial(port=serial_port, baudrate=baud_rate, timeout=timeout)
        print(f"Connected to {serial_port} at {baud_rate} baud rate.")
        while running:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8').strip()
                print(f"Received: {raw_data}")
                values = raw_data.split(',')
                if len(values) == 4:
                    acc_x, acc_y, acc_z, vib = map(float, values)
                    acc_x_data.append(acc_x)
                    acc_y_data.append(acc_y)
                    acc_z_data.append(acc_z)
                    vib_data.append(vib)
                    update_plot()
            time.sleep(0.1)  # Small delay for smoother plotting
    except Exception as e:
        print(f"Error reading serial data: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()

# Function to start the data reading
def start_reading():
    global running
    if not running:
        running = True
        threading.Thread(target=read_serial, daemon=True).start()

# Function to stop the data reading
def stop_reading():
    global running
    running = False

# Function to update the plot
def update_plot():
    ax.clear()
    ax.set_title("Sensor Data", color="white")
    ax.set_xlabel("Time", color="white")
    ax.set_ylabel("Values", color="white")
    ax.plot(acc_x_data[-50:], label="Acc_X", color="red")
    ax.plot(acc_y_data[-50:], label="Acc_Y", color="blue")
    ax.plot(acc_z_data[-50:], label="Acc_Z", color="green")
    ax.plot(vib_data[-50:], label="Vibration", color="yellow")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_facecolor("black")
    ax.tick_params(colors="white")
    canvas.draw()

# Create the GUI
root = tk.Tk()
root.title("Accelerometer and Vibration Data")
root.configure(bg="black")

# Title Label
title_label = tk.Label(root, text="Sensor Data Monitoring", font=("Helvetica", 16), bg="black", fg="white")
title_label.pack(pady=10)

# Start and Stop Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

start_button = ttk.Button(button_frame, text="Start", command=start_reading)
start_button.grid(row=0, column=0, padx=5)

stop_button = ttk.Button(button_frame, text="Stop", command=stop_reading)
stop_button.grid(row=0, column=1, padx=5)

# Matplotlib figure for the plot
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_facecolor("black")
ax.tick_params(colors="white")
fig.patch.set_facecolor("black")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Run the GUI event loop
root.protocol("WM_DELETE_WINDOW", stop_reading)
root.mainloop()
