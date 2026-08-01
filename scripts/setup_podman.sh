#!/bin/bash

PREFIX_DB="[DB]"
EXIT_CODE=0
MESSAGE="Ok"

if ! podman container exists $CONTAINER_NAME; then
    echo "$PREFIX_DB" Database container does not exist. Creating new one...;

    if podman compose --env-file diplomancy.conf --file database/compose.yaml up -d > /dev/null; then
        sleep 5
        MESSAGE="Database container created successfully."
    else
        MESSAGE="Failed to create database container."
        EXIT_CODE=1
    fi
fi

if [ $EXIT_CODE = 0 ] && ! podman ps | grep $CONTAINER_NAME > /dev/null; then
    echo "$PREFIX_DB" Starting database container...;

    if ! podman start $CONTAINER_NAME > /dev/null; then
        MESSAGE="Failed to start database container."
        EXIT_CODE=1
    fi
fi

echo -e "$PREFIX_DB $MESSAGE"
return $EXIT_CODE
