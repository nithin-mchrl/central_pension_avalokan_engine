import argparse
import configparser
from typing import List
from pathlib import Path

from .core import get_corpus_info, PensionCompareParams


DIRECT_ARGS_ORDER = [
    "current_service",
    "years_to_retire",
    "current_basic_pay",
    "current_da_rate",
    "current_total_nps_corpus",
    "withdrawal_percentage",
    "current_annual_expense",
]
def parse_args_from_file(file_path: Path) -> List[str]:
    config = configparser.ConfigParser()
    config.read(file_path)

    personal_section = "personal_data"
    assumptions_section = "assumptions"

    if not config.has_section(personal_section):
        raise ValueError(f"Missing [{personal_section}] section in {file_path}")

    missing_args = [
        arg for arg in DIRECT_ARGS_ORDER if not config.has_option(personal_section, arg)
    ]
    if missing_args:
        missing_str = ", ".join(missing_args)
        raise ValueError(
            f"Missing argument(s) in [{personal_section}] section: {missing_str}"
        )

    # Collect positional args in order
    args_list = [config.get(personal_section, arg) for arg in DIRECT_ARGS_ORDER]

    # Append optional assumptions as --key value pairs
    if config.has_section(assumptions_section):
        for key, value in config.items(assumptions_section):
            args_list.extend([f"--{key}", value])

    return args_list

def parse_args_from_file(file_path):
    config = configparser.ConfigParser()

    config.read(file_path)

    if "personal_data" not in config:
        raise ValueError(f"Missing [personal_data] section in {file_path}")

    args_list = []
    missing_required_args = []
    for required_arg in DIRECT_ARGS_ORDER:
        if not required_arg in config["personal_data"]:
            missing_required_args.append(required_arg)
            continue
        args_list.append(config["personal_data"][required_arg])

    if missing_required_args:
        list_in_err_string = ", ".join(missing_required_args)
        raise ValueError(
            "Missing argument(s) in [personal_data] section: " f"{list_in_err_string}"
        )

    # Optionally include assumptions
    if "assumptions" in config:
        for key, value in config["assumptions"].items():
            args_list.append(f"--{key}")
            args_list.append(str(value))
    return args_list


def build_direct_parser(subparser):
    # Required positional arguments (no defaults)
    subparser.add_argument(
        "current_service", type=int, help="Years of service completed"
    )
    subparser.add_argument(
        "years_to_retire", type=int, help="Years remaining until retirement"
    )
    subparser.add_argument("current_basic_pay", type=float, help="Current basic pay")
    subparser.add_argument("current_da_rate", type=float, help="Current DA rate")
    subparser.add_argument(
        "current_total_nps_corpus", type=float, help="Current total NPS corpus"
    )
    subparser.add_argument(
        "withdrawal_percentage",
        type=float,
        help="Percentage of corpus withdrawn at retirement",
    )
    subparser.add_argument(
        "current_annual_expense", type=float, help="Current annual expenses"
    )

    # Optional arguments (have defaults)
    subparser.add_argument(
        "--expected_da_hike",
        type=float,
        default=0.05,
        help="Expected DA hike (default: 0.05)",
    )
    subparser.add_argument(
        "--expected_basic_pay_hike",
        type=float,
        default=0.05,
        help="Expected basic pay hike (default: 0.05)",
    )
    subparser.add_argument(
        "--expected_nps_return",
        type=float,
        default=0.10,
        help="Expected NPS return (default: 0.10)",
    )
    subparser.add_argument(
        "--expected_benchmark_corpus_return",
        type=float,
        default=0.08,
        help="Expected benchmark corpus return (default: 0.08)",
    )
    subparser.add_argument(
        "--expected_annuity_rate",
        type=float,
        default=0.06,
        help="Expected annuity rate (default: 0.06)",
    )
    subparser.add_argument(
        "--expected_ups_pension_growth",
        type=float,
        default=0.05,
        help="Expected UPS pension growth (default: 0.05)",
    )
    subparser.add_argument(
        "--expected_rate_of_return_nps_corpus_after_retirement",
        type=float,
        default=0.07,
        help="Expected post-retirement NPS corpus return (default: 0.07)",
    )
    subparser.add_argument(
        "--expected_rate_of_inflation",
        type=float,
        default=0.05,
        help="Expected inflation rate (default: 0.05)",
    )


def _existing_file(file_path_str):
    file_path = Path(file_path_str)
    if not file_path.is_file():
        raise argparse.ArgumentTypeError(f"Config file not found: {file_path}")
    return file_path

def main():

    parser = argparse.ArgumentParser(description="Run pension simulation")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Subparser for direct input
    direct_parser = subparsers.add_parser("direct", help="Provide all inputs directly")
    build_direct_parser(direct_parser)
    direct_parser.add_argument(
        "--save-csv", type=Path, help="Optional: Save corpus history to this CSV file"
    )
    
    # Subparser for loading from file
    file_parser = subparsers.add_parser("from-file", help="Load inputs from .ini file")
    file_parser.add_argument(
        "file", type=_existing_file, help="Path to .ini file"
    )
    file_parser.add_argument(
        "--save-csv", type=Path, help="Optional: Save corpus history to this CSV file"
    )

    args = parser.parse_args()

    # Handle file input
    if args.mode == "from-file":
        file_args_list = parse_args_from_file(args.file)

        # Reuse direct parser logic to validate and parse values
        direct_parser = argparse.ArgumentParser()
        sava_csv_arg = getattr(args, "save_csv", None)
        build_direct_parser(direct_parser)
        args = direct_parser.parse_args(file_args_list)
        args.save_csv = sava_csv_arg  

    # Instantiate the dataclass using parsed arguments
    params = PensionCompareParams(
        current_service=args.current_service,
        years_to_retire=args.years_to_retire,
        current_basic_pay=args.current_basic_pay,
        current_da_rate=args.current_da_rate,
        current_total_nps_corpus=args.current_total_nps_corpus,
        withdrawal_percentage=args.withdrawal_percentage,
        current_annual_expense=args.current_annual_expense,
        expected_da_hike=args.expected_da_hike,
        expected_basic_pay_hike=args.expected_basic_pay_hike,
        expected_nps_return=args.expected_nps_return,
        expected_benchmark_corpus_return=args.expected_benchmark_corpus_return,
        expected_annuity_rate=args.expected_annuity_rate,
        expected_ups_pension_growth=args.expected_ups_pension_growth,
        expected_rate_of_return_nps_corpus_after_retirement=args.expected_rate_of_return_nps_corpus_after_retirement,
        expected_rate_of_inflation=args.expected_rate_of_inflation,
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
        print(args.save_csv)
        
        if args.save_csv:
            corpus_history.save_to_csv(args.save_csv)
    else:
        print("Nothing to show. Wrong arguments or unknown error calculating!")
    

if __name__ == "__main__":
    main()
