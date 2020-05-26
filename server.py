# -*- coding: utf-8 -*-

# переменные
players = {}
settings = {
'max players': 3,
'port': 9090
}
started = False

import socket, json, uuid

def fj(s):
    return json.dumps(s)

def tj(s):
    return json.loads(s)

# сервер
sock = socket.socket()
sock.bind(('', settings['port']))
sock.listen(settings['max players']+5)
print('started server on '+str(settings['port']))

# обработка подключений
while True:
    conn, addr = sock.accept()

    ans = {}

    data = b''
    while True:
        data += conn.recv(1024)
        if data.find(b'EOF') != -1:
            data = data.replace(b'EOF', b'')
            break

    print(data.decode())
    data = data.decode()
    data = tj(data)
    com = data['com']

    if com == 'init':
        if len(players) >= settings['max players']:
            ans['err'] = 'too many players'
        else:
            id = uuid.uuid1().int
            id1 = uuid.uuid1().int
            ans['id'] = id
            ans['id1'] = id1
            players[id] = {'nick':data['nick'], 'y': 100, 'id': id1}
            print('new player:', data['nick'], id)
    elif data.get('id', 0) not in players:
        ans['err'] = 'need to register'
    elif data.get('id', 0) in players:
        if com == 'get_players':
            ans = {'players': [players[p] for p in players]}
        elif com == 'quit':
            del players[data['id']]
        elif com == 'set_pos':
            players[data[id]] = data.get('pos', 100)
            ans['ans'] = True
        elif com == 'change_name':
            name = data.get('name', 'player')
            if data.get('name', 'player') == '':
                name = 'player'
            players[data['id']]['nick'] = name
        elif com == 'check_start':
            check = True
            for id in players:
                if players[id].get('start', False) == False:
                    check = False
                    break
            players[data['id']]['start'] = True
            ans['started'] = check

    conn.send(fj(ans).encode() + b'EOF')
    conn.close()
