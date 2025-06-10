import os
import subprocess
import shutil
from pathlib import Path

def check_sox_installation():
    """Check if SoX is installed and available."""
    try:
        result = subprocess.run(['sox', '--version'], capture_output=True, text=True)
        print(f"SoX found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("Error: SoX is not installed or not in PATH")
        print("Please install SoX:")
        print("  Ubuntu/Debian: sudo apt-get install sox")
        print("  macOS: brew install sox")
        print("  Windows: Download from http://sox.sourceforge.net/")
        return False

def get_audio_info(input_file):
    """Get audio file information using SoX."""
    try:
        result = subprocess.run(['soxi', input_file], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception as e:
        print(f"Error getting audio info: {e}")
        return None

def add_noise_with_sox(input_file, output_file, noise_type, snr_db=None, intensity=None):
    """
    Add noise to audio file using SoX.
    
    Args:
        input_file: Path to input audio file
        output_file: Path to output audio file
        noise_type: 'white', 'pink', or 'brown'
        snr_db: Signal-to-noise ratio in dB (if using SNR method)
        intensity: Noise intensity factor (if using intensity method)
    """
    temp_noise = None
    try:
        # Get input file duration
        duration_result = subprocess.run(
            ['soxi', '-D', input_file], 
            capture_output=True, text=True
        )
        
        if duration_result.returncode != 0:
            print(f"Error getting duration for {input_file}")
            return False
            
        duration = float(duration_result.stdout.strip())
        
        # Get sample rate
        rate_result = subprocess.run(
            ['soxi', '-r', input_file], 
            capture_output=True, text=True
        )
        
        if rate_result.returncode != 0:
            print(f"Error getting sample rate for {input_file}")
            return False
            
        sample_rate = int(rate_result.stdout.strip())
        
        # Create temporary noise file
        temp_noise = f"temp_noise_{noise_type}.wav"
        
        # Generate noise based on type - FIXED COMMAND STRUCTURE
        if noise_type == 'white':
            # Generate white noise
            noise_cmd = [
                'sox', '-n', '-r', str(sample_rate), temp_noise, 
                'synth', str(duration), 'whitenoise'
            ]
        elif noise_type == 'pink':
            # Generate pink noise
            noise_cmd = [
                'sox', '-n', '-r', str(sample_rate), temp_noise, 
                'synth', str(duration), 'pinknoise'
            ]
        elif noise_type == 'brown':
            # Generate brown noise (Brownian/red noise)
            noise_cmd = [
                'sox', '-n', '-r', str(sample_rate), temp_noise, 
                'synth', str(duration), 'brownnoise'
            ]
        else:
            print(f"Unsupported noise type: {noise_type}")
            return False
        
        # Generate noise
        result = subprocess.run(noise_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error generating noise: {result.stderr}")
            return False
        
        # Mix the original audio with noise
        if snr_db is not None:
            # SNR-based mixing
            # Convert SNR to volume ratio
            # SNR(dB) = 20*log10(signal/noise), so noise_volume = 10^(-SNR/20)
            noise_volume = 10**(-snr_db/20)
            
            mix_cmd = [
                'sox', '-m', 
                input_file,
                '-v', str(noise_volume), temp_noise,
                output_file
            ]
        else:
            # Intensity-based mixing (simple volume scaling)
            if intensity is None:
                intensity = 0.1  # Default intensity
                
            mix_cmd = [
                'sox', '-m',
                input_file,
                '-v', str(intensity), temp_noise,
                output_file
            ]
        
        # Execute mixing command
        result = subprocess.run(mix_cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        if temp_noise and os.path.exists(temp_noise):
            os.remove(temp_noise)
        
        if result.returncode != 0:
            print(f"Error mixing audio: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        # Clean up temp file if it exists
        if temp_noise and os.path.exists(temp_noise):
            os.remove(temp_noise)
        return False

def process_directory_snr(input_dir, output_dir, 
                         snr_values=[20, 15, 10, 5, 0, -5], 
                         noise_types=['white', 'pink', 'brown']):
    """Process directory using SNR-based noise addition with SoX."""
    
    if not check_sox_installation():
        return
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get all audio files (not just .wav)
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aiff', '.au']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(Path(input_dir).glob(f"*{ext}"))
        audio_files.extend(Path(input_dir).glob(f"*{ext.upper()}"))
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    for audio_file in audio_files:
        print(f"\nProcessing {audio_file.name}...")
        
        # Get and display audio info
        info = get_audio_info(str(audio_file))
        if info:
            print("Audio info:")
            for line in info.split('\n')[:3]:  # Show first 3 lines
                if line.strip():
                    print(f"  {line}")
        
        for noise_type in noise_types:
            for snr_db in snr_values:
                # Create output filename
                stem = audio_file.stem
                out_name = f"{stem}_{noise_type}_snr_{snr_db}dB.wav"
                out_path = Path(output_dir) / out_name
                
                print(f"  Adding {noise_type} noise at {snr_db}dB SNR...")
                
                success = add_noise_with_sox(
                    str(audio_file), 
                    str(out_path), 
                    noise_type, 
                    snr_db=snr_db
                )
                
                if success:
                    print(f"    ✓ Saved {out_name}")
                else:
                    print(f"    ✗ Failed to create {out_name}")

def process_directory_intensity(input_dir, output_dir, 
                              intensities=[0.05, 0.1, 0.15, 0.2, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50], 
                              noise_types=['white', 'pink', 'brown']):
    """Process directory using intensity-based noise addition with SoX."""
    
    if not check_sox_installation():
        return
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get all audio files
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aiff', '.au']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(Path(input_dir).glob(f"*{ext}"))
        audio_files.extend(Path(input_dir).glob(f"*{ext.upper()}"))
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    for audio_file in audio_files:
        print(f"\nProcessing {audio_file.name}...")
        
        # Get and display audio info
        info = get_audio_info(str(audio_file))
        if info:
            print("Audio info:")
            for line in info.split('\n')[:3]:  # Show first 3 lines
                if line.strip():
                    print(f"  {line}")
        
        for noise_type in noise_types:
            for intensity in intensities:
                # Create output filename
                stem = audio_file.stem
                out_name = f"{stem}_{noise_type}_intensity_{intensity}.wav"
                out_path = Path(output_dir) / out_name
                
                print(f"  Adding {noise_type} noise at {intensity} intensity...")
                
                success = add_noise_with_sox(
                    str(audio_file), 
                    str(out_path), 
                    noise_type, 
                    intensity=intensity
                )
                
                if success:
                    print(f"    ✓ Saved {out_name}")
                else:
                    print(f"    ✗ Failed to create {out_name}")

def process_single_file(input_file, output_dir, noise_type='white', snr_db=10):
    """Process a single file for testing."""
    
    if not check_sox_installation():
        return
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    input_path = Path(input_file)
    out_name = f"{input_path.stem}_{noise_type}_snr_{snr_db}dB.wav"
    out_path = Path(output_dir) / out_name
    
    print(f"Processing {input_path.name} with {noise_type} noise at {snr_db}dB SNR...")
    
    success = add_noise_with_sox(str(input_path), str(out_path), noise_type, snr_db=snr_db)
    
    if success:
        print(f"✓ Saved {out_name}")
    else:
        print(f"✗ Failed to create {out_name}")

if __name__ == "__main__":
    # Configuration
    input_folder = "../wav_queries"     # Modify as needed
    output_folder = "../test_files_sox"  # Output folder
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        print("Please update the input_folder path or create the directory.")
        exit(1)
    
    print("SoX Audio Noise Addition Script")
    print("=" * 40)
    
    # Choose processing method
    method = input("\nChoose method:\n1. SNR-based (recommended)\n2. Intensity-based\n3. Test single file\nEnter choice (1-3): ").strip()
    
    if method == "1":
        print("\nUsing SNR-based noise addition with SoX...")
        process_directory_snr(input_folder, output_folder + "_snr")
        
    elif method == "2":
        print("\nUsing intensity-based noise addition with SoX...")
        process_directory_intensity(input_folder, output_folder + "_intensity")
        
    elif method == "3":
        # Test with a single file
        test_files = list(Path(input_folder).glob("*.wav"))
        if test_files:
            test_file = test_files[0]
            print(f"\nTesting with {test_file.name}...")
            process_single_file(str(test_file), output_folder + "_test")
        else:
            print("No .wav files found for testing")
    
    else:
        print("Invalid choice. Please run the script again.")
    
    print("\nDone!")