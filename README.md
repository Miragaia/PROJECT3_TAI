# PROJECT3_TAI

First Year - MEI - 2nd Semester Class (Universidade de Aveiro) - Algorithmic Theory of Information 

| Name              | Nmec   |
|-------------------|--------|
| Diogo Silva       | 107647 |
| Miguel Cruzeiro   | 107660 |
| Miguel Miragaia   | 108317 |

### Overview

This project performs music identification based on Normalized Compression Distance (NCD) using precomputed frequency features from WAV audio files. It compares noisy audio queries to a database of song snippets to identify the most similar matches.

## Get Max Freqs Implementaion

- dizer que fizemos uma implementação nossa

## Dataset

//change this later(n sei que escrever)

For this project, we selected 26 songs across diverse musical genres to create a comprehensive dataset for testing. Our selection includes tracks from various styles such as rock, hip-hop, electronic, pop, alternative, and metal, ensuring sufficient genre diversity to evaluate the robustness of our implementation. This varied collection allows us to test whether NCD can effectively distinguish between audio excerpts and accurately identify their source tracks, regardless of musical style or complexity. The dataset serves as a foundation for analyzing how compression-based similarity measures perform in audio pattern recognition tasks.

| Artista | Música |
|---------|--------|
| AC/DC | You Shook Me All Night Long |
| Alice In Chains | Them Bones |
| A$AP Rocky | Sandman |
| Avicii | Wake Me Up |
| Coldplay | Viva La Vida |
| Dio | End Of The Beginning |
| Frank Ocean | White Ferrari |
| Gorillaz | Feel Good Inc. |
| Imagine Dragons | Bones |
| Kanye West | Hurricane |
| Lady Gaga, Bruno Mars | Die With A Smile |
| Mac Miller | 2009 |
| Mark Ronson | Uptown Funk |
| Metro Boomin Don Toliver Future  | Too Many Nights |
| Nirvana | Come As You Are |
| OneRepublic | Counting Stars |
| Playboi Carti | Magnolia |
| Post Malone | White Iverson |
| Radiohead | No Surprises |
| Sabrina Carpenter | Espresso |
| Slipknot | Duality |
| SUR LE PONT D'AVIGNON | Mach-Hommy |
| System of a Down | Chop Suey |
| Taylor Swift | Fortnight (feat. Post Malone) |
| The Weeknd | Timeless with Playboi Carti |
| Travis Scott | NO BYSTANDERS |
| untitjapan | PYRAMIDZ |

## Frequency File

//write this better later

We craeted a bash script **generate_signatures.sh** that converts the inital audio files in .wav format to .freqs format and stores them in the database folder.

# Test Queries

We created a Python script **batch_segment_audio.py** that automatically splits every audio file in a given folder into a fixed number of segments of equal duration. Each segment can include silence padding if the audio is too short. The script supports common audio formats such as .wav and .mp3 and outputs the segments in .wav format to a specified output folder.

It works as follows:

- For each audio file, it generates a fixed number of segments (num_segments), each with a specified duration (segment_length in seconds).

- The segments are evenly distributed across the audio timeline, with optional padding at the end if the segment extends past the audio duration.

- All output segments are saved with sequential names (e.g., song_segment1.wav, song_segment2.wav, etc.) to the target output directory.



For the process of applying the different type of noise to each segment, we created a bash script **noise_generator.sh** that runs the program **noise_generator.py**

In that program we used SOX, which is  is a powerful command-line utility that allows audio processing tasks such as noise generation and mixing. We focused on adding noise based on intensity levels, where different types of noise (white, pink, and brown) were added to each input audio segment using predefined intensity values. The core function used for this was process_directory_intensity, which iterates through all audio files in the input directory and applies each noise type across a range of intensity values (from 0.05 to 0.50).

For each combination of audio file, noise type, and intensity, the program:

- Retrieves the duration and sample rate of the input audio using soxi.

- Ge- nerates a noise file of the same duration and sample rate using sox with the synth command and the specified noise type.

- Mixes the original audio with the generated noise using the sox -m command, scaling the noise volume according to the specified intensity (e.g., -v 0.2 for 20% noise intensity).

- Saves the output in the given output directory with filenames reflecting the original name, noise type, and intensity used.

## Implementation

### Main

//falar main, utilities e compressores usados

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