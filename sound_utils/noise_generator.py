import os
import numpy as np
from pydub import AudioSegment
from scipy.signal import lfilter
from scipy import signal

def generate_noise(noise_type, length, sample_rate=44100):
    """Generate different types of noise with proper spectral characteristics."""
    if noise_type == 'white':
        return np.random.normal(0, 1, length)
    
    elif noise_type == 'pink':
        # Better pink noise generation using frequency domain method
        # Create white noise
        white = np.random.randn(length)
        
        # Apply pink noise filter (1/f characteristic)
        # Using a more accurate pink noise filter
        b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
        a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
        
        # Apply filter
        pink = lfilter(b, a, white)
        
        # Remove DC component and normalize
        pink = pink - np.mean(pink)
        pink = pink / np.std(pink)  # Normalize to unit variance instead of peak
        return pink
    
    elif noise_type == 'brown':
        # Brown noise (Brownian motion) - integrate white noise
        white = np.random.normal(0, 1, length)
        brown = np.cumsum(white)
        
        # Remove DC and normalize to unit variance
        brown = brown - np.mean(brown)
        brown = brown / np.std(brown)
        return brown
    
    else:
        raise ValueError(f"Unsupported noise type: {noise_type}")

def calculate_rms(audio_data):
    """Calculate RMS (Root Mean Square) of audio data."""
    return np.sqrt(np.mean(audio_data**2))

def add_noise_snr_based(audio_segment, noise_type, snr_db):
    """Add noise based on Signal-to-Noise Ratio in dB."""
    # Get audio data
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float64)
    
    # Handle stereo audio
    if audio_segment.channels == 2:
        # Reshape to handle stereo (interleaved L,R,L,R...)
        samples = samples.reshape(-1, 2)
        mono_length = len(samples)
        
        # Generate noise for both channels
        noise_left = generate_noise(noise_type, mono_length, audio_segment.frame_rate)
        noise_right = generate_noise(noise_type, mono_length, audio_segment.frame_rate)
        noise = np.column_stack([noise_left, noise_right])
    else:
        # Mono audio
        noise = generate_noise(noise_type, len(samples), audio_segment.frame_rate)
        noise = noise.reshape(-1, 1) if len(samples.shape) == 1 else noise
        samples = samples.reshape(-1, 1) if len(samples.shape) == 1 else samples
    
    # Calculate RMS of original signal
    signal_rms = calculate_rms(samples)
    
    # Calculate desired noise RMS based on SNR
    # SNR(dB) = 20 * log10(signal_rms / noise_rms)
    # Therefore: noise_rms = signal_rms / (10^(SNR_dB/20))
    noise_rms_target = signal_rms / (10**(snr_db/20))
    
    # Scale noise to achieve target RMS
    current_noise_rms = calculate_rms(noise)
    if current_noise_rms > 0:
        noise = noise * (noise_rms_target / current_noise_rms)
    
    # Add noise to signal
    noisy_samples = samples + noise
    
    # Prevent clipping by scaling if necessary
    max_val = np.max(np.abs(noisy_samples))
    if max_val > 0.95:  # Leave some headroom
        scale_factor = 0.95 / max_val
        noisy_samples = noisy_samples * scale_factor
        print(f"Scaled by {scale_factor:.3f} to prevent clipping")
    
    # Convert back to original format
    if audio_segment.channels == 2:
        noisy_samples = noisy_samples.flatten()
    else:
        noisy_samples = noisy_samples.flatten()
    
    # Convert back to integer format
    if audio_segment.sample_width == 2:  # 16-bit
        noisy_samples = noisy_samples.astype(np.int16)
    elif audio_segment.sample_width == 4:  # 32-bit
        noisy_samples = noisy_samples.astype(np.int32)
    else:
        noisy_samples = noisy_samples.astype(np.int16)
    
    return audio_segment._spawn(noisy_samples.tobytes())

def add_noise_intensity_based(audio_segment, noise_type, intensity):
    """Add noise based on intensity factor (your original approach, but improved)."""
    # Get audio data
    samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float64)
    
    # Handle stereo audio
    if audio_segment.channels == 2:
        samples = samples.reshape(-1, 2)
        mono_length = len(samples)
        
        noise_left = generate_noise(noise_type, mono_length, audio_segment.frame_rate)
        noise_right = generate_noise(noise_type, mono_length, audio_segment.frame_rate)
        noise = np.column_stack([noise_left, noise_right])
    else:
        noise = generate_noise(noise_type, len(samples), audio_segment.frame_rate)
        noise = noise.reshape(-1, 1) if len(samples.shape) == 1 else noise
        samples = samples.reshape(-1, 1) if len(samples.shape) == 1 else samples
    
    # Scale noise by intensity and signal RMS for consistent relative levels
    signal_rms = calculate_rms(samples)
    noise = noise * intensity * signal_rms
    
    # Add noise
    noisy_samples = samples + noise
    
    # Prevent clipping
    max_val = np.max(np.abs(noisy_samples))
    if max_val > 0.95:
        scale_factor = 0.95 / max_val
        noisy_samples = noisy_samples * scale_factor
        print(f"Scaled by {scale_factor:.3f} to prevent clipping")
    
    # Convert back to original format
    if audio_segment.channels == 2:
        noisy_samples = noisy_samples.flatten()
    else:
        noisy_samples = noisy_samples.flatten()
    
    # Convert to appropriate integer format
    if audio_segment.sample_width == 2:
        noisy_samples = noisy_samples.astype(np.int16)
    elif audio_segment.sample_width == 4:
        noisy_samples = noisy_samples.astype(np.int32)
    else:
        noisy_samples = noisy_samples.astype(np.int16)
    
    return audio_segment._spawn(noisy_samples.tobytes())

def process_directory_intensity(input_dir, output_dir, 
                              intensities=[0.05, 0.1, 0.15, 0.2, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50], 
                              noise_types=['white', 'pink', 'brown']):
    """Process directory using intensity-based noise addition (your original method)."""
    os.makedirs(output_dir, exist_ok=True)
    
    for fname in os.listdir(input_dir):
        if fname.endswith(".wav"):
            path = os.path.join(input_dir, fname)
            try:
                audio = AudioSegment.from_wav(path)
                print(f"Processing {fname} - {audio.channels} channels, {audio.frame_rate}Hz")
                
                for noise_type in noise_types:
                    for intensity in intensities:
                        noisy_audio = add_noise_intensity_based(audio, noise_type, intensity)
                        out_name = f"{os.path.splitext(fname)[0]}_{noise_type}_intensity_{intensity}.wav"
                        out_path = os.path.join(output_dir, out_name)
                        noisy_audio.export(out_path, format="wav")
                        print(f"  Saved {out_name}")
                        
            except Exception as e:
                print(f"Error processing {fname}: {e}")

def process_directory_snr(input_dir, output_dir, 
                         snr_values=[20, 15, 10, 5, 0, -5], 
                         noise_types=['white', 'pink', 'brown']):
    """Process directory using SNR-based noise addition (more scientifically accurate)."""
    os.makedirs(output_dir, exist_ok=True)
    
    for fname in os.listdir(input_dir):
        if fname.endswith(".wav"):
            path = os.path.join(input_dir, fname)
            try:
                audio = AudioSegment.from_wav(path)
                print(f"Processing {fname} - {audio.channels} channels, {audio.frame_rate}Hz")
                
                for noise_type in noise_types:
                    for snr_db in snr_values:
                        noisy_audio = add_noise_snr_based(audio, noise_type, snr_db)
                        out_name = f"{os.path.splitext(fname)[0]}_{noise_type}_snr_{snr_db}dB.wav"
                        out_path = os.path.join(output_dir, out_name)
                        noisy_audio.export(out_path, format="wav")
                        print(f"  Saved {out_name}")
                        
            except Exception as e:
                print(f"Error processing {fname}: {e}")

if __name__ == "__main__":
    input_folder = "../wav_queries"     # Modify if needed
    output_folder = "../test_files"     # Output folder
    
    # Choose which method to use:
    
    # Method 1: Your original intensity-based approach (improved)
    print("Using intensity-based noise addition...")
    process_directory_intensity(input_folder, output_folder)
    
    # Method 2: SNR-based approach (more scientifically accurate)
    # Uncomment the following lines to use SNR-based method instead:
    # print("Using SNR-based noise addition...")
    # process_directory_snr(input_folder, output_folder + "_snr")