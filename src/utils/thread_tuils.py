import threading

class ThreadUtils:

    @classmethod
    def register(cls, 
                 entity):
        handler = threading.Thread(target = entity.daemon, 
                                   daemon = True)
        return handler