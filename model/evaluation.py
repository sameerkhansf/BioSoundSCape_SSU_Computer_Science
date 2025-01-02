import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

class HyperspectralEvaluator:
    """
    Utility class to evaluate hyperspectral classification models.
    """

    def __init__(self, label_encoder):
        self.label_encoder = label_encoder

    def evaluate_model(self, model, X_test, y_test_cat):
        """
        Evaluate model performance on test data, prints final accuracy.
        """
        test_loss, test_accuracy = model.evaluate(X_test, y_test_cat, verbose=1)
        logging.info(f"Test Accuracy: {test_accuracy:.4f}")
        return test_accuracy

    def confusion_matrix_plot(self, y_true, y_pred, title="Confusion Matrix"):
        """
        Plots a confusion matrix for the given y_true & y_pred (string labels).
        """
        y_true_enc = self.label_encoder.transform(y_true)
        y_pred_enc = self.label_encoder.transform(y_pred)
        cm = confusion_matrix(y_true_enc, y_pred_enc, labels=range(len(self.label_encoder.classes_)))

        plt.figure(figsize=(10,8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=self.label_encoder.classes_,
                    yticklabels=self.label_encoder.classes_)
        plt.title(title)
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.show()

    def classification_report(self, y_true, y_pred):
        """Prints a classification report."""
        print(classification_report(y_true, y_pred, target_names=self.label_encoder.classes_))
