# Python包发布到PyPI详细指南

## 概述

本文档将详细介绍如何将Python项目打包并发布到PyPI（Python Package Index），使用户能够通过`pip install`命令安装您的包。

## 准备工作

### 1. 注册PyPI账户

1. 访问 [PyPI官方网站](https://pypi.org/account/register/)
2. 注册一个账户（或者使用Test PyPI进行测试发布：https://test.pypi.org/account/register/）
3. 记住您的用户名和密码，后续会用到

### 2. 安装必要的工具

```bash
pip install --upgrade pip setuptools wheel twine
```

## 项目结构准备

### 1. 标准Python包结构

```
agency-core/
├── src/
│   └── agencyos/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── main.py
│       └── cli.py
├── pyproject.toml
├── setup.py (可选，推荐使用pyproject.toml)
├── README.md
├── LICENSE
└── tests/
    └── test_agencyos.py
```

### 2. 创建pyproject.toml文件

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "agencyos"
dynamic = ["version"]
description = "AgencyOS - 面向物理世界的自主智能体操作系统"
readme = "README.md"
authors = [
    {name = "AgencyOS Team", email = "contact@agencyos.local"}
]
license = {text = "Apache Software License"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
    "requests>=2.25.0",
    "pydantic>=1.8.0",
    "sqlalchemy>=1.4.0",
    "pyjwt>=2.0.0",
    "bcrypt>=3.2.0",
    "aiohttp>=3.8.0",
    "websockets>=10.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "black>=21.0",
    "flake8>=3.8",
    "mypy>=0.910"
]

[project.urls]
Homepage = "https://github.com/agencyos-cn/agency-core"
Repository = "https://github.com/agencyos-cn/agency-core"
Documentation = "https://docs.agencyos.cn"

[project.scripts]
agencyos = "agencyos.cli:main"
```

### 3. 在__init__.py中定义版本

在`src/agencyos/__init__.py`中添加版本信息：

```python
try:
    from importlib.metadata import version
except ImportError:
    # Python < 3.8
    from importlib_metadata import version

__version__ = version("agencyos")
```

## 打包过程

### 1. 构建包

```bash
# 清除旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
python -m build
```

这将创建两个文件：
- `dist/agencyos-x.x.x.tar.gz` - 源码分发包
- `dist/agencyos-x.x.x-py3-none-any.whl` - wheel分发包

### 2. 验证包

```bash
# 检查包的有效性
twine check dist/*
```

## 发布到PyPI

### 1. 发布到Test PyPI（推荐先测试）

```bash
# 上传到Test PyPI
twine upload --repository testpypi dist/*
```

### 2. 从Test PyPI测试安装

```bash
pip install --index-url https://test.pypi.org/simple/ agencyos
```

### 3. 发布到正式PyPI

```bash
# 上传到正式PyPI
twine upload dist/*
```

## 使用API令牌（推荐）

### 1. 生成API令牌

1. 登录PyPI账户
2. 进入"Account Settings" > "API tokens"
3. 生成新的API令牌
4. 保存令牌（只能查看一次）

### 2. 使用.templaterc或.netrc文件

创建`.netrc`文件（Linux/Mac）或`_netrc`文件（Windows）：

```
machine upload.pypi.org
  login __token__
  password pypi-your-api-token-here
```

## 自动化发布流程

### 1. 使用GitHub Actions

创建`.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### 2. 配置GitHub Secrets

在GitHub仓库的Settings > Secrets and variables > Actions中添加`PYPI_API_TOKEN`。

## 版本管理

### 1. 语义化版本控制

- MAJOR.MINOR.PATCH (例如: 1.0.0)
- MAJOR: 不兼容的API更改
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的问题修复

### 2. 使用setuptools_scm自动版本管理

在[pyproject.toml](file:///Users/Joye/Sites/AgencyOs/agency-core/pyproject.toml)中启用setuptools_scm：

```toml
[project]
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/agencyos/_version.py"
```

## 常见问题及解决方案

### 1. 包名已被占用

- 在PyPI上搜索包名是否已被占用
- 选择一个独特的包名
- 建议使用`agencyos-core`或`agencyos-cli`等变体

### 2. 上传失败

- 检查API令牌是否有效
- 确保包名和版本号唯一
- 验证包格式是否正确

### 3. 依赖问题

- 仔细列出所有依赖项
- 指定版本范围（例如：`requests>=2.25.0,<3.0.0`）
- 测试在干净环境中能否安装

## 安全注意事项

1. **永远不要在代码中硬编码敏感信息**
2. **使用API令牌而不是用户名/密码**
3. **定期轮换API令牌**
4. **检查依赖的安全漏洞**

## 维护和更新

### 1. 发布新版本

```bash
# 更新代码
git add .
git commit -m "Release version x.x.x"
git tag -a vx.x.x -m "Version x.x.x"
git push origin main
git push origin vx.x.x

# 构建并发布
python -m build
twine upload dist/*
```

### 2. 撤销发布

注意：PyPI不允许删除已发布的版本，但可以隐藏。因此发布前务必在Test PyPI上测试。

## 验证发布成功

发布后，用户应该能够：

```bash
# 从PyPI安装
pip install agencyos

# 使用命令行工具
agencyos init my-workspace
```

## 附录

### 参考资源

- [Python打包权威指南](https://packaging.python.org/en/latest/)
- [PyPA示例项目](https://github.com/pypa/sampleproject)
- [Twine文档](https://twine.readthedocs.io/)
- [setuptools文档](https://setuptools.pypa.io/)

### 检查清单

- [ ] 项目结构正确
- [ ] [pyproject.toml](file:///Users/Joye/Sites/AgencyOs/agency-core/pyproject.toml)配置完整
- [ ] README.md和LICENSE文件存在
- [ ] 依赖列表准确
- [ ] 版本号正确
- [ ] 在Test PyPI上测试安装
- [ ] 从Test PyPI成功安装
- [ ] API令牌安全存储
- [ ] CI/CD流程配置完成