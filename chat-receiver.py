import sys
import selectors
import socket


sel = selectors.DefaultSelector()

host = '127.0.0.1'
port = 30199
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.setblocking(False)
sock.connect_ex((host, port))
sel.register(sock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for sel_key, event_mask in events:
                sock = sel_key.fileobj
                if event_mask & selectors.EVENT_READ:
                    data = sock.recv(1024)
                    print(data.decode('utf-8'))
        if not sel.get_map():
            break
finally:
    sel.close()
