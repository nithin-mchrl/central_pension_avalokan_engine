from dataclasses import dataclass


@dataclass
class PensionCompareParams:
    current_service: int
    years_to_retire: int
    expected_year_in_retirement: int
    current_basic_pay: float
    current_da_rate: float
    current_monthly_nps_contribution: float
    current_total_nps_corpus: float
    expected_da_hike: float = 0.05
    expected_basic_pay_hike: float = 0.05
    expected_growth_in_nps_contribution: float = 0.1
    expected_nps_return: float = 0.1
    expected_benchmark_corpus_return: float = 0.08
    expected_annuity_rate: float = 0.06
    expected_ups_pension_growth: float = 0.05
    expected_rate_of_return_nps_corpus_after_retirement: float = 0.07


def get_lumpsum_growth(principle, interest, number_of_years, compound_frequency=1):
    return principle * (
        (1 + (interest / compound_frequency)) ** (number_of_years * compound_frequency)
    )


def get_sip_one_year_then_wait(monthly_contrib, annual_rate, total_years):
    r = annual_rate / 12  # monthly rate
    total = 0
    for month in range(12):  # 12 months of contributions
        months_to_grow = (total_years - 1) * 12 + (12 - month)
        fv = monthly_contrib * ((1 + r) ** months_to_grow)
        total += fv
    return total


def get_sip_growth(
    monthly_contribution, contribution_increase_rate, return_rate, number_of_years
):
    if contribution_increase_rate == return_rate:
        return (
            12
            * monthly_contribution
            * number_of_years
            * ((1 + return_rate) ** (number_of_years - 1))
        )
    else:
        P = 12 * monthly_contribution
        T1 = (1 + return_rate) ** number_of_years
        T2 = (1 + contribution_increase_rate + 0.0000001) ** number_of_years
        T3 = return_rate - contribution_increase_rate + 0.0000001
        return P * (T1 - T2) / T3


def _get_sip_growth(
    monthly_contribution,
    contribution_increase_rate,
    return_rate,
    number_of_years,
):
    corpus = 0.0
    print(
        monthly_contribution, contribution_increase_rate, return_rate, number_of_years
    )
    for accumulated_years in range(number_of_years):
        monthly_contribution_for_the_year = get_lumpsum_growth(
            monthly_contribution, contribution_increase_rate, accumulated_years
        )
        corpus_for_the_year = get_sip_one_year_then_wait(
            monthly_contribution_for_the_year,
            return_rate,
            number_of_years - accumulated_years,
        )
        corpus += corpus_for_the_year
        # print(f"year {accumulated_years +1}, monthly {round(monthly_contribution_for_the_year)}, principal {round(12 * monthly_contribution_for_the_year)}, growth_of_this {round(corpus_for_the_year)}")
    return corpus


def calculate_expected_corpus_at_retirement(
    _current_total_nps_corpus,
    expected_return,
    _years_to_retire,
    _expected_growth_in_nps_contribution,
    current_monthly_contribution,
):
    return get_lumpsum_growth(
        _current_total_nps_corpus,
        expected_return,
        _years_to_retire,
    ) + _get_sip_growth(
        current_monthly_contribution,
        _expected_growth_in_nps_contribution,
        expected_return,
        _years_to_retire,
    )


def get_yearly_accumulated_corpus(initial_corpus, return_rate, monthly_contrib):
    r = return_rate / 12  # monthly rate
    corpus = initial_corpus

    for month in range(12):  # 12 months of contributions
        corpus += (corpus * r) + monthly_contrib
    return corpus


def calculate_accumulated_corpus(
    years_to_retire: int,
    current_basic_pay: float,
    current_da_rate: float,
    current_total_nps_corpus: float,
    expected_da_hike: float,
    expected_basic_pay_hike: float,
    expected_nps_return: float,
    expected_benchmark_return: float,
):
    NPS_CONTRIB_RATE = 0.24
    UPS_CONTRIB_RATE = 0.20

    nps_corpus = ups_corpus = benchmark_corpus = current_total_nps_corpus
    basic_pay = current_basic_pay
    da_rate = current_da_rate

    growth_info = []

    for year in range(1, years_to_retire + 1):
        salary = basic_pay * (1 + da_rate)

        nps_contrib = salary * NPS_CONTRIB_RATE
        ups_contrib = salary * UPS_CONTRIB_RATE
        benchmark_contrib = ups_contrib  # same as UPS

        nps_corpus = get_yearly_accumulated_corpus(
            nps_corpus, expected_nps_return, nps_contrib
        )
        ups_corpus = get_yearly_accumulated_corpus(
            ups_corpus, expected_nps_return, ups_contrib
        )
        benchmark_corpus = get_yearly_accumulated_corpus(
            benchmark_corpus, expected_benchmark_return, benchmark_contrib
        )

        growth_info.append(
            {
                "year": year,
                "basic_pay": basic_pay,
                "da_rate": da_rate,
                "salary": salary,
                "monthly_nps_contrib": nps_contrib,
                "monthly_ups_contrib": ups_contrib,
                "monthly_benchmark_contrib": benchmark_contrib,
                "nps_corpus": nps_corpus,
                "ups_corpus": ups_corpus,
                "benchmark_corpus": benchmark_corpus,
            }
        )

        # Update DA and Basic Pay for next year
        da_rate = current_da_rate + (year * expected_da_hike)
        basic_pay *= 1 + expected_basic_pay_hike

        # You may want to store these values if needed:
        # if year == years_to_retire - 1:
        #     basic_pay_one_year_prior = basic_pay
        # elif year == years_to_retire:
        #     basic_pay_at_retirement = basic_pay
        #     final_da_rate = da_rate

    print(nps_corpus, ups_corpus, benchmark_corpus)
    return nps_corpus, ups_corpus, benchmark_corpus


def compare(params: PensionCompareParams):

    da_at_retiremnt = params.current_da_rate + (
        params.expected_da_hike * int(params.years_to_retire)
    )
    print(params.current_da_rate, params.expected_da_hike, da_at_retiremnt)
    ups_monthly_contribution = (params.current_monthly_nps_contribution * 20) / 24
    calculate_accumulated_corpus(
        params.years_to_retire,
        params.current_basic_pay,
        params.current_da_rate,
        params.current_total_nps_corpus,
        params.expected_da_hike,
        params.expected_basic_pay_hike,
        params.expected_nps_return,
        params.expected_benchmark_corpus_return,
    )
    nps_corpus_at_retiremnet = round(
        calculate_expected_corpus_at_retirement(
            params.current_total_nps_corpus,
            params.expected_nps_return,
            params.years_to_retire,
            params.expected_growth_in_nps_contribution,
            params.current_monthly_nps_contribution,
        )
    )
    print(nps_corpus_at_retiremnet)
    benchmark_corpus_at_retiremnet = round(
        calculate_expected_corpus_at_retirement(
            params.current_total_nps_corpus,
            params.expected_benchmark_corpus_return,
            params.years_to_retire,
            params.expected_growth_in_nps_contribution,
            ups_monthly_contribution,
        )
    )
    print(benchmark_corpus_at_retiremnet)
    expected_basic_pay_1_year_before = get_lumpsum_growth(
        params.current_basic_pay,
        params.expected_basic_pay_hike,
        params.years_to_retire - 1,
    )
    expected_basic_pay_retirement = get_lumpsum_growth(
        params.current_basic_pay,
        params.expected_basic_pay_hike,
        params.years_to_retire,
    )
    ups_retirement_basic_pay = round(
        (expected_basic_pay_1_year_before + expected_basic_pay_retirement) / 4, 2
    )


if __name__ == "__main__":
    params = PensionCompareParams(
        current_service=15,
        years_to_retire=15,
        expected_year_in_retirement=30,
        current_basic_pay=50000,
        current_da_rate=0.55,
        current_monthly_nps_contribution=18000,
        current_total_nps_corpus=4000000,
        expected_da_hike=0.05,
        expected_basic_pay_hike=0.05,
        expected_growth_in_nps_contribution=0.1,
        expected_nps_return=0.1,
        expected_benchmark_corpus_return=0.1,
        expected_annuity_rate=0.06,
        expected_ups_pension_growth=0.05,
        expected_rate_of_return_nps_corpus_after_retirement=0.07,
    )
    compare(params)
