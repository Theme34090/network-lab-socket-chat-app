import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
pool = dict()


def accept_wrapper(sock):
    conn, addr = sock.accept()
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    pool[addr] = conn


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
            pool.pop(data.addr, None)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = len(data.outb)
            for addr, conn in pool.items():
                if addr != data.addr:
                    print("echoing", repr(data.outb), "to", data.addr)
                    sent = conn.send(data.outb)
            data.outb = data.outb[sent:]


host = '127.0.0.1'
port = 30199
# port = int(sys.argv[1])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print("listening on", (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
