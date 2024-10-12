import pickle

left_knee_current_voltage = pickle.load(
    open("current_voltage.pkl", "rb")
)  # [(current, voltage), (current, voltage), ...]

import matplotlib.pyplot as plt

# Unpack current and voltage from the data
currents, voltages = zip(*left_knee_current_voltage)

fig, ax1 = plt.subplots()

# Plot current on the left y-axis
ax1.plot(currents, "b-", label="Current")
ax1.set_xlabel("Data Point Index")
ax1.set_ylabel("Current", color="b")

# Create a second y-axis for the voltage
ax2 = ax1.twinx()
ax2.plot(voltages, "r-", label="Voltage")
ax2.set_ylabel("Voltage", color="r")

plt.title("Current and Voltage Over Time")
plt.show()
