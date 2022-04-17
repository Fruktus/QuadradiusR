#!/bin/bash
set -e
python -m quadradiusr_server "$@" --host 0.0.0.0 --port 80 ${QUADRADIUSR_SERVER_OPTS}
