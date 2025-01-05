from pipelines.training_pipeline import train_pipeline
from steps.ingest_data import ingest_data
from steps.clean_data import clean_data
from steps.model_train import model_train
from steps.evaluation import evaluation
from zenml.integrations.mlflow.mlflow_utils import get_tracking_uri

if __name__ == "__main__":
    DATA_PATH = "data/samples.csv"

    training = train_pipeline(
        ingest_data=lambda: ingest_data(data_path=DATA_PATH),
        clean_data=clean_data,  
        model_train=model_train,
        evaluation=evaluation,
    )

    # Run the pipeline
    training.run()

    print(
        "Now run \n "
        f"    mlflow ui --backend-store-uri '{get_tracking_uri()}'\n"
        "To inspect your experiment runs within the mlflow UI.\n"
        "You can find your runs tracked within the `mlflow_example_pipeline`"
        "experiment. Here you'll also be able to compare the two runs."
    )
