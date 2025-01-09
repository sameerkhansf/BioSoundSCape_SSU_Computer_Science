import logging
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import LabelEncoder, RobustScaler
from tensorflow.keras.utils import to_categorical

class HyperspectralDataCleaner:
    """
    A data cleaner specialized for hyperspectral classification tasks.
    """
    @abstractmethod
    def handle_data(self, data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series, Tuple]:
        pass

    def combine_classes(
        self,
        df: pd.DataFrame,
        classes_to_combine,
        combined_class_name="Shrubs and Natural Grassland"
    ) -> pd.DataFrame:
        """Combine multiple classes into a single class."""
        df['Label'] = df['Label'].replace(
            dict.fromkeys(classes_to_combine, combined_class_name)
        )
        return df

class DataPreprocessStrategy(DataStrategy):
    """
    Data preprocessing strategy which preprocesses the data.
    """
    def handle_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, LabelEncoder]:
        """
        Preprocess the samples DataFrame by cleaning and encoding labels, 
        handling missing values, and preparing frequency columns.
        """
        try:
            logging.info("Starting DataPreprocessStrategy...")

            # Extract Sample_num from 'File' and clean 'Label'
            data['Sample_num'] = data['File'].str.split('_').str[0].astype(int)
            data['Label'] = data['Label'].str.split('(').str[0].str.strip()

            # Remove rows with "Mixed or Not Classified"
            before_remove = data.shape[0]
            data = data[data['Label'] != 'Mixed or Not Classified']
            after_remove = data.shape[0]
            logging.info(
                f"Removed {before_remove - after_remove} rows labeled 'Mixed or Not Classified'. "
                f"Remaining rows: {data.shape[0]}"
            )
            data.reset_index(drop=True, inplace=True)

            # Handle frequency columns
            frequency_columns = [col for col in data.columns if col.startswith('frq')]
            # Fill NaN with -9999
            data.loc[:, frequency_columns] = data[frequency_columns].fillna(-9999)
            # Drop rows if they still contain -9999
            before_freq_remove = data.shape[0]
            data = data[np.logical_not(data[frequency_columns].eq(-9999).any(axis=1))]
            after_freq_remove = data.shape[0]
            logging.info(
                f"Removed {before_freq_remove - after_freq_remove} rows due to missing freq data. "
                f"Remaining rows: {data.shape[0]}"
            )

            # Validate no invalid values remain in frequency columns
            assert data[frequency_columns].isna().sum().sum() == 0, \
                "NaN values still exist in frequency columns"
            assert (data[frequency_columns] == -9999).sum().sum() == 0, \
                "Invalid (-9999) values remain after filtering freq columns"

            # --- Additional logging: distribution of freq columns ---
            logging.info(
                f"Frequency columns stats:\n{data[frequency_columns].describe().round(2)}"
            )

            # Verify we still have data
            if data.empty:
                raise ValueError("No data remains after cleaning steps!")

            # Check label distribution
            label_counts = data['Label'].value_counts()
            logging.info(f"Label distribution after cleaning:\n{label_counts}")

            # Label Encoding
            label_encoder = LabelEncoder()
            data['Label_Encoded'] = label_encoder.fit_transform(data['Label'])

            return data, label_encoder

        except Exception as e:
            logging.error(f"Error in DataPreprocessStrategy: {str(e)}")
            raise e


class DataDivideStrategy(DataStrategy):
    """
    Data dividing strategy which divides the data into train and test data.
    Now includes RobustScaler for frequency columns to avoid data leakage.
    """

    def handle_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Stratified splitting of the data into train and test datasets, 
        followed by robust scaling of frequency columns and final reshaping 
        for Conv1D.

        Returns:
            X_train, X_test, y_train_cat, y_test_cat
        """
        try:
            logging.info("Starting DataDivideStrategy...")

            # Create a DataFrame with unique images and their labels
            image_samples_df = data[['Sample_num', 'Label_Encoded']].drop_duplicates()
            logging.info(f"Unique sample images: {image_samples_df.shape[0]}")

            # Stratified split at the image level
            sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
            train_indices, test_indices = next(
                sss.split(image_samples_df['Sample_num'], image_samples_df['Label_Encoded'])
            )

            # Get the Sample_num for training and testing
            train_sample_nums = image_samples_df['Sample_num'].iloc[train_indices]
            test_sample_nums = image_samples_df['Sample_num'].iloc[test_indices]

            # Create training and testing DataFrames
            train_df = data[data['Sample_num'].isin(train_sample_nums)]
            test_df = data[data['Sample_num'].isin(test_sample_nums)]

            logging.info(f"Train set shape: {train_df.shape}")
            logging.info(f"Test set shape: {test_df.shape}")

            # Log train/test label distribution
            train_label_counts = train_df['Label'].value_counts()
            test_label_counts = test_df['Label'].value_counts()
            logging.info(f"Train label distribution:\n{train_label_counts}")
            logging.info(f"Test label distribution:\n{test_label_counts}")

            # Extract frequency columns
            frequency_cols = [col for col in data.columns if 'frq' in col]
            X_train = train_df[frequency_cols].values
            X_test = test_df[frequency_cols].values
            y_train = train_df['Label_Encoded'].values
            y_test = test_df['Label_Encoded'].values

            logging.info("Applying RobustScaler to frequency columns...")

            # scaler = RobustScaler()
            # X_train = scaler.fit_transform(X_train)   # Fit on train, transform train
            # X_test = scaler.transform(X_test)         # Transform test

            # Add a channel dimension for Conv1D (now that we have scaled data)
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

            # Convert labels to one-hot encoding
            num_classes = len(data['Label_Encoded'].unique())
            y_train_cat = to_categorical(y_train, num_classes)
            y_test_cat = to_categorical(y_test, num_classes)

            logging.info(
                f"DataDivideStrategy complete.\n"
                f"X_train: {X_train.shape}, y_train: {y_train_cat.shape}\n"
                f"X_test: {X_test.shape}, y_test: {y_test_cat.shape}\n"
                f"Num classes: {num_classes}"
            )

            return X_train, X_test, y_train_cat, y_test_cat

        except Exception as e:
            logging.error(f"Error in DataDivideStrategy: {str(e)}")
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
        """Handle data based on the provided strategy."""
        return self.strategy.handle_data(self.df)
