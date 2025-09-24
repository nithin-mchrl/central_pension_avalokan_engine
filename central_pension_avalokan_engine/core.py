from dataclasses import dataclass
from .corpus_info import CorpusInfo
from .corpus_growth_calculation import calculate_accumulated_corpus
from .pension_compare_params import PensionCompareParams


# ------------------------------------------
# Corpus Growth Simulation
# ------------------------------------------
def get_corpus_info(params: PensionCompareParams) -> CorpusInfo:
    corpus_history = CorpusInfo()

    for year in range(params.years_to_retire):
        prev_info = corpus_history.last()
        corpus_info = calculate_accumulated_corpus(year, params, prev_info)
        corpus_history.add(corpus_info)

    return corpus_history


# ------------------------------------------
# Main Entry Point (Demo)
# ------------------------------------------
if __name__ == "__main__":
    params = PensionCompareParams(
        current_service=6,
        years_to_retire=28,
        current_basic_pay=59600,
        current_da_rate=0.55,
        current_total_nps_corpus=1800000,
        withdrawal_percentage=0.6,
        current_annual_expense=30000,
    )

    corpus_history = get_corpus_info(params)

    # Print final year summary
    final_year = corpus_history.last()
    if final_year:
        corpus_history.calculate_pension(params)
        print(f"\nProjected values at retirement (Year {final_year.year}):")
        print(f"NPS: ₹{final_year.nps_corpus:,.2f}")
        print(f"UPS: ₹{final_year.ups_corpus:,.2f}")
        print(f"NPS annuity (monthly): ₹{final_year.nps_annuity:,.2f}")
        print(f"UPS pension (including DA): ₹{final_year.ups_pension:,.2f}")

    # Get raw data for export
    corpus_dicts = corpus_history.as_list_of_dict()
    # print(corpus_dicts)  # Uncomment to debug or export

