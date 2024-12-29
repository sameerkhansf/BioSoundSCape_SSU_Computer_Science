import logging
import pandas as pd
from zenml import step
from zenml.client import Client
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from model.model_dev import CNNModel, PCATransformer
from .config import ModelNameConfig

experiment_tracker = Client().active_stack.experiment_tracker

def define_callbacks(checkpoint_path):
    early_stopping = EarlyStopping(monitor='val_accuracy', patience=30, verbose=1)
    lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=20, min_lr=1e-6, verbose=1)
    checkpoint = ModelCheckpoint(filepath=checkpoint_path, save_weights_only=True, monitor='val_accuracy', save_best_only=True, verbose=1)
    return [checkpoint, early_stopping, lr_scheduler]

@step(experiment_tracker=experiment_tracker.name)
def train_model(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    config: ModelNameConfig,
):
    """
    Train the CNN model with PCA preprocessing.

    Args:
        x_train: Training features
        x_test: Testing features
        y_train: Training labels
        y_test: Testing labels
        config: Model configuration parameters

    Returns:
        history: Training history object
    """
    try:
        if config.model_name == "cnn":
            model = CNNModel(input_shape=x_train.shape[1:], num_classes=len(y_train.unique()))
            callbacks = define_callbacks(config.checkpoint_path)
            history = model.train(x_train, y_train, x_test, y_test, epochs=config.epochs, batch_size=config.batch_size, callbacks=callbacks)
            return history
        else:
            raise ValueError("Model name not supported")
    except Exception as e:
        logging.error(e)
        raise e
