import customtkinter as ctk
import combatant
import threading
from math import sqrt


#socket imports
import socket
import select
from queue import Queue
from enum import Enum, auto

class TicketPurpose(Enum):
    PLAYER_CONNECT = auto()
    ADD_COMBATANT = auto()
    ASK_INITIATIVE = auto()
    START_COMBAT = auto()
    UPDATE_INITIATIVE = auto()
    NEXT_INITIATIVE = auto()
    SWAP_INITIATIVE = auto()
    REMOVE_COMBATANT = auto()
    CLEAR_INITIATIVE = auto()

class Ticket():
    def __init__(self, ticket_type: TicketPurpose, ticket_value: str):
        self.ticket_type = ticket_type
        self.ticket_value = ticket_value


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()    
        #Lists for keeping track of who is in the combat and the order of initiative
        self.combatantsList = []
        self.initiativeList = []
        self.playerList = []
        self.info_list_frame = None
        self.initiative_frame = None
        self.pythagorean_frame = None
        self.round_label = None
        self.combat_round = 0
        self.combat_start = False
        self.isDM = False
        self.initiativeSwapButton = None


        
        #Socket Information
        self.connections = {}
        self.sockets = []
        self.isConnected = False
        self.playerSelf = None
        self.message_queue = Queue()

        self.bind("<<CheckQueue>>", self.checkQueue)


        #Main Window
        self.geometry("1920x1080")
        self.title("DnD Companion")




    def establishUDPLisener(self):
        # Create UDP socket
        BROADCAST_PORT = 5005
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Bind to all network interfaces on the chosen port
        server_socket.bind(('', BROADCAST_PORT))

        print("Server listening for broadcasts...")

        self.sockets.append(server_socket)
        while True:
            try:
                data, addr = server_socket.recvfrom(2048)  # Receive data
                data = data.decode()
                info = data.split(":")
                print(f"Received broadcast from {addr}: {info[0]}")

                # Send response directly to sender
                response = f"Server IP: {socket.gethostbyname(socket.gethostname())}"
                server_socket.sendto(response.encode(), addr)

                ticket = Ticket(TicketPurpose.PLAYER_CONNECT, ticket_value=f"{data}:{addr[0]}")
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            except:
                break

    def establishUDPSender(self, message):
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
                self.connections["DM"] = (server_addr[0], None)
                self.isConnected = True
                client_socket.close()
                self.playerScreen()
            except socket.timeout:
                print("No response received.")

    def establishTCPListener(self):
        global sockets
        SERVER_HOST = '0.0.0.0'  # Listen on all available interfaces
        SERVER_PORT = 5006

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(False)
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen(10)

        self.sockets.append(server_socket)
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
                        self.parseMessage(data)

            except socket.error:
                break

    def establishTCPSender(self, addr, message):
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


    def closeAll(self):
        global sockets
        for i in range(len(sockets)):
            socketObj = sockets.pop(0)
            socketObj.close()


    def parseMessage(self, message):
        messageSplit = message.split("/")
        cmd = messageSplit[0]
        match cmd:
            case "addCombatant":
                ticket = Ticket(TicketPurpose.ADD_COMBATANT, messageSplit[1])
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "askInitiative":
                ticket = Ticket(TicketPurpose.ASK_INITIATIVE, "")
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "updateInitiative":
                ticket = Ticket(TicketPurpose.UPDATE_INITIATIVE, messageSplit[1])
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "startCombat":
                ticket = Ticket(TicketPurpose.START_COMBAT, "")
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "nextInitiative":
                ticket = Ticket(TicketPurpose.NEXT_INITIATIVE, "")
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "swapInitiative":
                ticket = Ticket(TicketPurpose.SWAP_INITIATIVE, messageSplit[1])
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "removeCombatant":
                ticket = Ticket(TicketPurpose.REMOVE_COMBATANT, messageSplit[1])
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case "clearInitiative":
                ticket = Ticket(TicketPurpose.CLEAR_INITIATIVE, "")
                self.message_queue.put(ticket)
                self.event_generate("<<CheckQueue>>")

            case _:
                pass
















    def checkQueue(self, event):
        msg: Ticket
        msg = self.message_queue.get()
        match msg.ticket_type:
            case TicketPurpose.PLAYER_CONNECT:
                info = msg.ticket_value.split(":")
                initiative = int(info[1])
                dex = int(info[2])
                ac = int(info[3])
                saveDC = None
                if not info[4] =="None":
                    saveDC= int(info[4])
                self.createCombatant(info[0], initiative, dex, True, None, ac, saveDC, True)

                for combatant in self.playerList:
                    if combatant.pName == info[0]:
                        temp = combatant
                self.connections[info[0]] = (info[5], temp)


            case TicketPurpose.ADD_COMBATANT:
                info = msg.ticket_value.split(":")
                saveDC = None
                if not info[4] == "None":
                    saveDC = int(info[4])
                isPlayer = False
                if info[5] == "True":
                    isPlayer = True
                self.createCombatant(info[0], int(info[1]), int(info[2]), isPlayer, None, info[3], saveDC, False)

            case TicketPurpose.ASK_INITIATIVE:
                self.askInitiative()
                self.restartCombat(None, None, None, None)

            case TicketPurpose.UPDATE_INITIATIVE:
                info = msg.ticket_value.split(":")
                playerRef = None
                for player in self.playerList:
                    if player.pName == info[0]:
                        playerRef = player
                self.updateInitiative(playerRef, int(info[1]))


            case TicketPurpose.START_COMBAT:
                self.startCombat(None, None, None, None)


            case TicketPurpose.NEXT_INITIATIVE:
                self.nextInitiative()

            case TicketPurpose.SWAP_INITIATIVE:
                info = msg.ticket_value.split(":")
                player1 = None
                player2 = None
                for player in self.playerList:
                    if player.pName == info[0]:
                        player1 = player
                    elif player.pName == info[1]:
                        player2 = player
                self.swapInitiative(player1, player2)

            case TicketPurpose.REMOVE_COMBATANT:
                for combatant in self.combatantsList:
                    if combatant.pName == msg.ticket_value:
                        self.removeCombatant(combatant)
            case TicketPurpose.CLEAR_INITIATIVE:
                self.clearInitiative(None, None, None, None)

    
            case _:
                pass
        

    def nextInitiative(self):
        if self.isDM:
            for player in self.connections:
                self.establishTCPSender(self.connections[player][0], "nextInitiative")
        if self.initiativeList[1] == "End":
            self.initiativeList.append(self.initiativeList.pop(0))
            self.combat_round += 1
            self.round_label.configure(text = f"Round: {self.combat_round}")
        self.initiativeList.append(self.initiativeList.pop(0))
        self.drawInitiative()

    def restartCombat(self, restart_button, next_button, clear_button, combat_start_button):
        self.combat_start = False
        self.combat_round = 0
        self.round_label.configure(text = f"Round: {self.combat_round}")
        if self.isDM:
            self.initiativeSwapButton.pack()
            combat_start_button.grid(row = 0, column = 4)
            next_button.grid_forget()
            clear_button.grid_forget()
            restart_button.grid_forget()
            for player in self.playerList:
                if not player.connected:
                    dialog = ctk.CTkInputDialog(text= "New initiative for " + player.pName)
                    newInitiative = int(dialog.get_input())
                    player.setInitiative(newInitiative)
                    for playerCon in self.connections:
                        self.establishTCPSender(self.connections[playerCon][0], f"updateInitiative/{player.pName}:{newInitiative}")
            for player in self.connections:
                self.establishTCPSender(self.connections[player][0], "askInitiative")

        self.combatantsList = self.playerList.copy()
        self.initiativeList.clear()
        self.buildInitiative()
        self.drawInitiative()

    def updateInitiative(self, player, initiative):
        if self.isDM:
            for player in self.connections:
                self.establishTCPSender(self.connections[player][0], f"updateInitiative/{player}:{initiative}")
        player.setInitiative(initiative)
        self.buildInitiative()
        self.drawInitiative()

    def clearInitiative(self, restart_button, next_button, clear_button, combat_start_button):
        if not self.isDM:
            self.initiativeList.clear()
            self.playerList.clear()
            self.combatantsList.clear()
            self.connections.clear()
            self.playerSelf = None
            self.playerStartScreen()
        else:
            for player in self.connections:
                self.establishTCPSender(self.connections[player][0], "clearInitiative")
            self.combat_start = False
            self.combat_round = 0
            self.round_label.configure(text = f"Round: {self.combat_round}")
            self.initiativeSwapButton.pack()
            combat_start_button.grid(row = 0, column = 4)
            next_button.grid_forget()
            clear_button.grid_forget()
            restart_button.grid_forget()
            self.initiativeList.clear()
            self.playerList.clear()
            self.combatantsList.clear()
            self.connections.clear()
            self.drawInitiative()
        
    def startCombat(self, restart_button, next_button, clear_button, combat_start_button):
        if self.isDM:
            for player in self.connections:
                self.establishTCPSender(self.connections[player][0], "startCombat")
            self.initiativeSwapButton.pack_forget()
            combat_start_button.grid_forget()
            next_button.grid(row = 0, column = 0, padx = 10)
            clear_button.grid(row = 0, column = 1, padx = 10)
            restart_button.grid(row = 0, column = 2, padx = 10)
        self.combat_start = True
        self.combat_round = 1
        self.round_label.configure(text = f"Round: {self.combat_round}")
        self.drawInitiative()
        

    def isPlayerCheckBoxCommand(self, health_entry, isPlayerCheckbox):
        if(isPlayerCheckbox.get()):
            health_entry.grid_forget()
        else:
            health_entry.grid(row= 0, column = 4, padx = 10)

    def hasSaveDCCheckBoxCommand(self, saveDC_entry, hasSaveDCCheckbox):
        if(hasSaveDCCheckbox.get()):
            saveDC_entry.grid(row= 0, column = 5, padx = 10)
        else:
            saveDC_entry.grid_forget()

    def removeCombatant(self, combatant):
        self.initiativeList.remove(combatant)
        self.combatantsList.remove(combatant)
        if combatant.isPlayer:
            self.playerList.remove(combatant)
        self.drawInitiative()

    def promptInitiativeSwap(self):
        promptWindow = ctk.CTkToplevel(self)
        promptWindow.title("Initiative Swap")
        promptWindow.geometry("400x200")
        promptWindow.resizable(False, False)
        entry_frame = ctk.CTkFrame(promptWindow)
        entry_frame.pack()
        entry1 = ctk.CTkEntry(entry_frame, placeholder_text="Player 1")
        entry2 = ctk.CTkEntry(entry_frame, placeholder_text="Player 2")
        entry1.grid(row = 0, column = 0, padx = (50, 25), pady = 50)
        entry2.grid(row = 0, column = 1, padx = (25, 50), pady = 50)
        enter_button = ctk.CTkButton(promptWindow, text="Enter", command= lambda entry1 = entry1, entry2 = entry2, promptWindow = promptWindow: self.dmSwapInitiative(entry1, entry2, promptWindow))
        enter_button.pack()

    
    def dmSwapInitiative(self, entry1, entry2, promptWindow):
        p1Name = entry1.get()
        p2Name = entry2.get()
        for player in self.connections:
            self.establishTCPSender(self.connections[player][0], f"swapInitiative/{p1Name}:{p2Name}")
        player1 = None
        player2 = None
        for player in self.playerList:
            if player.pName == p1Name:
                player1 = player
            elif player.pName == p2Name:
                player2 = player
        self.swapInitiative(player1, player2)
        promptWindow.destroy()

    def swapInitiative(self, combatant1, combatant2):
        combatant1.initiative, combatant2.initiative = combatant2.initiative, combatant1.initiative
        self.buildInitiative()
        self.drawInitiative()
    
    def healCombatant(self, combatant, entry):
        combatant.health += int(entry.get())
        self.drawInfoFrame()


    def harmCombatant(self, combatant, entry):
        combatant.health -= int(entry.get())
        self.drawInfoFrame()


    def pythagoreanTheorum(self, x_entry, y_entry):
        x = int(x_entry.get())
        y = int(y_entry.get())
        hypotenuse = sqrt((x*x) + (y*y))
        self.drawPythagoreanFrame(hypotenuse)

    def drawPythagoreanFrame(self, hypotenuse):
        for child in self.pythagorean_frame.winfo_children():
            child.destroy()
        entry_frame = ctk.CTkFrame(self.pythagorean_frame)
        entry_frame.pack()
        x_entry = ctk.CTkEntry(entry_frame, placeholder_text="X")
        y_entry = ctk.CTkEntry(entry_frame, placeholder_text="Y")
        x_entry.grid(row = 0, column = 0, padx = 10)
        y_entry.grid(row = 0, column = 1, padx = 10)
        pythagorean_button = ctk.CTkButton(self.pythagorean_frame, text="Calculate Hypotenuse", command= lambda x_entry = x_entry, y_entry = y_entry: self.pythagoreanTheorum(x_entry, y_entry))
        pythagorean_button.pack()

        answer_label = ctk.CTkLabel(self.pythagorean_frame, text=hypotenuse)
        answer_label.pack()

    def drawInfoFrame(self):
        for child in self.info_list_frame.winfo_children():
            child.destroy()

        name_label = ctk.CTkLabel(self.info_list_frame, text="Name", font = ctk.CTkFont(size=15, weight="bold"))
        name_label.grid(row = 0, column = 0, padx = 50)
        AC_label = ctk.CTkLabel(self.info_list_frame, text="AC", font = ctk.CTkFont(size=15, weight="bold"))
        AC_label.grid(row = 0, column = 1, padx = 50)
        DC_label = ctk.CTkLabel(self.info_list_frame, text="Save DC", font = ctk.CTkFont(size=15, weight="bold"))
        DC_label.grid(row = 0, column = 2, padx = 50)
        health_label = ctk.CTkLabel(self.info_list_frame, text="Health", font = ctk.CTkFont(size=15, weight="bold"))
        health_label.grid(row = 0, column = 3, padx = 50)
        
        if self.isDM:
            for i in range(len(self.combatantsList)):
                pName_label = ctk.CTkLabel(self.info_list_frame, text = self.combatantsList[i].pName)
                pAC_label = ctk.CTkLabel(self.info_list_frame, text = self.combatantsList[i].ac)
                pName_label.grid(row = i + 1, column = 0)
                pAC_label.grid(row = i + 1, column = 1)

                if not self.combatantsList[i].saveDC == None:
                    psaveDCInitiative_label = ctk.CTkLabel(self.info_list_frame, text = self.combatantsList[i].saveDC)
                    psaveDCInitiative_label.grid(row = i + 1, column = 2)

                if not self.combatantsList[i].health == None:
                    cHealth_label = ctk.CTkLabel(self.info_list_frame, text = self.combatantsList[i].health)
                    cHealth_label.grid(row = i + 1, column = 3)
                    health_adjust_frame = ctk.CTkFrame(self.info_list_frame)
                    health_adjust_frame.grid(row = i+1, column = 4, padx = 10, pady = 10)
                    cHealth_entry = ctk.CTkEntry(health_adjust_frame, 100, 40)
                    cHealth_heal_button = ctk.CTkButton(health_adjust_frame, text = "Heal", command = lambda combatant = self.combatantsList[i], entry = cHealth_entry: self.healCombatant(combatant, entry))
                    cHealth_harm_button = ctk.CTkButton(health_adjust_frame, text = "Harm", command = lambda combatant = self.combatantsList[i], entry = cHealth_entry: self.harmCombatant(combatant, entry))
                    cHealth_heal_button.pack()
                    cHealth_entry.pack()
                    cHealth_harm_button.pack()



    #Draw the initiative order
    def drawInitiative(self):
        for child in self.initiative_frame.winfo_children():
            child.destroy()

        if self.isDM:
            self.drawInfoFrame()

        #Inside Frame
        name_label = ctk.CTkLabel(self.initiative_frame, text = "Name", font = ctk.CTkFont(size = 15, weight = "bold"))
        name_label.grid(row = 0, column = 0, padx = 100)
        initiative_label = ctk.CTkLabel(self.initiative_frame, text = "Initiative", font = ctk.CTkFont(size = 15, weight = "bold"))
        initiative_label.grid(row = 0, column = 1, padx = 100)


        if((not self.combat_start) and (not self.isDM)):
            for i in range(len(self.playerList)):
                cName_label = ctk.CTkLabel(self.initiative_frame, text = self.playerList[i].pName)
                cInitiative_label = ctk.CTkLabel(self.initiative_frame, text = self.playerList[i].initiative)
                cName_label.grid(row = i+1, column = 0, pady = 10)
                cInitiative_label.grid(row = i+1, column = 1, pady = 10)
        elif self.combat_round == 1 and not self.isDM:
            cName_label = ctk.CTkLabel(self.initiative_frame, text = self.initiativeList[0].pName)
            cInitiative_label = ctk.CTkLabel(self.initiative_frame, text = self.initiativeList[0].initiative)
            cName_label.grid(row = 1, column = 0, pady = 10)
            cInitiative_label.grid(row = 1, column = 1, pady = 10)
        else:
            for i in range(len(self.initiativeList)):
                if not self.initiativeList[i] == "End":
                    cName_label = ctk.CTkLabel(self.initiative_frame, text = self.initiativeList[i].pName)
                    cInitiative_label = ctk.CTkLabel(self.initiative_frame, text = self.initiativeList[i].initiative)
                    cName_label.grid(row = i + 1, column = 0, pady = 10)
                    cInitiative_label.grid(row = i + 1, column = 1, pady = 10)

                    if self.isDM:
                        remove_button = ctk.CTkButton(self.initiative_frame, text= "Remove", command= lambda combatant = self.initiativeList[i]:self.removeCombatant(combatant))
                        remove_button.grid(row = i + 1, column = 2, padx = 20, pady = 10)


    def displayAddCombatant(self, display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, add_combatant_button, ac_entry, checkBoxFrame, hasSaveDCCHeckbox):
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


    def addCombatant(self, display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, ac_entry, saveDC_entry, isPlayerCheckBox, hasSaveDCCheckBox, add_comabtant_button, checkBoxFrame):
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
        
        for player in self.connections:
            self.establishTCPSender(self.connections[player][0], f"addCombatant/{name}:{initiative}:{dex}:{ac}:{SaveDC}:{isPlayer}")
        
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

        self.createCombatant(name, initiative, dex, isPlayer, health, ac, SaveDC, False)


    def createCombatant(self, name, initiative, dex, isPlayer, health, ac, saveDC, connected):
        temp = combatant.combatant(initiative, dex, name, isPlayer, health, ac, saveDC, connected)

        if isPlayer:
            self.playerList.append(temp)


        if len(self.initiativeList)>0:
            currentTurn = self.initiativeList[0]
        else:
            currentTurn = temp
        self.combatantsList.append(temp)

        self.buildInitiative()
        
        if self.combat_start:
            while not self.initiativeList[0] == currentTurn:
                self.initiativeList.append(self.initiativeList.pop(0))
        self.drawInitiative()

    def buildInitiative(self):
        tempCombatantsList = self.combatantsList.copy()
        self.initiativeList.clear()
        while len(tempCombatantsList) > 0:
            nextcombatant = tempCombatantsList[0]
            for combatant in tempCombatantsList:
                if combatant.initiative > nextcombatant.initiative:
                    nextcombatant = combatant
                elif combatant.initiative == nextcombatant.initiative and combatant.dex > nextcombatant.dex:
                    nextcombatant = combatant
                elif combatant.initiative == nextcombatant.initiative and combatant.dex == nextcombatant.dex and combatant.isPlayer:
                    nextcombatant = combatant
            self.initiativeList.append(nextcombatant)
            tempCombatantsList.remove(nextcombatant)
        self.initiativeList.append("End")



    def dmScreen(self):
        clientListen = threading.Thread(target=self.establishUDPLisener, daemon=True)
        clientListen.start()
        #Clear whats currently on the screen
        for child in self.winfo_children():
            child.destroy()

        self.isDM = True
        
        #Title for the main window
        title_label = ctk.CTkLabel(self, text = "Combat Tracker", font = ctk.CTkFont(size = 30, weight = "bold"))
        title_label.pack(padx = 0, pady = 20)

        self.round_label = ctk.CTkLabel(self, text = f"Round: {self.combat_round}", font = ctk.CTkFont(size = 20, weight = "bold"))
        self.round_label.pack(pady = 10)

        #Options Buttons
        button_frame = ctk.CTkFrame(self, 1400, 100)
        button_frame.pack()
        next_button = ctk.CTkButton(button_frame, text="Next Initiative")
        clear_button = ctk.CTkButton(button_frame, text = "Clear Initiative")
        restart_button = ctk.CTkButton(button_frame, text = "Restart Initiative")
        combat_start_button = ctk.CTkButton(button_frame, text= "Start Combat")
        main_frame = ctk.CTkFrame(self, 1920, 800)
        main_frame.pack()
        self.info_list_frame = ctk.CTkScrollableFrame(main_frame, 1400, 800)
        self.info_list_frame.grid(row = 0, column = 1, pady= 10)

        next_button.configure(command=self.nextInitiative)
        restart_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:self.restartCombat(restart_button, next_button, clear_button, combat_start_button))
        clear_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:self.clearInitiative(restart_button, next_button, clear_button, combat_start_button))
        combat_start_button.configure(command= lambda next_button = next_button, clear_button = clear_button, combat_start_button = combat_start_button:self.startCombat(restart_button, next_button, clear_button, combat_start_button))

        side_frame = ctk.CTkFrame(main_frame, 500, 800)
        side_frame.grid(row = 0, column = 0)
        swap_button_frame = ctk.CTkFrame(side_frame)
        swap_button_frame.pack()
        self.initiativeSwapButton = ctk.CTkButton(swap_button_frame, text="Swap Initiatives", command=self.promptInitiativeSwap)
        self.initiativeSwapButton.pack()
        self.initiative_frame = ctk.CTkScrollableFrame(side_frame, 500, 400)
        self.initiative_frame.pack()
        self.pythagorean_frame = ctk.CTkFrame(side_frame, 500, 400)
        self.pythagorean_frame.pack()

        self.drawPythagoreanFrame("")

        #Scrollale Frame for the initiative order
        

        self.drawInitiative()

        isPlayer = ctk.BooleanVar(value=False)
        hasSaveDC = ctk.BooleanVar(value=False)
        
        display_combatant_button = ctk.CTkButton(self, text = "Add Combatant")
        display_combatant_button.pack(pady = 10)

        checkBoxFrame = ctk.CTkFrame(self, 400, 100)
        combatant_entry_frame = ctk.CTkFrame(self, 1400, 800)
        name_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Name...")
        initiative_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Initiative...")
        dex_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Dex Mod...")
        ac_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Armor Class...")
        health_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Health...")
        saveDC_entry = ctk.CTkEntry(combatant_entry_frame, 100, 40, placeholder_text="Save DC...")
        isPlayerCheckBox = ctk.CTkCheckBox(checkBoxFrame, text= "Is Player", variable=isPlayer, onvalue=True, offvalue=False)
        hasSaveDCCheckBox = ctk.CTkCheckBox(checkBoxFrame, text= "Has Save DC", variable=hasSaveDC, onvalue=True, offvalue=False)
        add_combatant_button = ctk.CTkButton(self, text="Add Combatant")

        isPlayerCheckBox.configure(command= lambda health_entry = health_entry:self.isPlayerCheckBoxCommand(health_entry, isPlayerCheckBox))
        hasSaveDCCheckBox.configure(command = lambda saveDC_entry = saveDC_entry:self.hasSaveDCCheckBoxCommand(saveDC_entry, hasSaveDCCheckBox))

        display_combatant_button.configure(command = lambda combatant_entry_frame = combatant_entry_frame, name_entry = name_entry, initiative_entry = initiative_entry, dex_entry = dex_entry, health_entry = health_entry, isPlayerCheckBox = isPlayerCheckBox, 
                                        add_combatant_button = add_combatant_button, ac_entry = ac_entry, hasSaveDCCheckBox = hasSaveDCCheckBox:self.displayAddCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, isPlayerCheckBox, add_combatant_button, ac_entry, checkBoxFrame, hasSaveDCCheckBox))
        
        add_combatant_button.configure(command = lambda combatant_entry_frame = combatant_entry_frame, name_entry = name_entry, initiative_entry = initiative_entry, dex_entry = dex_entry, health_entry = health_entry,
                                        isPlayerCheckBox = isPlayerCheckBox, ac_entry = ac_entry, hasSaveDCCheckBox = hasSaveDCCheckBox:self.addCombatant(display_combatant_button, combatant_entry_frame, name_entry, initiative_entry, dex_entry, health_entry, ac_entry, saveDC_entry, isPlayerCheckBox,hasSaveDCCheckBox,add_combatant_button, checkBoxFrame))


        combat_start_button.grid(row = 0, column = 4)


    def playerScreen(self):
        #Clear whats currently on the screen
        for child in self.winfo_children():
            child.destroy()


        self.playerList.append(self.playerSelf)
        self.combatantsList.append(self.playerSelf)

        #Title for the main window
        title_label = ctk.CTkLabel(self, text = "Combat Tracker", font = ctk.CTkFont(size = 30, weight = "bold"))
        title_label.pack(padx = 0, pady = 20)

        self.round_label = ctk.CTkLabel(self, text = f"Round: {self.combat_round}", font = ctk.CTkFont(size = 20, weight = "bold"))
        self.round_label.pack(pady = 10)

        main_frame = ctk.CTkFrame(self, 1920, 800)
        main_frame.pack()

        side_frame = ctk.CTkFrame(main_frame, 500, 800)
        side_frame.grid(row = 0, column = 0)
        self.initiative_frame = ctk.CTkScrollableFrame(main_frame, 1400, 800)
        self.initiative_frame.grid(row = 0, column = 0)
        self.pythagorean_frame = ctk.CTkFrame(side_frame, 500, 400)
        self.pythagorean_frame.grid(row = 1, column = 0)

        self.drawPythagoreanFrame("")

        #Scrollale Frame for the initiative order
        self.drawInitiative()



    def playerConnect(self, name_entry,initiative_entry, dex_entry, ac_entry, saveDC_entry):
        name = name_entry.get()
        initiative = initiative_entry.get()
        dex = dex_entry.get()
        ac = ac_entry.get()
        saveDC = None
        if not saveDC_entry.get() == "":
            saveDC = saveDC_entry.get()

        self.playerSelf = combatant.combatant(int(initiative), int(dex), name, True, None, int(ac), saveDC, True)
        message = f"{name}:{initiative}:{dex}:{ac}:{saveDC}"
        self.establishUDPSender(message)


    def playerStartScreen(self):
        self.isDM = False
        
        #Clear whats currently on the screen
        for child in self.winfo_children():
            child.destroy()

        hasSaveDC = ctk.BooleanVar(value=False)

        hasSaveDCCheckBox = ctk.CTkCheckBox(self, text= "Has Save DC", variable=hasSaveDC, onvalue=True, offvalue=False)
        hasSaveDCCheckBox.pack(pady= (500, 0))

        entry_frame = ctk.CTkFrame(self, 600, 100)
        name_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Name...")
        initiative_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Initiative...")
        dex_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Dex Mod...")
        ac_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Armor Class...")
        saveDC_entry = ctk.CTkEntry(entry_frame, 100, 40, placeholder_text="Save DC...")
        connect_button = ctk.CTkButton(self, 100, 40, text= "Connect", command= lambda name_entry = name_entry:self.playerConnect(name_entry, initiative_entry, dex_entry, ac_entry, saveDC_entry))

        entry_frame.pack(pady=20)
        name_entry.grid(padx = 10, row = 0, column = 0)
        initiative_entry.grid(padx = 10, row = 0, column = 1)
        dex_entry.grid(padx = 10, row = 0, column = 2)
        ac_entry.grid(padx = 10, row = 0, column = 3)
        connect_button.pack()

        hasSaveDCCheckBox.configure(command = lambda saveDC_entry = saveDC_entry:self.hasSaveDCCheckBoxCommand(saveDC_entry, hasSaveDCCheckBox))


    def askInitiative(self):
        dialog = ctk.CTkInputDialog(text= "What did you get for Initiative")
        newInitiative = int(dialog.get_input())
        message = f"updateInitiative/{self.playerSelf.pName}:{newInitiative}"
        self.establishTCPSender(self.connections["DM"][0], message)


    def startScreen(self):
        for child in self.winfo_children():
            child.destroy()

        tcpListener = threading.Thread(target=self.establishTCPListener, daemon=True)
        tcpListener.start()
        
        button_frame = ctk.CTkFrame(self)
        dm_button = ctk.CTkButton(button_frame, 100, 40, text= "DM", command=self.dmScreen)
        player_button = ctk.CTkButton(button_frame, 100, 40, text= "Player", command=self.playerStartScreen)
        button_frame.pack(pady = 500)
        dm_button.grid(row = 0, column = 0, padx = 20)
        player_button.grid(row = 0, column = 1, padx = 20)

main_window = MainWindow()

main_window.startScreen()
main_window.mainloop()