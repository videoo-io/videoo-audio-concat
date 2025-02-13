# videoo-audio-concat

# You will find pieces of audio in b3a77cca directory with names output_audio_1 2 3 ....

# Each audio has a  silence given as example below (you can find the exact values for each output_audio_ in data.py -> sentences_data)
# part1 0,48
# Part2 10.704
# part3 16.32

# You need to create a final_audio file "output_audio.wav" which will include all the output_audio_X.wav content concatenated
# without the silence at the begining of the audio files.

# The outline of final audio will be as below :

# 0 - 0.48 (output_audio_1.wav) ends somewhere - 10.704 (output_audio_2.wav) ends somewhere - ...

# How can I concat them, without having them the silence at the beginning using ffmpeg or sox

# Re-write concat_all_audio_with_trim_using_sox function and correct it 

# or 

# Write concat_all_audio_with_trim_using_ffmpeg equavalent
