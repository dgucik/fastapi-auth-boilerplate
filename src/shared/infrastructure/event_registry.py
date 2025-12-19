from shared.application.event_handling import EventRegistry
from shared.application.exceptions import EventReconstructionException
from shared.domain.events import Event


class EventRegistryImpl(EventRegistry):
    def __init__(self, events: list[type[Event]] | None = None):
        self._name_to_cls: dict[str, type[Event]] = {}
        self._cls_to_name: dict[type[Event], str] = {}

        if events:
            for event in events:
                self.register(event)

    def register(self, event_class: type[Event]) -> None:
        event_name = event_class.__name__

        self._name_to_cls[event_name] = event_class
        self._cls_to_name[event_class] = event_name

    def get_class(self, event_name: str) -> type[Event]:
        if event_name not in self._name_to_cls:
            raise EventReconstructionException(f"Event {event_name} not registered.")
        return self._name_to_cls[event_name]

    def get_name(self, event_cls: type[Event]) -> str:
        return self._cls_to_name.get(event_cls, event_cls.__name__)
