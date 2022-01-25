import pyaudio
import time


def mix_audio_bytes(chunks: list, chunk_size: int):
    all_chunks = {}
    amount_of_chunks = len(chunks)
    for i in range(0, chunk_size // 2):
        all_chunks[i] = []
    for chunk in chunks:
        current_chunk_index = 0
        for chunk_list in all_chunks.values():
            chunk_list.append(chunk[current_chunk_index:2 + current_chunk_index])
            current_chunk_index += 2

    final_bytes = b''
    for bytes_list in all_chunks.values():
        audio_int = 0
        for bytes_ in bytes_list:
            audio_int += int.from_bytes(bytes_, "little", signed=True) // amount_of_chunks
        final_bytes += audio_int.to_bytes(2, "little", signed=True)
    return final_bytes


def mix_audio_frames(frames_list: list):
    all_frames = {}
    for frames in frames_list:
        for i in range(0, len(frames)):
            all_frames[i] = []

    for frames in frames_list:
        current_frames_index = 0
        for frame_list in all_frames.values():
            try:
                frame_list.append(frames[current_frames_index])
                current_frames_index += 1
            except IndexError:
                break

    final_frames = []
    for chunk_list in all_frames.values():
        final_frames.append(mix_audio_bytes(chunk_list, 2048))
    return final_frames



CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream1 = p.open(format=FORMAT,
                 channels=CHANNELS,
                 rate=RATE,
                 input=True,
                 frames_per_buffer=CHUNK)

stream2 = p.open(format=FORMAT,
                 channels=CHANNELS,
                 rate=RATE,
                 output=True,
                 frames_per_buffer=CHUNK)

print("recording first time")
frames1 = []
for i in range(int(RATE / CHUNK * 3)):
    data = stream1.read(CHUNK)
    # if you want to hear your voice while recording
    # stream.write(data)
    frames1.append(data)

print("finished")
print("recording second time")
frames2 = []
for i in range(int(RATE / CHUNK * 3)):
    data = stream1.read(CHUNK)
    # if you want to hear your voice while recording
    # stream.write(data)
    frames2.append(data)

print("finished")

for frame in mix_audio_frames([frames1, frames2]):
    stream2.write(frame)

while True:
    pass
