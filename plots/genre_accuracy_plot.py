import pandas as pd
import matplotlib.pyplot as plt
import os
import re

csv_folder = "../results/genre/"
accuracies = {}

for filename in os.listdir(csv_folder):
    if filename.endswith(".csv") and filename.startswith("results_genre_"):
        compressor = filename.replace("results_genre_", "").replace(".csv", "")
        file_path = os.path.join(csv_folder, filename)

        try:
            df = pd.read_csv(file_path, usecols=["music query", "identified genre"])
        except Exception as e:
            print(f"Erro ao ler {filename}: {e}")
            continue

        correct = 0
        total = 0

        for _, row in df.iterrows():
            query = row["music query"]
            identified_genre = row["identified genre"]

            if isinstance(query, str):
                match = re.match(r"([a-zA-Z]+)_", query)
                if match:
                    expected_genre = match.group(1).lower()
                    if isinstance(identified_genre, str) and expected_genre == identified_genre.lower():
                        correct += 1
                    total += 1

        accuracy = correct / total if total > 0 else 0
        accuracies[compressor] = accuracy

# Plot
plt.figure(figsize=(10, 6))
plt.bar(accuracies.keys(), accuracies.values(), color='skyblue')
plt.ylim(0, 1)
plt.xlabel('Compressor')
plt.ylabel('Accuracy')
plt.title('Genre Identification Accuracy per Compressor')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save and show
plt.savefig("genre_accuracy.png")
plt.show()

