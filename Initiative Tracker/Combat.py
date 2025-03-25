import customtkinter as ctk
import Combatent
import socket
import queue
import threading

#Lists for keeping track of who is in the combat and the order of initiative
tempCombatantsList = []
combatantsList = []
initiativeList = []
playerList = []
info_list_frame = None
combat_round = 1
combat_start = False
isDM = False
player = None


#Main Window
root = ctk.CTk()
root.geometry("1920x1080")
root.title("DnD Companion")

def nextInitiative(scrollable_frame):
    global initiativeList
    global combat_round
    if initiativeList[1] == "End":
        initiativeList.append(initiativeList.pop(0))
        combat_round += 1
    initiativeList.append(initiativeList.pop(0))
    drawInitiative(scrollable_frame)


def restartCombat(restart_button, next_button, clear_button, combat_start_button, scrollable_frame):
    global initiativeList
    global tempCombatantsList
    global combatantsList
    global combat_start
    global playerList
    combat_start = False
    combat_start_button.grid(row = 0, column = 4)
    next_button.grid_forget()
    clear_button.grid_forget()
    restart_button.grid_forget()
    for player in playerList:
        dialog = ctk.CTkInputDialog(text= "New initiative for " + player.pName)
        newInitiative = int(dialog.get_input())
        player.setInitiative(newInitiative)

    tempCombatantsList = playerList
    combatantsList = playerList
    initiativeList.clear()
    buildInitiative()
    drawInitiative(scrollable_frame)


def clearInitiative(restart_button, next_button, clear_button, combat_start_button, scrollable_frame):
    global initiativeList
    global tempCombatantsList
    global playerList
    global combatantsList
    global combat_start 
    combat_start = False
    combat_start_button.grid(row = 0, column = 4)
    next_button.grid_forget()
    clear_button.grid_forget()
    restart_button.grid_forget()
    initiativeList.clear()
    tempCombatantsList.clear()
    playerList.clear()
    combatantsList.clear()
    drawInitiative(scrollable_frame)
    
def startCombat(restart_button, next_button, clear_button, combat_start_button):
    global combat_start
    global playerList
    combat_start = True
    combat_start_button.grid_forget()
    next_button.grid(row = 0, column = 0, padx = 10)
    clear_button.grid(row = 0, column = 1, padx = 10)
    restart_button.grid(row = 0, column = 2, padx = 10)

def isPlayerCheckBoxCommand(health_entry, isPlayerCheckbox):
    if(isPlayerCheckbox.get()):
        health_entry.grid_forget()
    else:
        health_entry.grid(row= 0, column = 4, padx = 10)

def hasSaveDCCheckBoxCommand(saveDC_entry, hasSaveDCCheckbox):
    if(hasSaveDCCheckbox.get()):
        saveDC_entry.grid(row= 0, column = 5, padx = 10)
    else:
        saveDC_entry.grid_forget()

def removeCombatant(combatant, scrollable_frame):
    global initiativeList
    global playerList
    global combatantsList

    initiativeList.remove(combatant)
    combatantsList.remove(combatant)
    if combatant.isPlayer:
        playerList.remove(combatant)
    drawInitiative(scrollable_frame)

def healCombatant(combatant, entry):
    combatant.health += int(entry.get())
    drawInfoFrame()


def harmCombatant(combatant, entry):
    combatant.health -= int(entry.get())
    drawInfoFrame()


def drawInfoFrame():
    global initiativeList
    global info_list_frame
    global isDM

    for child in info_list_frame.winfo_children():
        child.destroy()

    name_label = ctk.CTkLabel(info_list_frame, text="Name", font = ctk.CTkFont(size=15, weight="bold"))
    name_label.grid(row = 0, column = 0)
    AC_label = ctk.CTkLabel(info_list_frame, text="AC", font = ctk.CTkFont(size=15, weight="bold"))
    AC_label.grid(row = 0, column = 1, padx = 20)
    DC_label = ctk.CTkLabel(info_list_frame, text="Save DC", font = ctk.CTkFont(size=15, weight="bold"))
    DC_label.grid(row = 0, column = 2, padx = 20)
    health_label = ctk.CTkLabel(info_list_frame, text="Health", font = ctk.CTkFont(size=15, weight="bold"))
    health_label.grid(row = 0, column = 3)
    
    if isDM:
        for i in range(len(combatantsList)):
            pName_label = ctk.CTkLabel(info_list_frame, text = combatantsList[i].pName)
            pAC_label = ctk.CTkLabel(info_list_frame, text = combatantsList[i].ac)
            pName_label.grid(row = i + 1, column = 0)
            pAC_label.grid(row = i + 1, column = 1)

            if not combatantsList[i].saveDC == None:
                psaveDCInitiative_label = ctk.CTkLabel(info_list_frame, text = combatantsList[i].saveDC)
                psaveDCInitiative_label.grid(row = i + 1, column = 2)

            if not combatantsList[i].health == None:
                cHealth_label = ctk.CTkLabel(info_list_frame, text = combatantsList[i].health)
                cHealth_label.grid(row = i + 1, column = 3)
                health_adjust_frame = ctk.CTkFrame(info_list_frame)
                health_adjust_frame.grid(row = i+1, column = 4, padx = 10, pady = 10)
                cHealth_entry = ctk.CTkEntry(health_adjust_frame, 100, 40)
                cHealth_heal_button = ctk.CTkButton(health_adjust_frame, text = "Heal", command = lambda combatant = combatantsList[i], entry = cHealth_entry: healCombatant(combatant, entry))
                cHealth_harm_button = ctk.CTkButton(health_adjust_frame, text = "Harm", command = lambda combatant = combatantsList[i], entry = cHealth_entry: harmCombatant(combatant, entry))
                cHealth_heal_button.pack()
                cHealth_entry.pack()
                cHealth_harm_button.pack()


#Draw the initiative order
def drawInitiative(scrollable_frame):
    global combat_round
    global combat_start
    global isDM
    for child in scrollable_frame.winfo_children():
        child.destroy()
    initiative_frame = ctk.CTkFrame(scrollable_frame, 1400, 800)
    initiative_frame.pack()
    
    if not combat_start:
        drawInfoFrame()
    #Inside Frame
    name_label = ctk.CTkLabel(initiative_frame, text = "Name", font = ctk.CTkFont(size = 15, weight = "bold"))
    name_label.grid(row = 0, column = 0)
    initiative_label = ctk.CTkLabel(initiative_frame, text = "Initiative", font = ctk.CTkFont(size = 15, weight = "bold"))
    initiative_label.grid(row = 0, column = 1, padx = 200)

    if combat_round == 1 and not isDM and len(initiativeList) > 0:
        cName_label = ctk.CTkLabel(initiative_frame, text = initiativeList[0].pName)
        cInitiative_label = ctk.CTkLabel(initiative_frame, text = initiativeList[0].initiative)
        cName_label.grid(row = 1, column = 0, pady = 10)
        cInitiative_label.grid(row = 1, column = 1, pady = 10)
    else:
        for i in range(len(initiativeList)):
            if not initiativeList[i] == "End":
                cName_label = ctk.CTkLabel(initiative_frame, text = initiativeList[i].pName)
                cInitiative_label = ctk.CTkLabel(initiative_frame, text = initiativeList[i].initiative)
                cName_label.grid(row = i + 1, column = 0, pady = 10)
                cInitiative_label.grid(row = i + 1, column = 1, pady = 10)

                if isDM:
                    remove_button = ctk.CTkButton(initiative_frame, text= "Remove", command= lambda combatant = initiativeList[i], scrollable_frame =scrollable_frame:removeCombatant(combatant, scrollable_frame))
                    remove_button.grid(row = i + 1, column = 2, padx = 20, pady = 10)


def displayAddCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, add_combatant_button, ac_entry, checkBoxFrame, hasSaveDCCHeckbox):
    display_combatant_button.pack_forget()
    checkBoxFrame.pack()
    combatant_entry_frame.pack(pady = 10)
    isPlayerCheckBox.grid(row = 0, column = 0, padx = 10)
    hasSaveDCCHeckbox.grid(row = 0, column = 1, padx = 10)
    name_entry.grid(row = 0, column = 0, padx = 10)
    initiative_entry.grid(row = 0, column = 1, padx = 10)
    dex_entry.grid(row = 0, column = 2, padx = 10)
    ac_entry.grid(row =0, column = 3, padx = 10)
    health_entry.grid(row= 0, column = 4, padx = 10)
    add_combatant_button.pack()


def addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, ac_entry, saveDC_entry, isPlayerCheckBox, hasSaveDCCheckBox, add_comabtant_button, checkBoxFrame, scrollable_frame):
    global tempCombatantsList
    global combatantsList
    global initiativeList
    global combat_start
    global playerList
    health = None
    SaveDC = None
    if not health_entry.get() =='':
        health = int(health_entry.get())
    if not saveDC_entry.get() == '':
        SaveDC = int(saveDC_entry.get())
    temp = Combatent.Combatent(int(initiative_entry.get()), int(dex_entry.get()), name_entry.get(), isPlayerCheckBox.get(), health, int(ac_entry.get()), SaveDC)

    combatantsList.append(temp)
    if isPlayerCheckBox.get():
        playerList.append(temp)

    initiative_entry.delete(0, ctk.END)
    dex_entry.delete(0, ctk.END)
    name_entry.delete(0, ctk.END)
    health_entry.delete(0, ctk.END)
    ac_entry.delete(0, ctk.END)
    saveDC_entry.delete(0, ctk.END)
    isPlayerCheckBox.deselect()
    hasSaveDCCheckBox.deselect()

    tempCombatantsList.append(temp)
    combatant_entry_frame.pack_forget()
    checkBoxFrame.pack_forget()
    add_comabtant_button.pack_forget()
    saveDC_entry.grid_forget()
    display_combatant_button.pack()
    if len(initiativeList)>0:
        currentTurn = initiativeList[0]
    else:
        currentTurn = temp
    buildInitiative()

    if combat_start:
        while not initiativeList[0] == currentTurn:
            nextInitiative(scrollable_frame)
    drawInitiative(scrollable_frame)



def buildInitiative():
    global tempCombatantsList
    global initiativeList
    try:
        initiativeList.remove("End")
    except:
        pass
    tempCombatantsList += initiativeList
    initiativeList.clear()
    while len(tempCombatantsList) > 0:
        nextCombatent = tempCombatantsList[0]
        for combatent in tempCombatantsList:
            if combatent.initiative > nextCombatent.initiative:
                nextCombatent = combatent
            elif combatent.initiative == nextCombatent.initiative and combatent.dex > nextCombatent.dex:
                nextCombatent = combatent
            elif combatent.initiative == nextCombatent.initiative and combatent.dex == nextCombatent.dex and combatent.isPlayer:
                nextCombatent = combatent
        initiativeList.append(nextCombatent)
        tempCombatantsList.remove(nextCombatent)
    initiativeList.append("End")


def server():
    # Create UDP socket
    BROADCAST_PORT = 5005
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to all network interfaces on the chosen port
    server_socket.bind(('', BROADCAST_PORT))

    print("Server listening for broadcasts...")

    while True:
        data, addr = server_socket.recvfrom(1024)  # Receive data
        print(f"Received broadcast from {addr}: {data.decode()}")

        startScreen()
        # Send response directly to sender
        response = f"Server IP: {socket.gethostbyname(socket.gethostname())}"
        server_socket.sendto(response.encode(), addr)



def dmScreen():
    #Clear whats currently on the screen
    for child in root.winfo_children():
        child.destroy()

    global isDM
    global info_list_frame

    isDM = True
    
    #Title for the main window
    title_label = ctk.CTkLabel(root, text = "Combat Tracker", font = ctk.CTkFont(size = 30, weight = "bold"))
    title_label.pack(padx = 0, pady = 20)

    #Options Buttons
    button_frame = ctk.CTkFrame(root, 1400, 100)
    button_frame.pack()
    next_button = ctk.CTkButton(button_frame, text="Next Initiative")
    clear_button = ctk.CTkButton(button_frame, text = "Clear Initiative")
    restart_button = ctk.CTkButton(button_frame, text = "Restart Initiative")
    combat_start_button = ctk.CTkButton(button_frame, text= "Start Combat")
    main_frame = ctk.CTkFrame(root, 1920, 800)
    main_frame.pack()
    scrollable_frame = ctk.CTkScrollableFrame(main_frame, 1400, 800)

    next_button.configure(command=lambda scrollable_frame = scrollable_frame:nextInitiative(scrollable_frame))
    restart_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button, scrollable_frame = scrollable_frame:restartCombat(restart_button, next_button, clear_button, combat_start_button, scrollable_frame))
    clear_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button, scrollable_frame = scrollable_frame:clearInitiative(restart_button, next_button, clear_button, combat_start_button, scrollable_frame))
    combat_start_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:startCombat(restart_button, next_button, clear_button, combat_start_button))

    side_frame = ctk.CTkFrame(main_frame, 500, 800)
    side_frame.grid(row = 0, column = 0)
    info_list_frame = ctk.CTkFrame(side_frame, 500, 400)
    info_list_frame.grid(row = 0, column = 0)
    pythagorean_frame = ctk.CTkFrame(side_frame, 500, 400)
    pythagorean_frame.grid(row = 1, column = 0)

    #Scrollale Frame for the initiative order
    scrollable_frame.grid(row = 0, column = 1, pady= 10)

    drawInitiative(scrollable_frame)

    isPlayer = ctk.BooleanVar(value=False)
    hasSaveDC = ctk.BooleanVar(value=False)
    
    display_combatant_button = ctk.CTkButton(root, text = "Add Combatant")
    display_combatant_button.pack(pady = 10)

    checkBoxFrame = ctk.CTkFrame(root, 400, 100)
    combatant_entry_frame = ctk.CTkFrame(root, 1400, 800)
    name_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Name...")
    initiative_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Initiative...")
    dex_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Dex Mod...")
    ac_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Armor Class...")
    health_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Health...")
    saveDC_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Save DC...")
    isPlayerCheckBox = ctk.CTkCheckBox(checkBoxFrame, text= "Is Player", variable=isPlayer, onvalue=True, offvalue=False)
    hasSaveDCCheckBox = ctk.CTkCheckBox(checkBoxFrame, text= "Has Save DC", variable=hasSaveDC, onvalue=True, offvalue=False)
    add_combatant_button = ctk.CTkButton(root, text="Add Combatant")

    isPlayerCheckBox.configure(command= lambda health_entry = health_entry:isPlayerCheckBoxCommand(health_entry, isPlayerCheckBox))
    hasSaveDCCheckBox.configure(command = lambda saveDC_entry = saveDC_entry:hasSaveDCCheckBoxCommand(saveDC_entry, hasSaveDCCheckBox))

    display_combatant_button.configure(command = lambda combatant_entry_frame = combatant_entry_frame, name_entry = name_entry, initiative_entry = initiative_entry, dex_entry = dex_entry, health_entry = health_entry, isPlayerCheckBox = isPlayerCheckBox, 
                                       add_combatant_button = add_combatant_button, ac_entry = ac_entry, saveDC_entry = saveDC_entry, hasSaveDCCheckBox = hasSaveDCCheckBox:displayAddCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, add_combatant_button, ac_entry, checkBoxFrame, hasSaveDCCheckBox))
    
    add_combatant_button.configure(command = lambda combatant_entry_frame = combatant_entry_frame, name_entry = name_entry, initiative_entry = initiative_entry, dex_entry = dex_entry, health_entry = health_entry,
                                    isPlayerCheckBox = isPlayerCheckBox, scrollable_frame = scrollable_frame, ac_entry = ac_entry, hassaveDCCheckBox = hasSaveDCCheckBox:addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, ac_entry, saveDC_entry, isPlayerCheckBox,hasSaveDCCheckBox,add_combatant_button, checkBoxFrame, scrollable_frame))


    combat_start_button.grid(row = 0, column = 4)


def playerConnect():
    pass

def playerStartScreen():
    #Clear whats currently on the screen
    for child in root.winfo_children():
        child.destroy()


    hasSaveDC = ctk.BooleanVar(value=False)

    hasSaveDCCheckBox = ctk.CTkCheckBox(root, text= "Has Save DC", variable=hasSaveDC, onvalue=True, offvalue=False)
    hasSaveDCCheckBox.pack(pady= (500, 0))

    entry_frame = ctk.CTkFrame(root, 600, 100)
    name_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Name...")
    initiative_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Initiative...")
    dex_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Dex Mod...")
    health_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Health...")
    ac_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Armor Class...")
    saveDC_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Save DC...")
    connect_button = ctk.CTkButton(root, 100, 40, text= "Connect", command=playerConnect)

    entry_frame.pack(pady=20)
    name_entry.grid(padx = 10, row = 0, column = 0)
    initiative_entry.grid(padx = 10, row = 0, column = 1)
    dex_entry.grid(padx = 10, row = 0, column = 2)
    health_entry.grid(padx = 10, row = 0, column = 3)
    ac_entry.grid(padx = 10, row = 0, column = 4)
    connect_button.pack()

    hasSaveDCCheckBox.configure(command = lambda saveDC_entry = saveDC_entry:hasSaveDCCheckBoxCommand(saveDC_entry, hasSaveDCCheckBox))



def startScreen():
    for child in root.winfo_children():
        child.destroy()

    
    button_frame = ctk.CTkFrame(root)
    dm_button = ctk.CTkButton(button_frame, 100, 40, text= "DM", command=dmScreen)
    player_button = ctk.CTkButton(button_frame, 100, 40, text= "Player", command=playerStartScreen)
    button_frame.pack(pady = 500)
    dm_button.grid(row = 0, column = 0, padx = 20)
    player_button.grid(row = 0, column = 1, padx = 20)


def main():
    thread = threading.Thread(target= server)
    thread.start()
    startScreen()
    root.mainloop()

main()