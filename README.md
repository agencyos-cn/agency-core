# AgencyOS - 面向物理世界的自主智能体操作系统

> Agentic Companion - 构建具备自主性、个性化和实体化的个人智能体伴侣

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/agencyos-cn/agentic-core)

## 🚀 项目愿景

AgencyOS 代表了从传统GUI操作系统向以自然语言交互（NUI）为主导、主动服务为特征的新一代操作系统演进。我们致力于构建真正的"Agentic Companion"——具备自主性、个性化和实体化的个人智能体伴侣。

### 核心理念：Agentic Computing（能动性计算）

AgencyOS 不仅仅是一个软件，而是对计算范式的重新思考。我们关注的核心问题是如何让智能体真正具备"能动性"（Agency），而非仅仅是被动响应的工具。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   交互层        │    │   运行时层        │    │   执行层        │
│                │    │                 │    │                │
│  • IM渠道       │    │  • 自主智能体内核  │    │  • 个人计算域    │
│  • 专用终端     │◄──►│  • 世界模型引擎   │◄──►│  • 可穿戴感知域  │
│  • Web控制台    │    │  • 安全内核       │    │  • 具身智能域    │
│                │    │  • 第三方生态集成  │    │  • 泛在物联域    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 架构特色：原生第三方生态集成

AgencyOS 现在原生集成了第三方模型和技能生态系统，包括：

- **模型生态**：支持 HuggingFace、魔搭(ModelScope)、OpenAI、Anthropic、百度千帆、阿里云百炼等主流提供商
- **技能生态**：通过 Dify 和 OpenClaw 无缝集成第三方技能市场
- **模型市场**：支持从各大模型平台直接引入预训练模型

## 🌍 全球模型生态集成

AgencyOS 原生支持以下全球主流模型生态：

### 模型提供商集成
- **Hugging Face**: 全球最大的开源模型社区
- **魔搭(ModelScope)**: 阿里巴巴开源模型平台，中文优化
- **OpenAI**: GPT系列模型
- **Anthropic**: Claude系列模型
- **火山方舟**: 字节跳动MaaS平台
- **百度千帆**: ERNIE Bot系列
- **阿里云百炼**: 通义千问系列
- **智谱AI**: ChatGLM、GLM系列
- **讯飞星火**: 讯飞大模型
- **月之暗面**: Moonshot系列

### 技能生态集成
- **Dify**: 集成其丰富的应用模板和工作流
- **OpenClaw**: 支持其IM渠道和技能市场
- **开放技能API**: 支持标准格式的第三方技能

## 🌟 核心特性

### 1. 混合架构 - 智能选择AI服务
- **本地规则匹配**（最快响应）
- **本地LLM**（隐私保护、简单请求）
- **第三方模型**（复杂对话、专业领域）
- **Dify/OpenClaw**（工作流处理、多渠道接入）

### 2. 第三方生态优先
- 默认优先使用第三方成熟模型和技能
- 本地模型作为隐私和离线场景的备选
- 支持动态切换不同提供商的服务

### 3. 模型提供商多样性
- 支持多种模型提供商的自动切换
- 智能降级机制确保服务可用性
- 无缝集成全球模型市场

### 4. 安全与隐私
- 内置安全内核，强制执行伦理规则
- 数据加密传输与存储
- 智能判断敏感信息不上云

## 📦 快速开始

### 环境要求
- Python 3.10+
- 8GB+ 内存（推荐）

### 安装
```bash
# 1. 克隆项目
git clone https://github.com/agencyos-cn/agentic-core.git
cd agentic-core

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install agencyos

# 4. 初始化配置
agencyos init my-workspace
cd my-workspace
```

### 配置第三方服务
```bash
# 编辑配置文件
cp config.example.json config.json
vim config.json  # 或使用你喜欢的编辑器
```

在配置文件中填入你需要的第三方服务API密钥：

```json
{
  "llm": {
    "default_provider": "openai",
    "providers": {
      "openai": {
        "api_key": "your-openai-api-key"
      },
      "anthropic": {
        "api_key": "your-anthropic-api-key"
      }
    }
  },
  "dify": {
    "api_base": "https://your-dify-instance/v1",
    "api_key": "your-dify-api-key",
    "app_id": "your-app-id"
  },
  "openclaw": {
    "api_base": "https://your-openclaw-instance/v1",
    "api_key": "your-openclaw-api-key",
    "app_id": "your-app-id"
  }
}
```

### 使用
```bash
# 运行系统
agencyos run "明天上午提醒我开会"

# 或在代码中使用
from agencyos import AgentRuntime, RuntimeContext

# 创建运行时实例
runtime = AgentRuntime()

# 创建上下文
context = RuntimeContext(
    user_id="user_001",
    session_id="session_001"
)

# 处理用户请求
result = await runtime.process("帮我查一下今天的天气", context)
print(result)
```

### Docker 部署
```bash
docker run -d \
  --name agencyos \
  -p 18789:18789 \
  -v ./workspace:/workspace \
  -e AGENCY_LLM_DEFAULT_PROVIDER=openai \
  -e OPENAI_API_KEY=your_openai_api_key \
  agencyos/agentic-core:latest
```

## 🏗️ 架构详解

### 混合AI服务架构

```python
# 意图解析优先级
1. 本地规则匹配（最快响应）
2. 本地LLM（隐私、简单请求）
3. 第三方模型提供商（复杂请求）
4. Dify（工作流、复杂业务）
5. OpenClaw（多渠道接入）
```

### 第三方生态集成策略

1. **模型提供商集成**：
   - 通过统一适配器接口集成不同提供商
   - 支持实时切换和智能降级
   - 提供模型性能监控和评估

2. **技能生态集成**：
   - 通过Dify和OpenClaw引入丰富技能
   - 支持第三方技能市场的动态同步
   - 提供技能冲突解决机制

3. **模型市场集成**：
   - 支持从主流平台引入预训练模型
   - 提供模型性能基准测试
   - 支持模型的在线评估和替换

## 🤝 贡献

我们欢迎任何形式的贡献：

1. **Star ⭐** 项目表示支持
2. **提交 Issue** 报告 bug 或提出新想法
3. **Pull Request** 帮助改进代码
4. **文档完善** 帮助改善文档

## 📄 许可证

Apache License 2.0 © [AgencyOS-CN](https://github.com/agencyos-cn)

## 🌐 更多信息

- [官方文档](docs/)
- [模型生态对比](docs/global-model-ecology.md)
- [社区论坛](https://community.agencyos.cn)
- [API 参考](https://api.agencyos.cn)

---

<div align="center">

**AgencyOS** - 构建未来的Agentic Companion

_让智能体真正拥有自主性_

</div>
```
# AgencyOS Backend Service

## 项目概述

AgencyOS 后端服务实现了完整的用户认证系统，包括用户注册、登录和JWT令牌管理功能。

## 功能特性

- **用户认证系统**：支持用户注册、登录和身份验证
- **JWT令牌管理**：安全的令牌生成和验证
- **API端点**：
  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/login` - 用户登录
  - `GET /api/auth/me` - 获取当前用户信息
  - `GET /api/health` - 健康检查
- **安全配置**：使用环境变量管理加密密钥

## 安全配置

本项目遵循加密密钥安全管理规范：
- 使用至少32字节（256位）的随机密钥
- 通过环境变量管理密钥，避免硬编码
- 配置文件已添加到.gitignore防止提交
- 不将加密密钥存储在数据库中

## 快速开始

### 1. 环境配置
```bash
# 复制环境配置文件
cp .env.example .env

# 生成安全密钥
python generate_key.py

# 将生成的密钥添加到 .env 文件中的 ENCRYPTION_KEY 变量
# 设置安全权限
chmod 600 .env
```

### 2. 依赖安装
```bash
pip install -r requirements.txt
```

### 3. 启动服务
```bash
python main.py --port 18789
```

### 4. 验证部署
```bash
# 验证环境配置
python verify_env.py

# 测试API
curl http://localhost:18789/api/health
```

## 项目结构

- [AUTH_IMPLEMENTATION.md](file:///Users/Joye/Sites/AgencyOs/agency-core/AUTH_IMPLEMENTATION.md) - 认证系统实现指南
- [KEY_SECURITY_GUIDE.md](file:///Users/Joye/Sites/AgencyOs/agency-core/KEY_SECURITY_GUIDE.md) - 密钥安全配置指南
- [DEPLOYMENT_GUIDE.md](file:///Users/Joye/Sites/AgencyOs/agency-core/DEPLOYMENT_GUIDE.md) - 部署指南
- [IMPLEMENTATION_COMPLETE.md](file:///Users/Joye/Sites/AgencyOs/agency-core/IMPLEMENTATION_COMPLETE.md) - 实施完成报告
- [init_database.sql](file:///Users/Joye/Sites/AgencyOs/agency-core/init_database.sql) - 数据库初始化脚本
- [generate_key.py](file:///Users/Joye/Sites/AgencyOs/agency-core/generate_key.py) - 密钥生成工具
- [verify_env.py](file:///Users/Joye/Sites/AgencyOs/agency-core/verify_env.py) - 环境变量验证脚本

## 前后端集成

前端项目 (agencyos-user-panel) 已配置为与此后端服务集成，通过环境变量 `VITE_API_BASE_URL` 指定API基础URL。

## 安全说明

- JWT令牌使用HS256算法加密
- 密码使用bcrypt进行哈希处理
- 所有API端点均受适当的身份验证和授权保护
- 实施了适当的错误处理和输入验证

## 维护

- 定期轮换加密密钥
- 监控API访问日志
- 定期更新依赖包
