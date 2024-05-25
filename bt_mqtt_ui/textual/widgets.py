import json

import aiomqtt.client
from textual.widgets import RichLog
from textual import work, on
from textual.messages import Message
from textual.reactive import var
from tenacity import retry, wait_fixed, retry_if_exception_type


class Terminal(RichLog):
    """Terminal Widget"""

    hidden: var[bool] = var(False)
    bg_color: var[str] = var("black")

    def watch_hidden(self):
        pass

    def watch_bg_color(self):
        self.styles.bg_color = self.bg_color


class MqttClientWidget(RichLog):
    """A RichLog that posts mqtt messages"""

    msg_counter: var[int] = var(0)

    class MQTTMessage(Message):
        def __init__(self, topic: str, payload: str, qos: int):
            super().__init__()
            self.topic = topic
            self.payload = payload
            self.qos = qos

    def __init__(
        self,
        host: str,
        port: int = 1883,
        keepalive: int = 60,
        retry_interval_sec: int = 5,
        topics: tuple[str] = ("#",),
        pretty_json: bool = True,
        clear_on_n_msgs: int = 100,
        mqtt_username: str | None = None,
        mqtt_password: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self.user_name = mqtt_username
        self.password = mqtt_password
        self.topics = topics
        self.pretty_json = pretty_json
        self.retry_interval = retry_interval_sec
        self.clear_on_n_msgs = clear_on_n_msgs

    def on_mount(self):
        self.start_worker()

    @on(MQTTMessage)
    def write_msg(self, msg: MQTTMessage):
        self.write(f"TOPIC: {msg.topic}")
        if self.pretty_json:
            self.write(json.loads(msg.payload))
        else:
            self.write(msg.payload)

    def watch_msg_counter(self):
        if self.msg_counter == self.clear_on_n_msgs:
            self.clear()
            self.write(f"Clearing terminal every {self.clear_on_n_msgs} messages")

    @work(thread=False)
    async def start_worker(self) -> None:
        from aiomqtt import Client as MQTTClient

        @retry(
            wait=wait_fixed(self.retry_interval),
            retry=retry_if_exception_type(aiomqtt.client.MqttError),
        )
        async def run():
            try:
                async with MQTTClient(
                    hostname=self.host,
                    port=self.port,
                    username=self.user_name,
                    password=self.password,
                    identifier=self.id or "zzzz",
                    clean_session=True,
                    keepalive=self.keepalive,
                ) as client:
                    for to in self.topics:
                        self.write(f"SUBSCRIBE TO: {to}")
                        await client.subscribe(to)

                    async for msg in client.messages:
                        self.msg_counter += 1
                        self.post_message(
                            self.MQTTMessage(
                                msg.topic.value, msg.payload.decode("utf-8"), msg.qos
                            )
                        )
            except aiomqtt.client.MqttCodeError as e:
                self.write(e)
                self.msg_counter += 1
                raise
            except aiomqtt.client.MqttError as e:
                self.write(e)
                self.msg_counter += 1
                raise

        await run()
