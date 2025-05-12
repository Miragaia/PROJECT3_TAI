#!/bin/bash

# Ensure the results directory exists
mkdir -p results

# List of compressors to test
compressors=("zlib" "bzip2" "zstd" "lzma" "lzo" "snappy")

# Path to the compiled executable
EXECUTABLE="./match"

# Run for each compressor
for compressor in "${compressors[@]}"
do
    echo "Running with compressor: $compressor"
    $EXECUTABLE --compressor "$compressor" --output "results/results_${compressor}.csv"
done
