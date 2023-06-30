# list available receipes
@default:
  just --list

up:
  docker-compose -f tests/docker-compose.yaml up -d

down:
  docker-compose -f tests/docker-compose.yaml down

test filter='':
  poetry run pytest -m 'not e2e' --capture=tee-sys -k '{{filter}}'

e2e filter='': up
  poetry run pytest -m e2e --capture=tee-sys -k '{{filter}}'

run srv="http://localhost:28088":
  poetry run pykli {{srv}}

ksqldb-cli srv="http://host.docker.internal:28088":
  docker run -it --rm --add-host=ksqldb:host-gateway \
    confluentinc/ksqldb-cli:0.29.0 ksql {{srv}}
