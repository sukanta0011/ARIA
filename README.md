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

### Docker setup
Very important
local environment and ocker is different, so what ever service is running, we should always keep defau;l to local host and docker to the docker container name,