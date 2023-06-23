# list available receipes
@default:
  just --list

up:
  docker-compose -f tests/docker-compose.yaml up -d

down:
  docker-compose -f tests/docker-compose.yaml down

test filter='':
  poetry run pytest --capture=tee-sys -k '{{filter}}'

run srv="http://localhost:28088":
  poetry run pykli {{srv}}
