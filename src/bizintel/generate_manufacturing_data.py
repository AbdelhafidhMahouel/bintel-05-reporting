"""generate_manufacturing_data.py

Generates a synthetic manufacturing process engineering dataset
for use in Phase 5: Apply the Skills to a New Problem.

Simulates daily production records across multiple production lines,
shifts, and machines over two years (2024-2025), including units
produced, defective units, downtime, and process temperature.

Output:
    data/manufacturing/manufacturing_process_abdelhafidh.csv
"""

from pathlib import Path
import random

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = Path("data/manufacturing")
OUTPUT_FILE = OUTPUT_DIR / "manufacturing_process_abdelhafidh.csv"

PRODUCTION_LINES = ["Line-A", "Line-B", "Line-C", "Line-D"]
SHIFTS = ["Morning", "Afternoon", "Night"]

# Each line has a small fleet of machines.
LINE_MACHINES = {
    "Line-A": ["M-101", "M-102"],
    "Line-B": ["M-201", "M-202"],
    "Line-C": ["M-301", "M-302", "M-303"],
    "Line-D": ["M-401", "M-402"],
}

# Give a couple of machines a higher baseline defect/downtime rate,
# so the "top N worst machines" analysis has a meaningful answer.
PROBLEM_MACHINES = {"M-303", "M-201"}

OPERATORS = [f"OP-{i:03d}" for i in range(1, 21)]

START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")


def generate_records() -> pd.DataFrame:
    """Generate one production record per line/shift/day combination."""
    records = []
    record_id = 1

    dates = pd.date_range(START_DATE, END_DATE, freq="D")

    for date in dates:
        for line in PRODUCTION_LINES:
            machines = LINE_MACHINES[line]

            for shift in SHIFTS:
                # Not every line runs every shift every day (adds realism).
                if random.random() < 0.08:
                    continue

                machine = random.choice(machines)
                operator = random.choice(OPERATORS)

                base_units = np.random.normal(loc=480, scale=60)
                units_produced = max(50, int(base_units))

                is_problem_machine = machine in PROBLEM_MACHINES

                defect_rate = np.random.normal(
                    loc=0.045 if is_problem_machine else 0.018,
                    scale=0.01,
                )
                defect_rate = min(max(defect_rate, 0.0), 0.35)
                defective_units = int(round(units_produced * defect_rate))

                downtime_minutes = max(
                    0,
                    int(
                        np.random.normal(
                            loc=35 if is_problem_machine else 12,
                            scale=15,
                        )
                    ),
                )

                cycle_time_seconds = round(
                    np.random.normal(
                        loc=42 if is_problem_machine else 30,
                        scale=5,
                    ),
                    2,
                )
                cycle_time_seconds = max(10.0, cycle_time_seconds)

                process_temp_c = round(np.random.normal(loc=68, scale=4), 1)

                records.append(
                    {
                        "RecordID": record_id,
                        "ProductionDate": date.strftime("%Y-%m-%d"),
                        "ProductionLine": line,
                        "Shift": shift,
                        "MachineID": machine,
                        "OperatorID": operator,
                        "UnitsProduced": units_produced,
                        "DefectiveUnits": defective_units,
                        "DowntimeMinutes": downtime_minutes,
                        "CycleTimeSeconds": cycle_time_seconds,
                        "ProcessTempC": process_temp_c,
                    }
                )
                record_id += 1

    return pd.DataFrame.from_records(records)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = generate_records()
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated {len(df)} manufacturing records.")
    print(f"Saved to: {OUTPUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()
