from dataclasses import dataclass

@dataclass
class PensionCompareParams:
    current_service: int
    years_to_retire: int
    current_basic_pay: float
    current_da_rate: float
    current_total_nps_corpus: float
    withdrawal_percentage: float
    current_annual_expense: float

    expected_da_hike: float = 0.05
    expected_basic_pay_hike: float = 0.05
    expected_nps_return: float = 0.10
    expected_benchmark_corpus_return: float = 0.08
    expected_annuity_rate: float = 0.06
    expected_ups_pension_growth: float = 0.05
    expected_rate_of_return_nps_corpus_after_retirement: float = 0.07
    expected_rate_of_inflation: float = 0.05

