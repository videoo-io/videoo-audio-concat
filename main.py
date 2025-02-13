import os
import subprocess
import math
import shutil
import traceback
import glob

DIRECTORY="b3a77cca-818c-4962-9a1e-d99b4f7ebba9"
START_STRING = "start"

from helper import get_audio_duration, add_two_audio_files
from data import sentences_data


def main():
    batch_size = 5
    audio_final = f"{DIRECTORY}/output_audio.wav"
    batch_dict = []
    prev_audio_one = None
    for i, (key, sentence) in enumerate(sentences_data.items()):
        index = i + 1
        batch_index = math.ceil(index / batch_size)
        print(f"Adding batch_count index: {index} audio files")
        audio_one = os.path.join(DIRECTORY, f"output_audio_part_{batch_index}.wav")
        audio_two = os.path.join(DIRECTORY, f"output_audio_{index}.wav")
        sentence_start = sentence[START_STRING] / 1000
        if prev_audio_one != audio_one: batch_dict.append(tuple([audio_one, sentence_start]))
        current_audio_indicator = get_audio_duration(audio_one)
        gap = sentence_start - get_audio_duration(audio_one) if sentence_start > current_audio_indicator else 0
        print("BATCH CONCAT AUDIO FILES: ", audio_one, audio_two, gap, sentence_start, current_audio_indicator)
        add_two_audio_files(audio_one, audio_two, gap)
        prev_audio_one = audio_one

    concat_all_audio_with_trim_using_sox(batch_dict, audio_final)

    pattern = os.path.join(DIRECTORY, "output_audio_part_*.wav")
    for file_path in glob.glob(pattern):
        try:
            os.remove(file_path)
            print(f"Removed file: {file_path}")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

def concat_all_audio_with_trim_using_sox(batch_dict, audio_final):
    temp_files = []
    for idx, (audio_path, silence_gap) in enumerate(batch_dict):
        if silence_gap > 0:
            combined_file = os.path.join(DIRECTORY, f"temp_trimmed_{idx}.wav")
            # Remove the silence_gap duration from the beginning of the audio file
            cmd_trim = f'sox "{audio_path}" "{combined_file}" trim {silence_gap}'
            subprocess.run(cmd_trim, shell=True, check=True)
            temp_files.append(combined_file)
        else:
            temp_files.append(audio_path)

    # Concatenate all the (possibly modified) audio files into the combined file
    combined_file = os.path.join(DIRECTORY, audio_final)
    inputs = " ".join(f'"{f}"' for f in temp_files)
    cmd_concat = f'sox {inputs} "{audio_final}"'
    subprocess.run(cmd_concat, shell=True, check=True)

    # Remove temporary trimmed files
    for file_path in temp_files:
        if os.path.basename(file_path).startswith("temp_trimmed_"):
            try:
                os.remove(file_path)
                print(f"Removed temporary file: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

if __name__ == "__main__":
    main()
