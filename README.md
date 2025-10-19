# 高并发秒杀系统演示项目 (High-Concurrency Flash Sale System Demo)

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.119-blue?logo=fastapi)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-blue?logo=apachekafka)
![Redis](https://img.shields.io/badge/Redis-red?logo=redis)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

这是一个基于 Python 技术栈实现的高并发秒杀（Flash Sale）场景的演示项目。它通过一系列精心设计的策略，展示了如何构建一个能够应对瞬时高流量、防止超卖并保证系统稳定性的后端服务。

## 核心理念与架构

秒杀场景的核心挑战在于：如何在极短时间内处理海量请求，同时确保库存的精确性和系统的可用性。本项目采用了以下架构来应对这些挑战：

```
                               +-----------------+      +------------------+
                               |                 |      |                  |
[用户请求] --> [FastAPI API] --> | L1 本地缓存熔断 | -->  | L2 Redis 缓存熔断 |
                               | (cachetools)    |      | (Redis)          |
                               +-----------------+      +------------------+
                                       |
                                       | (库存充足)
                                       v
                               +-----------------+      +------------------+      +-----------------+
                               |                  |      |                  |      |                 |
                               | Redis 原子扣减库存 | -->  | Kafka 消息队列   | -->  | Consumer 服务   | --> [数据库]
                               | (Lua or INCR)    |      | (aiokafka)       |      | (异步处理订单)    |
                               +-----------------+      +------------------+      +-----------------+
                                       |
                                       | (库存不足)
                                       v
                               +-----------------+
                               |                 |
                               | 写入 Redis 售罄标志 |
                               | (全局熔断)        |
                               +-----------------+
```

### 关键设计

1.  **多级缓存与熔断**：
    *   **L1 本地缓存** (`cachetools`): 在应用实例内存中缓存商品售罄状态。这是最快的检查层，能阻断绝大部分无效请求，避免网络开销。
    *   **L2 Redis 缓存** (`Redis`): 分布式缓存层，作为全局售罄状态的权威来源。当库存耗尽时，会设置一个带 TTL 的售罄标志，作为分布式环境下的主要熔断器。

2.  **库存原子操作**：
    *   利用 Redis 的单线程模型和原子操作（如 `INCRBY` / `DECRBY`）来预扣库存，从根本上解决了并发环境下的数据竞争问题，确保不会超卖。

3.  **异步化处理**：
    *   抢购请求在通过缓存和库存检查后，并不会立即写入数据库。而是将订单信息作为消息发送到 **Apache Kafka** 消息队列。
    *   独立的 **Consumer 服务** 订阅 Kafka 主题，异步地、批量地处理订单，并将其持久化到数据库。这种方式极大地提高了 API 的响应速度和吞吐量，将前端请求与后端慢速 I/O 操作解耦。

4.  **容器化部署**：
    *   整个项目（包括 API 服务、Consumer 服务、Redis、Kafka）都通过 **Docker** 和 **Docker Compose** 进行管理，实现了开发、测试和生产环境的一致性与一键部署。

## 技术栈

*   **Web 框架**: [FastAPI](https://fastapi.tiangolo.com/) - 高性能的异步 Python Web 框架。
*   **消息队列**: [Apache Kafka](https://kafka.apache.org/) - 用于订单消息的异步处理和系统解耦。
*   **缓存/原子操作**: [Redis](https://redis.io/) - 用于库存管理、分布式锁和 L2 售罄状态缓存。
*   **本地缓存**: [cachetools](https://github.com/tkem/cachetools) - 用于实现 L1 内存级缓存。
*   **异步 Kafka 客户端**: [aiokafka](https://github.com/aio-libs/aiokafka) - 用于与 Kafka 进行异步通信。
*   **负载测试**: [Locust](https://locust.io/) - 用于模拟大量用户并发请求。
*   **容器化**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) - 用于环境隔离和一键部署。
*   **包管理/运行器**: [uv](https://github.com/astral-sh/uv) - 极速的 Python 包管理器。

## 本地开发与测试指南

请确保您的本地环境已安装 `Git` 和 `Docker` / `Docker Compose`。

### 步骤 1: 启动所有服务

首先，克隆本项目，然后使用 Docker Compose 一键启动所有依赖的基础设施和服务（Redis, Kafka, API, Consumer）。

```bash
# 克隆项目
git clone <your-repository-url>
cd sec-kill-project-demo

# 以后台模式启动所有容器
docker compose -p flash-purchase up -d --build
```

该命令会完成以下工作：
*   构建 API 和 Consumer 服务的 Docker 镜像。
*   启动 Redis 容器。
*   启动 Kafka 容器。
*   启动 API 服务容器，并监听 `8000` 端口。
*   启动 Consumer 服务容器。

您可以通过 `docker-compose ps` 查看所有服务的运行状态。

### 步骤 2: 初始化商品库存

在进行秒杀测试前，需要向 Redis 中填充模拟的商品及其库存数据。项目中的 `mock_products.py` 脚本用于此目的。

项目在启动时会自动初始化商品库存，但您可以手动执行以下命令来初始化商品库存。

*注意：此步骤为模拟操作，实际项目中应有专门的后台管理功能来设置商品信息。*

### 步骤 3: 模拟高并发秒杀请求

本项目使用 `Locust` 来模拟大量用户并发抢购。

1.  **安装 Locust**:
    如果您的本地 Python 环境没有安装 Locust，请先安装。推荐使用 `uv` 或 `pip`。
    ```bash
    # 使用 uv
    uv pip install locust

    # 或者使用 pip
    pip install locust
    ```

2.  **运行负载测试**:
    执行以下命令启动 Locust，它会使用 `scripts/mock_user_orders.py` 文件中定义的测试场景。
    ```bash
    locust -f scripts/mock_user_orders.py
    ```

3.  **开始测试**:
    *   在浏览器中打开 Locust 的 Web UI: `http://localhost:8089`。
    *   输入您希望模拟的并发用户数（例如 `1000`）和每秒生成的虚拟用户数（例如 `100`）。
    *   点击 "Start swarming" 开始发起大量请求。

### 步骤 4: 观察和验证

1.  **API 文档**:
    *   在浏览器中访问 `http://localhost:8000/docs`，可以查看由 FastAPI 自动生成的 Swagger UI 接口文档。

2.  **服务日志**:
    *   通过 `docker-compose logs -f` 命令可以实时查看 API 和 Consumer 服务的日志输出，观察订单处理流程、库存扣减情况和售罄信息的打印。
    ```bash
    # 实时跟踪 api 和 consumer 服务的日志
    docker-compose logs -f api consumer
    ```

3.  **Redis 数据**:
    *   您可以连接到 Redis 实例，检查商品库存 (`item:<product_id>:stock`) 和售罄标志 (`item:<product_id>:sold_out`) 的变化。
    ```bash
    # 进入 Redis 容器的 CLI
    docker-compose exec redis redis-cli

    # 查看某个商品的库存 (例如 product_id=10000000)
    GET item:10000000:stock
    ```

## 项目结构

```
.
├── app/                # 核心应用代码
│   ├── consumer/       # Kafka 消费者逻辑
│   ├── core/           # 配置和核心设置
│   ├── mock/           # 数据模拟脚本
│   ├── models/         # 数据传输对象 (DTO) 和响应模型
│   ├── rest/           # FastAPI 相关代码 (API端点、生命周期事件)
│   └── services/       # 业务服务层 (秒杀逻辑、Redis/Kafka服务)
├── docker-compose.yml  # Docker 服务编排文件
├── Dockerfile          # 应用的 Docker 镜像定义
├── main.py             # FastAPI 应用主入口
├── consumer.py         # Kafka 消费者主入口
├── scripts/            # 外部脚本 (如 Locust 负载测试)
└── pyproject.toml      # 项目依赖和配置 (PEP 621)
```

## 贡献

欢迎对本项目进行贡献！如果您有任何改进建议或发现 Bug，请随时提交 Pull Request 或创建 Issue。

## 许可证

本项目采用 [MIT License](LICENSE) 开源。
