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

if source diplomancy.conf; then
    if [ -z "$CONTAINER_NAME" ]; then
        MESSAGES+=("CONTAINER_NAME variable is not set in the config file.")
        EXIT_CODE=1
    fi

    if [ -z "$DB_NAME" ]; then
        MESSAGES+=("DB_NAME variable is not set in the config file.")
        EXIT_CODE=1
    fi

    if [ -z "$DB_PASSWORD" ]; then
        MESSAGES+=("DB_PASSWORD variable is not set in the config file.")
        EXIT_CODE=1
    fi

    if [ -z "$DB_PORT" ]; then
        MESSAGES+=("PORT variable is not set in the config file.")
        EXIT_CODE=1
    fi

else
    MESSAGES+=("Unable to load configuration.")
    EXIT_CODE=1
fi

if [ $EXIT_CODE = 0 ] && ! . scripts/setup_podman.sh; then
    EXIT_CODE=1
fi

if [ $EXIT_CODE = 0 ]; then
    MESSAGES+=("Database $DB_NAME will is running at http://127.0.0.1:$DB_PORT")
    MESSAGES+=("Starting backend services...")
fi

for message in "${MESSAGES[@]}"; do
    echo -e "$PREFIX_SETUP $message"
done

if [ $EXIT_CODE = 0 ] && ! python3 diplomancy/main.py $DB_PORT $DB_NAME $DB_PASSWORD; then
    echo -e "$PREFIX_SETUP Failed to start primary script."
    EXIT_CODE=1
fi

exit $EXIT_CODE
