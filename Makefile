up:
	docker compose -f docker-compose.local.yml up -d

down:
	docker compose -f docker-compose.local.yml down

build:
	docker buildx build --platform linux/amd64 -t twitchdropsminer-miner:amd64 --load .
