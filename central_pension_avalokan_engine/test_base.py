import unittest

from .pension_compare_params import PensionCompareParams

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.params = PensionCompareParams(
            current_service=10,
            years_to_retire=5,
            current_basic_pay=50000,
            current_da_rate=0.5,
            current_total_nps_corpus=1000000,
            withdrawal_percentage=0.6,
            current_annual_expense=300000,
            expected_basic_pay_hike=0.05,
            expected_da_hike=0.05,
            expected_nps_return=0.10,
            expected_benchmark_corpus_return=0.08,
            expected_annuity_rate=0.06,
            expected_ups_pension_growth=0.05,
            expected_rate_of_return_nps_corpus_after_retirement=0.07,
            expected_rate_of_inflation=0.05,
        )

