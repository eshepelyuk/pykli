

# list available receipes
@default:
  just --list

up:
  docker-compose -f tests/docker-compose.yaml up -d

down:
  docker-compose -f tests/docker-compose.yaml down -v --remove-orphans

test-unit filter='':
  poetry run pytest -o junit_suite_name='Unit tests' -m 'not e2e' --capture=tee-sys --junit-xml=test-unit.xml -k '{{filter}}'

test-e2e filter='': up
  poetry run pytest -o junit_suite_name='E2E tests' -m e2e --capture=tee-sys --junit-xml=test-e2e.xml -k '{{filter}}'

test: test-unit test-e2e

run srv="http://localhost:28088":
  poetry run pykli {{srv}}

ksqldb-cli srv="http://host.docker.internal:28088":
  docker run -it --rm --add-host=ksqldb:host-gateway \
    confluentinc/ksqldb-cli:0.29.0 ksql {{srv}}
