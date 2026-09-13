
import pandas as pd
from pathlib import Path
data_path = Path(r"C:\Users\Hi\Desktop\Risk-Analysis\data\raw\healthcare_patient_readmission.csv")


def load_data(data_path):
    data = pd.read_csv(data_path)
    return data


# cleaned dataset
clean_data_path = Path(r"C:\Users\Hi\Desktop\Risk-Analysis\data\processed\PrData.csv")

def load_clean_data(clean_data_path):
    clean_data = pd.read_csv(clean_data_path)
    return clean_data
