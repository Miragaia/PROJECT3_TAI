#!/bin/bash

mkdir -p database

for wavfile in wav_sounds/*.wav; do
    filename=$(basename "$wavfile" .wav)
    echo "Processing $filename.wav ..."
    python3 get_max_freqs.py "$wavfile" "database/$filename.freqs"
done

echo "All files processed."
