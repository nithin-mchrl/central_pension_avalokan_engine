import unittest
from .test_base import BaseTest
from dataclasses import replace
from .corpus_growth_calculation import (
    PensionCompareParams,
    YearlyCorpusInfo,
    CorpusInfo,
    get_yearly_accumulated_corpus,
    calculate_salary,
    calculate_accumulated_corpus,
)

class TestPensionFunctions(BaseTest):

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

    def test_calculate_salary(self):
        salary = calculate_salary(50000, 0.5)
        self.assertEqual(salary, 75000)

    def test_get_yearly_accumulated_corpus(self):
        positive_interest, negative_interest, zero_interest = 0.02, -0.02, 0
        monthly_contrib = 10000
        initial_corpus = 100000

        result = get_yearly_accumulated_corpus(
            initial_corpus, positive_interest, monthly_contrib
        )
        self.assertGreater(result, initial_corpus + (12 * monthly_contrib))
        result = get_yearly_accumulated_corpus(
            initial_corpus, negative_interest, monthly_contrib
        )
        self.assertLess(result, initial_corpus + (12 * monthly_contrib))

        result = get_yearly_accumulated_corpus(
            initial_corpus, zero_interest, monthly_contrib
        )
        self.assertEqual(result, initial_corpus + (12 * monthly_contrib))

    def test_calculate_accumulated_corpus_first_year(self):
        first_year_info = calculate_accumulated_corpus(0, self.params, None)
        self.assertIsInstance(first_year_info, YearlyCorpusInfo)
        self.assertEqual(first_year_info.salary, 75000)

    def test_calculate_accumulated_corpus_next_year(self):
        # make expected nps retruns zero to simplyfy asseritions
        modified_params = replace(
            self.params,
            expected_nps_return = 0,
            expected_benchmark_corpus_return = 0,
        )
        # Create first year's info
        # Test 4 year no return growth to verify 
        # correct addition over the years
        
        prev_info = calculate_accumulated_corpus(0, modified_params, None)
        info = calculate_accumulated_corpus(1, modified_params, prev_info)
        accumulated_nps_for_the_year = 12 * info.monthly_nps_contrib
        self.assertEqual(
            info.nps_corpus, prev_info.nps_corpus + accumulated_nps_for_the_year)
        accumulated_ups_for_the_year = 12 * info.monthly_ups_contrib
        self.assertEqual(
            info.ups_corpus, prev_info.ups_corpus + accumulated_ups_for_the_year)
        accumulated_benchmark_c_for_the_year = 12 * info.monthly_ups_contrib
        self.assertEqual(
            info.benchmark_corpus, prev_info.benchmark_corpus + accumulated_benchmark_c_for_the_year)

    def test_corpus_history_add_and_last(self):
        history = CorpusInfo()
        self.assertIsNone(history.last())  # empty case
        info = calculate_accumulated_corpus(0, self.params, None)
        history.add(info)
        self.assertEqual(len(history), 1)
        self.assertEqual(history.last(), info)

    def test_corpus_history_as_list_of_dict(self):
        history = CorpusInfo()
        info = calculate_accumulated_corpus(0, self.params, None)
        history.add(info)
        dict_list = history.as_list_of_dict()
        self.assertIsInstance(dict_list, list)
        self.assertIsInstance(dict_list[0], dict)
        test_keys = (
            "nps_corpus",
            "basic_pay",
            "da_rate",
            "next_year_basic_pay",
            "next_year_da_rate",
            "ups_corpus",
            "benchmark_corpus",
        )
        for test_key in test_keys:
            with self.subTest(test_key=test_key):
                self.assertIn(test_key, dict_list[0])


if __name__ == "__main__":
    unittest.main()

