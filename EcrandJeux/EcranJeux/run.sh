#!/bin/bash
cd "$(dirname "$0")"
source ~/DrinkingGame/env/bin/activate
export QT_QPA_PLATFORM=linuxfb
python main.py