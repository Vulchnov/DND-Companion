import os
import vlc
import customtkinter as ctk
from customtkinter import filedialog

instanceDict = {}
playerDict = {}

root = ctk.CTk()
root.geometry("1920x1080")
root.title("SoundBoard")


def pause_all_songs(pause_all_button):
    if pause_all_button.cget("text") == "Pause All":
        for name in playerDict:
            if playerDict[name][1].cget("text") == "Pause":
                pause_song(name)
        pause_all_button.configure(text = "Play All")
    elif pause_all_button.cget("text") == "Play All":
        for name in playerDict:
            if playerDict[name][1].cget("text") == "Play":
                pause_song(name)
        pause_all_button.configure(text = "Pause All")



title_label = ctk.CTkLabel(root, text="SoundBoard", font=ctk.CTkFont(size=30, weight="bold"))
title_label.pack(padx = 10, pady = (20, 0))


pause_all_button = ctk.CTkButton(root, width=400,  text = "Play All", command= lambda: pause_all_songs(pause_all_button))
pause_all_button.pack(pady = 20)


scrollable_frame = ctk.CTkScrollableFrame(root, width= 1400, height=800)
scrollable_frame.pack()


def set_song_loop(player, check_var):
    if check_var.get():
        player.set_playback_mode(vlc.PlaybackMode(1))
    else:
        player.set_playback_mode(vlc.PlaybackMode(0))
    
def add_song_list():
    filenames = filedialog.askopenfilenames()
    for fileName in filenames:
        add_song(fileName)


def add_song(fileName):
    frame = ctk.CTkFrame(scrollable_frame, width=1000, height=400)
    frame.pack()
    instance = vlc.Instance("--aout=directsound")
    media_list = instance.media_list_new()
    player = instance.media_list_player_new()
    media = instance.media_new(fileName)
    media_list.add_media(media)
    player.set_media_list(media_list)

    splitName = fileName.split("/")
    name = splitName[len(splitName)-1]
    song_label = ctk.CTkLabel(frame, text = name)
    song_label.pack()
    slider = ctk.CTkSlider(frame, from_ = 0, to = 100, number_of_steps = 100, command = lambda val, name = name: slider_event(val, name))
    slider.set(100)
    slider.pack(pady = (0, 20))

    check_var = ctk.BooleanVar(value = False)
    loop_checkbox = ctk.CTkCheckBox(frame, text="Loop", variable=check_var, onvalue=True, offvalue=False, command= lambda player = player, check_var = check_var: set_song_loop(player, check_var))
    loop_checkbox.pack()

    pause_button = ctk.CTkButton(frame, text = "Play", width = 500, command = lambda name = name: pause_song(name))
    pause_button.pack(pady = 20)

    delete_button = ctk.CTkButton(frame, text = "Remove", width = 500, command = lambda name = name, frame = frame: remove_song(name, frame))
    delete_button.pack()

    playerDict[name] = (player, pause_button)
    instanceDict[name] = instance
    

def pause_song(name):
    pause_button = playerDict[name][1]
    if pause_button.cget("text") == "Pause":
        pause_button.configure(text = "Play")
        playerDict[name][0].pause()
    else:
        pause_button.configure(text = "Pause")
        playerDict[name][0].play()
    

def slider_event(value, name):
    playerDict[name][0].get_media_player().audio_set_volume(int(value))

def remove_song(name, frame):
    playerDict[name][0].stop()
    playerDict[name][0].release()
    instanceDict[name].release()
    playerDict.pop(name)
    instanceDict.pop(name)
    frame.destroy()

add_button = ctk.CTkButton(root, text = "Add", width = 500, command = add_song_list)
add_button.pack(pady = 20)

root.mainloop()