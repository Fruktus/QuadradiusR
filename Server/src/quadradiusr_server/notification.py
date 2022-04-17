import abc
import asyncio
import fnmatch
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Notification:
    topic: str
    subject_id: str
    data: dict


class Handler(ABC):
    @abc.abstractmethod
    async def handle(self, notification: Notification):
        pass


class NotificationService:
    def __init__(self) -> None:
        self.handlers: Dict[str, List[Tuple[str, Handler]]] = \
            defaultdict(lambda: [])

    def register_handler(
            self, subject_id: str,
            topic: str, handler: Handler):
        self.handlers[subject_id].append((topic, handler))

    def unregister_handler(
            self, subject_id: str,
            topic: str, handler: Handler):
        self.handlers[subject_id].remove((topic, handler))

    def notify(self, notification: Notification):
        import asyncio
        asyncio.create_task(self.notify_now(notification))

    async def notify_now(self, notification: Notification):
        handlers = set()
        for subject_id, tpl in self.handlers.items():
            for topic, handler in tpl:
                if self._subject_matches(notification.subject_id, subject_id) and \
                        self._topic_matches(notification.topic, topic):
                    handlers.add(handler)
        await asyncio.gather(*[h.handle(notification) for h in handlers])

    def _subject_matches(self, subject_id: str, subject_id_wildcard: str):
        if subject_id_wildcard == '*':
            return True
        return subject_id == subject_id_wildcard

    def _topic_matches(self, topic: str, topic_wildcard: str):
        if topic_wildcard == '*':
            return True
        filtered = fnmatch.filter([topic], topic_wildcard)
        if filtered:
            return True
