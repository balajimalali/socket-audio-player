import socket
import json
import threading
import io
import pyaudio
import threading
import time

HOST = 'localhost'
PORT = 12345

buffer = io.BytesIO()

AUDIO = ""

play_song = True

def play_pause():
    global play_song
    if play_song:
        play_song = False
    else:
        play_song = True

def set_audio(name):
    global AUDIO
    AUDIO = name

audio_format = pyaudio.paInt16
channels = None
rate = None
size = 0
pos = 0
total_size = 0

lock = threading.Lock()
seek_lock = threading.Lock()

def receive(client_socket, name, update_seekbar):
    global size, buffer, AUDIO
    global total_size, pos

    
    buffer.truncate(0)
    buffer.seek(0)
    pos = 0
    size = 0
    step = 0

    while size<total_size and name==AUDIO:
        with lock:
            data = client_socket.recv(1024)
            # print("receiing..")
            buffer.seek(size)
            buffer.write(data)
            size = size+1024
            step += 1
            if step>=10:
                with seek_lock:
                    step = 0
                    update_seekbar(lp=size*100/total_size)



def play(name, update_seekbar):
    
    global pos, AUDIO, play_song
    global total_size, channels, rate, audio_format

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format, channels=channels, rate=rate, output=True)
    while pos<total_size and name==AUDIO:
        while not play_song:
            time.sleep(0.1)
            if name!=AUDIO:
                break
        data = None
        with lock:
            chunk_size = 1024
            if size>=pos+chunk_size:

                # print("playing..")
                
                buffer.seek(pos)
                data = buffer.read(chunk_size)
            else:
                print("buffering..")
        if name==AUDIO and data!=None:
            stream.write(data)
            pos = pos+chunk_size
        with seek_lock:
            update_seekbar(pp=pos*100/total_size)
    stream.stop_stream()
    stream.close()
    p.terminate()



def get_initial_data():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(f"{"Audios":<{16}}".encode())
    data_size = int(client_socket.recv(16).decode())
    print(data_size)
    data = ""

    while len(data)<data_size:
        data += client_socket.recv(1024).decode()

    client_socket.close()

    return json.loads(data)

def play_song(name,update_seekbar):
    global channels, rate, total_size, AUDIO, buffer, pos, size

    AUDIO = name
    # time.sleep(5)
    buffer.truncate(0)
    buffer.seek(0)
    pos = 0
    size = 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(f"{"Play":<{16}}".encode())

    client_socket.send(f"{name:<{50}}".encode())

    ch = client_socket.recv(10)
    channels = int(ch.decode())

    fr = client_socket.recv(10)
    rate = int(fr.decode())

    ts = client_socket.recv(10)
    total_size = int(ts.decode())

    print(f"ch {channels}, fr {rate}, total_size {total_size} ")

    stream_thread = threading.Thread(target=receive, args=(client_socket, name, update_seekbar), daemon=True)
    play_thread = threading.Thread(target=play, args=(name, update_seekbar), daemon=True)

    stream_thread.start()
    play_thread.start()

    stream_thread.join()
    play_thread.join()
    
    update_seekbar(lp=0.2, pp=0.2)
    print("done")
    client_socket.close()