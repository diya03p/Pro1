import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Load the CSV file
file_path = "data.csv"  # Replace with your CSV file path
df = pd.read_csv(file_path)

# Display the first few rows of the dataset
print("Dataset Head:")
print(df.head())

# Encode the target variable
label_encoder = LabelEncoder()
df['Earthquake'] = label_encoder.fit_transform(df['Earthquake'])

# **EDA: Correlation Heatmap**
plt.figure(figsize=(8, 6))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.show()

# **EDA: Feature Distributions**
df[['acc_x', 'acc_y', 'acc_z', 'vib']].hist(bins=20, figsize=(10, 8))
plt.suptitle("Feature Distributions")
plt.show()

# Feature and target separation
X = df[['acc_x', 'acc_y', 'acc_z', 'vib']].values
y = df['Earthquake'].values

# Normalize features
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Reshape input data for LSTM
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# **LSTM Model**
model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=10, batch_size=4, validation_data=(X_test, y_test), verbose=1)

# Model Evaluation
_, accuracy = model.evaluate(X_test, y_test)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# **Plot Training History**
plt.figure(figsize=(12, 5))

# Loss plot
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title("Loss Over Epochs")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()

# Accuracy plot
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title("Accuracy Over Epochs")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()

plt.show()

# **Predictions vs Actual**
y_pred = model.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype(int).flatten()

plt.figure(figsize=(10, 6))
plt.scatter(range(len(y_test)), y_test, color='blue', label='True Values')
plt.scatter(range(len(y_pred_classes)), y_pred_classes, color='red', label='Predicted Values', alpha=0.5)
plt.title("Predictions vs True Values")
plt.legend()
plt.show()

# Save the trained LSTM model to an H5 file
model.save("lstm_model.h5")
print("LSTM model has been saved as 'lstm_model.h5'.")
