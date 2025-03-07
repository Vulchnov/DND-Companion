import customtkinter as ctk
import Combatent

#Lists for keeping track of who is in the combat and the order of initiative
combatents = []
initiativeList = []
combat_start = False

#Main Window
root = ctk.CTk()
root.geometry("1920x1080")
root.title("Combat Tracker")

#Title for the main window
title_label = ctk.CTkLabel(root, text = "Combat Tracker", font = ctk.CTkFont(size = 30, weight = "bold"))
title_label.pack(padx = 0, pady = 20)


def nextInitiative():
    global initiativeList
    initiativeList.append(initiativeList.pop(0))
    drawInitiative()


def restartCombat():
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
    drawInitiative()


def clearInitiative():
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
    drawInitiative()
    
def startCombat():
    global combat_start
    combat_start = True
    combat_start_button.grid_forget()
    next_button.grid(row = 0, column = 0, padx = 10)
    clear_button.grid(row = 0, column = 1, padx = 10)
    restart_button.grid(row = 0, column = 2, padx = 10)


#Options Buttons
button_frame = ctk.CTkFrame(root, 1400, 100)
button_frame.pack()
next_button = ctk.CTkButton(button_frame, text="Next Initiative", command= nextInitiative)
clear_button = ctk.CTkButton(button_frame, text = "Clear Initiative", command= clearInitiative)
restart_button = ctk.CTkButton(button_frame, text = "Restart Initiative", command= restartCombat)


#Scrollale Frame for the initiative order
scrollable_frame = ctk.CTkScrollableFrame(root, 1400, 800)
scrollable_frame.pack(pady= 10)


isPlayer = ctk.BooleanVar(value=False)


def removeCombatant(combatant):
    global initiativeList
    initiativeList.remove(combatant)
    drawInitiative()

def healCombatant(combatant, entry):
    combatant.health += int(entry.get())
    drawInitiative()

def harmCombatant(combatant, entry):
    combatant.health -= int(entry.get())
    drawInitiative()


#Draw the initiative order
def drawInitiative():
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
        health_adjust_frame.grid(row = i+1, column = 3, pady = 10)
        cHealth_entry = ctk.CTkEntry(health_adjust_frame, 100, 40)
        cHealth_heal_button = ctk.CTkButton(health_adjust_frame, text = "Heal", command = lambda combatant = initiativeList[i], entry = cHealth_entry: healCombatant(combatant, entry))
        cHealth_harm_button = ctk.CTkButton(health_adjust_frame, text = "Harm", command = lambda combatant = initiativeList[i], entry = cHealth_entry: harmCombatant(combatant, entry))
        cHealth_heal_button.pack()
        cHealth_entry.pack()
        cHealth_harm_button.pack()

        remove_button = ctk.CTkButton(initiative_frame, text= "Remove", command= lambda combatant = initiativeList[i]:removeCombatant(combatant))
        remove_button.grid(row = i + 1, column = 4, padx = 40)


drawInitiative()

def displayAddCombatant():
    display_combatant_button.pack_forget()
    combatant_entry_frame.pack()
    name_entry.grid(row = 0, column = 0, padx = 10)
    initiative_entry.grid(row = 0, column = 1, padx = 10)
    dex_entry.grid(row = 0, column = 2, padx = 10)
    health_entry.grid(row=0, column = 3, padx = 10)
    isPlayerCheckBox.grid(row = 0, column = 4, padx = 10)
    add_combatant_button.grid(row = 0, column = 5)


def addCombatant():
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
    drawInitiative()



display_combatant_button = ctk.CTkButton(root, text = "Add Combatant", command = displayAddCombatant)
display_combatant_button.pack(pady = 10)

combatant_entry_frame = ctk.CTkFrame(root, 1400, 800)
name_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Name...")
initiative_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Initiative...")
dex_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Dex Mod...")
health_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Health...")
isPlayerCheckBox = ctk.CTkCheckBox(combatant_entry_frame, text= "Is Player", variable=isPlayer, onvalue=True, offvalue=False)
add_combatant_button = ctk.CTkButton(combatant_entry_frame, text="Add Combatant", command=addCombatant)


combat_start_button = ctk.CTkButton(button_frame, text= "Start Combat", command=startCombat)
combat_start_button.grid(row = 0, column = 4)


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

root.mainloop()

