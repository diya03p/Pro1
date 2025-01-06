import serial

# Configure the serial connection
serial_port = 'COM4'  # Replace with your port (e.g., 'COM3' on Windows)
baud_rate = 9600  # Match the baud rate with your device
timeout = 1  # Time in seconds to wait for data

try:
    # Initialize serial connection
    ser = serial.Serial(port=serial_port, baudrate=baud_rate, timeout=timeout)
    print(f"Connected to {serial_port} at {baud_rate} baud rate.")

    while True:
        if ser.in_waiting > 0:  # Check if data is available to read
            data = ser.readline().decode('utf-8').strip()  # Read a line and decode it
            print(f"Received: {data}")
except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("Exiting program.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
