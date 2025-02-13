import os
import subprocess
import math
import shutil
import traceback

sentences_data = {
    "1": {
        "start": 480,
    },
    "2": {
        "start": 3088,
    },
    "3": {
        "start": 3912,
    },
    "4": {
        "start": 6720,
    },
    "5": {
        "start": 9760,
    },
    "6": {
        "start": 10704,
    },
    "7": {
        "start": 12232,
    },
    "8": {
        "start": 13064,
    },
    "9": {
        "start": 13840,
    },
    "10": {
        "start": 15456,
    },
    "11": {
        "start": 16320,
    },
    "12": {
        "start": 18008,
    },
    "13": {
        "start": 20768,
    },
    "14": {
        "start": 21848,
    }
}

DIRECTORY="b3a77cca-818c-4962-9a1e-d99b4f7ebba9"
START_STRING = "start"

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

def concat_all_audio_with_trim_using_sox(batch_dict, audio_final):
    temp_files = []
    for idx, (audio_path, silence_gap) in enumerate(batch_dict):
        if silence_gap > 0:
            silence_file = os.path.join(DIRECTORY, f"silence_{idx}.wav")
            # Create a silence audio file of the specified gap duration
            cmd_silence = f'sox -n -r 22050 -c 1 "{silence_file}" trim 0 {silence_gap}'
            subprocess.run(cmd_silence, shell=True, check=True)
            # Prepend the silence to the current batch audio file
            combined_file = os.path.join(DIRECTORY, f"temp_concat_{idx}.wav")
            cmd_combine = f'sox "{silence_file}" "{audio_path}" "{combined_file}"'
            subprocess.run(cmd_combine, shell=True, check=True)
            temp_files.append(combined_file)
        else:
            temp_files.append(audio_path)

    # Concatenate all the (possibly modified) audio files into the final output
    inputs = " ".join(f'"{f}"' for f in temp_files)
    cmd_concat = f'sox {inputs} "{audio_final}"'
    subprocess.run(cmd_concat, shell=True, check=True)

def get_audio_duration(file_path):
    if not os.path.exists(file_path):
        return 0
    command = f'ffprobe -i "{file_path}" -show_entries format=duration -v quiet -of csv="p=0"'
    print(f"Getting audio duration: {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Audio duration: {result.stdout} for {file_path}")
    if result.returncode != 0:
        print(f"Failed to get audio duration: {result.stderr}")
        return 0
    return float(result.stdout)

def add_two_audio_files(audio_file, audio1, start):
    try:
        if not os.path.exists(audio_file):
            if start > 0:
                print("Creating silence of duration:", start)
                silence_file = DIRECTORY + "/" + f'output_audio_silence.wav'
                silence_command = f'''sox -n "{silence_file}" synth {start} sine 0 rate 22050'''
                subprocess.run(silence_command, shell=True, check=True)
                print("Silence created successfully.")

                print("Adding silence to the first audio file : ", audio1)
                audio1_with_silence = DIRECTORY + "/" + f'audio1_with_silence.wav'
                add_silence_command = f'''sox {silence_file} "{audio1}" "{audio1_with_silence}"'''
                subprocess.run(add_silence_command, shell=True, check=True)
                print("Silence added successfully with silence gap of {start} to the FIRST audio file : ", audio1)

                os.replace(audio1_with_silence, audio_file)
            else:
                print("Silence added successfully without silence gap to the FIRST audio file : ", audio1)
                shutil.copy(audio1, audio_file)

        else:
            temp_output_audio = str(DIRECTORY) + "/" + "temp_output_audio.wav"

            if start > 0:
                print("Creating silence of duration:", start)
                silence_file = DIRECTORY + "/" + f'output_audio_silence.wav'
                silence_command = f'''sox -n "{silence_file}" synth {start} sine 0 rate 22050'''
                subprocess.run(silence_command, shell=True, check=True)
                print("Silence created successfully.")

                print("Adding silence to the first audio file : ", audio1)
                audio1_with_silence = DIRECTORY + "/" + f'audio1_with_silence.wav'
                add_silence_command = f'''sox {silence_file} "{audio1}" "{audio1_with_silence}"'''
                subprocess.run(add_silence_command, shell=True, check=True)
                print("Silence added successfully to the first audio file : ", audio1)

                print("Mixing two audios : ", audio_file, audio1_with_silence, temp_output_audio)
                # concat_command = f'ffmpeg -loglevel error -y -i "concat:{audio_file}|{audio1_with_silence}" -acodec copy {temp_output_audio}'
                concat_command = f'sox "{audio_file}" "{audio1_with_silence}" "{temp_output_audio}"'
                print(f"Concatenating audio part {concat_command} with itself: {audio1_with_silence}")
                subprocess.run(concat_command, shell=True, check=True)
                print(f"add_two_audio_files - Replaced the audio file successfully")
                os.replace(temp_output_audio, audio_file)
            else:
                print("Mixing two audios without a gap : ", audio_file, temp_output_audio)
                # concat_command = f'ffmpeg -loglevel error -y -i "concat:{audio_file}|{audio1}" -acodec copy {temp_output_audio}'
                concat_command = f'sox "{audio_file}" "{audio1}" "{temp_output_audio}"'
                print(f"Concatenating audio part {concat_command} with itself: {audio1}")
                subprocess.run(concat_command, shell=True, check=True)
                print(f"add_two_audio_files - Replaced the audio file successfully")
                os.replace(temp_output_audio, audio_file)

    except:
        print("Failed to add two audio files {audio_file} and {audio1}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
