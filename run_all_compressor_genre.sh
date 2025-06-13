#!/bin/bash

# Ensure the results directory exists
mkdir -p results

# List of compressors to test
compressors=("gzip" "bzip2" "zstd" "lzma" "lzo" "snappy" "lz4")

# Path to the compiled executable
EXECUTABLE="./match"

# Run for each compressor
for compressor in "${compressors[@]}"
do
    echo "Running with compressor: $compressor"
    $EXECUTABLE --genre --compressor "$compressor" --output "results/results_${compressor}.csv"
done
