import serial
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Load the trained model
model_path = "lstm_model.h5"  # Path to the saved model
model = load_model(model_path)

# Configure the serial connections
read_port = 'COM3'  # Port for reading data
write_port = 'COM4'  # Port for writing data
baud_rate = 9600  # Match the baud rate with your devices
timeout = 1  # Time in seconds to wait for data

# Initialize the MinMaxScaler (same configuration as used during training)
scaler = MinMaxScaler(feature_range=(0, 1))

# Simulated scaling values (replace with the actual feature range from training data)
scaler.fit([[300, 340, 400, 90], [350, 360, 450, 100]])  # Adjust range based on training data

try:
    # Initialize serial connections
    ser_read = serial.Serial(port=read_port, baudrate=baud_rate, timeout=timeout)
    ser_write = serial.Serial(port=write_port, baudrate=baud_rate, timeout=timeout)
    print(f"Connected to {read_port} for reading and {write_port} for writing.")

    while True:
        if ser_read.in_waiting > 0:  # Check if data is available to read
            raw_data = ser_read.readline().decode('utf-8').strip()  # Read and decode the data
            print(f"Received: {raw_data}")

            # Process the data
            try:
                values = np.array([list(map(float, raw_data.split(',')))])  # Convert to float array
                if values.shape[1] == 4:  # Ensure there are 4 features
                    # Normalize the data
                    scaled_values = scaler.transform(values)

                    # Reshape the data for LSTM
                    reshaped_values = scaled_values.reshape(1, 4, 1)  # Batch size = 1, Time steps = 4, Features = 1

                    # Make prediction
                    prediction = model.predict(reshaped_values)

                    # Interpret the prediction and write to another port
                    if prediction[0][0] > 0.5:
                        output = "Earthquake"
                        print(f"Prediction: {output}")
                        ser_write.write(b'a')  # Send 'a' for Earthquake
                        print("Sent 'a' to write port.")
                    else:
                        output = "Normal"
                        print(f"Prediction: {output}")
                        ser_write.write(b'n')  # Send 'n' for Normal
                        print("Sent 'n' to write port.")
                else:
                    print("Invalid input dimensions.")
            except Exception as e:
                print(f"Error processing data: {e}")
except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("Exiting program.")
finally:
    # Close the serial connections
    if 'ser_read' in locals() and ser_read.is_open:
        ser_read.close()
        print("Read port closed.")
    if 'ser_write' in locals() and ser_write.is_open:
        ser_write.close()
        print("Write port closed.")
