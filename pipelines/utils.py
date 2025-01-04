import logging
import pandas as pd
from model.data_cleaning import DataCleaning, DataPreprocessStrategy, DataDivideStrategy

def get_sample_data_for_testing(file_path: str, sample_size: int = 100) -> pd.DataFrame:
    """
    Load a sample of the data for testing purposes.

    Args:
        file_path (str): Path to the CSV file containing sample data.
        sample_size (int): Number of samples to extract.

    Returns:
        pd.DataFrame: Sampled and preprocessed data.
    """
    try:
        logging.info("Loading sample data for testing...")
        # Load data and sample
        df = pd.read_csv(file_path)
        df_sample = df.sample(n=sample_size)

        # Apply preprocessing strategy
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning = DataCleaning(df_sample, preprocess_strategy)
        preprocessed_sample, label_encoder = data_cleaning.handle_data()

        logging.info("Sample data loaded and preprocessed successfully.")
        return preprocessed_sample, label_encoder
    except Exception as e:
        logging.error(f"Error in get_sample_data_for_testing: {str(e)}")
        raise e