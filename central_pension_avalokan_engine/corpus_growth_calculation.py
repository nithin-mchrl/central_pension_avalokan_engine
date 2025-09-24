from typing import Optional

from .pension_compare_params import PensionCompareParams
from .corpus_info import YearlyCorpusInfo, CorpusInfo
# ---------------------------
# Constants
# ------------------------------------------
NPS_CONTRIB_RATE = 0.24
UPS_CONTRIB_RATE = 0.20


# ------------------------------------------
# Helper Functions
# ------------------------------------------
def calculate_salary(basic_pay: float, da_rate: float) -> float:
    """Calculate gross salary including DA."""
    return basic_pay * (1 + da_rate)


def get_yearly_accumulated_corpus(
    initial_corpus: float, return_rate: float, monthly_contrib: float
) -> float:
    r = return_rate / 12
    n = 12

    if r == 0:
        return initial_corpus + monthly_contrib * n

    fv_corpus = initial_corpus * (1 + r)**n
    fv_contrib = monthly_contrib * (((1 + r)**n - 1) / r)
    return fv_corpus + fv_contrib

# ------------------------------------------
# Annual Calculation
# ------------------------------------------
def calculate_accumulated_corpus(
    calculation_year: int,
    params: PensionCompareParams,
    last_year_corpus_info: Optional[YearlyCorpusInfo] = None
) -> YearlyCorpusInfo:
    if last_year_corpus_info is None:
        annual_expense = params.current_annual_expense * (
            1 + params.expected_rate_of_inflation
            )
        basic_pay = params.current_basic_pay
        da_rate = params.current_da_rate
        start_nps_corpus = start_ups_corpus = start_benchmark_corpus = params.current_total_nps_corpus
    else:
        annual_expense = last_year_corpus_info.annual_expense * (
            1 + params.expected_rate_of_inflation
            )
        basic_pay = last_year_corpus_info.next_year_basic_pay
        da_rate = last_year_corpus_info.next_year_da_rate
        start_nps_corpus = last_year_corpus_info.nps_corpus
        start_ups_corpus = last_year_corpus_info.ups_corpus
        start_benchmark_corpus = last_year_corpus_info.benchmark_corpus

    salary = calculate_salary(basic_pay, da_rate)

    # Contributions
    nps_contrib = salary * NPS_CONTRIB_RATE
    ups_contrib = salary * UPS_CONTRIB_RATE
    benchmark_contrib = ups_contrib  # same as UPS

    # Next year projections
    next_year_basic_pay = basic_pay * (1 + params.expected_basic_pay_hike)
    next_year_da_rate = da_rate + params.expected_da_hike

    return YearlyCorpusInfo(
        year=calculation_year + 1,
        basic_pay=basic_pay,
        da_rate=da_rate,
        salary=salary,
        next_year_basic_pay=next_year_basic_pay,
        next_year_da_rate=next_year_da_rate,
        annual_expense=annual_expense,
        monthly_nps_contrib=nps_contrib,
        monthly_ups_contrib=ups_contrib,
        monthly_benchmark_contrib=benchmark_contrib,
        nps_corpus=get_yearly_accumulated_corpus(start_nps_corpus, params.expected_nps_return, nps_contrib),
        ups_corpus=get_yearly_accumulated_corpus(start_ups_corpus, params.expected_nps_return, ups_contrib),
        benchmark_corpus=get_yearly_accumulated_corpus(start_benchmark_corpus, params.expected_benchmark_corpus_return, benchmark_contrib),
    )

