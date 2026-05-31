#!/bin/bash

PREFIX_DB="[DB]"
EXIT_CODE=0
MESSAGE="Ok"

if ! podman container exists diplomancy_db; then
    echo "$PREFIX_DB" Database container does not exist. Creating new one...;

    if ! podman compose --file database/compose.yaml up -d > /dev/null; then
        MESSAGE="Failed to create database container."
        EXIT_CODE=1
    fi
fi

if [ $EXIT_CODE = 0 ] && ! podman ps | grep diplomancy_db > /dev/null; then
    echo "$PREFIX_DB" Starting database container...;

    if ! podman start diplomancy_db > /dev/null; then
        MESSAGE="Failed to start database container."
        EXIT_CODE=1
    fi
fi

echo -e "$PREFIX_DB $MESSAGE"
return $EXIT_CODE
