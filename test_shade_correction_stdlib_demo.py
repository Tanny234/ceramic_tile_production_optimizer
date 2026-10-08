import unittest

from shade_correction_stdlib_demo import (
    CHANNEL_COUNT,
    CONTEXT_COUNT,
    OUTPUT_NAMES,
    ShadeCorrectionModel,
    generate_synthetic_dataset,
    synthetic_process_output,
    train_and_evaluate,
)


class ShadeCorrectionDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = generate_synthetic_dataset(batch_count=36, samples_per_batch=20)
        cls.model, cls.evaluation, cls.train_indices, cls.test_indices = train_and_evaluate(cls.dataset)

    def test_batch_split_has_no_leakage(self) -> None:
        train_batches = {self.dataset.batch_ids[index] for index in self.train_indices}
        test_batches = {self.dataset.batch_ids[index] for index in self.test_indices}
        self.assertFalse(train_batches & test_batches)

    def test_held_out_prediction_error_is_reasonable_for_synthetic_process(self) -> None:
        self.assertEqual(set(self.evaluation.rmse_by_output), set(OUTPUT_NAMES))
        self.assertLess(max(self.evaluation.rmse_by_output.values()), 0.5)

    def test_recommendation_is_bounded_and_improves_synthetic_error(self) -> None:
        context = self.dataset.features[self.test_indices[0]][CHANNEL_COUNT:]
        initial = (57.0, 45.0, 56.0, 53.0, 47.0, 55.0)
        target = synthetic_process_output((50.0,) * CHANNEL_COUNT, (0.0,) * CONTEXT_COUNT)
        recommendation = self.model.recommend(initial, context, target)

        self.assertTrue(recommendation.accepted)
        self.assertIsNotNone(recommendation.adjusted_channels)
        assert recommendation.adjusted_channels is not None
        self.assertTrue(all(0.0 <= value <= 100.0 for value in recommendation.adjusted_channels))
        self.assertTrue(all(abs(value - old) <= 12.0 for value, old in zip(recommendation.adjusted_channels, initial)))

        initial_output = synthetic_process_output(initial, context)
        adjusted_output = synthetic_process_output(recommendation.adjusted_channels, context)
        self.assertLess(
            ShadeCorrectionModel._scaled_error(adjusted_output, target),
            ShadeCorrectionModel._scaled_error(initial_output, target),
        )

    def test_model_abstains_outside_training_context(self) -> None:
        recommendation = self.model.recommend(
            (50.0,) * CHANNEL_COUNT,
            (99.0, 0.0, 0.0),
            (55.0, 1.0, 8.0, 65.0),
        )
        self.assertFalse(recommendation.accepted)
        self.assertIn("outside training coverage", recommendation.reason)

    def test_unfitted_model_cannot_predict(self) -> None:
        with self.assertRaises(RuntimeError):
            ShadeCorrectionModel().predict(((0.0,) * (CHANNEL_COUNT + CONTEXT_COUNT),))


if __name__ == "__main__":
    unittest.main()