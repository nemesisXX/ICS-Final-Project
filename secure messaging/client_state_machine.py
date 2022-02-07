"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
from Crypto.Cipher import PKCS1_OAEP
import jsonpickle


class ClientSM:
    def __init__(self, s, key):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.key = key
        self.server_key = None

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def set_server_key(self, key):
        self.server_key = key

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action": "disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action": "time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += str(logged_in)

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer):
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action": "search", "target": term}))
                    search_rslt = json.loads(myrecv(self.s))["results"]
                    if (len(search_rslt)) > 0:
                        self.out_msg += str(search_rslt) + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action": "poem", "target": poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif my_msg[:4].lower() == "ping":
                    self.out_msg += "pong" + my_msg[4:] + "\n\n"

                elif my_msg.lower() == "power overwhelming":
                    self.out_msg += "You are now INVINCIBLE!\n\n"

                elif my_msg == "operation CWAL":
                    self.out_msg += "You can build Rome in ONE DAY!\n\n"

                elif my_msg.lower() == "show me the money":
                    self.out_msg += "Wow, You are so RICH!\n\n"

                elif my_msg.lower() == "black sheep wall":
                    self.out_msg += "Wow, You can see EVERYTHING!\n\n"

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err:
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
            
                if peer_msg["action"] == "connect":

                    # ----------your code here------#
                    peer = peer_msg["from"]
                    self.state = S_CHATTING
                    self.peer += peer
                    self.out_msg += 'Request from ' + peer + '\nYou are connect with' + peer + '. Chat away!\n\n'
                    self.out_msg += '-----------------------------------\n'
                    # ----------end of your code----#
                    
# ==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
# ==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                if my_msg[:6].lower() == "_flip_":
                    my_msg_ls = my_msg[6:].split()
                    my_msg_ls.reverse()
                    my_msg = "_flip_" + " ".join(my_msg_ls)
                text_with_time = text_proc(my_msg, self.me)
                cipher = PKCS1_OAEP.new(self.server_key)
                cipher_text = jsonpickle.encode(cipher.encrypt(text_with_time.encode()))
                mysend(self.s, json.dumps({"action": "exchange", "from": self.me,
                                           "message": cipher_text}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                # ----------your code here------#
                peer_msg = json.loads(peer_msg)
                # print(peer_msg)
                # print(type(peer_msg))
                if peer_msg["action"] == "exchange":
                    cipher = PKCS1_OAEP.new(self.key)
                    message = cipher.decrypt(jsonpickle.decode(peer_msg["message"])).decode()
                    self.out_msg += "[" + peer_msg["from"] + "] "
                    self.out_msg += message + "\n"
                elif peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.out_msg += "Everyone left, you are disconnected"
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ""
                # ----------end of your code----#
                
            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
