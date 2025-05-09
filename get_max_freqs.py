import sys
import numpy as np
import soundfile as sf
from scipy.fftpack import fft

def get_max_freqs(
    filename,
    ws=1024,
    sh=256,
    ds=4,
    nf=4
):
    audio, sr = sf.read(filename)

    if sr != 44100:
        raise ValueError("Sample rate must be 44100 Hz.")
    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("Only stereo audio is supported.")

    mono = np.sum(audio, axis=1)
    mono_down = np.convolve(mono, np.ones(ds)/ds, mode='valid')[::ds]

    num_windows = (len(mono_down) - ws) // sh + 1
    signatures = []

    for i in range(num_windows):
        start = i * sh
        end = start + ws
        window = mono_down[start:end]
        if len(window) != ws:
            continue

        fft_out = fft(window)
        power = np.abs(fft_out[:ws // 2]) ** 2
        top_indices = np.argpartition(-power, nf)[:nf]
        top_indices_sorted = sorted(top_indices, key=lambda x: -power[x])
        top_indices_clamped = [min(idx, 255) for idx in top_indices_sorted]
        signatures.append(top_indices_clamped)

    return signatures

def write_signature_to_file(signatures, outfile):
    with open(outfile, "wb") as f:
        for window in signatures:
            for freq in window:
                f.write(bytes([freq]))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 get_max_freqs.py <input_wav> <output_freqs>")
        sys.exit(1)

    input_wav = sys.argv[1]
    output_freqs = sys.argv[2]

    sigs = get_max_freqs(input_wav)
    write_signature_to_file(sigs, output_freqs)
