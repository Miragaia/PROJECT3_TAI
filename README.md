# PROJECT3_TAI

First Year - MEI - 2nd Semester Class (Universidade de Aveiro) - Algorithmic Theory of Information 

### Overview

This project performs music identification based on Normalized Compression Distance (NCD) using precomputed frequency features from WAV audio files. It compares noisy audio queries to a database of song snippets to identify the most similar matches.

### Requirements
### Python Dependencies

Install the Python requirements for generating the .freqs files:

```bash
pip install -r requirements.txt
```

### C++ Dependencies

Ensure the following libraries are installed on your system:

```bash
sudo apt install libbz2-dev libzstd-dev liblzma-dev libsnappy-dev liblz4-dev liblzo2-dev zlib1g-dev
```

## Python Script - Generate Freqs

### Usage

Place your .wav songs in a directory called wav_sounds.

**Single File:**

```bash
python3 get_max_freqs.py wav_sounds/song.wav database/song.freqs
```
**Batch Processing:**

```bash
chmod +x generate_signatures.sh
./generate_signatures.sh
```
## C++ Code - NCD Matcher

### Compilation

Compile the code using:

```bash
make
```
### Usage

**Full Batch Evaluation:**

```bash
./match
```

**Full Batch Evaluation with specified Compressor:**

```bash
./match --compressor zlib
```

**Specify Output CSV:**

```bash
./match --compressor zlib --output results/results_zlib.csv
```

**Single Query File:**

```bash
./match --compressor zlib --query queries/query-example.freqs
```

## Evaluate with All Compressors

Run the following script to test multiple compressors:

```bash
chmod +x run_all_compressors.sh
./run_all_compressors.sh
```
The results will be saved in the `results/` folder as `results_<compressor>.csv` for each tested compressor.

## Supported Compressors

- zlib
- bzip2
- zstd
- lzma
- lz4
- lzo
- snappy

## Output CSV
The format of the CSV file:

```bash
music query,noise type,noise intensity,result,NCD,expected
```
Where `expected` is true or false depending on whether the identified result matches the query’s expected base name.



## Notes

- Ensure your query files follow the naming format: `queryname_<noise>_intensity_<value>.freqs`

- The `database/` directory must contain the reference `.freqs` files.

- The `queries/` directory must contain noisy queries for evaluation.

## Clean Up

To remove compiled binaries:

```bash
make clean
```