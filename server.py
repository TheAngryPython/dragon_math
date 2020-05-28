# -*- coding: utf-8 -*-

# переменные
players = {}
settings = {
'max players': 3,
'port': int(input("port (9090): ") or 9090)
}
mn = 0
mx = 9
speed = -1
started = False
t_num = 0
generated = False

import socket, json, uuid, random

def fj(s):
    return json.dumps(s)

def tj(s):
    return json.loads(s)

def is_simple(num):
    nms = [(num / i, int(num / i), i) for i in range(mn + 2, mx + 1)]
    lst = []
    for nm in nms:
        if nm[0] == nm[1]:
            lst.append(nm[2])
    if len(lst) == 0:
        return (False, lst)
    else:
        return (True, lst)

# генерировать правильный ответ
def generate_true(num):
    if is_simple(num)[0]:
        r = random.randint(1, 4)
    else:
        r = random.randint(1, 2)
    if r == 1:
        nm = random.randint(mn, num)
        nm = num - nm
        nm1 = num - nm
        sep = '+'
    elif r == 2:
        sep = '-'
        nm = random.randint(num, mx)
        nm1 = (num - nm) * -1
    elif r == 3:
        sep = '*'
        nm = random.choice(is_simple(num)[1])
        nm1 = int(num / nm)
    elif r == 4:
        sep = '/'
        nm1 = random.choice(is_simple(num)[1])
        nm = int(num * nm1)
    return (nm, nm1, sep, True)

# генерировать не правильный ответ
def generate_false(num):
    sep = random.choice(['-', '+', '/', '*'])
    while 1:
        nm = random.randint(mn, mx)
        nm1 = random.randint(mn, mx)

        if nm1 == 0 or nm == 0 and sep == '/':
            continue

        if nm + nm1 != num and nm - nm1 != num and nm / nm1 != num and nm * nm1 != num:
            break

    return (nm, nm1, sep, False)

def next_nums():
    global t_num

    # создаём список
    a_num = random.randint(mn, mx)
    t_num = generate_true(a_num)
    nums = [t_num, generate_false(a_num), generate_false(a_num)]

    # мешаем список
    random.shuffle(nums)

    # ищем правильный вариант
    for i in range(len(nums)):
        if nums[i] == t_num:
            t_num = i

    return (a_num, nums, t_num)

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
            players[data['id']]['y'] = data.get('pos', 100)
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
        elif com == 'next_nums':
            if not generated:
                ans['nums'] = next_nums()
                speed -= 1
        elif com == 'get_speed':
            ans['speed'] = speed
        elif com == 'check_answer':
            generated = False
            if t_num == data['num']:
                ans['num'] = True
            else:
                 ans['num'] = False

    conn.send(fj(ans).encode() + b'EOF')
    conn.close()
