# API 参考文档

*本文档将在代码实现后逐步完善*

## 核心 API

### AgentRuntime
- `__init__(config)`
- `process(user_input, context)`
- `create_agent(name, config)`

## 技能 API

- `Skill.register(name, function)`
- `Skill.execute(name, params)`

## 设备 API

- `Device.discover()`
- `Device.connect(device_id)`
- `Device.send_command(command)`