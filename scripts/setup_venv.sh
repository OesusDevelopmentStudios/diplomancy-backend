#!/bin/bash

PREFIX_VENV="[VENV]"
EXIT_CODE=0
MESSAGE="Ok"

if ! test -d .venv; then
    echo "$PREFIX_VENV" Virtual enviroment not detected. Setting up a new one...;

    if ! python3 -m venv .venv; then
        MESSAGE="Failed to create .venv. Check your python installation.";
        EXIT_CODE=1;
    fi

    if [ $EXIT_CODE = 0 ] && ! . .venv/bin/activate; then
        MESSAGE="Failed to activate local venv enviroment.";
        EXIT_CODE=1;
    fi

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        MESSAGE="There is an issue with venv enviroment.";
        EXIT_CODE=1;
    fi

    if ! pip3 install -r requirements.txt > /dev/null; then
        MESSAGE="Failed to install requirements.txt.";
        EXIT_CODE=1;
    fi
else
    if ! . .venv/bin/activate; then
        MESSAGE="Failed to activate local venv enviroment.";
        EXIT_CODE=1;
    fi

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        MESSAGE="There is an issue with venv enviroment.";
        EXIT_CODE=1;
    fi
fi

echo -e "$PREFIX_VENV $MESSAGE"
return $EXIT_CODE
