import sys
import selectors
import socket


sel = selectors.DefaultSelector()
# sel_stdin = selectors.DefaultSelector()
# sel_stdin.register(sys.stdin, selectors.EVENT_READ, data=None)
if len(sys.argv) != 2:
    print("usage:", sys.argv[0], "<username>")
    sys.exit(1)

username = sys.argv[1]
host = '127.0.0.1'
port = 30199
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex((host, port))
sel.register(sock, selectors.EVENT_WRITE | selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=1)
        # event_stdin = sel_stdin.select(timeout=1)
        if events:
            for sel_key, event_mask in events:
                sock = sel_key.fileobj
                if event_mask & selectors.EVENT_WRITE:
                    msg = username + ': ' + sys.stdin.readline().rstrip()
                    msg_enc = msg.encode('utf-8')
                    sock.send(msg_enc)
                    print(msg)
                # if event_mask & selectors.EVENT_READ:
                #     data = sock.recv(1024)
                #     if data:
                #         print(repr(data))
        if not sel.get_map():
            break
finally:
    sel.close()
