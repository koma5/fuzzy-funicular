#!/usr/bin/env bash

set -eu

source .venv/bin/activate
textual run --dev bt_mqtt_ui/textual/app.py
