"""Dependency-free synthetic demo of batch-start tile shade correction.

All data and process behavior in this file are fictional. This demonstrates
the model workflow only; it is not a production model or customer evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

CHANNEL_COUNT = 6
CONTEXT_COUNT = 3
OUTPUT_NAMES = ("L*", "a*", "b*", "gloss")
FEATURE_NAMES = tuple(f"channel_{index}" for index in range(1, 7)) + (
    "kiln_offset_min",
    "body_tone_offset",
    "glaze_gloss_offset",
)
OUTPUT_SCALE = (2.0, 2.0, 2.0, 3.0)
CHANNEL_RESPONSE = (
    (4.0, 0.4, 0.2, 0.1),
    (1.0, 3.2, 0.4, 0.1),
    (0.5, 0.5, 4.1, 0.2),
    (-3.1, 0.2, 0.4, 0.1),
    (0.2, 1.5, 0.8, 0.3),
    (0.1, 0.3, 1.2, 1.0),
)
CONTEXT_RESPONSE = (
    (-0.8, 0.1, 0.2, 0.4),
    (0.7, 0.2, -0.1, 0.1),
    (0.1, -0.1, 0.1, 1.2),
)
OUTPUT_BASE = (55.0, 1.0, 8.0, 65.0)
NOISE_SCALE = (0.12, 0.10, 0.12, 0.18)

Vector = tuple[float, ...]
Matrix = list[list[float]]


@dataclass(frozen=True)
class SyntheticDataset:
    features: tuple[Vector, ...]
    outputs: tuple[Vector, ...]
    batch_ids: tuple[int, ...]


@dataclass(frozen=True)
class Evaluation:
    train_batch_count: int
    test_batch_count: int
    train_row_count: int
    test_row_count: int
    rmse_by_output: dict[str, float]
    mae_by_output: dict[str, float]


@dataclass(frozen=True)
class CorrectionRecommendation:
    accepted: bool
    reason: str
    adjusted_channels: Vector | None = None
    predicted_before: Vector | None = None
    predicted_after: Vector | None = None
    predicted_error_before: float | None = None
    predicted_error_after: float | None = None


def synthetic_process_output(
    channels: Vector,
    context: Vector,
    rng: random.Random | None = None,
) -> Vector:
    """Fictional linear response with optional simulated measurement noise."""
    if len(channels) != CHANNEL_COUNT or len(context) != CONTEXT_COUNT:
        raise ValueError("invalid channel or process-context length")
    result = []
    for output_index, baseline in enumerate(OUTPUT_BASE):
        value = baseline
        value += sum(
            (channels[channel_index] - 50.0) * CHANNEL_RESPONSE[channel_index][output_index]
            for channel_index in range(CHANNEL_COUNT)
        )
        value += sum(
            context[context_index] * CONTEXT_RESPONSE[context_index][output_index]
            for context_index in range(CONTEXT_COUNT)
        )
        if rng is not None:
            value += rng.gauss(0.0, NOISE_SCALE[output_index])
        result.append(value)
    return tuple(result)


def generate_synthetic_dataset(
    batch_count: int = 72,
    samples_per_batch: int = 24,
    seed: int = 42,
) -> SyntheticDataset:
    if batch_count < 5 or samples_per_batch < 2:
        raise ValueError("use at least five batches and two samples per batch")
    rng = random.Random(seed)
    features: list[Vector] = []
    outputs: list[Vector] = []
    batch_ids: list[int] = []

    for batch_id in range(batch_count):
        context = (
            rng.uniform(-1.5, 1.5),
            rng.uniform(-2.0, 2.0),
            rng.uniform(-1.0, 1.0),
        )
        for _ in range(samples_per_batch):
            channels = tuple(
                min(100.0, max(0.0, rng.gauss(50.0, 13.0)))
                for _ in range(CHANNEL_COUNT)
            )
            features.append(channels + context)
            outputs.append(synthetic_process_output(channels, context, rng))
            batch_ids.append(batch_id)

    return SyntheticDataset(tuple(features), tuple(outputs), tuple(batch_ids))


def _solve_linear_system(matrix: Matrix, rhs: Matrix) -> Matrix:
    """Solve A X = B using Gaussian elimination with partial pivoting."""
    size = len(matrix)
    augmented = [matrix[row][:] + rhs[row][:] for row in range(size)]
    rhs_columns = len(rhs[0])

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row: abs(augmented[row][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            raise ValueError("training data do not support a stable linear fit")
        augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]
        pivot = augmented[pivot_index][pivot_index]
        augmented[pivot_index] = [value / pivot for value in augmented[pivot_index]]

        for row in range(size):
            if row == pivot_index:
                continue
            factor = augmented[row][pivot_index]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[pivot_index])
            ]

    return [row[size : size + rhs_columns] for row in augmented]


class ShadeCorrectionModel:
    """Ridge linear response model with bounded random-search corrections."""

    def __init__(self, ridge_alpha: float = 0.05) -> None:
        self.ridge_alpha = ridge_alpha
        self._weights: Matrix | None = None
        self._minimum: Vector | None = None
        self._maximum: Vector | None = None

    def fit(self, features: tuple[Vector, ...], outputs: tuple[Vector, ...]) -> "ShadeCorrectionModel":
        if not features or len(features) != len(outputs):
            raise ValueError("features and outputs must have equal non-zero row counts")
        if any(len(row) != len(FEATURE_NAMES) for row in features):
            raise ValueError(f"features must have {len(FEATURE_NAMES)} columns")
        if any(len(row) != len(OUTPUT_NAMES) for row in outputs):
            raise ValueError(f"outputs must have {len(OUTPUT_NAMES)} columns")

        design = [(1.0,) + row for row in features]
        column_count = len(design[0])
        gram = [[0.0] * column_count for _ in range(column_count)]
        cross = [[0.0] * len(OUTPUT_NAMES) for _ in range(column_count)]
        for x_row, y_row in zip(design, outputs):
            for left in range(column_count):
                for right in range(column_count):
                    gram[left][right] += x_row[left] * x_row[right]
                for output_index in range(len(OUTPUT_NAMES)):
                    cross[left][output_index] += x_row[left] * y_row[output_index]

        for diagonal in range(1, column_count):
            gram[diagonal][diagonal] += self.ridge_alpha
        self._weights = _solve_linear_system(gram, cross)
        self._minimum = tuple(min(row[index] for row in features) for index in range(column_count - 1))
        self._maximum = tuple(max(row[index] for row in features) for index in range(column_count - 1))
        return self

    def predict(self, features: tuple[Vector, ...] | list[Vector]) -> tuple[Vector, ...]:
        self._require_fitted()
        assert self._weights is not None
        predictions = []
        for row in features:
            if len(row) != len(FEATURE_NAMES):
                raise ValueError(f"features must have {len(FEATURE_NAMES)} columns")
            augmented = (1.0,) + row
            predictions.append(
                tuple(
                    sum(augmented[index] * self._weights[index][output_index]
                        for index in range(len(augmented)))
                    for output_index in range(len(OUTPUT_NAMES))
                )
            )
        return tuple(predictions)

    def recommend(
        self,
        current_channels: Vector,
        context: Vector,
        target: Vector,
        max_change: float = 12.0,
        candidate_count: int = 8000,
        seed: int = 101,
    ) -> CorrectionRecommendation:
        self._require_fitted()
        if len(current_channels) != CHANNEL_COUNT or len(context) != CONTEXT_COUNT:
            raise ValueError("invalid channel or process-context length")
        if len(target) != len(OUTPUT_NAMES):
            raise ValueError(f"target must have {len(OUTPUT_NAMES)} values")
        if max_change <= 0.0 or candidate_count < 1:
            raise ValueError("search bounds must be positive")

        current_features = current_channels + context
        if not self._inside_training_range(current_features):
            return CorrectionRecommendation(False, "Current recipe or context is outside training coverage.")

        assert self._minimum is not None
        assert self._maximum is not None
        lower = tuple(
            max(0.0, self._minimum[index], current_channels[index] - max_change)
            for index in range(CHANNEL_COUNT)
        )
        upper = tuple(
            min(100.0, self._maximum[index], current_channels[index] + max_change)
            for index in range(CHANNEL_COUNT)
        )
        if any(low > high for low, high in zip(lower, upper)):
            return CorrectionRecommendation(False, "No candidate adjustment within validated bounds.")

        rng = random.Random(seed)
        candidates = [current_channels]
        candidates.extend(
            tuple(rng.uniform(lower[index], upper[index]) for index in range(CHANNEL_COUNT))
            for _ in range(candidate_count)
        )
        candidate_features = tuple(candidate + context for candidate in candidates)
        predictions = self.predict(candidate_features)

        def objective(candidate: Vector, predicted: Vector) -> float:
            output_error = sum(
                ((predicted[index] - target[index]) / OUTPUT_SCALE[index]) ** 2
                for index in range(len(OUTPUT_NAMES))
            )
            change_cost = 0.015 * sum(
                ((candidate[index] - current_channels[index]) / max_change) ** 2
                for index in range(CHANNEL_COUNT)
            )
            return output_error + change_cost

        best_index = min(
            range(len(candidates)),
            key=lambda index: objective(candidates[index], predictions[index]),
        )
        before_error = self._scaled_error(predictions[0], target)
        after_error = self._scaled_error(predictions[best_index], target)
        return CorrectionRecommendation(
            accepted=True,
            reason="Within synthetic training coverage; human review required.",
            adjusted_channels=candidates[best_index],
            predicted_before=predictions[0],
            predicted_after=predictions[best_index],
            predicted_error_before=before_error,
            predicted_error_after=after_error,
        )

    def _inside_training_range(self, features: Vector) -> bool:
        assert self._minimum is not None and self._maximum is not None
        return all(
            self._minimum[index] - 1e-9 <= value <= self._maximum[index] + 1e-9
            for index, value in enumerate(features)
        )

    @staticmethod
    def _scaled_error(actual: Vector, target: Vector) -> float:
        return math.sqrt(
            sum(((actual[index] - target[index]) / OUTPUT_SCALE[index]) ** 2
                for index in range(len(OUTPUT_NAMES)))
        )

    def _require_fitted(self) -> None:
        if self._weights is None or self._minimum is None or self._maximum is None:
            raise RuntimeError("fit the model before predicting or recommending")


def split_by_batch(
    dataset: SyntheticDataset,
    test_fraction: float = 0.25,
    seed: int = 7,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be between zero and one")
    batch_ids = sorted(set(dataset.batch_ids))
    rng = random.Random(seed)
    rng.shuffle(batch_ids)
    test_count = max(1, round(len(batch_ids) * test_fraction))
    test_batches = set(batch_ids[:test_count])
    train_indices = tuple(index for index, batch in enumerate(dataset.batch_ids) if batch not in test_batches)
    test_indices = tuple(index for index, batch in enumerate(dataset.batch_ids) if batch in test_batches)
    return train_indices, test_indices


def train_and_evaluate(
    dataset: SyntheticDataset,
    seed: int = 7,
) -> tuple[ShadeCorrectionModel, Evaluation, tuple[int, ...], tuple[int, ...]]:
    train_indices, test_indices = split_by_batch(dataset, seed=seed)
    model = ShadeCorrectionModel().fit(
        tuple(dataset.features[index] for index in train_indices),
        tuple(dataset.outputs[index] for index in train_indices),
    )
    predictions = model.predict(tuple(dataset.features[index] for index in test_indices))
    errors = tuple(
        tuple(prediction[axis] - dataset.outputs[row_index][axis] for axis in range(len(OUTPUT_NAMES)))
        for prediction, row_index in zip(predictions, test_indices)
    )
    rmse = {
        name: math.sqrt(sum(error[index] ** 2 for error in errors) / len(errors))
        for index, name in enumerate(OUTPUT_NAMES)
    }
    mae = {
        name: sum(abs(error[index]) for error in errors) / len(errors)
        for index, name in enumerate(OUTPUT_NAMES)
    }
    evaluation = Evaluation(
        train_batch_count=len({dataset.batch_ids[index] for index in train_indices}),
        test_batch_count=len({dataset.batch_ids[index] for index in test_indices}),
        train_row_count=len(train_indices),
        test_row_count=len(test_indices),
        rmse_by_output=rmse,
        mae_by_output=mae,
    )
    return model, evaluation, train_indices, test_indices


def run_demo() -> None:
    dataset = generate_synthetic_dataset()
    model, evaluation, _, test_indices = train_and_evaluate(dataset)
    print("SYNTHETIC DEMO ONLY: values and results are fictional.")
    print(
        f"Train: {evaluation.train_row_count} samples / {evaluation.train_batch_count} batches; "
        f"test: {evaluation.test_row_count} samples / {evaluation.test_batch_count} batches"
    )
    print("Held-out prediction errors:")
    for name in OUTPUT_NAMES:
        print(f"  {name}: RMSE={evaluation.rmse_by_output[name]:.3f}, MAE={evaluation.mae_by_output[name]:.3f}")

    context = (0.0,) * CONTEXT_COUNT
    target = synthetic_process_output((50.0,) * CHANNEL_COUNT, context)
    current = (57.0, 45.0, 56.0, 53.0, 47.0, 55.0)
    before = synthetic_process_output(current, context)
    recommendation = model.recommend(current, context, target)
    print("\nExample held-out batch correction:")
    print(f"  master target [L*, a*, b*, gloss]: {[round(value, 2) for value in target]}")
    print(f"  current sample: {[round(value, 2) for value in before]}")
    if not recommendation.accepted or recommendation.adjusted_channels is None:
        print(f"  model abstained: {recommendation.reason}")
        return
    after = synthetic_process_output(recommendation.adjusted_channels, context)
    print(f"  recommended channels: {[round(value, 1) for value in recommendation.adjusted_channels]}")
    print(f"  simulated output after change: {[round(value, 2) for value in after]}")
    print(
        "  synthetic normalized error: "
        f"{ShadeCorrectionModel._scaled_error(before, target):.3f} -> "
        f"{ShadeCorrectionModel._scaled_error(after, target):.3f}"
    )
    print("  Production changes still require client validation and human approval.")


if __name__ == "__main__":
    run_demo()