import logging
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error, r2_score, accuracy_score, f1_score,
    confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns


class Evaluation(ABC):
    """
    Abstract base class defining the strategy for evaluating model performance.
    """

    @abstractmethod
    def calculate_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate a performance score based on true and predicted values.

        Args:
            y_true (np.ndarray): Array of ground truth values.
            y_pred (np.ndarray): Array of predicted values.

        Returns:
            float: The calculated score.
        """
        pass

    @abstractmethod
    def visualize(self, y_true: np.ndarray, y_pred: np.ndarray, **kwargs):
        """
        Visualize the performance metrics.

        Args:
            y_true (np.ndarray): Array of ground truth values.
            y_pred (np.ndarray): Array of predicted values.
            kwargs: Additional parameters for visualization.
        """
        pass


class MSE(Evaluation):
    """
    Evaluation strategy for regression using Mean Squared Error (MSE).
    """

    def calculate_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate the Mean Squared Error (MSE).

        Args:
            y_true (np.ndarray): Ground truth values.
            y_pred (np.ndarray): Predicted values.

        Returns:
            float: The MSE value.
        """
        try:
            logging.info("Calculating MSE...")
            mse = mean_squared_error(y_true, y_pred)
            logging.info(f"MSE: {mse}")
            return mse
        except Exception as e:
            logging.error(f"Error calculating MSE: {str(e)}")
            raise e

    def visualize(self, y_true: np.ndarray, y_pred: np.ndarray, **kwargs):
        # No visualization specific to MSE
        pass


class R2Score(Evaluation):
    """
    Evaluation strategy for regression using R-squared (R2) score.
    """

    def calculate_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate the R2 score.

        Args:
            y_true (np.ndarray): Ground truth values.
            y_pred (np.ndarray): Predicted values.

        Returns:
            float: The R2 score value.
        """
        try:
            logging.info("Calculating R2 Score...")
            r2 = r2_score(y_true, y_pred)
            logging.info(f"R2 Score: {r2}")
            return r2
        except Exception as e:
            logging.error(f"Error calculating R2 Score: {str(e)}")
            raise e

    def visualize(self, y_true: np.ndarray, y_pred: np.ndarray, **kwargs):
        # No visualization specific to R2 Score
        pass


class ClassificationMetrics(Evaluation):
    """
    Evaluation strategy for classification tasks, including pixel-level and
    image-level metrics.

    Supports metrics such as accuracy, F1-score, confusion matrix, and
    classification report.
    """

    def calculate_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate pixel-level accuracy as the primary metric for classification.

        Args:
            y_true (np.ndarray): Ground truth labels.
            y_pred (np.ndarray): Predicted labels.

        Returns:
            float: Pixel-level accuracy.
        """
        try:
            logging.info("Calculating Pixel-Level Accuracy...")
            accuracy = accuracy_score(y_true, y_pred)
            logging.info(f"Pixel-Level Accuracy: {accuracy}")
            return accuracy
        except Exception as e:
            logging.error(f"Error calculating Pixel-Level Accuracy: {str(e)}")
            raise e

    def calculate_image_level_metrics(self, test_df: pd.DataFrame, label_encoder) -> dict:
        """
        Calculate image-level accuracy and confusion matrix using majority voting.

        Args:
            test_df (pd.DataFrame): DataFrame with pixel-level predictions.
            label_encoder: LabelEncoder instance for encoding/decoding class labels.

        Returns:
            dict: Contains image-level accuracy and confusion matrix.
        """
        try:
            # Aggregate predictions per image
            image_predictions = (
                test_df.groupby('Sample_num')['Predicted_Pixel_Label']
                .apply(lambda x: np.bincount(x).argmax())  # Majority vote
                .reset_index()
                .rename(columns={'Predicted_Pixel_Label': 'Predicted_Image_Label'})
            )

            # Merge ground truth labels
            ground_truth_mapping = test_df[['Sample_num', 'Label']].drop_duplicates()
            image_predictions = image_predictions.merge(
                ground_truth_mapping, on='Sample_num', how='left'
            )

            # Encode labels
            image_predictions['Encoded_Label'] = label_encoder.transform(image_predictions['Label'])
            image_predictions['Encoded_Predicted_Label'] = image_predictions['Predicted_Image_Label']

            # Calculate image-level accuracy
            correct_predictions = (
                image_predictions['Encoded_Label'] == image_predictions['Encoded_Predicted_Label']
            )
            image_accuracy = correct_predictions.mean()
            logging.info(f"Image-Level Accuracy: {image_accuracy}")

            # Compute confusion matrix
            image_conf_matrix = confusion_matrix(
                image_predictions['Encoded_Label'],
                image_predictions['Encoded_Predicted_Label'],
                labels=range(len(label_encoder.classes_)),
            )

            return {
                "image_accuracy": image_accuracy,
                "image_confusion_matrix": image_conf_matrix,
            }
        except Exception as e:
            logging.error(f"Error calculating Image-Level Metrics: {str(e)}")
            raise e

    def visualize(self, y_true: np.ndarray, y_pred: np.ndarray, **kwargs):
        """
        Visualize classification metrics, including confusion matrix and
        classification report.

        Args:
            y_true (np.ndarray): Ground truth labels.
            y_pred (np.ndarray): Predicted labels.
            kwargs: Optional parameters such as label_encoder and class_names.
        """
        label_encoder = kwargs.get("label_encoder", None)
        class_names = kwargs.get("class_names", None)

        try:
            if label_encoder:
                y_true = label_encoder.inverse_transform(y_true)
                y_pred = label_encoder.inverse_transform(y_pred)

            # Confusion Matrix
            cm = confusion_matrix(y_true, y_pred)
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                        xticklabels=class_names, yticklabels=class_names)
            plt.xlabel("Predicted Labels")
            plt.ylabel("True Labels")
            plt.title("Confusion Matrix")
            plt.show()

            # Classification Report
            report = classification_report(y_true, y_pred, target_names=class_names)
            logging.info(f"Classification Report:\n{report}")
            print(f"Classification Report:\n{report}")
        except Exception as e:
            logging.error(f"Error visualizing classification metrics: {str(e)}")
            raise e


class TrainingVisualizer:
    """
    Utility class for visualizing training progress, including accuracy and loss curves.
    """

    @staticmethod
    def plot_training_curves(history, model_name="Model"):
        """
        Plot training and validation accuracy and loss over epochs.

        Args:
            history: Training history object from Keras.
            model_name (str): Name of the model for labeling plots.
        """
        try:
            plt.figure(figsize=(12, 5))

            # Accuracy
            plt.subplot(1, 2, 1)
            plt.plot(history.history['accuracy'], label='Train Accuracy', marker='o')
            plt.plot(history.history['val_accuracy'], label='Validation Accuracy', marker='o')
            plt.title(f'{model_name} Accuracy')
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.legend()
            plt.grid(True)

            # Loss
            plt.subplot(1, 2, 2)
            plt.plot(history.history['loss'], label='Train Loss', marker='o')
            plt.plot(history.history['val_loss'], label='Validation Loss', marker='o')
            plt.title(f'{model_name} Loss')
            plt.xlabel('Epoch')
            plt.ylabel('Loss')
            plt.legend()
            plt.grid(True)

            plt.tight_layout()
            plt.show()
        except Exception as e:
            logging.error(f"Error plotting training curves: {str(e)}")
            raise e
