#!/bin/bash
set -e

if [ -z "$HREF" ]; then
  echo "Environment variable HREF needs to be set. "
  echo "It should point to the address the user sees in their browser, e.g. HREF=example.com:8080"
  exit 1
fi

python -m quadradiusr_server \
  --host 0.0.0.0 \
  --port 80 \
  --set server.database.create_metadata=true \
  --set server.href="$HREF" \
  ${QUADRADIUSR_SERVER_OPTS} \
  "$@"
