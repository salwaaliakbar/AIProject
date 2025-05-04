from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

# Specify input video and output audio file
input_video = "test.mp4"
output_audio = "test_audio.mp3"

# Extract audio using MoviePy's ffmpeg_tools
ffmpeg_extract_audio(input_video, output_audio)
