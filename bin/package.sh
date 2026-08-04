#!/usr/bin/env bash

set -eu

mkdir -p build
cd "./${VENV_NAME}/lib/python3.14/site-packages"
zip -r "../../../../build/canary.zip" .
cd -
cd "./src"
zip -r --grow "../build/canary.zip" .
cd -
