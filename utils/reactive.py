from collections import defaultdict

class EventEmitter:
    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event, callback):
        self.listeners[event].append(callback)

    def unsubscribe(self, event, callback):
        if callback in self.listeners[event]:
            self.listeners[event].remove(callback)

    def emit(self, event, *args, **kwargs):
        for callback in self.listeners[event]:
            callback(*args, **kwargs)
