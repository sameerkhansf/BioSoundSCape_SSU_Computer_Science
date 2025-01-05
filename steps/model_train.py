import logging
from typing import Tuple
import numpy as np  
import pandas as pd
from zenml import step
from zenml.client import Client
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.models import Model

from model.model_dev import CNNModel, PCATransformer
from .config import ModelNameConfig

experiment_tracker = Client().active_stack.experiment_tracker

def define_callbacks(checkpoint_path: str):
    """
    Utility function to define Keras callbacks for training.

    Args:
        checkpoint_path (str): Path to save the best model weights.

    Returns:
        list: A list of Keras callbacks.
    """
    early_stopping = EarlyStopping(
        monitor='val_accuracy', patience=30, verbose=1
    )
    lr_scheduler = ReduceLROnPlateau(
        monitor='val_loss', factor=0.2, patience=20, min_lr=1e-6, verbose=1
    )
    checkpoint = ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
    return [checkpoint, early_stopping, lr_scheduler]

@step(experiment_tracker=experiment_tracker.name)
def model_train(
    x_train: np.ndarray,    
    x_test: np.ndarray,
    y_train: np.ndarray,     
    y_test: np.ndarray,      
    config: ModelNameConfig = ModelNameConfig()
) -> Model:
    """
    Trains a CNN model on the provided data (NumPy arrays).

    Args:
        x_train (np.ndarray): Training features (Conv1D-ready shape).
        x_test (np.ndarray): Testing features (Conv1D-ready shape).
        y_train (np.ndarray): One-hot encoded training labels.
        y_test (np.ndarray): One-hot encoded testing labels.
        config (ModelNameConfig): Configuration for the model training.

    Returns:
        Model: The trained Keras model.
    """
    try:
        # Check model name from config
        if config.model_name == "cnn":
            # Build the CNN model
            num_classes = (
                y_train.shape[1] if y_train.ndim > 1 
                else len(set(y_train.ravel()))
            )
            cnn_model = CNNModel(
                input_shape=x_train.shape[1:], 
                num_classes=num_classes,
                wd=1e-6,
                drop_rate=0.3,
                learning_rate=0.0001
            )

            # Define training callbacks
            callbacks = define_callbacks(config.checkpoint_path)

            # Train the model
            history = cnn_model.train(
                x_train,
                y_train,
                x_test,
                y_test,
                epochs=config.epochs,
                batch_size=config.batch_size,
                callbacks=callbacks
            )

            logging.info("Model training completed successfully.")
            # Return the underlying Keras model
            return cnn_model.model
        
        else:
            raise ValueError(f"Model name '{config.model_name}' not supported.")

    except Exception as e:
        logging.error(f"Error during model training: {str(e)}")
        raise e
