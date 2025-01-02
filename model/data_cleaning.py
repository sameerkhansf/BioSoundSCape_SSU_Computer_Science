import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class HyperspectralDataCleaner:
    """
    A data cleaner specialized for hyperspectral classification tasks.
    """

    def __init__(self):
        self.label_encoder = None

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

    def remove_class_name(self, df: pd.DataFrame, class_name: str) -> pd.DataFrame:
        """Remove rows that contain `class_name` in the `Label` column."""
        mask = df['Label'].str.contains(class_name, na=False)
        df = df[~mask].reset_index(drop=True)
        return df

    def preprocess_data(self, df: pd.DataFrame):
        """
        Preprocess the DataFrame:
        1) Extract Sample_num, Clean Labels
        2) Remove "Mixed or Not Classified"
        3) Replace NaNs/invalid frequency values
        4) Label-encode classes
        """
        # Basic cleaning
        df['Sample_num'] = df['File'].str.split('_').str[0].astype(int)
        df['Label'] = df['Label'].str.split('(').str[0].str.strip()

        # Remove "Mixed or Not Classified"
        df = df[df['Label'] != 'Mixed or Not Classified'].reset_index(drop=True)

        # Fill freq columns with -9999 and remove those rows
        freq_cols = [c for c in df.columns if c.startswith('frq')]
        df[freq_cols] = df[freq_cols].fillna(-9999)
        df = df[~df[freq_cols].eq(-9999).any(axis=1)]

        # Label encoding
        self.label_encoder = LabelEncoder()
        df['Label_Encoded'] = self.label_encoder.fit_transform(df['Label'])

        return df, self.label_encoder
