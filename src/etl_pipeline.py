import os
import logging
import zipfile
import pandas as pd

# ----------------------
# CONFIG
# ----------------------
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

DATASET_NAME = "superstore-dataset-final"
CSV_NAME = "Sample - Superstore.csv"
KAGGLE_DATASET = "vivek468/superstore-dataset-final"

# ----------------------
# LOGGING SETUP
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----------------------
# EXTRACT
# ----------------------
def download_dataset():
    """Download dataset from Kaggle if not already present."""
    zip_path = os.path.join(RAW_DIR, f"{DATASET_NAME}.zip")

    if os.path.exists(os.path.join(RAW_DIR, CSV_NAME)):
        logging.info("Dataset already exists. Skipping download.")
        return

    logging.info("Downloading dataset from Kaggle...")
    os.makedirs(RAW_DIR, exist_ok=True)

    os.system(f"kaggle datasets download -d {KAGGLE_DATASET} -p {RAW_DIR}")

    if not os.path.exists(zip_path):
        raise FileNotFoundError("Download failed: ZIP file not found.")

    logging.info("Download complete.")

    return zip_path

def extract_dataset(zip_path):
    """Extract dataset ZIP file."""
    logging.info("Extracting dataset...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(RAW_DIR)

    logging.info("Extraction complete.")

# ----------------------
# TRANSFORM
# ----------------------
def load_csv(file_path):
    try:
        return pd.read_csv(
            file_path,
            parse_dates=["Order Date", "Ship Date"],
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            file_path,
            parse_dates=["Order Date", "Ship Date"],
            encoding="latin-1"
        )

def transform_data():
    """Clean and prepare dataset."""
    file_path = os.path.join(RAW_DIR, CSV_NAME)

    logging.info("Loading dataset...")
    df = load_csv(file_path)

    logging.info("Cleaning data...")

    df.columns = (
        df.columns
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    df = df.drop_duplicates()
    df = df.dropna(subset=["sales", "profit"])

    # Add useful columns
    df["Year"] = df["order_date"].dt.year
    df["Month"] = df["order_date"].dt.month

    logging.info(f"Dataset shape after cleaning: {df.shape}")

    return df

# ----------------------
# LOAD
# ----------------------
def save_processed_data(df):
    """Save cleaned dataset."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    output_path = os.path.join(PROCESSED_DIR, "superstore_cleaned.csv")

    df.to_csv(output_path, index=False)

    logging.info(f"Processed data saved to {output_path}")

# ----------------------
# MAIN PIPELINE
# ----------------------
def run_pipeline():
    logging.info("Starting ETL pipeline...")

    zip_path = download_dataset()

    if zip_path:
        extract_dataset(zip_path)

    df = transform_data()
    save_processed_data(df)

    logging.info("ETL pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()