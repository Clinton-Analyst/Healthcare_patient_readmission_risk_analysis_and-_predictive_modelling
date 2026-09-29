import argparse
import json
from pathlib import Path

import joblib


BACKEND_DIR = Path(__file__).parent
DEFAULT_MODEL_PATH = BACKEND_DIR / "model" / "readmission_logistic_model.pkl"
DEFAULT_OUTPUT_PATH = BACKEND_DIR / "model" / "readmission_logistic_model.json"


def export_model(model_path: Path, output_path: Path) -> None:
    pipeline = joblib.load(model_path)
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["model"]
    numeric_features = list(preprocessor.transformers_[0][2])
    categorical_features = list(preprocessor.transformers_[1][2])
    scaler = preprocessor.named_transformers_["num"].named_steps["scaler"]
    encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]

    portable_model = {
        "model_version": "1.0.0",
        "numeric_features": numeric_features,
        "numeric_mean": scaler.mean_.tolist(),
        "numeric_scale": scaler.scale_.tolist(),
        "categorical_features": categorical_features,
        "categories": [categories.tolist() for categories in encoder.categories_],
        "coefficients": classifier.coef_[0].tolist(),
        "intercept": float(classifier.intercept_[0]),
    }
    output_path.write_text(
        json.dumps(portable_model, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Portable model written to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the trained pipeline for pure-Python inference."
    )
    parser.add_argument("model", nargs="?", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT_PATH)
    arguments = parser.parse_args()
    export_model(arguments.model, arguments.output)


if __name__ == "__main__":
    main()