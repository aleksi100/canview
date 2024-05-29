import socket


HOST = "127.0.0.1"  # canlogserver host
PORT = 28700  # canlogserver port


def getCanFrames(updateFrames):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
                d = s.recv(1024)
                if d:
                    updateFrames(d.decode("utf-8"))
    except KeyboardInterrupt:
        exit(0)
