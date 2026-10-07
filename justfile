compose := "docker compose -f docker-compose.local.yml"

# 列出所有命令
default:
    @just --list

# 安装/同步依赖
sync:
    uv sync

# 以 GUI 模式运行
run *args:
    uv run python main.py {{args}}

# 以 headless 模式运行
headless *args:
    uv run python main.py --headless {{args}}

# Rationale: 挂载的宿主机文件不存在时，Docker 会把它们创建成目录，导致容器内读写失败
# 创建 Docker 挂载需要的文件
[private]
ensure-mounts:
    @mkdir -p cache
    @touch cookies.jar log.txt
    @test -s settings.json || cp settings.example.json settings.json

# 启动 headless 容器（后台运行）
up: ensure-mounts
    {{compose}} up -d

# 重新构建镜像并启动容器（代码改动后用这个）
rebuild: ensure-mounts
    {{compose}} up -d --build

# 重启容器（修改代理设置后需要重启才生效）
restart:
    {{compose}} restart

# 停止并移除容器
down:
    {{compose}} down

# 查看容器状态
ps:
    {{compose}} ps

# 实时查看容器日志（首次登录时的激活码也在这里）
logs:
    {{compose}} logs -f --tail 100

# 进入容器的 shell
shell:
    {{compose}} exec miner sh

# 构建 linux/amd64 Docker 镜像
build:
    docker buildx build --platform linux/amd64 -t twitchdropsminer-miner:amd64 --load .
