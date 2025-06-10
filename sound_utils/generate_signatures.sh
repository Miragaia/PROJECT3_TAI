#!/bin/bash

directory="../test_files_sox_intensity"

for wavfile in "$directory"/*.wav; do
    filename=$(basename "$wavfile" .wav)
    echo "Processing $filename.wav ..."
    python3 get_max_freqs.py "$wavfile" "../queries/$filename.freqs"
done

echo "All files processed."
