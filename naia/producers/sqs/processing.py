import base64
import json
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4

from aiobotocore.session import ClientCreatorContext, get_session  # type: ignore

from naia.producers.producer import Producer


class TaskNames(StrEnum):
    pass


class SqsAsyncProducer(Producer):
    def __init__(
        self,
        queue_url: str,
        aws_settings: dict[str, Any],
        default_route: str = '',
    ) -> None:
        self._client: Optional[ClientCreatorContext] = None
        self.queue_url: str = queue_url
        self.default_route = default_route or 'did-not-set-default-route'
        self.aws_settings = aws_settings.copy()

    @property
    def client(self) -> ClientCreatorContext:
        if self._client is None:
            self._client = get_session().create_client(**self.aws_settings)
        return self._client

    async def send_message(self, data: dict[str, Any], producer_specifics: dict[str, Any]) -> None:
        prepared_data = self._prepare_data(
            data,
            producer_specifics['task_name'],
            producer_specifics.get('routing_key', ''),
        )
        async with self.client() as client:
            client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=prepared_data,
            )

    def _prepare_data(
        self,
        data: dict[str, Any],
        task_name: TaskNames,
        routing_key: str,
    ) -> str:
        """Prepares data to enqueue into SQS that will be read by Celery"""
        task = {
            'task': task_name,
            'id': str(uuid4()),
            'args': [data],
            'kwargs': {},
            'retries': 0,
            'eta': None,
            'expires': None,
            'utc': True,
            'callbacks': None,
            'errbacks': None,
            'timelimit': [None, None],
            'taskset': None,
            'chord': None,
        }
        envelope = {
            'body': base64.b64encode(bytes(json.dumps(task), 'utf-8')).decode('utf-8'),
            'content-encoding': 'utf-8',
            'content-type': 'application/json',
            'headers': {},
            'properties': {
                'reply_to': str(uuid4()),
                'correlation_id': str(uuid4()),
                'delivery_mode': 2,
                'delivery_info': {
                    'priority': 0,
                    'exchange': 'default',
                    'routing_key': routing_key or self.default_route,
                },
                'body_encoding': 'base64',
                'delivery_tag': str(uuid4()),
            },
        }
        return base64.b64encode(bytes(json.dumps(envelope), 'utf-8')).decode('utf-8')
