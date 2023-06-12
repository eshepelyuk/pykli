# list available receipes
@default:
  just --list

ksqldb:
  #!/usr/bin/env bash
  set -euo pipefail

  docker rm -f pykli-ksqldb || true
  docker run --name pykli-ksqldb -d --add-host=host.k3d.internal:host-gateway -p 8088:8088 \
    -e KSQL_BOOTSTRAP_SERVERS=host.k3d.internal:9092 \
    -e KSQL_LISTENERS=http://0.0.0.0:8088/ \
    confluentinc/ksqldb-server:0.28.2
