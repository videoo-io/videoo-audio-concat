import os
import subprocess
import math
import shutil
import traceback
import glob

DIRECTORY="b3a77cca-818c-4962-9a1e-d99b4f7ebba9"

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
