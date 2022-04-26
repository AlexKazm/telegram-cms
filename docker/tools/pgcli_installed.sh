#!/bin/bash
set -e

if [ "$pgcli" ]; then
  echo "pgcli installed"

else
  exec sudo apt-get install pgcli
fi
