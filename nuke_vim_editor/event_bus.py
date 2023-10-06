class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_name: str, callback):
        self.subscribers.setdefault(event_name, []).append(callback)

    def publish(self, event_name: str, *args, **kwargs):
        for callback in self.subscribers.get(event_name, []):
            callback(*args, **kwargs)

event_bus = EventBus()