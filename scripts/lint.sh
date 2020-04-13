#!/bin/sh -e

SOURCE_FILES="scraper"

GREEN="\033[32m"
NC="\033[0m" # No Color

if [[ "$1" = "yes" ]]
then
    echo -e "${GREEN}Formating ${NC}code..."
    autoflake --in-place --recursive $SOURCE_FILES
    black -t py38 $SOURCE_FILES
    echo -e "${GREEN}Sorting ${NC}imports..."
    isort -rc -y -l 87 $SOURCE_FILES
else
    echo -e "${GREEN}Checking ${NC}code format..."
    autoflake --recursive $SOURCE_FILES
    black -t py38 --check --diff $SOURCE_FILES
    echo -e "${GREEN}Checking ${NC}imports order..."
    isort -c -df -rc -l 87 $SOURCE_FILES
    echo -e "${GREEN}Checking ${NC}static type..."
    mypy $SOURCE_FILES
fi
