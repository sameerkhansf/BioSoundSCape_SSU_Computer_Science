from zenml.steps import BaseParameters

class ModelNameConfig(BaseParameters):
    """Model Configurations"""
    model_name: str = "cnn"
    fine_tuning: bool = False
    checkpoint_path: str = "model_checkpoint.h5"
    epochs: int = 10
    batch_size: int = 32