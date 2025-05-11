import os
import numpy as np
from pydub import AudioSegment
from scipy.signal import lfilter

def generate_noise(noise_type, length):
    if noise_type == 'white':
        return np.random.normal(0, 1, length)
    elif noise_type == 'pink':
        # Voss-McCartney approximation with filter
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        white = np.random.randn(length)
        pink = lfilter(b, a, white)
        pink = pink - np.mean(pink)  # remove DC offset
        pink = pink / np.max(np.abs(pink))  # normalize to [-1, 1]
        return pink
    elif noise_type == 'brown':
        brown = np.cumsum(np.random.normal(0, 1, length))
        brown = brown - np.mean(brown)
        brown = brown / np.max(np.abs(brown))
        return brown
    else:
        raise ValueError(f"Unsupported noise type: {noise_type}")

def add_noise(audio_segment, noise_type, intensity):
    samples = np.array(audio_segment.get_array_of_samples())
    noise = generate_noise(noise_type, len(samples))
    noisy = samples + intensity * noise
    noisy = noisy / np.max(np.abs(noisy)) * np.max(np.abs(samples))  # Normalize
    return audio_segment._spawn(noisy.astype(samples.dtype).tobytes())

def process_directory(input_dir, output_dir, intensities=[0.05, 0.1, 0.15, 0.2], noise_types=['white', 'pink', 'brown']):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.endswith(".wav"):
            path = os.path.join(input_dir, fname)
            audio = AudioSegment.from_wav(path)
            for noise_type in noise_types:
                for intensity in intensities:
                    noisy_audio = add_noise(audio, noise_type, intensity)
                    out_name = f"{os.path.splitext(fname)[0]}_{noise_type}_intensity_{intensity}.wav"
                    out_path = os.path.join(output_dir, out_name)
                    noisy_audio.export(out_path, format="wav")
                    print(f"Saved {out_path}")

if __name__ == "__main__":
    input_folder = "wav_queries"     # Modify if needed
    output_folder = "test_files"     # Output folder
    process_directory(input_folder, output_folder)
