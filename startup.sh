#!/bin/bash

PREFIX_SETUP="[SETUP]"
EXIT_CODE=0
MESSAGES=()

if ! command -v podman info > /dev/null; then
    MESSAGES+=("Podman is not installed. Cannot setup database.")
    EXIT_CODE=1
fi

if ! python3 --version > /dev/null; then
    MESSAGES+=("Python is required to run backend script.")
    EXIT_CODE=1
fi

if [ $EXIT_CODE = 0 ] && ! . scripts/setup_venv.sh; then
    EXIT_CODE=1
fi

if [ $EXIT_CODE = 0 ] && ! . scripts/setup_podman.sh; then
    EXIT_CODE=1
fi

if [ $EXIT_CODE = 0 ]; then
    MESSAGES+=("Ok")
    MESSAGES+=("Starting backend services...")
fi

for message in "${MESSAGES[@]}"; do
    echo -e "$PREFIX_SETUP $message"
done

if [ $EXIT_CODE = 0 ] && ! python3 diplomancy/main.py; then
    echo -e "$PREFIX_SETUP Failed to start primary script."
    EXIT_CODE=1
fi

exit $EXIT_CODE
