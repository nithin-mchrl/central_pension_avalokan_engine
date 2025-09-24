import unittest
from .test_base import BaseTest
from .core import get_corpus_info, CorpusInfo

class TestPensionFunctions(BaseTest):
    def test_get_corpus_info(self):
        history = get_corpus_info(self.params)
        n = len(history)
        self.assertIsInstance(history, CorpusInfo)
        self.assertEqual(n, self.params.years_to_retire)
        final = history.last()
        self.assertAlmostEqual(
            final.next_year_basic_pay,
            self.params.current_basic_pay* (1 +  self.params.expected_basic_pay_hike)**n,
            places = 6,
        )
        self.assertAlmostEqual(
            final.next_year_da_rate,
            self.params.current_da_rate + (self.params.expected_da_hike * n),
            places = 6,
        )


if __name__ == "__main__":
    unittest.main()

