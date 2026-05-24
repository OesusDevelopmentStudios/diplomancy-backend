#!/bin/bash

if ! test -d .venv; then
    echo -e "[VENV]" Virtual enviroment not detected. Setting up new one '\n';

    if ! python3 -m venv .venv; then
        echo "[VENV]" Failed to create .venv. Check your python installation.;
        exit 0;
    fi

    if ! . .venv/bin/activate; then
        echo "[VENV]" Failed to activate local venv enviroment.;
        exit 0;
    fi

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "[VENV]" There is an issue with venv enviroment.;
        exit 0;
    fi

    if ! pip3 install -r requirements.txt; then
        echo "[VENV]" Failed to install requirements.txt.;
        exit 0;
    fi

    echo -e '\n';
else
    if ! . .venv/bin/activate; then
        echo "[VENV]" Failed to activate local venv enviroment.;
        exit 0;
    fi

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "[VENV]" There is an issue with venv enviroment.;
        exit 0;
    fi

    echo -e "[VENV]" Ok;
fi

echo -e "[DIPLOMANCY]" Starting backend services '\n';

if ! python3 diplomancy/main.py; then
    echo "[DIPLOMANCY]" Failed to start backend script.;
    exit 0;
fi
