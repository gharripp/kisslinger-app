import pandas as pd
import numpy as np


def check_duplicates(filename):
    print(f"Checking {filename}...")
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    # Check for consecutive duplicates within each Phi_Deg group
    total_consecutive_dups = 0

    for phi in df["Phi_Deg"].unique():
        group = df[df["Phi_Deg"] == phi]

        # Shift to compare with next row
        r_diff = group["R_mm"].diff().iloc[1:]
        z_diff = group["Z_mm"].diff().iloc[1:]

        # Check where both diffs are 0 (or very close)
        is_dup = (np.abs(r_diff) < 1e-9) & (np.abs(z_diff) < 1e-9)

        num_dups = is_dup.sum()
        if num_dups > 0:
            print(f"Phi {phi}: {num_dups} consecutive duplicates found.")
            # Print the first few
            dup_indices = is_dup[is_dup].index
            for idx in dup_indices[:3]:
                print(
                    f"  Row {idx}: {group.loc[idx].values} vs {group.loc[idx - 1].values}"
                )
            total_consecutive_dups += num_dups

    if total_consecutive_dups == 0:
        print("No consecutive duplicates found.")
    else:
        print(f"Total consecutive duplicates: {total_consecutive_dups}")


check_duplicates("chamber_coordinates_fixed.csv")
check_duplicates("chamber_coordinates_fixed_smooth.csv")
