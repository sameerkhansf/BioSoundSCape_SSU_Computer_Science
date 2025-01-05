import logging
import mlflow
from zenml import step
from zenml.client import Client
from typing import Tuple, Dict

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from typing_extensions import Annotated
from tensorflow.keras.models import Model

experiment_tracker = Client().active_stack.experiment_tracker

@step(enable_cache=True, experiment_tracker=experiment_tracker.name)
def evaluation(
    model: Model,
    x_test: np.ndarray,
    y_test: np.ndarray,
    label_encoder: LabelEncoder
) -> Tuple[
    Annotated[Dict[str, float], "Pixel-level metrics"],
    Annotated[Dict[str, float], "Image-level metrics"]
]:
    """
    Evaluate the model's performance at both pixel-level and image-level.

    With caching enabled, if model, x_test, y_test remain unchanged,
    ZenML will skip re-running. However, typically the model artifact
    changes if training changes.

    Logs confusion matrices and accuracy/F1 metrics to MLflow.

    Args:
        model (Model): Trained Keras model for evaluation.
        x_test (np.ndarray): Test features.
        y_test (np.ndarray): One-hot encoded test labels.
        label_encoder (LabelEncoder): For inverse-transforming label indices.

    Returns:
        (dict, dict): A tuple of two dictionaries:
          - Pixel-level metrics (accuracy, f1, etc.)
          - Image-level metrics (accuracy, etc.)
    """
    try:
        logging.info("Starting model evaluation...")

        # Decode true labels from one-hot encoding
        y_true_int = np.argmax(y_test, axis=1)

        # Model predictions
        y_pred_probs = model.predict(x_test, verbose=0)
        y_pred_int = np.argmax(y_pred_probs, axis=1)

        # Convert integer labels back to class names
        y_true_labels = label_encoder.inverse_transform(y_true_int)
        y_pred_labels = label_encoder.inverse_transform(y_pred_int)

        # -----------------------
        # Pixel-level Metrics
        # -----------------------
        pixel_accuracy = accuracy_score(y_true_labels, y_pred_labels)
        pixel_f1 = f1_score(y_true_labels, y_pred_labels, average="weighted")

        mlflow.log_metric("pixel_accuracy", pixel_accuracy)
        mlflow.log_metric("pixel_f1", pixel_f1)

        # Pixel-level Confusion Matrix
        pixel_cm = confusion_matrix(y_true_labels, y_pred_labels)
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            pixel_cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_
        )
        plt.title("Pixel-Level Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        mlflow.log_figure(plt.gcf(), "pixel_confusion_matrix.png")
        plt.close()

        pixel_metrics = {
            "pixel_accuracy": pixel_accuracy,
            "pixel_f1": pixel_f1
        }

        # -----------------------
        # Image-level Metrics
        # -----------------------
        test_df = pd.DataFrame({
            "Sample_num": np.arange(len(y_true_labels)),  
            "Label": y_true_labels,
            "Predicted_Pixel_Label": y_pred_int
        })

        # Majority vote across each Sample_num
        image_predictions = (
            test_df.groupby("Sample_num")["Predicted_Pixel_Label"]
            .apply(lambda x: np.bincount(x).argmax())
            .reset_index()
            .rename(columns={"Predicted_Pixel_Label": "Predicted_Image_Label"})
        )

        # Merge ground truth labels
        image_predictions["Label"] = y_true_labels[:len(image_predictions)]
        image_predictions["Encoded_Label"] = label_encoder.transform(image_predictions["Label"])
        image_predictions["Encoded_Predicted_Label"] = image_predictions["Predicted_Image_Label"]

        # Image-level Accuracy
        image_accuracy = accuracy_score(
            image_predictions["Encoded_Label"],
            image_predictions["Encoded_Predicted_Label"]
        )
        mlflow.log_metric("image_accuracy", image_accuracy)

        # Image-level Confusion Matrix
        image_cm = confusion_matrix(
            image_predictions["Encoded_Label"],
            image_predictions["Encoded_Predicted_Label"]
        )
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            image_cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_
        )
        plt.title("Image-Level Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        mlflow.log_figure(plt.gcf(), "image_confusion_matrix.png")
        plt.close()

        image_metrics = {
            "image_accuracy": image_accuracy
        }

        logging.info("Model evaluation completed successfully.")
        return pixel_metrics, image_metrics

    except Exception as e:
        logging.error(f"Error during model evaluation: {str(e)}")
        raise e
