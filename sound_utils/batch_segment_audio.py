from pydub import AudioSegment
import os

def create_fixed_segments(input_file, output_dir, num_segments, segment_duration_sec):
    audio = AudioSegment.from_file(input_file)
    total_duration_ms = len(audio)

    segment_duration_ms = segment_duration_sec * 1000

    # Compute step size to evenly distribute N segments, possibly overlapping
    total_needed_duration = (num_segments - 1) * (total_duration_ms - segment_duration_ms) / (num_segments - 1)
    step_ms = (total_duration_ms - segment_duration_ms) / (num_segments - 1)

    base_name = os.path.splitext(os.path.basename(input_file))[0]

    for i in range(num_segments):
        start_ms = int(i * step_ms)
        end_ms = start_ms + segment_duration_ms
        if end_ms > total_duration_ms:
            # Padding with silence if needed
            segment = audio[start_ms:] + AudioSegment.silent(duration=end_ms - total_duration_ms)
        else:
            segment = audio[start_ms:end_ms]

        output_filename = os.path.join(output_dir, f"{base_name}_segment{i+1}.wav")
        segment.export(output_filename, format="wav")
        print(f"Exported: {output_filename}")

def process_folder(folder_path, output_dir, num_segments, segment_duration_sec):
    os.makedirs(output_dir, exist_ok=True)
    supported_exts = ('.wav', '.mp3', '.flac', '.ogg')

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_exts):
            file_path = os.path.join(folder_path, filename)
            try:
                create_fixed_segments(file_path, output_dir, num_segments, segment_duration_sec)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

# Example usage
if __name__ == "__main__":
    input_folder = "../wav_sounds"       # Replace with your input folder path
    output_folder = "../wav_queries"   # Where to save segments
    num_segments = 10                   # Number of segments to create per song
    segment_length = 5                  # Duration of each segment in seconds

    process_folder(input_folder, output_folder, num_segments, segment_length)
