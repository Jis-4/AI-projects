import json
import tempfile
import unittest
from pathlib import Path

from generative_ai_image_creator.dataset import SyntheticShapesDataset
from generative_ai_image_creator.gan import GANTrainer
from generative_ai_image_creator.io_utils import save_pgm_grid
from generative_ai_image_creator.vae import VAETrainer


class GenerativeAIImageCreatorTests(unittest.TestCase):
    def test_dataset_generation_shape(self):
        dataset = SyntheticShapesDataset(samples_per_class=3, seed=1).generate()
        self.assertEqual(len(dataset), 9)
        self.assertTrue(all(len(sample) == 64 for sample in dataset))
        self.assertTrue(all(0.0 <= pixel <= 1.0 for sample in dataset for pixel in sample))

    def test_vae_train_save_and_sample(self):
        dataset = SyntheticShapesDataset(samples_per_class=2, seed=2).generate()
        trainer = VAETrainer(seed=3)
        history = trainer.train(epochs=1, dataset=dataset)
        self.assertEqual(len(history), 1)
        self.assertTrue(history[0]["loss"] > 0.0)
        samples = trainer.sample(4)
        self.assertEqual(len(samples), 4)
        self.assertEqual(len(samples[0]), 64)

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint = Path(tmpdir) / "vae.json"
            grid = Path(tmpdir) / "vae.pgm"
            trainer.save(checkpoint)
            self.assertTrue(checkpoint.exists())
            reloaded = VAETrainer.load(checkpoint)
            save_pgm_grid(reloaded.sample(4), grid, image_size=8)
            self.assertIn('"latent_dim": 8', checkpoint.read_text(encoding="utf-8"))
            self.assertTrue(grid.exists())
            self.assertTrue(grid.read_text(encoding="utf-8").startswith("P2"))

    def test_gan_train_save_and_sample(self):
        dataset = SyntheticShapesDataset(samples_per_class=2, seed=4).generate()
        trainer = GANTrainer(seed=5)
        history = trainer.train(epochs=1, dataset=dataset)
        self.assertEqual(len(history), 1)
        self.assertTrue(history[0]["generator_loss"] > 0.0)
        self.assertTrue(history[0]["discriminator_loss"] > 0.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint = Path(tmpdir) / "gan.json"
            trainer.save(checkpoint)
            payload = json.loads(checkpoint.read_text(encoding="utf-8"))
            self.assertEqual(payload["noise_dim"], 8)
            reloaded = GANTrainer.load(checkpoint)
            self.assertEqual(len(reloaded.sample(2)), 2)


if __name__ == "__main__":
    unittest.main()
