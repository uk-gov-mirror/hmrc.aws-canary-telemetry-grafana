#!/usr/bin/env bash

set -eu

# Initialise directories
BASEDIR=/data
cd ${BASEDIR}

# Force Debian to use HTTPS
cp /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list.d/debian.sources.bak
sed --in-place 's|http://|https://|g' /etc/apt/sources.list.d/debian.sources

# Update the package listing, so we know what package exist:
apt-get update && apt-get -y upgrade && apt-get install -y zip

# Install requirements
python -m venv "${VENV_NAME}"
source "${VENV_NAME}/bin/activate"
pip install --requirement "${REQUIREMENTS_FILE}"

exec "$@"
