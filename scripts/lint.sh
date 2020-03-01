#!/bin/sh -e

SOURCE_FILES="scraper"

GREEN="\033[32m"
NC="\033[0m" # No Color

if [[ "$1" = "yes" ]]
then
    echo -e "${GREEN}Formating ${NC}code..."
    black -t py37 $SOURCE_FILES
    echo -e "${GREEN}Sorting ${NC}imports..."
    isort -rc -y $SOURCE_FILES
else
    echo -e "${GREEN}Checking ${NC}code format..."
    black -t py37 --check --diff $SOURCE_FILES
    echo -e "${GREEN}Checking ${NC}imports order..."
    isort -c -df -rc $SOURCE_FILES
    echo -e "${GREEN}Checking ${NC}static type..."
    mypy $SOURCE_FILES
fi
