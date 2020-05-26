# -*- coding: utf-8 -*-

import socket, json

nickname = 'player'
port = 9090
players = {}
sock = socket.socket()
data = 0
id = 0
id1 = 0
ip = 'localhost'
port = 9090
started = False

def fj(s):
    return json.dumps(s)

def tj(s):
    return json.loads(s)

def init():
    global sock
    try:
        sock.close()
    except:
        pass
    sock = socket.socket()
    sock.connect((ip, int(port)))

def ex(err=1):
    send({'com': 'quit'},q=1)

def send(s, q=0):
    init()
    global sock, data, id
    sock.send(fj({**s, 'id': id}).encode() + b'EOF')
    data = b''
    while True:
        data += sock.recv(1024)
        if data.find(b'EOF') != -1:
            data = data.replace(b'EOF', b'')
            break
    sock.close()
    if q != 0:
        quit(q)
    data = tj(data)
    if data.get('err'):
        print(data['err'])
        ex(1)
    else:
        return data

def get_players():
    global players
    send({'com': 'get_players'})
    for player in data['players']:
        if player['id'] == id1:
            break
    else:
        data['players'].pop(player)
    players = data['players']

def set_pos(y):
    send({'com':'set_pos', 'pos': y})

def connect():
    global id, id1, players
    send({'com': 'init', 'nick': nickname})
    id = data['id']
    id1 = data['id1']
    players = get_players()

def change_name(name):
    send({'com': 'change_name', 'name': name})

def check_start():
    global started
    send({'com':'check_start'})
    started = data['started']
    return started
