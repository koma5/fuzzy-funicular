import click


@click.group()
def cli():
    pass


@click.group()
def cli():
    pass


@cli.command()
@click.option("-h", "--host", default="127.0.0.1")
@click.option("--port", default=1883, help="MQTT broker port")
@click.option(
    "-t", "--topic", multiple=True, default=("tasmota/discovery/+/+", "tele/+/+")
)
def listen(host, port, topic):
    """Listen to mqtt messages"""
    import asyncio
    import signal

    from gmqtt import Client as MQTTClient

    # gmqtt also compatibility with uvloop
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    STOP = asyncio.Event()

    def on_connect(client, flags, rc, properties):
        print("Connected")
        for to in topic:
            client.subscribe(to)

    def on_message(client, topic, payload, qos, properties):
        print(f"RECV MSG topic {topic}:", payload)

    def on_disconnect(client, packet, exc=None):
        print("Disconnected")

    def on_subscribe(client, mid, qos, properties):
        print("SUBSCRIBED")

    def ask_exit(*args):
        STOP.set()

    async def main(broker_host, token):
        client = MQTTClient(None)

        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe

        # client.set_auth_credentials(token, None)
        await client.connect(broker_host)

        # client.publish('TEST/TIME', str(time.time()), qos=1)

        await STOP.wait()
        await client.disconnect()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main(host, None))


if __name__ == "__main__":
    cli()
