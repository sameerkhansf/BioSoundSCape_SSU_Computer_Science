import logging
import pandas as pd
from zenml import step

class IngestData:
    """
    Data ingestion class which ingests data from the source and returns a DataFrame.
    """

    def __init__(self, data_path: str) -> None:
        """
        Initialize with the path to the dataset.

        Args:
            data_path (str): Path to the dataset CSV file.
        """
        self.data_path = data_path

    def get_data(self) -> pd.DataFrame:
        """
        Load the dataset from the given path.

        Returns:
            pd.DataFrame: Loaded dataset.
        """
        try:
            logging.info(f"Ingesting data from {self.data_path}")
            df = pd.read_csv(self.data_path)
            logging.info(f"Data successfully loaded. Shape: {df.shape}")
            return df
        except Exception as e:
            logging.error(f"Error while reading data: {e}")
            raise e


@step
def ingest_data(data_path: str) -> pd.DataFrame:
    """
    ZenML step to ingest data.

    Args:
        data_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Ingested data as a DataFrame.
    """
    try:
        ingestor = IngestData(data_path)
        return ingestor.get_data()
    except Exception as e:
        logging.error(f"Error in ingest_data step: {e}")
        raise e
