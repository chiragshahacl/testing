import csv
from pathlib import Path

import numpy as np


def generate_dataset_from_csv(csv_path: Path, column: str, amount: int = 1000):
    with open(csv_path, encoding="UTF8") as csvfile:
        result = []
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        index = next(reader).index(column)
        for row in reader:
            result.append(float(row[index]))
            if len(result) >= amount:
                break
        return result


def generate_pleth_dataset(num_samples, sample_rate=256, max_amplitude=1.0, noise_level=0.1):
    timeslot = np.arange(num_samples) / sample_rate
    pleth = max_amplitude * np.sin(2 * np.pi * 2 * timeslot) + max_amplitude * np.sin(
        2 * np.pi * 4 * timeslot
    )
    noise = np.random.normal(scale=noise_level, size=num_samples)
    pleth += noise
    pleth = np.clip(pleth, -max_amplitude, max_amplitude)
    return pleth


def generate_rr_dataset(num_samples) -> np.ndarray:
    mean = 15.4
    std = 2.35
    signal = np.random.normal(mean, std, num_samples)
    return signal
