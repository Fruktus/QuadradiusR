import abc
import fnmatch
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Notification:
    topic: str
    subject_id: str
    data: dict


class Handler(ABC):
    @abc.abstractmethod
    def get_topic(self):
        pass

    @abc.abstractmethod
    async def handle(self, notification: Notification):
        pass


class NotificationService:
    def __init__(self) -> None:
        self.handlers: Dict[str, List[Handler]] = \
            defaultdict(lambda: [])

    def register_handler(
            self, subject_id: str,
            handler: Handler):
        self.handlers[subject_id].append(handler)

    def unregister_handler(self, handler: Handler):
        for handlers in self.handlers.values():
            try:
                handlers.remove(handler)
            except ValueError:
                pass

    def notify(self, notification: Notification):
        import asyncio
        asyncio.create_task(self.notify_now(notification))

    async def notify_now(self, notification: Notification):
        for subject_id, handlers in self.handlers.items():
            for handler in handlers:
                topic = handler.get_topic()
                if self._subject_matches(notification.subject_id, subject_id) and \
                        self._topic_matches(notification.topic, topic):
                    await handler.handle(notification)

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
