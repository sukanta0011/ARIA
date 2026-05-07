# ARIA

### ollama setup
- to check server
curl http://localhost:11434/api/tags

- pull model
ollama pull qwen3:8b
- inside docker
docker exec -it ollama ollama pull qwen3:0.6b

- run model
ollama run qwen3:8b

- ollama commands
ollama list
ollama ps
ollama rm qwen3:8b (delete model)


### Migration
uv run alembic revision --autogenerate -m "commit message"
uv run alembic upgrade head

Safe way to new nullable column in an existing table:
- crate the column with nullable = True -> migrate
- fill the column with some random(semi-random) values.
- Change the nullable = False and migrate again.
- If we do not follow this step, migration will fail.
- In production system, this is first done locally, and once every checks passes, it id done on production db.

Here our db exists inside docker, once the docker is started, we have to run the manual migration
- We need to set port forwarding in the docker compose to communicate with the db from the outside (ports: - "5432:5432")
- Make sure the port is not occupied in the computer.
- Then change the postgres url in the .env file to localhost:port_no
- follow the normal commands.


### Issures
- Serialization problem
All pydantic model should be serialized to dict before saving to db

- Docker setup
Very important
local environment and ocker is different, so what ever service is running, we should always keep default to local host and docker to the docker container name,
