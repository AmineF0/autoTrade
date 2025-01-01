import random
import time
import csv
from datetime import datetime
import numpy as np

# Define sensor codes and their descriptions
SENSOR_CODES = {
    "SMS-001": "Soil Moisture Sensors",
    "HML-002": "Heavy Metal Sensors (Lead)",
    "HMA-003": "Heavy Metal Sensors (Arsenic)",
    "HMM-004": "Heavy Metal Sensors (Mercury)",
    "NLS-005": "Noise Level Sensors",
    "HML-006": "Heavy Metal Sensors (Lead)",
    "HMA-007": "Heavy Metal Sensors (Arsenic)",
    "HMM-008": "Heavy Metal Sensors (Mercury)",
    "HML-009": "Heavy Metal Sensors (Lead)",
    "HMA-010": "Heavy Metal Sensors (Arsenic)",
    "HMM-011": "Heavy Metal Sensors (Mercury)",
    "OS-012": "Opacity Sensors",
    "PMS25-013": "Particulate Matter (PM2.5) Sensor",
    "PMS10-014": "Particulate Matter (PM10)",
    "CO2S-015": "Gas Sensor (CO₂)",
    "NOXS-016": "Gas Sensor (NOx)",
    "SO2S-017": "Gas Sensor (SO₂)",
    "O3S-018": "Gas Sensor (O₃)",
    "VOC-019": "Gas Sensor (VOC)",
    "PHS-006": "pH Sensors",
    "TS-007": "Turbidity Sensors",
    "DOS-008": "Dissolved Oxygen Sensors",
    "CS-009": "Conductivity Sensors",
    "AS-010": "Ammonia Sensors",
    "NS-011": "Nitrate Sensors",
    "HML-013": "Heavy Metal Sensors (Lead)",
    "HMA-014": "Heavy Metal Sensors (Arsenic)",
    "HMM-015": "Heavy Metal Sensors (Mercury)"
}


def get_next_value(last_value, sensor_code):
    """
    Generate the next value for a sensor based on the last value.
    Includes continuity and simulates anomalies and spikes.
    """
    if sensor_code.startswith("SMS"):
        # Soil Moisture Sensor
        next_value = max(0, min(100, last_value + random.uniform(-1, 1)))
        if random.random() < 0.05:
            next_value += random.uniform(10, 20)  # Spike
            next_value = min(next_value, 100)
        return round(next_value, 2)

    elif sensor_code.startswith(("HML", "HMA", "HMM")):
        # Heavy Metal Sensors
        base_value = last_value if last_value is not None else random.uniform(0, 0.01)
        variation = random.uniform(-0.001, 0.001)
        next_value = round(base_value + variation, 5)
        # Simulate spike anomaly
        if random.random() < 0.02:
            spike = random.uniform(0.01, 0.02)
            next_value += spike
        return max(0, next_value)

    elif sensor_code.startswith("NLS"):
        # Noise Level Sensors
        hour = datetime.now().hour
        base_noise = random.randint(60, 80) if 6 <= hour <= 22 else random.randint(30, 50)
        if last_value is not None:
            next_value = last_value + random.randint(-1, 1)
        else:
            next_value = base_noise
        if random.random() < 0.05:
            next_value += random.randint(10, 20)  # Spike
        return max(0, next_value)

    elif sensor_code.startswith("OS"):
        # Opacity Sensors
        base_value = last_value if last_value is not None else random.uniform(0, 100)
        next_value = base_value + random.uniform(-5, 5)
        if random.random() < 0.03:
            next_value += random.uniform(20, 30)  # Spike
        return max(0, min(round(next_value, 2), 100))

    elif sensor_code.startswith(("PMS25", "PMS10")):
        # Particulate Matter Sensors
        base_value = last_value if last_value is not None else random.uniform(0, 500)
        next_value = base_value + random.uniform(-10, 10)
        if random.random() < 0.05:
            next_value += random.uniform(50, 100)  # Spike
        return max(0, round(next_value, 2))

    elif sensor_code.startswith("CO2S"):
        # CO2 Sensor
        base_value = last_value if last_value is not None else random.uniform(300, 600)
        next_value = base_value + random.uniform(-5, 5)
        if random.random() < 0.05:
            next_value += random.uniform(50, 100)  # Spike
        return max(0, round(next_value, 2))

    elif sensor_code.startswith(("NOXS", "SO2S", "O3S", "VOC")):
        # Gas Sensors
        base_value = last_value if last_value is not None else random.uniform(0, 5)
        next_value = base_value + random.uniform(-0.1, 0.1)
        if random.random() < 0.03:
            next_value += random.uniform(1, 2)  # Spike
        return max(0, round(next_value, 4))

    elif sensor_code.startswith("PHS"):
        # pH Sensors
        base_value = last_value if last_value is not None else np.random.normal(loc=7.0, scale=0.5)
        next_value = round(base_value + np.random.normal(0, 0.1), 2)
        if random.random() < 0.03:
            next_value += random.uniform(-1, 1)
        return max(0, min(next_value, 14))

    elif sensor_code.startswith("TS"):
        # Turbidity Sensors
        next_value = max(0, last_value + random.uniform(-2, 2)) if last_value is not None else random.uniform(50, 100)
        if random.random() < 0.05:
            next_value += random.uniform(10, 50)  # Spike
        return round(next_value, 2)

    elif sensor_code.startswith("DOS"):
        # Dissolved Oxygen Sensors
        next_value = max(0, last_value + random.uniform(-0.5, 0.5)) if last_value is not None else random.uniform(5, 14)
        if random.random() < 0.05:
            next_value -= random.uniform(1, 4)  # Drop due to anomaly
        return round(next_value, 2)

    elif sensor_code.startswith("CS"):
        # Conductivity Sensors
        base_value = last_value if last_value is not None else random.uniform(1000, 5000)
        next_value = base_value + random.uniform(-50, 50)
        if random.random() < 0.04:
            next_value += random.uniform(500, 1000)  # Spike
        return max(0, round(next_value, 2))

    elif sensor_code.startswith(("AS", "NS")):
        # Ammonia and Nitrate Sensors
        base_value = last_value if last_value is not None else random.uniform(0, 50)
        next_value = base_value + random.uniform(-1, 1)
        if random.random() < 0.05:
            next_value += random.uniform(5, 10)  # Spike
        return max(0, round(next_value, 3))

    else:
        # Default Handler for any other sensors
        base_value = last_value if last_value is not None else random.uniform(0, 100)
        next_value = base_value + random.uniform(-1, 1)
        if random.random() < 0.05:
            next_value += random.uniform(10, 20)
        return max(0, round(next_value, 2))

def get_next_record(codes, last_record):
    """
    Generate the next sensor readings for all sensors.
    """
    next_record = {}
    for code in codes:
        sensor_code = code.split("-")[0]
        last_value = last_record[code]
        next_value = get_next_value(last_value, sensor_code)
        next_record[code] = next_value
        
    return next_record
    

def get_initial_record(codes):
    """
    Generate the initial sensor readings for all sensors.
    """
    initial_record = {}
    for code in codes:
        sensor_code = code.split("-")[0]
        if sensor_code == "SMS":
            initial_record[code] = round(random.uniform(20, 100), 2)
        elif sensor_code.startswith(("HML", "HMA", "HMM")):
            initial_record[code] = round(random.uniform(0, 0.01), 5)
        elif sensor_code == "NLS":
            initial_record[code] = random.randint(30, 80)
        elif sensor_code == "OS":
            initial_record[code] = round(random.uniform(0, 100), 2)
        elif sensor_code == "PMS25": # TODO: Check if this is correct
            initial_record[code] = round(random.uniform(20, 80), 2)
        elif sensor_code == "PMS10": # TODO: Check if this is correct
            initial_record[code] = round(random.uniform(55, 145), 2)
        elif sensor_code == "CO2S":
            initial_record[code] = round(random.uniform(250, 550), 2)
        elif sensor_code == "NOXS":
            initial_record[code] = round(random.uniform(0, 0.2), 4)
        elif sensor_code == "SO2S":
            initial_record[code] = round(random.uniform(0, 0.1), 4)
        elif sensor_code == "O3S":
            initial_record[code] = round(random.uniform(0, 0.2), 4)
        elif sensor_code == "VOC":
            initial_record[code] = round(random.uniform(0, 0.5), 4)
        elif sensor_code == "PHS":
            initial_record[code] = round(np.random.normal(loc=7.0, scale=0.5), 2)
            initial_record[code] = max(0, min(initial_record[code], 14))
        elif sensor_code == "TS":
            initial_record[code] = round(random.uniform(50, 100), 2)
        elif sensor_code == "DOS":
            initial_record[code] = round(random.uniform(4, 9), 2)
        elif sensor_code == "CS":
            initial_record[code] = round(random.uniform(1000, 5000), 2)
        elif sensor_code.startswith(("AS", "NS")):
            initial_record[code] = round(random.uniform(0, 50), 3)
        else:
            initial_record[code] = round(random.uniform(0, 100), 2)
    return initial_record

def log_sensor_data(sensor_data, filename='sensor_data_log.csv'):
    """
    Log the sensor data to a CSV file.
    """
    fieldnames = ["timestamp"] + list(sensor_data.keys())
    file_exists = False
    try:
        with open(filename, 'r', newline='') as csvfile:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(sensor_data)

def main():
    # Extract sensor codes
    sensor_codes = list(SENSOR_CODES.keys())

    # Initialize last_values with initial records
    last_values = get_initial_record(sensor_codes)

    # Run the simulation indefinitely
    while True:
        sensor_data = {
            "timestamp": datetime.now().isoformat()
        }

        for code in sensor_codes:
            sensor_type = code.split("-")[0]
            current_value = last_values.get(code)
            next_value = get_next_value(current_value, sensor_type)
            sensor_data[code] = next_value
            last_values[code] = next_value

        # Log the sensor data
        log_sensor_data(sensor_data)

        # Print the sensor data to console (optional)
        print(sensor_data)

        # Wait for the next interval (e.g., 10 seconds)
        time.sleep(10)

if __name__ == "__main__":
    main()
