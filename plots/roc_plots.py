import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import os
from glob import glob

def plot_roc_true_vs_false(csv_path, output_dir):
    df = pd.read_csv(csv_path)

    required_cols = ["result", "NCD", "expected"]
    if not all(col in df.columns for col in required_cols):
        print(f"Skipping {csv_path}: missing required columns.")
        return

    # Convert 'expected' column to binary
    df["expected"] = df["expected"].astype(str).str.lower().map({"true": 1, "false": 0})

    y_true = df["expected"]
    y_scores = -df["NCD"]  # menor NCD = melhor match

    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.2f})", color="darkorange", lw=2)
    plt.plot([0, 1], [0, 1], 'k--', label='Random classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve — {os.path.basename(csv_path)}')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()

    # Save figure
    filename = os.path.splitext(os.path.basename(csv_path))[0] + "_roc.png"
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path)
    plt.close()
    print(f"Saved ROC plot to {output_path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Define script_dir here
    input_dir = os.path.join(script_dir, "../results")
    output_dir = os.path.join(script_dir, "roc_plots")
    os.makedirs(output_dir, exist_ok=True)

    csv_files = glob(os.path.join(input_dir, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in {input_dir}.")
        return

    for csv_file in csv_files:
        plot_roc_true_vs_false(csv_file, output_dir)

if __name__ == "__main__":
    main()
