import customtkinter as ctk
import combatant
import threading


#socket imports
import socket
import select

#Socket Globals
connections = {}
sockets = []
isConnected = False
player = None


def establishUDPLisener():
    global sockets
    # Create UDP socket
    BROADCAST_PORT = 5005
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to all network interfaces on the chosen port
    server_socket.bind(('', BROADCAST_PORT))

    print("Server listening for broadcasts...")

    sockets.append(server_socket)
    while True:
        try:
            data, addr = server_socket.recvfrom(2048)  # Receive data
            data = data.decode()
            info = data.split(":")
            print(f"Received broadcast from {addr}: {info[0]}")

            # Send response directly to sender
            response = f"Server IP: {socket.gethostbyname(socket.gethostname())}"
            server_socket.sendto(response.encode(), addr)

            saveDC = None
            if not info[4] == "None":
                saveDC = int(info[4])
            
            createCombatant(info[0], int(info[1]), int(info[2]), True, None, int(info[3]), saveDC, True)
            temp = None
            print(info[0])
            for combatant in playerList:
                if combatant.pName == info[0]:
                    temp = combatant
            connections[info[0]] = (addr[0], temp)
        except:
            break

def establishUDPSender(message):
    BROADCAST_PORT = 5005

    # Step 1: Get the local hostname.
    local_hostname = socket.gethostname()

    # Step 2: Get a list of IP addresses associated with the hostname.
    ip_addresses = socket.gethostbyname_ex(local_hostname)[2]

    # Step 3: Filter out loopback addresses (IPs starting with "127.").
    filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]

    for ip in filtered_ips:
        ipSplit = ip.split(".")
        ipSplit[3] = "255"
        BROADCAST_IP = ".".join(ipSplit)  # Broadcast address for local network

        # Create UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        client_socket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))
        print("Broadcast message sent.")

        # Listen for response
        client_socket.settimeout(3)  # Wait for a response for up to 3 seconds
        try:
            response, server_addr = client_socket.recvfrom(2048)
            print(f"Received response from {server_addr}: {response.decode()}")
            connections["DM"] = (server_addr[0], None)
            global isConnected
            isConnected = True
            client_socket.close()
        except socket.timeout:
            print("No response received.")

def establishTCPListener():
    global sockets
    SERVER_HOST = '0.0.0.0'  # Listen on all available interfaces
    SERVER_PORT = 5006

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(10)

    sockets.append(server_socket)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
    clients = [server_socket]

    while True:
        try:
            readable, writable, errored = select.select(clients, [], [], 0.1)
            for s in readable:
                if s is server_socket:
                    client_socket, client_address = server_socket.accept()
                    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
                    clients.append(client_socket)
                else:
                    data = client_socket.recv(2048).decode()
                    if not data:
                        clients.remove(s)
                        s.close
                        continue
                    print(f"Received: {data}")
                    parseMessage(data)

        except socket.error:
            break

def establishTCPSender(addr, message):
    SERVER_HOST = addr  # Replace with the actual IP address of the server

    SERVER_PORT = 5006

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")

        client_socket.send(message.encode())

    except socket.error as e:
        print(f"Connection error: {e}")

    finally:
        client_socket.close()


def closeAll():
    global sockets
    for i in range(len(sockets)):
        socketObj = sockets.pop(0)
        socketObj.close()


def parseMessage(message):
    messageSplit = message.split("/")
    cmd = messageSplit[0]
    match cmd:
        case "addCombatant":
            info = messageSplit[1].split(":")
            createCombatant(info[0], info[1], info[2], True, None, info[3], info[4], True)

        case "askInitiative":
            askInitiative()

        case "updateInitiative":
            info = messageSplit[1].split(":")
            updateInitiative(connections[info[0]][1], info[1])

        case "startCombat":
            startCombat()

        case _:
            pass
    


























#Lists for keeping track of who is in the combat and the order of initiative
tempCombatantsList = []
combatantsList = []
initiativeList = []
playerList = []
info_list_frame = None
initiative_frame = None
combat_round = 1
combat_start = False
isDM = False

#Main Window
root = ctk.CTk()
root.geometry("1920x1080")
root.title("DnD Companion")


def nextInitiative():
    global initiativeList
    global combat_round
    if initiativeList[1] == "End":
        initiativeList.append(initiativeList.pop(0))
        combat_round += 1
    initiativeList.append(initiativeList.pop(0))
    drawInitiative()


def restartCombat(restart_button, next_button, clear_button, combat_start_button):
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
        if not player.connected:
            dialog = ctk.CTkInputDialog(text= "New initiative for " + player.pName)
            newInitiative = int(dialog.get_input())
            player.setInitiative(newInitiative)
        else:
            playerList.remove(player)
            establishTCPSender(connections[player.pName][0], "askInitiative")

    tempCombatantsList = playerList
    combatantsList = playerList
    initiativeList.clear()
    buildInitiative()
    drawInitiative()

def updateInitiative(player, initiative):
    player.setInitiative(initiative)
    buildInitiative()
    drawInitiative()

def clearInitiative(restart_button, next_button, clear_button, combat_start_button):
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
    drawInitiative()
    
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

def removeCombatant(combatant):
    global initiativeList
    global playerList
    global combatantsList

    initiativeList.remove(combatant)
    combatantsList.remove(combatant)
    if combatant.isPlayer:
        playerList.remove(combatant)
    drawInitiative()
    drawInfoFrame()

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
def drawInitiative():
    global initiative_frame
    global combat_round
    global isDM
    for child in initiative_frame.winfo_children():
        child.destroy()
        
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
                    remove_button = ctk.CTkButton(initiative_frame, text= "Remove", command= lambda combatant = initiativeList[i]:removeCombatant(combatant))
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


def addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, ac_entry, saveDC_entry, isPlayerCheckBox, hasSaveDCCheckBox, add_comabtant_button, checkBoxFrame):
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
    name = name_entry.get()
    initiative = int(initiative_entry.get())
    dex = int(dex_entry.get())
    isPlayer = isPlayerCheckBox.get()
    ac = int(ac_entry.get())
    
    
    initiative_entry.delete(0, ctk.END)
    dex_entry.delete(0, ctk.END)
    name_entry.delete(0, ctk.END)
    health_entry.delete(0, ctk.END)
    ac_entry.delete(0, ctk.END)
    saveDC_entry.delete(0, ctk.END)
    isPlayerCheckBox.deselect()
    hasSaveDCCheckBox.deselect()

    combatant_entry_frame.pack_forget()
    checkBoxFrame.pack_forget()
    add_comabtant_button.pack_forget()
    saveDC_entry.grid_forget()
    display_combatant_button.pack()

    createCombatant(name, initiative, dex, isPlayer, health, ac, SaveDC, False)


def createCombatant(name, initiative, dex, isPlayer, health, ac, saveDC, connected):
    temp = combatant.combatant(initiative, dex, name, isPlayer, health, ac, saveDC, connected)

    combatantsList.append(temp)
    if isPlayer:
        playerList.append(temp)


    if len(initiativeList)>0:
        currentTurn = initiativeList[0]
    else:
        currentTurn = temp
    tempCombatantsList.append(temp)

    buildInitiative()

    if combat_start:
        while not initiativeList[0] == currentTurn:
            nextInitiative()
    drawInitiative()
    if not combat_start:
        drawInfoFrame()

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
        nextcombatant = tempCombatantsList[0]
        for combatant in tempCombatantsList:
            if combatant.initiative > nextcombatant.initiative:
                nextcombatant = combatant
            elif combatant.initiative == nextcombatant.initiative and combatant.dex > nextcombatant.dex:
                nextcombatant = combatant
            elif combatant.initiative == nextcombatant.initiative and combatant.dex == nextcombatant.dex and combatant.isPlayer:
                nextcombatant = combatant
        initiativeList.append(nextcombatant)
        tempCombatantsList.remove(nextcombatant)
    initiativeList.append("End")



def dmScreen():
    clientListen = threading.Thread(target=establishUDPLisener)
    clientListen.start()
    #Clear whats currently on the screen
    for child in root.winfo_children():
        child.destroy()

    global isDM
    global info_list_frame
    global initiative_frame

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
    initiative_frame = ctk.CTkScrollableFrame(main_frame, 1400, 800)

    next_button.configure(command=nextInitiative)
    restart_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:restartCombat(restart_button, next_button, clear_button, combat_start_button))
    clear_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:clearInitiative(restart_button, next_button, clear_button, combat_start_button))
    combat_start_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:startCombat(restart_button, next_button, clear_button, combat_start_button))

    side_frame = ctk.CTkFrame(main_frame, 500, 800)
    side_frame.grid(row = 0, column = 0)
    info_list_frame = ctk.CTkFrame(side_frame, 500, 400)
    info_list_frame.grid(row = 0, column = 0)
    pythagorean_frame = ctk.CTkFrame(side_frame, 500, 400)
    pythagorean_frame.grid(row = 1, column = 0)

    #Scrollale Frame for the initiative order
    initiative_frame.grid(row = 0, column = 1, pady= 10)

    drawInitiative()

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
                                    isPlayerCheckBox = isPlayerCheckBox, ac_entry = ac_entry, hassaveDCCheckBox = hasSaveDCCheckBox:addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, ac_entry, saveDC_entry, isPlayerCheckBox,hasSaveDCCheckBox,add_combatant_button, checkBoxFrame))


    combat_start_button.grid(row = 0, column = 4)


def playerScreen():
    pass

def playerConnect(name_entry,initiative_entry, dex_entry, ac_entry, saveDC_entry):
    global player
    name = name_entry.get()
    initiative = initiative_entry.get()
    dex = dex_entry.get()
    ac = ac_entry.get()
    saveDC = None
    if not saveDC_entry.get() == "":
        saveDC = saveDC_entry.get()

    player = combatant.combatant(int(initiative), int(dex), name, True, None, int(ac), saveDC, True)
    message = f"{name}:{initiative}:{dex}:{ac}:{saveDC}"
    establishUDPSender(message)


def playerStartScreen():
    global isDM 
    isDM = False
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
    ac_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Armor Class...")
    saveDC_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Save DC...")
    connect_button = ctk.CTkButton(root, 100, 40, text= "Connect", command= lambda name_entry = name_entry:playerConnect(name_entry, initiative_entry, dex_entry, ac_entry, saveDC_entry))

    entry_frame.pack(pady=20)
    name_entry.grid(padx = 10, row = 0, column = 0)
    initiative_entry.grid(padx = 10, row = 0, column = 1)
    dex_entry.grid(padx = 10, row = 0, column = 2)
    ac_entry.grid(padx = 10, row = 0, column = 3)
    connect_button.pack()

    hasSaveDCCheckBox.configure(command = lambda saveDC_entry = saveDC_entry:hasSaveDCCheckBoxCommand(saveDC_entry, hasSaveDCCheckBox))


def askInitiative():
    global player
    dialog = ctk.CTkInputDialog(text= "What did you get for Initiative")
    newInitiative = int(dialog.get_input())
    message = f"addCombatant/{player.pName}:{newInitiative}:{player.dex}:{player.ac}:{player.saveDC}"
    establishTCPSender(connections["DM"][0], message)


def startScreen():
    for child in root.winfo_children():
        child.destroy()

    
    button_frame = ctk.CTkFrame(root)
    dm_button = ctk.CTkButton(button_frame, 100, 40, text= "DM", command=dmScreen)
    player_button = ctk.CTkButton(button_frame, 100, 40, text= "Player", command=playerStartScreen)
    button_frame.pack(pady = 500)
    dm_button.grid(row = 0, column = 0, padx = 20)
    player_button.grid(row = 0, column = 1, padx = 20)


tcpListener = threading.Thread(target=establishTCPListener)
tcpListener.start()

startScreen()
root.mainloop()

closeAll()