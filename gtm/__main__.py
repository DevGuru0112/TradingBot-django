from .server import Server

server = Server()

if __name__ == "__main__":
    
    try:
        server.start()

    except KeyboardInterrupt:
        pass













