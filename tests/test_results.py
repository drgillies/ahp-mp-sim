import io
import unittest
from contextlib import redirect_stdout

import pandas as pd

from src.simulation.results import summarize_results


class ResultsTests(unittest.TestCase):
    def test_summarize_results_prints_summary(self) -> None:
        df = pd.DataFrame({"value": [1, 2, 3]})
        buf = io.StringIO()

        with redirect_stdout(buf):
            summarize_results(df)

        output = buf.getvalue()
        self.assertIn("Simulation Results Summary", output)
        self.assertIn("value", output)


if __name__ == "__main__":
    unittest.main()
