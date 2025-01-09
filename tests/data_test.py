import logging
import pytest
import pandas as pd
import numpy as np
from model.data_cleaning import DataCleaning, DataPreprocessStrategy, DataDivideStrategy


def test_preprocessing_shapes():
    """
    Test if the preprocessing step outputs the correct data structure and shapes.
    """
    try:
        logging.info("Testing preprocessing shapes...")

        # Sample data for testing
        df = pd.read_csv("./data/samples.csv")
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning = DataCleaning(df, preprocess_strategy)
        preprocessed_data, label_encoder = data_cleaning.handle_data()

        # Check required columns exist
        assert "Sample_num" in preprocessed_data.columns, "'Sample_num' column missing after preprocessing."
        assert "Label_Encoded" in preprocessed_data.columns, "'Label_Encoded' column missing after preprocessing."
        assert label_encoder is not None, "LabelEncoder instance is not returned."

        # Check frequency columns
        frequency_cols = [col for col in preprocessed_data.columns if col.startswith("frq")]
        assert len(frequency_cols) > 0, "Frequency columns are missing after preprocessing."

        logging.info("Preprocessing shapes test passed.")
    except Exception as e:
        pytest.fail(f"Preprocessing shapes test failed: {str(e)}")


def test_train_test_split_shapes():
    """
    Test if the train-test split step produces correctly shaped outputs.
    """
    try:
        logging.info("Testing train-test split shapes...")

        # Sample data for testing
        df = pd.read_csv("./data/samples.csv")
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning_preprocess = DataCleaning(df, preprocess_strategy)
        preprocessed_data, _ = data_cleaning_preprocess.handle_data()

        divide_strategy = DataDivideStrategy()
        data_cleaning_divide = DataCleaning(preprocessed_data, divide_strategy)
        X_train, X_test, y_train, y_test = data_cleaning_divide.handle_data()

        # Validate the shapes of train and test datasets
        assert X_train.ndim == 3, "X_train is not 3-dimensional for Conv1D input."
        assert X_test.ndim == 3, "X_test is not 3-dimensional for Conv1D input."
        assert y_train.ndim == 2, "y_train is not 2-dimensional (one-hot encoded)."
        assert y_test.ndim == 2, "y_test is not 2-dimensional (one-hot encoded)."
        assert X_train.shape[1:] == X_test.shape[1:], "Feature dimensions of train and test datasets do not match."
        assert y_train.shape[1] == y_test.shape[1], "Number of classes in train and test labels do not match."

        logging.info("Train-test split shapes test passed.")
    except Exception as e:
        pytest.fail(f"Train-test split shapes test failed: {str(e)}")


def test_no_data_leakage():
    """
    Test if there is any data leakage between training and testing datasets.
    """
    try:
        logging.info("Testing for data leakage...")

        # Sample data for testing
        df = pd.read_csv("./data/samples.csv")
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning_preprocess = DataCleaning(df, preprocess_strategy)
        preprocessed_data, _ = data_cleaning_preprocess.handle_data()

        divide_strategy = DataDivideStrategy()
        data_cleaning_divide = DataCleaning(preprocessed_data, divide_strategy)
        X_train, X_test, y_train, y_test = data_cleaning_divide.handle_data()

        # Convert to DataFrame for easier comparison
        X_train_df = pd.DataFrame(X_train.reshape(X_train.shape[0], -1))
        X_test_df = pd.DataFrame(X_test.reshape(X_test.shape[0], -1))

        # Check for overlapping samples
        assert len(pd.merge(X_train_df, X_test_df, how="inner")) == 0, "Data leakage detected between train and test sets."

        logging.info("Data leakage test passed.")
    except Exception as e:
        pytest.fail(f"Data leakage test failed: {str(e)}")


def test_label_range_consistency():
    """
    Test if label encoding is consistent and within expected range.
    """
    try:
        logging.info("Testing label encoding consistency...")

        # Sample data for testing
        df = pd.read_csv("./data/samples.csv")
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning = DataCleaning(df, preprocess_strategy)
        preprocessed_data, label_encoder = data_cleaning.handle_data()

        # Validate label encoding range
        encoded_labels = preprocessed_data["Label_Encoded"]
        num_classes = len(label_encoder.classes_)
        assert encoded_labels.min() >= 0, "Label encoding contains negative values."
        assert encoded_labels.max() < num_classes, "Label encoding exceeds expected range."

        logging.info("Label range consistency test passed.")
    except Exception as e:
        pytest.fail(f"Label range consistency test failed: {str(e)}")


def test_frequency_columns_integrity():
    """
    Test if frequency columns contain valid values after preprocessing.
    """
    try:
        logging.info("Testing frequency column integrity...")

        # Sample data for testing
        df = pd.read_csv("./data/samples.csv")
        preprocess_strategy = DataPreprocessStrategy()
        data_cleaning = DataCleaning(df, preprocess_strategy)
        preprocessed_data, _ = data_cleaning.handle_data()

        # Check for invalid values
        frequency_cols = [col for col in preprocessed_data.columns if col.startswith("frq")]
        assert not preprocessed_data[frequency_cols].isnull().any().any(), "Frequency columns contain NaN values."
        assert (preprocessed_data[frequency_cols] == -9999).sum().sum() == 0, "Frequency columns contain invalid values (-9999)."

        logging.info("Frequency column integrity test passed.")
    except Exception as e:
        pytest.fail(f"Frequency column integrity test failed: {str(e)}")
