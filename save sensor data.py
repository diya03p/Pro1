import serial
import csv

# Configure the serial connection
serial_port = 'COM6'  # Replace with your port (e.g., 'COM3' on Windows)
baud_rate = 9600  # Match the baud rate with your device
timeout = 1  # Time in seconds to wait for data

# Specify the CSV file name
csv_file = "serial_data1.csv"

try:
    # Initialize serial connection
    ser = serial.Serial(port=serial_port, baudrate=baud_rate, timeout=timeout)
    print(f"Connected to {serial_port} at {baud_rate} baud rate.")

    # Open the CSV file in write mode
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Value1", "Value2", "Value3", "Value4"])  # CSV headers

        print(f"Saving serial data to {csv_file}. Press Ctrl+C to stop.")

        while True:
            if ser.in_waiting > 0:  # Check if data is available to read
                data = ser.readline().decode('utf-8').strip()  # Read and decode the data
                print(f"Received: {data}")

                # Split the data into individual values and save them to the CSV file
                values = data.split(',')
                if len(values) == 4:  # Ensure the data has 4 columns as expected
                    writer.writerow(values)
except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("Exiting program. Data saved to CSV.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
