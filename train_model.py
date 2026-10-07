"""Train and export a multi-output career matching model."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


DATASET_PATH = Path("it_career_matching_dataset.csv")
MODEL_PATH = Path("career_model_pipeline.joblib")
RANDOM_STATE = 42
CATEGORICAL_FEATURES = ["Q1_Zodiac", "Q2_MBTI", "Q3_Energy", "Q4_Personality"]
BEHAVIORAL_FEATURES = [
    "Q5_Event_Role",
    "Q6_Assembly_Style",
    "Q7_Puzzle_Approach",
    "Q8_Tech_Preference",
    "Q9_Learning_Style",
    "Q10_Cleaning_Style",
    "Q11_Proud_Compliment",
]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + BEHAVIORAL_FEATURES

# Column names used by older versions of this repository's data generator.
LEGACY_BEHAVIORAL_COLUMNS = [
    "Q5_Assembly_Style",
    "Q6_Trip_Role",
    "Q7_Puzzle_Feeling",
    "Q8_Cleaning_Style",
    "Q9_Games_Activities",
    "Q10_Learning_Style",
    "Q11_Frustration",
    "Q12_Proud_Compliment",
]


def load_dataset(path=DATASET_PATH):
    """Load expected 11-question data and validate feature and target schema."""
    df = pd.read_csv(path)
    if not set(FEATURE_COLUMNS).issubset(df.columns):
        # Support the immediately preceding 11-question generator schema by
        # renaming its eight behavioral fields into the current seven fields.
        # Older nine-option A–I data cannot represent the new five-option quiz.
        if all(name in df.columns for name in LEGACY_BEHAVIORAL_COLUMNS):
            df = df.rename(
                columns=dict(zip(LEGACY_BEHAVIORAL_COLUMNS, BEHAVIORAL_FEATURES))
            )
        else:
            missing = sorted(set(FEATURE_COLUMNS) - set(df.columns))
            raise ValueError(
                "Dataset does not match the updated 11-question schema. "
                f"Missing feature columns: {missing}. Regenerate it with "
                "generate_it_career_dataset.py."
            )

    target_columns = [column for column in df.columns if column.startswith("Role_")]
    if len(target_columns) != 9:
        raise ValueError(f"Expected 9 Role_ target columns, found {len(target_columns)}")

    for column in CATEGORICAL_FEATURES:
        if df[column].isna().any():
            raise ValueError(f"Feature {column} contains missing values")
        df[column] = df[column].astype(str)

    for column in BEHAVIORAL_FEATURES:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isna().any() or not values.isin(range(5)).all():
            raise ValueError(
                f"Feature {column} must contain integer option indices from 0 to 4"
            )
        df[column] = values.astype(int)

    targets = df[target_columns].apply(pd.to_numeric, errors="coerce")
    if targets.isna().any().any() or not np.isfinite(targets.to_numpy()).all():
        raise ValueError("Role targets must contain finite numeric probabilities")
    if (targets < 0).any().any():
        raise ValueError("Role target probabilities cannot be negative")

    return df, target_columns


def prepare_features(df):
    """One-hot encode categorical profiles and preserve integer answers."""
    categorical = pd.get_dummies(df[CATEGORICAL_FEATURES], dtype=int)
    behavioral = df[BEHAVIORAL_FEATURES].astype(int)
    return pd.concat([categorical, behavioral], axis=1)


def normalize_predictions(predictions):
    """Clip invalid negatives and normalize each prediction row to a distribution."""
    values = np.asarray(predictions, dtype=float)
    values = np.clip(values, 0.0, None)
    row_sums = values.sum(axis=1, keepdims=True)
    zero_rows = row_sums[:, 0] == 0
    if zero_rows.any():
        values[zero_rows] = 1.0 / values.shape[1]
        row_sums = values.sum(axis=1, keepdims=True)
    normalized = values / row_sums
    # Eliminate floating point summation drift in the final role column.
    normalized[:, -1] = 1.0 - normalized[:, :-1].sum(axis=1)
    return normalized


def main():
    df, target_columns = load_dataset()
    x = prepare_features(df)
    y = df[target_columns].to_numpy(dtype=float)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.20, random_state=RANDOM_STATE
    )
    model = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE)
    model.fit(x_train, y_train)

    raw_predictions = model.predict(x_test)
    y_pred = normalize_predictions(raw_predictions)
    y_true = normalize_predictions(y_test)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    true_top1 = np.argmax(y_true, axis=1)
    predicted_top1 = np.argmax(y_pred, axis=1)
    top1_accuracy = np.mean(predicted_top1 == true_top1) * 100.0
    predicted_top3 = np.argsort(y_pred, axis=1)[:, -3:]
    top3_accuracy = np.mean(
        [true_top1[index] in predicted_top3[index] for index in range(len(true_top1))]
    ) * 100.0

    print("Evaluation metrics")
    print(f"MAE: {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"Top-1 Accuracy: {top1_accuracy:.2f}%")
    print(f"Top-3 Accuracy: {top3_accuracy:.2f}%")

    # Build a valid categorical profile from known dataset values. Option index
    # 1 on each behavioral question is the requested pure UI/UX bias case.
    sanity_case = {
        column: df[column].iloc[0] for column in CATEGORICAL_FEATURES
    }
    sanity_case.update({column: 1 for column in BEHAVIORAL_FEATURES})
    sanity_frame = pd.DataFrame([sanity_case])
    sanity_features = pd.get_dummies(sanity_frame, columns=CATEGORICAL_FEATURES, dtype=int)
    sanity_features = sanity_features.reindex(columns=x.columns, fill_value=0)
    sanity_prediction = normalize_predictions(model.predict(sanity_features))[0]

    role_names = [column.removeprefix("Role_") for column in target_columns]
    ui_ux_index = role_names.index("UI_UX_Design")
    ui_ux_probability = float(sanity_prediction[ui_ux_index])
    sanity_top_role = role_names[int(np.argmax(sanity_prediction))]
    print("\nSanity check: all behavioral choices = option 1")
    print(f"Top role: {sanity_top_role}")
    print(f"Role_UI_UX_Design: {ui_ux_probability * 100.0:.2f}%")
    if sanity_top_role != "UI_UX_Design" or ui_ux_probability <= 0.70:
        raise AssertionError(
            "Pure UI/UX bias sanity check failed: expected UI_UX_Design at #1 "
            "with probability greater than 70%."
        )

    percentage_sum = float((sanity_prediction * 100.0).sum())
    print(f"Sanity check: predicted role percentages sum to {percentage_sum:.10f}%")
    if not np.isclose(percentage_sum, 100.0, rtol=0.0, atol=1e-10):
        raise AssertionError("Predicted role percentages do not sum to 100%")

    joblib.dump(
        {
            "model": model,
            "feature_columns": list(x.columns),
            "target_roles": role_names,
            "categorical_features": CATEGORICAL_FEATURES,
            "behavioral_features": BEHAVIORAL_FEATURES,
        },
        MODEL_PATH,
    )
    print(f"\nSuccess: trained model, feature layout, and target roles saved to {MODEL_PATH}")
    print(f"Training rows: {len(x_train)} | Test rows: {len(x_test)} | Roles: {len(role_names)}")


if __name__ == "__main__":
    main()
