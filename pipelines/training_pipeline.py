from zenml.config import DockerSettings
from zenml.integrations.constants import MLFLOW
from zenml.pipelines import pipeline

docker_settings = DockerSettings(required_integrations=[MLFLOW])


@pipeline(enable_cache=False, settings={"docker": docker_settings})
def train_pipeline(ingest_data, clean_data, model_train, evaluation, visualization):
    """
    A ZenML pipeline for data ingestion, preprocessing, model training, evaluation, and visualization.

    Args:
        ingest_data: Step that ingests raw data and returns a DataFrame.
        clean_data: Step for data cleaning and splitting into training and testing sets.
        model_train: Step to train the model and return the trained model.
        evaluation: Step to evaluate the model using pixel-level and image-level metrics.
        visualization: Step for visualizing training curves, confusion matrices, and classification reports.

    Returns:
        A tuple of evaluation metrics including pixel-level and image-level metrics.
    """
    # Step 1: Data Ingestion
    df = ingest_data()

    # Step 2: Data Cleaning and Splitting
    x_train, x_test, y_train, y_test, label_encoder = clean_data(df)

    # Step 3: Model Training
    model, history = model_train(x_train, y_train, x_test, y_test)

    # Step 4: Model Evaluation
    pixel_metrics, image_metrics = evaluation(model, x_test, y_test, label_encoder)

    # Step 5: Visualization
    visualization(model, history, pixel_metrics, image_metrics, x_test, y_test, label_encoder)

    return pixel_metrics, image_metrics
