import unittest
from pathlib import Path

from tests.test_snippets import TestSnippets


def run_tests(path: Path = Path("tests")):
    suite = unittest.TestLoader().discover(
        start_dir=path.absolute().as_posix(),
        pattern="test_*.py",
    )

    ######################################################
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSnippets)
    ######################################################

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        exit(1)


if __name__ == "__main__":
    run_tests()
