import tkinter as tk
from tkinter import ttk
from module import get_initial_data, play_song, set_audio, play_pause
import threading
import time

loaded_percentage = 0
play_percentage = 0

def on_row_select(event):
    selected_item = playlist.selection()
    if selected_item:
        tags = playlist.item(selected_item[0], "tags")
        audio_name = tags[0]
        print(f"playing {audio_name}")
        update_seekbar(lp=0.2, pp=0.2)
        thread = threading.Thread(target=play_song, args=(audio_name, update_seekbar), daemon=True)
        thread.start()

def toggle_play():
    # Placeholder for play/pause functionality
    if play_pause():
        play_button["text"] = "Pause"
    else:
        play_button["text"] = "Play"
    
    print("Play/Pause toggled")

def on_close():
    print("Stoping")
    set_audio("xyz")
    root.destroy()

def update_seekbar(event=None, lp=None, pp=None):
    global play_percentage
    global loaded_percentage
    if pp:
        play_percentage = pp
    if lp:
        loaded_percentage = lp

    current_width = seekbar_canvas.winfo_width()
    
    seekbar_canvas.coords(loaded_rect, 0, 0, current_width * (loaded_percentage / 100), 10)
    seekbar_canvas.coords(play_rect, 0, 0, current_width * (play_percentage / 100), 10)



root = tk.Tk()
root.title("Music Player")
root.geometry("500x400")


playlist_frame = ttk.Frame(root)
playlist_frame.pack(fill=tk.BOTH, expand=True)

# Treeview for playlist with rows acting as buttons
columns = ("Name", "Aritst", "Album", "Duration")
playlist = ttk.Treeview(playlist_frame, columns=columns, show="headings")

for col in columns:
    playlist.heading(col, text=col)
    playlist.column(col, width=100, anchor=tk.CENTER)


playlist.bind("<<TreeviewSelect>>", on_row_select)

playlist.pack(fill=tk.BOTH, expand=True)


control_frame = ttk.Frame(root)
control_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Play/Pause Button
play_button = ttk.Button(control_frame, text="Pause", command=toggle_play)
play_button.pack(side=tk.LEFT, padx=10, pady=10)

# Seekbar Frame
seekbar_frame = ttk.Frame(control_frame)
seekbar_frame.pack(fill=tk.X, expand=True, padx=10)

# Timeline Labels
# loaded_label = tk.Label(seekbar_frame, text="0:00")
# loaded_label.pack(side=tk.LEFT)

# Canvas for Seekbar
seekbar_width = 300
seekbar_canvas = tk.Canvas(seekbar_frame, width=seekbar_width, height=10, bg="gray", highlightthickness=0)
seekbar_canvas.pack(fill=tk.X, expand=True, padx=5)

# Background (Gray)
seekbar_canvas.create_rectangle(0, 0, seekbar_width, 10, fill="gray", outline="")

# Loaded progress (White)
loaded_rect = seekbar_canvas.create_rectangle(0, 0, 0, 10, fill="white", outline="")

# Play progress (Red)
play_rect = seekbar_canvas.create_rectangle(0, 0, 0, 10, fill="red", outline="")

# Playtime Label
# playtime_label = tk.Label(seekbar_frame, text="0:00")
# playtime_label.pack(side=tk.RIGHT)


seekbar_canvas.bind("<Configure>", update_seekbar)

# root.after(100, lambda: update_seekbar(lp=100, pp=30))

songs = get_initial_data()
# print(playlist)
for song in songs:
    tag = song.pop()
    playlist.insert("", tk.END, values=song, tags=(tag,))

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
