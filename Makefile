build:
	docker buildx build --platform linux/amd64 -t twitchdropsminer-miner:amd64 --load .