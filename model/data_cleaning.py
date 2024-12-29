import logging
from abc import ABC, abstractmethod
from typing import Union, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

class DataStrategy(ABC):
    """
    Abstract Class defining strategy for handling data
    """

    @abstractmethod
    def handle_data(self, data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
        pass


class DataPreprocessStrategy(DataStrategy):
    """
    Data preprocessing strategy which preprocesses the data.
    """

    def handle_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, LabelEncoder]:
        """
        Preprocess the samples DataFrame by cleaning and encoding labels, handling missing values,
        and preparing frequency columns.
        """
        try:
            # Extract Sample_num and clean labels
            data['Sample_num'] = data['File'].str.split('_').str[0].astype(int)
            data['Label'] = data['Label'].str.split('(').str[0].str.strip()

            # Remove rows with "Mixed or Not Classified"
            data = data[data['Label'] != 'Mixed or Not Classified']
            data.reset_index(drop=True, inplace=True)

            # Handle frequency columns
            frequency_columns = [col for col in data.columns if col.startswith('frq')]
            data.loc[:, frequency_columns] = data[frequency_columns].fillna(-9999)
            data = data[~data[frequency_columns].eq(-9999).any(axis=1)]

            # Verify no invalid values remain
            assert data[frequency_columns].isna().sum().sum() == 0, "NaN values still exist in frequency columns"
            assert (data[frequency_columns] == -9999).sum().sum() == 0, "Invalid values remain after filtering"

            # Label Encoding
            label_encoder = LabelEncoder()
            data['Label_Encoded'] = label_encoder.fit_transform(data['Label'])

            return data, label_encoder
        except Exception as e:
            logging.error(e)
            raise e


class DataDivideStrategy(DataStrategy):
    """
    Data dividing strategy which divides the data into train and test data.
    """

    def handle_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Stratified splitting of the data into train and test datasets.
        """
        try:
            image_samples_df = data[['Sample_num', 'Label_Encoded']].drop_duplicates()
            sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
            train_indices, test_indices = next(
                sss.split(image_samples_df['Sample_num'], image_samples_df['Label_Encoded'])
            )

            train_sample_nums = image_samples_df['Sample_num'].iloc[train_indices]
            test_sample_nums = image_samples_df['Sample_num'].iloc[test_indices]

            train_df = data[data['Sample_num'].isin(train_sample_nums)]
            test_df = data[data['Sample_num'].isin(test_sample_nums)]

            frequency_cols = [col for col in data.columns if 'frq' in col]

            X_train = train_df[frequency_cols].values
            y_train = train_df['Label_Encoded'].values
            X_test = test_df[frequency_cols].values
            y_test = test_df['Label_Encoded'].values

            # Add a channel dimension for Conv1D
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

            # Convert labels to one-hot encoding
            num_classes = len(data['Label_Encoded'].unique())
            y_train_cat = to_categorical(y_train, num_classes)
            y_test_cat = to_categorical(y_test, num_classes)

            return X_train, X_test, y_train_cat, y_test_cat
        except Exception as e:
            logging.error(e)
            raise e


class DataCleaning:
    """
    Data cleaning class which preprocesses the data and divides it into train and test data.
    """

    def __init__(self, data: pd.DataFrame, strategy: DataStrategy) -> None:
        """Initializes the DataCleaning class with a specific strategy."""
        self.df = data
        self.strategy = strategy

    def handle_data(self) -> Union[pd.DataFrame, pd.Series, Tuple]:
        """Handle data based on the provided strategy"""
        return self.strategy.handle_data(self.df)
