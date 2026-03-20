# AgencyOS 安装指南

## 系统要求

- Python 3.8 或更高版本
- 操作系统：macOS/Linux/Windows
- 推荐内存：8GB+（运行本地模型需要更多）

## 基础安装

### 1. 克隆仓库

```bash
git clone https://github.com/agencyos-cn/agency-core.git
cd agency-core
```

### 2. 创建虚拟环境（推荐）
#### 这样可以确保您的项目依赖关系相互隔离，避免版本冲突问题。在您的项目 agency-core 中使用虚拟环境是一个最佳实践。
```bash
# 创建名称为 "venv" 的虚拟环境
python -m venv venv
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 完成开发后停用虚拟环境
deactivate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

或者直接安装：

```bash
pip install agencyos # 暂不支持
```

### 4. 初始化工作区

```bash
agencyos init my-workspace
cd my-workspace
```

## 从源码安装

```bash
git clone https://github.com/agencyos-cn/agency-core.git
cd agency-core

# 文档位于 docs/ 目录
# 查看完整文档：docs/README.md
```

## 开发安装

如果您计划对 AgencyOS 进行开发，请使用以下命令：

```bash
git clone https://github.com/agencyos-cn/agency-core.git
cd agency-core
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
# 停用虚拟环境
deactivate
# 安装依赖
pip install -e .
```

其中 `-e` 表示可编辑安装，这样可以直接修改源码而不需要重新安装。

## Docker 安装

如果您更喜欢使用 Docker 进行部署：

```bash
docker run -d \
  --name agencyos \
  -p 18789:18789 \
  -v ./workspace:/workspace \
  agencyos/agency-core:latest
```

## 验证安装

安装完成后，您可以运行以下命令验证安装是否成功：

```bash
agencyos --version
```

或者运行一个简单的测试：

```bash
agencyos run "Hello, AgencyOS!"
```

## 故障排除

### 问题：Python 版本过低

如果遇到 Python 版本问题，请确保安装了 Python 3.8 或更高版本：

```bash
python --version
# 或
python3 --version
```

### 问题：权限不足

如果在安装过程中遇到权限问题，可以尝试使用 `--user` 参数：

```bash
pip install --user agencyos
```

### 问题：依赖冲突

如果遇到依赖冲突，建议使用虚拟环境隔离安装：

```bash
python -m venv fresh_env
source fresh_env/bin/activate
pip install agencyos
```

## 下一步

安装完成后，您可以参考 [README.md](../docs/README.md) 文件了解如何开始使用 AgencyOS。