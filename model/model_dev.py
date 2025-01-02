import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv1D,
    MaxPooling1D,
    Flatten,
    Dense,
    Dropout,
    BatchNormalization,
    Input,
)
from tensorflow.keras.optimizers import Adam
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler


class CNNModel:
    """
    CNN model for classification tasks.
    """

    def __init__(
        self, input_shape, num_classes, wd=1e-6, drop_rate=0.3, learning_rate=0.0001
    ):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = self._build_model(wd, drop_rate, learning_rate)

    def _build_model(self, wd, drop_rate, learning_rate):
        model = Sequential(
            [
                Input(shape=self.input_shape),
                Conv1D(512, kernel_size=3, activation="relu"),
                MaxPooling1D(pool_size=2),
                Conv1D(256, kernel_size=3, activation="relu"),
                MaxPooling1D(pool_size=2),
                Conv1D(128, kernel_size=3, activation="relu"),
                BatchNormalization(),
                Flatten(),
                Dense(128, activation="relu"),
                Dropout(drop_rate),
                Dense(64, activation="relu"),
                Dropout(drop_rate),
                Dense(self.num_classes, activation="softmax"),
            ]
        )
        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        return model

    def train(self, x_train, y_train, x_test, y_test, epochs, batch_size, callbacks):
        history = self.model.fit(
            x_train,
            y_train,
            validation_data=(x_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
        )
        return history


class PCATransformer:
    """
    PCA transformer for dimensionality reduction.
    """

    def __init__(self, n_components=0.95):
        self.scaler = RobustScaler()
        self.pca = PCA(n_components=n_components)

    def fit_transform(self, x_train):
        x_scaled = self.scaler.fit_transform(x_train)
        x_pca = self.pca.fit_transform(x_scaled)
        return x_pca

    def transform(self, x_test):
        x_scaled = self.scaler.transform(x_test)
        x_pca = self.pca.transform(x_scaled)
        return x_pca
