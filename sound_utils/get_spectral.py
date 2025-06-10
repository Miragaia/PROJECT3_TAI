import sys
import numpy as np
import soundfile as sf
from scipy.fftpack import fft

def get_spectral(
    filename,
    ws=1024,
    sh=256,
    ds=4
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
        power = np.abs(fft_out[:ws // 2])  # magnitude espectral (não ao quadrado)

        # Normalizar para 0-255 e converter para uint8
        power_norm = power / power.max() if power.max() > 0 else power
        power_scaled = np.round(power_norm * 255).astype(np.uint8)

        # Limita o vetor a 256 bins para ficar igual ao seu maxfreq (top freq clamped)
        if len(power_scaled) > 256:
            power_scaled = power_scaled[:256]

        signatures.append(power_scaled)

    return signatures

def write_signature_to_file(signatures, outfile):
    with open(outfile, "wb") as f:
        for window in signatures:
            f.write(window.tobytes())

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 get_spectral.py <input_wav> <output_freqs>")
        sys.exit(1)

    input_wav = sys.argv[1]
    output_freqs = sys.argv[2]

    sigs = get_spectral(input_wav)
    write_signature_to_file(sigs, output_freqs)
