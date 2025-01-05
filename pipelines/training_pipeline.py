from zenml.config import DockerSettings
from zenml.integrations.constants import MLFLOW
from zenml.pipelines import pipeline

docker_settings = DockerSettings(required_integrations=[MLFLOW])


@pipeline(enable_cache=False, settings={"docker": docker_settings})
def train_pipeline(ingest_data, clean_data, model_train, evaluation):
    """
    A ZenML pipeline for data ingestion, preprocessing, model training, and evaluation.

    Args:
        ingest_data: Step for data ingestion.
        clean_data: Step for cleaning and splitting data.
        model_train: Step for training the model.
        evaluation: Step for evaluating the model.

    Returns:
        A dictionary of evaluation metrics.
    """
    # Data ingestion
    df = ingest_data()

    # Data cleaning and splitting
    clean_data_outputs = clean_data(data=df)
    X_train, X_test, y_train, y_test, label_encoder = clean_data_outputs

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
