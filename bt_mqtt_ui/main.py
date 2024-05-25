import json

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
@click.option("--pretty", is_flag=True, default=False)
def listen(host, port, topic, pretty):
    """Listen to mqtt messages"""
    import asyncio
    import signal

    from aiomqtt import Client as MQTTClient

    def shutdown():
        print("Received shutdown signal, exiting...")
        for task in asyncio.all_tasks():
            task.cancel()

    async def handle_message(client, pretty_json: bool = False):
        def format_msg(payload: str):
            if pretty_json:
                return json.dumps(json.loads(payload), indent=2)
            return payload

        async for msg in client.messages:
            print(f"Qos: {msg.qos} | Topic: {msg.topic} - {format_msg(msg.payload)}")

    async def main(broker_host, token):
        async with MQTTClient(hostname=broker_host, clean_session=True) as client:
            for to in topic:
                print(f"Subscribing to topic '{to}'")
                await client.subscribe(to)
            await handle_message(client, pretty)

    loop = asyncio.get_event_loop()
    for handler in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(handler, shutdown)
    try:
        loop.run_until_complete(main(host, None))
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    cli()
