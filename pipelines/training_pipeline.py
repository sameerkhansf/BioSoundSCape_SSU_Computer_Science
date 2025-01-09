from zenml.config import DockerSettings
from zenml.integrations.constants import MLFLOW
from zenml.pipelines import pipeline

from steps.ingest_data import ingest_data
from steps.clean_data import clean_data
from steps.model_train import model_train
from steps.evaluation import evaluation

# Configure Docker settings to include MLflow integration
docker_settings = DockerSettings(required_integrations=[MLFLOW])

# The path to our CSV data file
DATA_PATH = "data/samples.csv"


@pipeline(enable_cache=True, settings={"docker": docker_settings})
def train_pipeline():
    """
    A ZenML pipeline for data ingestion, preprocessing, model training, and evaluation.
    
    Caching is enabled, so if the input data or step outputs do not change
    between runs, ZenML will skip re-running those steps.

    Steps:
      1. ingest_data: Read data from a CSV file.
      2. clean_data: Preprocess and split the data into training and testing sets.
      3. model_train: Train a CNN model on the clean data.
      4. evaluation: Evaluate the model at pixel-level and image-level, 
         logging metrics (accuracy, F1, confusion matrices) to MLflow.
    """
    # Data ingestion
    df = ingest_data(data_path=DATA_PATH)

    # Data cleaning and splitting
    X_train, X_test, y_train, y_test, label_encoder = clean_data(data=df)

    # Model training
    model = model_train(
        x_train=X_train, 
        y_train=y_train, 
        x_test=X_test, 
        y_test=y_test
    )

    # Model evaluation
    pixel_metrics, image_metrics = evaluation(
        model=model, 
        x_test=X_test, 
        y_test=y_test, 
        label_encoder=label_encoder
    )

    return {"pixel_metrics": pixel_metrics, "image_metrics": image_metrics}
