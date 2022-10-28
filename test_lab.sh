#!/bin/bash

SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
INTEGRATION_TESTS_DIR="${SCRIPT_DIR}/integration_tests"
ANALIZATOR_DIR="${SCRIPT_DIR}/analizator"


for file in "$INTEGRATION_TESTS_DIR"/*
do
  # iterate over .lan files
  if [[ $file == *.lan ]]; then
    # execute GLA.py
    echo ${file}
    rm -rf "${ANALIZATOR_DIR}/tablice"
    python3 "${SCRIPT_DIR}/GLA.py" < "${file}"
    rm "${SCRIPT_DIR}/target.lan"

    # execute LA.py
    # redirect .in file to stdin and call LA.py, compare it with .out file
    # if they are equal write "OK", else write where they differ
    ASSERT="$(diff -B <(python3 "${ANALIZATOR_DIR}/LA.py" < "${file::-4}.in") <(cat "${file::-4}.out"))"
    # if ASSERT is empty write OK
    if [ -z "$ASSERT" ]; then
      echo "OK"
    else
      echo $ASSERT
    fi
    echo "*************************************************************"
    rm -rf "${ANALIZATOR_DIR}/tablice"
  fi
done