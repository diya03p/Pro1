import tkinter as tk
from tkinter import ttk
import serial
import threading
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load the trained model
model_path = "lstm_model.h5"  # Path to the saved model
model = load_model(model_path)

# Configure the serial connection
serial_port = 'COM6'  # Replace with your port
baud_rate = 9600  # Match the baud rate with your device
timeout = 1  # Time in seconds to wait for data

# Initialize the MinMaxScaler (same configuration as used during training)
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit([[300, 340, 400, 90], [350, 360, 450, 100]])  # Simulated scaling values

# Data lists for plotting
acc_x_data, acc_y_data, acc_z_data, vib_data = [], [], [], []
running = False
prediction_output = "Normal"

# Serial reading function
def read_serial():
    global running, acc_x_data, acc_y_data, acc_z_data, vib_data, prediction_output
    try:
        ser = serial.Serial(port=serial_port, baudrate=baud_rate, timeout=timeout)
        print(f"Connected to {serial_port} at {baud_rate} baud rate.")
        while running:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8').strip()
                print(f"Received: {raw_data}")
                values = raw_data.split(',')
                if len(values) == 4:
                    try:
                        acc_x, acc_y, acc_z, vib = map(float, values)
                        acc_x_data.append(acc_x)
                        acc_y_data.append(acc_y)
                        acc_z_data.append(acc_z)
                        vib_data.append(vib)

                        # Keep only the last 50 points for visualization
                        acc_x_data, acc_y_data, acc_z_data, vib_data = (
                            acc_x_data[-50:], acc_y_data[-50:], acc_z_data[-50:], vib_data[-50:]
                        )

                        # Normalize and predict
                        scaled_values = scaler.transform([[acc_x, acc_y, acc_z, vib]])
                        reshaped_values = scaled_values.reshape(1, 4, 1)
                        prediction = model.predict(reshaped_values)
                        prediction_output = "Earthquake" if prediction[0][0] > 0.5 else "Normal"

                        # Update the UI
                        update_plot()
                        update_light(prediction_output)
                        update_prediction_label(prediction_output)
                    except Exception as e:
                        print(f"Error processing data: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()

# Function to start serial reading
def start_reading():
    global running
    if not running:
        running = True
        threading.Thread(target=read_serial, daemon=True).start()

# Function to stop serial reading
def stop_reading():
    global running
    running = False

# Function to update the plot
def update_plot():
    ax.clear()
    ax.set_title("Sensor Data", color="white")
    ax.set_xlabel("Time", color="white")
    ax.set_ylabel("Values", color="white")
    ax.plot(acc_x_data, label="Acc_X", color="red")
    ax.plot(acc_y_data, label="Acc_Y", color="blue")
    ax.plot(acc_z_data, label="Acc_Z", color="green")
    ax.plot(vib_data, label="Vibration", color="yellow")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_facecolor("black")
    ax.tick_params(colors="white")
    canvas.draw()

# Function to update the light indicator
def update_light(prediction):
    if prediction == "Earthquake":
        light_label.config(bg="red")
    else:
        light_label.config(bg="green")

# Function to update the prediction label
def update_prediction_label(prediction):
    prediction_label.config(text=f"Prediction: {prediction}")

# Create the GUI
root = tk.Tk()
root.title("Sensor Data Monitoring")
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

# Light Indicator
light_label = tk.Label(root, text=" ", width=5, height=2, bg="green")
light_label.pack(pady=10)

# Prediction Label
prediction_label = tk.Label(root, text="Prediction: Normal", font=("Helvetica", 14), bg="black", fg="white")
prediction_label.pack(pady=10)

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
