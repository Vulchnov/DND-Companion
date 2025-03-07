import vlc
import customtkinter as ctk
from customtkinter import filedialog

instanceDict = {}
playerDict = {}

root = ctk.CTk()
root.geometry("1920x1080")
root.title("SoundBoard")

title_label = ctk.CTkLabel(root, text="SoundBoard", font=ctk.CTkFont(size=30, weight="bold"))
title_label.pack(padx = 10, pady = (40, 20))

scrollable_frame = ctk.CTkScrollableFrame(root, width= 1400, height=800)
scrollable_frame.pack()


def add_song():
    frame = ctk.CTkFrame(scrollable_frame, width=1000, height=400)
    frame.pack()
    fileName = filedialog.askopenfilename()
    instance = vlc.Instance("--aout=directsound")
    player = instance.media_player_new()
    media = instance.media_new(fileName)
    player.set_media(media)

    splitName = fileName.split("/")
    name = splitName[len(splitName)-1]
    song_label = ctk.CTkLabel(frame, text = name)
    song_label.pack()
    slider = ctk.CTkSlider(frame, from_ = 0, to = 100, number_of_steps = 100, command = lambda val, name = name: slider_event(val, name))
    slider.set(100)
    slider.pack()
    pause_button = ctk.CTkButton(frame, text = "Play", width = 500, command = lambda name = name: pause_song(name, pause_button))
    pause_button.pack(pady = 20)

    delete_button = ctk.CTkButton(frame, text = "Remove", width = 500, command = lambda name = name, frame = frame: remove_song(name, frame))
    delete_button.pack()

    playerDict[name] = player
    instanceDict[name] = instance
    

def pause_song(name, pause_button):
    if pause_button.cget("text") == "Pause":
        pause_button.configure(text = "Play")
        playerDict[name].pause()
    else:
        pause_button.configure(text = "Pause")
        playerDict[name].play()
    

def slider_event(value, name):
    playerDict[name].audio_set_volume(int(value))

def remove_song(name, frame):
    playerDict[name].release()
    instanceDict[name].release()
    playerDict.pop(name)
    instanceDict.pop(name)
    frame.destroy()

add_button = ctk.CTkButton(root, text = "Add", width = 500, command = add_song)
add_button.pack(pady = 20)

root.mainloop()