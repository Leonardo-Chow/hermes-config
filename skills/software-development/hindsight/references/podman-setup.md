# Podman on macOS in China

本机通过 **Podman** 代替 Docker Desktop，原因：Docker Desktop 安装程序被 GFW 阻断，Colima 的 GitHub 镜像下载同样超时。Podman 的方案如下：

## 装了什么

```bash
brew install podman docker docker-compose
```

- Podman 5.8.2 — 容器引擎（无 daemon 进程）
- Docker CLI 29.4.3 — 通过 `DOCKER_HOST` 连接 Podman
- Docker Compose — 通过 Podman 插件运行

## 初始化

```bash
# 创建 VM（首次）
podman machine init --cpus 4 --memory 8192

# 启动 VM
podman machine start

# 验证
podman info
docker run --rm hello-world
```

## DOCKER_HOST 配置

Podman 的 API socket 路径是动态的，已写入 `~/.zshrc`：

```bash
export DOCKER_HOST="unix:///var/folders/9f/z0hvvddn6_j1s9s912j3qjc40000gn/T/podman/podman-machine-default-api.sock"
```

如需用默认 `/var/run/docker.sock`，需安装 podman-mac-helper（需 sudo）：

```bash
sudo /opt/homebrew/Cellar/podman/5.8.2/bin/podman-mac-helper install
podman machine stop; podman machine start
```

## Docker Hub 镜像加速

因 Docker Hub 在中国访问慢，配置了 DaoCloud 镜像：

```bash
podman machine ssh -- "sudo tee /etc/containers/registries.conf.d/mirrors.conf" << 'EOF'
unqualified-search-registries = ["docker.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry.mirror]]
location = "docker.m.daocloud.io"
EOF
```

修改后无需重启 Machine，直接 pull 镜像时自动使用镜像。

## 日常维护

```bash
# 启动 VM（开机后）
podman machine start

# 停止 VM
podman machine stop

# 查看状态
podman machine list

# 查看资源使用
podman stats

# 调大 VM 资源配置
podman machine stop
podman machine set --cpus 6 --memory 12288
podman machine start
```

## 根用户模式（rootful）

Podman Machine 默认在 **rootless** 模式下运行。部分需要绑定低端口（<1024）或依赖标准 Docker socket 的工具需要 **rootful** 模式：

```bash
# 切换到 rootful
podman machine stop
podman machine set --rootful
podman machine start

# 切换回 rootless
podman machine stop
podman machine set --rootful=false
podman machine start
```

Rootful 模式下 `-p` 端口映射转发机制不同（通过 gvproxy），但应用本身的端口绑定行为不变。

## 网络与端口转发

Podman Machine 内部网络架构（rootful 模式）：

```
macOS  ←[gvproxy]→  Podman VM (192.168.127.2)
                      └─ conmon → 容器 (10.88.0.x)
```

关键排查点：
- `curl localhost:<port>` 连接建立后立刻 `connection reset by peer` → **大概率是容器内应用未就绪**（如还在下载模型），不是端口转发问题
- 确诊方法：`docker logs -f <container>` 查看应用日志是否有错误或仍在启动中
- 如果是内存/磁盘问题，用 `podman machine ssh -- free -h && df -h` 检查 VM 资源

## 连接 Podman Machine 内部

```bash
# SSH 进入 VM
podman machine ssh

# 或直接执行命令
podman machine ssh -- curl -s http://127.0.0.1:8888/health

# 通过 SSH 端口转发（备选方案）
ssh -i ~/.local/share/containers/podman/machine/machine \
  -L 18888:127.0.0.1:8888 \
  -N root@127.0.0.1 -p $(podman system connection list --format "{{.URI}}" | grep root | sed 's/.*://' | sed 's/\/run.*//')
```

## 故障排查
|------|------|
| `docker run` 超时 | Podman Machine 未启动：`podman machine start` |
| 镜像拉取失败 | 检查 ghcr.io / docker.io 可达性；用 `curl -sI https://docker.m.daocloud.io` 验证镜像 |
| 端口占用 | `podman ps` 查看已运行的容器，`podman stop <id>` 停止冲突容器 |
| Docker Compose 报错 | 确保 `~/.docker/config.json` 有 cliPluginsExtraDirs 指向 `/opt/homebrew/lib/docker/cli-plugins` |
| 容器网络不通 | 检查 Podman Machine 网络模式（默认 rootless，端口映射工作正常） |

## 对比其他方案

| 方案 | 结论 |
|------|------|
| Docker Desktop | `brew install --cask docker` 下载超时 |
| Colima | GitHub 镜像下载超时（`gh-proxy.com` 不支持 colima 内部 HTTP 客户端） |
| OrbStack | 付费软件，未测试 |
| **Podman ✓** | **可用。quay.io 镜像可达，无需付费** |
