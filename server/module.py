import json
import os
from tinytag import TinyTag
from pydub import AudioSegment
import io

AUDIO_FOLDER = './audios'  # Folder containing audio files

# Function to extract metadata from an audio file
def get_audio_metadata(file_path):
    audio_file = TinyTag.get(file_path)
    dur = int(audio_file.duration)
    metadata = [
        audio_file.title,
        audio_file.artist,
        audio_file.album,
        # f'{audio_file.duration:.2f}',
        f"{dur//60}:{dur%60}",
        os.path.basename(file_path)
    ]
    return metadata

# Function to send metadata to client
def send_audio_metadata(client_socket):
    audio_files = os.listdir(AUDIO_FOLDER)
    audio_metadata = []

    for audio_file in audio_files:
        file_path = os.path.join(AUDIO_FOLDER, audio_file)
        if os.path.isfile(file_path) and audio_file.endswith(".mp3"):
            metadata = get_audio_metadata(file_path)
            audio_metadata.append(metadata)
    
    # Convert the list of dictionaries to JSON and send it to the client
    metadata_json = json.dumps(audio_metadata).encode()
    client_socket.send(str(len(metadata_json)).zfill(16).encode())
    client_socket.send(metadata_json)

def stream_audio(client_socket):

    name = client_socket.recv(50).decode()
    audio = AudioSegment.from_mp3(os.path.join('audios',name))
    buffer = io.BytesIO()

    audio.export(buffer, format="raw")

    client_socket.send(str(audio.channels).zfill(10).encode())
    client_socket.send(str(audio.frame_rate).zfill(10).encode())

    buffer.seek(0, io.SEEK_END)
    print(buffer.tell())
    client_socket.send(str(buffer.tell()).zfill(10).encode())

    chunk_size = 1024
    buffer.seek(0)
    data = buffer.read(chunk_size)

    while data:
        client_socket.send(data)
        data = buffer.read(chunk_size)

    client_socket.send("end".encode('utf-8'))