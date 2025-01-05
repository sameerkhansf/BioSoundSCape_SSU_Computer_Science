import logging
from typing import Tuple
import pandas as pd
import numpy as np
from zenml import step
from typing_extensions import Annotated
from sklearn.preprocessing import LabelEncoder

from model.data_cleaning import (
    DataCleaning,
    DataPreprocessStrategy,
    DataDivideStrategy
)

@step(enable_cache=True)  
def clean_data(
    data: pd.DataFrame,
) -> Tuple[
    Annotated[np.ndarray, "X_train"],
    Annotated[np.ndarray, "X_test"],
    Annotated[np.ndarray, "y_train"],
    Annotated[np.ndarray, "y_test"],
    Annotated[LabelEncoder, "LabelEncoder"]
]:
    """
    Preprocesses and cleans the input data, then divides it into training 
    and testing datasets using strategy classes from model.data_cleaning.
    Steps:
      1. Cleaning and preprocessing (label encoding, frequency handling).
      2. Stratified splitting into train and test sets.
      3. Reshaping features for Conv1D and one-hot encoding of labels.

    Args:
        data (pd.DataFrame): The raw data to be cleaned and split.

    Returns:
        Tuple:
            - X_train (np.ndarray): Training features for 1D CNN.
            - X_test (np.ndarray): Testing features for 1D CNN.
            - y_train (np.ndarray): One-hot encoded training labels.
            - y_test (np.ndarray): One-hot encoded testing labels.
            - label_encoder (LabelEncoder): For decoding predicted labels.
    """
    try:
        logging.info("Initializing data preprocessing strategy...")
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning_preprocess = DataCleaning(data, preprocess_strategy)
        preprocessed_data, label_encoder = data_cleaning_preprocess.handle_data()

        logging.info("Preprocessing completed successfully.")
        logging.info("Initializing data division strategy...")
        divide_strategy = DataDivideStrategy()
        data_cleaning_divide = DataCleaning(preprocessed_data, divide_strategy)
        X_train, X_test, y_train, y_test = data_cleaning_divide.handle_data()

        logging.info("Data division into train and test sets completed successfully.")
        return X_train, X_test, y_train, y_test, label_encoder

    except Exception as e:
        logging.error(f"Error during data cleaning and division: {str(e)}")
        raise e
