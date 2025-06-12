import pandas as pd
from sklearn.metrics import f1_score
import numpy as np
import os
from glob import glob

def find_best_f1(csv_path):
    df = pd.read_csv(csv_path)

    # Validação mínima
    if "expected" not in df.columns or "NCD" not in df.columns:
        print(f"❌ {csv_path}: missing 'expected' or 'NCD' column.")
        return

    # Converter para binário (1 = correto, 0 = incorreto)
    df["expected"] = df["expected"].astype(str).str.lower().map({"true": 1, "false": 0})
    y_true = df["expected"]
    ncd_scores = df["NCD"]

    thresholds = np.linspace(ncd_scores.min(), ncd_scores.max(), 200)
    best_f1 = 0
    best_threshold = None

    for threshold in thresholds:
        y_pred = (ncd_scores < threshold).astype(int)
        f1 = f1_score(y_true, y_pred)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    filename = os.path.basename(csv_path)
    print(f"{filename:<30} → Best F1: {best_f1:.4f} at threshold: {best_threshold:.5f}")

def main():
    input_dir = "../results"
    csv_files = glob(os.path.join(input_dir, "*.csv"))

    if not csv_files:
        print("Nenhum ficheiro CSV encontrado.")
        return

    print("📊 F1-scores por ficheiro:")
    for csv_file in csv_files:
        find_best_f1(csv_file)

if __name__ == "__main__":
    main()
