import unittest


@unittest.skip(
    "Embedding tests are optional (heavy deps). Enable when torch/transformers are installed."
)
class TestEmbed(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

