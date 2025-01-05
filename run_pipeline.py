from pipelines.training_pipeline import train_pipeline
from zenml.integrations.mlflow.mlflow_utils import get_tracking_uri

def main():
    """
    Main entry point to run the training pipeline. This pipeline will:
      1. Ingest data from the specified CSV.
      2. Clean and preprocess the data.
      3. Train a CNN model.
      4. Evaluate the model with both pixel-level and image-level metrics.
    """
    # Instantiate the pipeline
    training_pipeline_instance = train_pipeline()

    # Execute the pipeline
    training_pipeline_instance.run()

    print(
        "Now run \n "
        f"    mlflow ui --backend-store-uri '{get_tracking_uri()}'\n"
        "to inspect your experiment runs within the MLflow UI.\n"
        "You can find your runs tracked within the `mlflow_example_pipeline` "
        "experiment. Here you'll also be able to compare multiple runs."
    )

if __name__ == "__main__":
    main()
