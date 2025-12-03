# ContainerWeb - 现代化容器管理平台

ContainerWeb 是一个基于 Python Flask 的现代化容器管理平台，支持统一管理 Docker、Podman、LXC 等多种容器引擎。

## 🚀 主要特性

### 多引擎支持
- **Docker**: 完整支持 Docker 容器管理
- **Podman**: 支持无守护进程的 Podman 容器
- **LXC**: 支持 Linux 容器技术

### 用户管理
- 多用户注册和登录
- 基于角色的权限控制
- 资源配额管理（容器数量、端口、存储、CPU、内存）
- 金币系统和设备权限分配

### 容器管理
- 容器生命周期管理（创建、启动、停止、删除）
- 端口映射和网络配置
- 卷挂载和环境变量设置
- 实时状态监控和日志查看

### 网络管理
- 自定义网络创建和管理
- 容器网络连接和断开
- 网络隔离和通信控制

### 模板系统
- 镜像模板管理
- Dockerfile 构建模板
- Docker Compose 模板支持
- 模板分享和使用统计

### Web 终端
- 实时 Web 终端访问
- 命令执行和文件管理
- 多用户终端会话支持

### 管理功能
- 系统设置和配置管理
- 用户权限和资源管理
- 引擎配置和监控
- 系统统计和监控

## 🛠️ 技术栈

### 后端
- **Flask**: Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **Flask-Login**: 用户认证
- **Flask-SocketIO**: WebSocket 实时通信
- **Docker SDK**: Docker API 客户端
- **Requests**: HTTP 客户端（Podman/LXC API）

### 前端
- **Bootstrap 5**: 响应式 UI 框架
- **Font Awesome**: 图标库
- **Socket.IO**: 实时通信客户端
- **Axios**: HTTP 客户端

### 数据库
- **SQLite**: 默认数据库（可配置其他数据库）

## 📦 安装部署

### 环境要求
- Python 3.8+
- 容器引擎（Docker/Podman/LXC）

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd ContainerWeb
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置文件
cp config.py.example config.py

# 编辑配置文件
vim config.py
```

4. **启动应用**
```bash
python run.py
```

5. **访问应用**
- 打开浏览器访问: http://localhost:5000
- 默认管理员账户: admin / admin123

### Docker 部署

```bash
# 构建镜像
docker build -t containerweb .

# 运行容器
docker run -d \
  --name containerweb \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containerweb
```

## 🔧 配置说明

### 基础配置
```python
# config.py
SECRET_KEY = 'your-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///containerweb.db'

# 默认用户限制
DEFAULT_MAX_CONTAINERS = 10
DEFAULT_MAX_PORTS = 20
DEFAULT_MAX_STORAGE = 10  # GB
DEFAULT_MAX_CPU = 2.0
DEFAULT_MAX_MEMORY = 4096  # MB
```

### 引擎配置
```python
# Docker 配置
DOCKER_HOST = 'unix://var/run/docker.sock'

# Podman 配置
PODMAN_HOST = 'unix://run/podman/podman.sock'

# 网络配置
NETWORK_SUBNET_BASE = '172.20.0.0/16'
```

## 📚 API 文档

### 容器管理 API

#### 获取容器列表
```http
GET /api/containers
```

#### 创建容器
```http
POST /api/containers
Content-Type: application/json

{
  "name": "my-container",
  "image": "nginx:latest",
  "port_mappings": {"80/tcp": "8080"},
  "environment_vars": {"ENV": "production"}
}
```

#### 启动容器
```http
POST /api/containers/{id}/start
```

#### 停止容器
```http
POST /api/containers/{id}/stop
```

### 网络管理 API

#### 创建网络
```http
POST /api/networks
Content-Type: application/json

{
  "name": "my-network",
  "driver": "bridge",
  "subnet": "172.20.1.0/24"
}
```

## 🎯 使用指南

### 用户操作

1. **注册账户**
   - 访问注册页面创建账户
   - 如需注册码请联系管理员

2. **创建容器**
   - 选择模板或自定义配置
   - 配置端口映射和环境变量
   - 启动容器并监控状态

3. **网络管理**
   - 创建自定义网络
   - 将容器连接到网络
   - 管理网络配置

4. **使用终端**
   - 通过 Web 终端访问容器
   - 执行命令和管理文件
   - 查看容器日志

### 管理员操作

1. **用户管理**
   - 管理用户账户和权限
   - 设置资源配额限制
   - 分配设备和GPU权限

2. **系统设置**
   - 配置注册策略
   - 设置系统资源限制
   - 管理引擎配置

3. **模板管理**
   - 创建和管理模板
   - 设置模板公开状态
   - 监控模板使用情况

## 🔒 安全特性

- 用户认证和会话管理
- 基于角色的访问控制
- 资源配额和权限限制
- 容器隔离和网络安全
- 审计日志和监控

## 🐛 故障排除

### 常见问题

1. **容器引擎连接失败**
   - 检查 Docker/Podman 服务状态
   - 验证 socket 文件权限
   - 确认引擎配置正确

2. **权限不足**
   - 检查用户权限设置
   - 验证资源配额限制
   - 确认容器引擎权限

3. **网络问题**
   - 检查网络配置
   - 验证端口映射
   - 确认防火墙设置

### 日志查看
```bash
# 查看应用日志
tail -f logs/containerweb.log

# 查看容器日志
docker logs containerweb
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：
- 提交 Issue
- 发送邮件
- 查看文档

---

**ContainerWeb** - 让容器管理更简单、更高效！