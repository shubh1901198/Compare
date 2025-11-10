import pandas as pd
import random
from datetime import datetime

# Load thresholds from CSV
threshold_file = "comparison_thresholds.csv"
threshold_df = pd.read_csv(threshold_file)
thresholds = dict(zip(threshold_df["Metric"], threshold_df["Acceptable Difference"]))

# Simulate 10 Trip A entries
trip_a_rows = []
for _ in range(10):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "Distance": round(120 + random.uniform(-5, 5), 1),
        "Fuel Used": round(8.5 + random.uniform(-0.3, 0.3), 2),
        "Avg Speed": round(48 + random.uniform(-3, 3), 1),
        "Duration": 150 + random.randint(-5, 5)
    }
    trip_a_rows.append({
        "Timestamp": timestamp,
        "Trip Meter": "Trip A",
        "Distance": data["Distance"],
        "Fuel Used": data["Fuel Used"],
        "Avg Speed": data["Avg Speed"],
        "Duration": data["Duration"]
    })

trip_a_df = pd.DataFrame(trip_a_rows)

# Load last 10 Trip B entries from CSV
log_file = "trip_log_history.csv"
try:
    csv_df = pd.read_csv(log_file)
    trip_b_df = csv_df[csv_df["Trip Meter"] == "Trip B"].tail(10).reset_index(drop=True)
except Exception as e:
    print(f"Error reading CSV: {e}")
    trip_b_df = pd.DataFrame()

# Compare and evaluate Pass/Fail
comparison_results = []
pass_count = 0
fail_count = 0

for i in range(min(len(trip_a_df), len(trip_b_df))):
    a = trip_a_df.iloc[i]
    b = trip_b_df.iloc[i]

    differences = {
        "Distance": abs(a["Distance"] - b["Distance"]),
        "Fuel Used": abs(a["Fuel Used"] - b["Fuel Used"]),
        "Avg Speed": abs(a["Avg Speed"] - b["Avg Speed"]),
        "Duration": abs(a["Duration"] - b["Duration"])
    }

    pass_fail = all(differences[key] <= thresholds[key] for key in thresholds)
    result = "Pass" if pass_fail else "Fail"
    if pass_fail:
        pass_count += 1
    else:
        fail_count += 1

    comparison_results.append({
        "Trip A Timestamp": a["Timestamp"],
        "Trip B Timestamp": b["Timestamp"],
        "Distance Diff": differences["Distance"],
        "Fuel Used Diff": differences["Fuel Used"],
        "Avg Speed Diff": differences["Avg Speed"],
        "Duration Diff": differences["Duration"],
        "Pass/Fail": result
    })

# Save to .log file
log_filename = "trip_comparison.log"
with open(log_filename, "w") as log_file:
    log_file.write(f"Trip Comparison Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write("=" * 80 + "\n")
    for row in comparison_results:
        log_file.write(
            f"{row['Trip A Timestamp']} | {row['Trip B Timestamp']} | "
            f"Distance Diff: {row['Distance Diff']:.2f} | "
            f"Fuel Used Diff: {row['Fuel Used Diff']:.2f} | "
            f"Avg Speed Diff: {row['Avg Speed Diff']:.2f} | "
            f"Duration Diff: {row['Duration Diff']} | "
            f"Result: {row['Pass/Fail']}\n"
        )
    log_file.write("=" * 80 + "\n")
    log_file.write(f"Summary: {pass_count} Passed, {fail_count} Failed\n")

print(f"\n✅ Comparison complete. Results saved to {log_filename}")