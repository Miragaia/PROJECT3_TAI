#!/bin/bash

mkdir -p database

directory="test_files"

for wavfile in "$directory"/*.wav; do
    filename=$(basename "$wavfile" .wav)
    echo "Processing $filename.wav ..."
    python3 get_max_freqs.py "$wavfile" "queries/$filename.freqs"
done

echo "All files processed."
