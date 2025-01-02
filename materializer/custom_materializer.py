# materializer/custom_materializer.py

import os
import pickle
from typing import Any, Type, Union

import numpy as np
import pandas as pd
from tensorflow.keras.models import Model, Sequential
from zenml.io import fileio
from zenml.materializers.base_materializer import BaseMaterializer

DEFAULT_FILENAME = "HyperspectralEnvironment"

class HyperspectralMaterializer(BaseMaterializer):
    """
    Handles saving/loading complex data types (models, arrays, DataFrames, etc.).
    """

    ASSOCIATED_TYPES = (
        str,
        np.ndarray,
        pd.Series,
        pd.DataFrame,
        Model,
        Sequential
    )

    def handle_input(self, data_type: Type[Any]) -> Any:
        super().handle_input(data_type)
        filepath = os.path.join(self.artifact.uri, DEFAULT_FILENAME)
        with fileio.open(filepath, "rb") as fid:
            obj = pickle.load(fid)
        return obj

    def handle_return(self, obj: Any) -> None:
        super().handle_return(obj)
        filepath = os.path.join(self.artifact.uri, DEFAULT_FILENAME)
        with fileio.open(filepath, "wb") as fid:
            pickle.dump(obj, fid)