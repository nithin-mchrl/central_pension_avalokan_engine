from dataclasses import dataclass, asdict
from typing import List, Optional
import csv

from .pension_compare_params import PensionCompareParams


# ------------------------------
# Data Model
# ------------------------------
@dataclass
class YearlyCorpusInfo:
    year: int
    basic_pay: float
    da_rate: float
    salary: float
    next_year_basic_pay: float
    next_year_da_rate: float
    monthly_nps_contrib: float
    monthly_ups_contrib: float
    monthly_benchmark_contrib: float
    nps_corpus: float
    ups_corpus: float
    benchmark_corpus: float
    annual_expense: float
    ups_pension: float = 0.0
    nps_annuity: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)


# ------------------------------
# Pension Calculator
# ------------------------------
def update_pension_info(info: YearlyCorpusInfo, params: PensionCompareParams):
    """
    Calculate updated pension and corpus values for the given YearlyCorpusInfo.
    """
    # NPS calculations
    nps_corpus = info.nps_corpus * params.withdrawal_percentage
    nps_annuity = (
        info.nps_corpus
        * (1 - params.withdrawal_percentage)
        * params.expected_annuity_rate
        / 12
    )

    # UPS calculations
    total_service_months = (params.years_to_retire + params.current_service) * 12
    service_ratio = min(total_service_months / 300, 1)

    avg_basic_pay = (info.basic_pay + info.next_year_basic_pay) / 2
    max_ups_pension = avg_basic_pay * service_ratio

    final_drawn_salary = info.next_year_basic_pay * (1 + info.next_year_da_rate)
    ups_lumpsum = (params.years_to_retire + params.current_service) * 2 * final_drawn_salary / 10

    remaining_ups_corpus = info.ups_corpus * (1 - params.withdrawal_percentage)
    ups_corpus = ups_lumpsum + (info.ups_corpus * params.withdrawal_percentage)

    if remaining_ups_corpus >= info.benchmark_corpus:
        ups_corpus += info.ups_corpus - info.benchmark_corpus
        ups_pension_basic_pay = max_ups_pension
    else:
        ups_pension_basic_pay = max_ups_pension * (remaining_ups_corpus / info.benchmark_corpus)

    if ups_pension_basic_pay < 10000:
        ups_pension_basic_pay = 10000

    ups_pension = ups_pension_basic_pay * (1 + info.next_year_da_rate)

    return ups_pension, nps_annuity, ups_corpus, nps_corpus


# ------------------------------
# Corpus History Manager
# ------------------------------
class CorpusInfo:
    def __init__(self):
        self._history: List[YearlyCorpusInfo] = []

    def add(self, info: YearlyCorpusInfo) -> None:
        """Add a new YearlyCorpusInfo entry."""
        self._history.append(info)

    def last(self) -> Optional[YearlyCorpusInfo]:
        """Return the last YearlyCorpusInfo entry, or None if empty."""
        return self._history[-1] if self._history else None

    def __getitem__(self, index: int) -> YearlyCorpusInfo:
        return self._history[index]

    def __len__(self) -> int:
        return len(self._history)

    def all(self) -> List[YearlyCorpusInfo]:
        """Return a shallow copy of all history entries."""
        return self._history.copy()

    def as_list_of_dict(self) -> List[dict]:
        """Return a list of dictionaries for each YearlyCorpusInfo entry."""
        return [entry.as_dict() for entry in self._history]

    def calculate_pension(self, params: PensionCompareParams) -> None:
        """
        Update the last YearlyCorpusInfo entry with calculated pension values.
        """
        retirement_year_info = self.last()
        if not retirement_year_info:
            raise IndexError("Cannot update last item because history is empty.")

        ups_pension, nps_annuity, ups_corpus, nps_corpus = update_pension_info(
            retirement_year_info, params
        )

        retirement_year_info.ups_pension = ups_pension
        retirement_year_info.nps_annuity = nps_annuity
        retirement_year_info.ups_corpus = ups_corpus
        retirement_year_info.nps_corpus = nps_corpus
    
    def save_to_csv(self, file_path: str) -> None:
        """
        Save all YearlyCorpusInfo entries to a CSV file.
        """
        if not self.last():
            raise ValueError("No corpus history to save.")

        # Get list of dictionaries
        data_dicts = self.as_list_of_dict()

        # Use keys from the first dict as CSV headers
        fieldnames = data_dicts[0].keys()

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_dicts)

        print(f"Corpus history saved to {file_path}")


