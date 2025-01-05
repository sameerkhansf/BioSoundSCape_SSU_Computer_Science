from zenml.config.strict_base_model import StrictBaseModel

class ModelNameConfig(StrictBaseModel):
    """Model Configurations"""
    model_name: str = "cnn"
    fine_tuning: bool = False
    checkpoint_path: str = "1D_model_checkpoint.weights.h5"
    epochs: int = 10
    batch_size: int = 32