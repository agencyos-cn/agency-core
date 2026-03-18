# AgencyOS 部署指南

## 概述
本文档介绍如何在生产或开发环境中部署AgencyOS后端服务。

## 环境配置

### 1. 环境变量配置
1. 复制示例配置文件：
   ```bash
   cp .env.example .env
   ```

2. 生成并配置安全密钥：
   ```bash
   python generate_key.py
   # 将生成的密钥填入 .env 文件中的 ENCRYPTION_KEY 变量
   ```

3. 设置配置文件权限：
   ```bash
   chmod 600 .env
   ```

### 2. 验证环境配置
运行验证脚本检查配置是否正确：
```bash
python verify_env.py
```

## 启动服务

### 开发环境启动
```bash
cd /Users/Joye/Sites/AgencyOs/agency-core
python main.py --port 18790
```

### 生产环境启动（推荐使用进程管理器）
```bash
# 使用 nohup 后台运行
nohup python main.py --host 0.0.0.0 --port 18789 > server.log 2>&1 &

# 或使用 systemd 服务（Linux）
# 创建 /etc/systemd/system/agencyos.service 文件
```

## API 功能验证

服务启动后，可通过以下端点验证功能：

1. **健康检查**：
   ```bash
   curl http://localhost:18789/api/health
   ```

2. **用户注册**：
   ```bash
   curl -X POST http://localhost:18789/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name":"测试用户","email":"test@example.com","password":"password123"}'
   ```

3. **用户登录**：
   ```bash
   curl -X POST http://localhost:18789/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

4. **获取当前用户**：
   ```bash
   TOKEN="从登录响应中获取的令牌"
   curl -X GET http://localhost:18789/api/auth/me \
     -H "Authorization: Bearer $TOKEN"
   ```

## 安全注意事项

1. **密钥管理**：
   - 确保使用至少32字符的强密钥
   - 定期轮换加密密钥
   - 不要将 .env 文件提交到版本控制系统

2. **访问控制**：
   - 限制对服务器的访问权限
   - 使用防火墙限制不必要的端口访问
   - 启用速率限制防止暴力攻击

3. **监控和日志**：
   - 定期检查服务器日志
   - 监控异常登录尝试
   - 设置警报机制

## 故障排除

### 常见问题

1. **服务无法启动**：
   - 检查端口是否被占用
   - 确认依赖包已安装：`pip install -r requirements.txt`

2. **环境变量未加载**：
   - 验证 .env 文件位置是否正确
   - 确认变量格式是否正确

3. **API返回500错误**：
   - 检查服务日志获取详细错误信息
   - 验证请求格式是否正确

### 验证部署
运行以下命令验证所有功能是否正常：
```bash
python verify_env.py
```

## 维护任务

1. **定期备份**：定期备份配置文件和重要数据
2. **密钥轮换**：建议每3-6个月更换一次加密密钥
3. **依赖更新**：定期更新依赖包以获得安全补丁
4. **日志清理**：定期清理旧的日志文件