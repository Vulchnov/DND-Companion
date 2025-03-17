import customtkinter as ctk
import Combatent

#Lists for keeping track of who is in the combat and the order of initiative
combatents = []
initiativeList = []
combat_start = False

#Main Window
root = ctk.CTk()
root.geometry("1920x1080")
root.title("DnD Companion")

def nextInitiative(scrollable_frame):
    global initiativeList
    initiativeList.append(initiativeList.pop(0))
    drawInitiative(scrollable_frame)


def restartCombat(restart_button, next_button, clear_button, combat_start_button, scrollable_frame):
    playersList = []
    global initiativeList
    global combatents
    global combat_start 
    combat_start = False
    combat_start_button.grid(row = 0, column = 4)
    next_button.grid_forget()
    clear_button.grid_forget()
    restart_button.grid_forget()
    for combatant in initiativeList:
        if combatant.isPlayer:
            playersList.append(combatant)
    for player in playersList:
        dialog = ctk.CTkInputDialog(text= "New initiative for " + player.pName)
        newInitiative = int(dialog.get_input())
        player.setInitiative(newInitiative)

    combatents = playersList
    initiativeList.clear()
    buildInitiative()
    drawInitiative(scrollable_frame)


def clearInitiative(restart_button, next_button, clear_button, combat_start_button, scrollable_frame):
    global initiativeList
    global combatents
    global combat_start 
    combat_start = False
    combat_start_button.grid(row = 0, column = 4)
    next_button.grid_forget()
    clear_button.grid_forget()
    restart_button.grid_forget()
    initiativeList.clear()
    combatents.clear()
    drawInitiative(scrollable_frame)
    
def startCombat(restart_button, next_button, clear_button, combat_start_button):
    global combat_start
    combat_start = True
    combat_start_button.grid_forget()
    next_button.grid(row = 0, column = 0, padx = 10)
    clear_button.grid(row = 0, column = 1, padx = 10)
    restart_button.grid(row = 0, column = 2, padx = 10)



def removeCombatant(combatant, scrollable_frame):
    global initiativeList
    initiativeList.remove(combatant)
    drawInitiative(scrollable_frame)

def healCombatant(combatant, entry, scrollable_frame):
    combatant.health += int(entry.get())
    drawInitiative(scrollable_frame)

def harmCombatant(combatant, entry, scrollable_frame):
    combatant.health -= int(entry.get())
    drawInitiative(scrollable_frame)


#Draw the initiative order
def drawInitiative(scrollable_frame):
    for child in scrollable_frame.winfo_children():
        child.destroy()
    initiative_frame = ctk.CTkFrame(scrollable_frame, 1400, 800)
    initiative_frame.pack()

    
    #Inside Frame
    name_label = ctk.CTkLabel(initiative_frame, text = "Name", font = ctk.CTkFont(size = 15, weight = "bold"))
    name_label.grid(row = 0, column = 0)
    initiative_label = ctk.CTkLabel(initiative_frame, text = "Initiative", font = ctk.CTkFont(size = 15, weight = "bold"))
    initiative_label.grid(row = 0, column = 1, padx = 200)
    health_label = ctk.CTkLabel(initiative_frame, text = "Health", font = ctk.CTkFont(size = 15, weight = "bold"))
    health_label.grid(row = 0, column = 2)
    for i in range(len(initiativeList)):
        cName_label = ctk.CTkLabel(initiative_frame, text = initiativeList[i].pName)
        cInitiative_label = ctk.CTkLabel(initiative_frame, text = initiativeList[i].initiative)
        cHealth_label = ctk.CTkLabel(initiative_frame, text = initiativeList[i].health)
        cName_label.grid(row = i + 1, column = 0)
        cInitiative_label.grid(row = i + 1, column = 1)
        cHealth_label.grid(row = i + 1, column = 2)

        health_adjust_frame = ctk.CTkFrame(initiative_frame)
        health_adjust_frame.grid(row = i+1, column = 3, padx = 10, pady = 10)
        cHealth_entry = ctk.CTkEntry(health_adjust_frame, 100, 40)
        cHealth_heal_button = ctk.CTkButton(health_adjust_frame, text = "Heal", command = lambda combatant = initiativeList[i], entry = cHealth_entry, scrollable_frame = scrollable_frame: healCombatant(combatant, entry, scrollable_frame))
        cHealth_harm_button = ctk.CTkButton(health_adjust_frame, text = "Harm", command = lambda combatant = initiativeList[i], entry = cHealth_entry, scrollable_frame = scrollable_frame: harmCombatant(combatant, entry, scrollable_frame))
        cHealth_heal_button.pack()
        cHealth_entry.pack()
        cHealth_harm_button.pack()

        remove_button = ctk.CTkButton(initiative_frame, text= "Remove", command= lambda combatant = initiativeList[i], scrollable_frame =scrollable_frame:removeCombatant(combatant, scrollable_frame))
        remove_button.grid(row = i + 1, column = 4, padx = 40)


def displayAddCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, add_combatant_button):
    display_combatant_button.pack_forget()
    combatant_entry_frame.pack()
    name_entry.grid(row = 0, column = 0, padx = 10)
    initiative_entry.grid(row = 0, column = 1, padx = 10)
    dex_entry.grid(row = 0, column = 2, padx = 10)
    health_entry.grid(row=0, column = 3, padx = 10)
    isPlayerCheckBox.grid(row = 0, column = 4, padx = 10)
    add_combatant_button.grid(row = 0, column = 5)


def addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, scrollable_frame):
    global combatents
    global initiativeList
    global combat_start
    temp = Combatent.Combatent(int(initiative_entry.get()), int(dex_entry.get()), name_entry.get(), isPlayerCheckBox.get(), int(health_entry.get()))
    initiative_entry.delete(0, ctk.END)
    dex_entry.delete(0, ctk.END)
    name_entry.delete(0, ctk.END)
    health_entry.delete(0, ctk.END)
    isPlayerCheckBox.deselect()

    combatents.append(temp)
    combatant_entry_frame.pack_forget()
    display_combatant_button.pack()
    if len(initiativeList)>0:
        currentTurn = initiativeList[0]
    else:
        currentTurn = temp
    buildInitiative()

    if combat_start:
        while not initiativeList[0] == currentTurn:
            nextInitiative()
    drawInitiative(scrollable_frame)



def buildInitiative():
    global combatents
    global initiativeList
    combatents += initiativeList
    initiativeList.clear()
    while len(combatents) > 0:
        nextCombatent = combatents[0]
        for combatent in combatents:
            if combatent.initiative > nextCombatent.initiative:
                nextCombatent = combatent
            elif combatent.initiative == nextCombatent.initiative and combatent.dex > nextCombatent.dex:
                nextCombatent = combatent
            elif combatent.initiative == nextCombatent.initiative and combatent.dex == nextCombatent.dex and combatent.isPlayer:
                nextCombatent = combatent
        initiativeList.append(nextCombatent)
        combatents.remove(nextCombatent)

def dmScreen():
    #Clear whats currently on the screen
    for child in root.winfo_children():
        child.destroy()

    
    #Title for the main window
    title_label = ctk.CTkLabel(root, text = "Combat Tracker", font = ctk.CTkFont(size = 30, weight = "bold"))
    title_label.pack(padx = 0, pady = 20)

    #Options Buttons
    button_frame = ctk.CTkFrame(root, 1400, 100)
    button_frame.pack()
    next_button = ctk.CTkButton(button_frame, text="Next Initiative")
    clear_button = ctk.CTkButton(button_frame, text = "Clear Initiative")
    restart_button = ctk.CTkButton(button_frame, text = "Restart Initiative")
    combat_start_button = ctk.CTkButton(button_frame, text= "Start Combat", command=startCombat)
    scrollable_frame = ctk.CTkScrollableFrame(root, 1400, 800)

    next_button.configure(command=lambda scrollable_frame = scrollable_frame:nextInitiative(scrollable_frame))
    restart_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button, scrollable_frame = scrollable_frame:restartCombat(restart_button, next_button, clear_button, combat_start_button, scrollable_frame))
    clear_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button, scrollable_frame = scrollable_frame:clearInitiative(restart_button, next_button, clear_button, combat_start_button, scrollable_frame))
    combat_start_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:startCombat(restart_button, next_button, clear_button, combat_start_button))



    #Scrollale Frame for the initiative order
    scrollable_frame.pack(pady= 10)

    drawInitiative(scrollable_frame)

    isPlayer = ctk.BooleanVar(value=False)
    
    display_combatant_button = ctk.CTkButton(root, text = "Add Combatant")
    display_combatant_button.pack(pady = 10)

    combatant_entry_frame = ctk.CTkFrame(root, 1400, 800)
    name_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Name...")
    initiative_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Initiative...")
    dex_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Dex Mod...")
    health_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Health...")
    isPlayerCheckBox = ctk.CTkCheckBox(combatant_entry_frame, text= "Is Player", variable=isPlayer, onvalue=True, offvalue=False)
    add_combatant_button = ctk.CTkButton(combatant_entry_frame, text="Add Combatant")

    display_combatant_button.configure(command = lambda combatant_entry_frame = combatant_entry_frame, name_entry = name_entry, initiative_entry = initiative_entry, dex_entry = dex_entry, health_entry = health_entry, isPlayerCheckBox = isPlayerCheckBox, 
                                       add_combatant_button = add_combatant_button:displayAddCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, add_combatant_button))
    
    add_combatant_button.configure(command = lambda combatant_entry_frame = combatant_entry_frame, name_entry = name_entry, initiative_entry = initiative_entry, dex_entry = dex_entry, health_entry = health_entry,
                                    isPlayerCheckBox = isPlayerCheckBox, scrollable_frame = scrollable_frame:addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, scrollable_frame))


    combat_start_button.grid(row = 0, column = 4)


def playerScreen():
    pass

def startScreen():
    for child in root.winfo_children():
        child.destroy()

    
    button_frame = ctk.CTkFrame(root)
    dm_button = ctk.CTkButton(button_frame, 100, 40, text= "DM", command=dmScreen)
    player_button = ctk.CTkButton(button_frame, 100, 40, text= "Player", command=playerScreen)
    button_frame.pack(pady = 500)
    dm_button.grid(row = 0, column = 0, padx = 20)
    player_button.grid(row = 0, column = 1, padx = 20)


startScreen()

root.mainloop()

