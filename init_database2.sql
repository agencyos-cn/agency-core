-- =====================================================
-- AgencyOS 数据库建表语句（混合策略版）
-- 版本: 2.1
-- 说明: 平台元数据使用业务主键，用户数据使用自增ID
-- 所有字段语法已修正，适配 MySQL 5.7
-- =====================================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS agencyos_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE agencyos_db;

-- =====================================================
-- 1. 平台层表结构（使用业务主键）
-- =====================================================

-- 1.1 角色模板表 - 平台预定义的智能体角色模板
CREATE TABLE platform_role_templates (
    id VARCHAR(64) PRIMARY KEY COMMENT '模板ID，如 tmpl_teacher_001',
    name VARCHAR(100) NOT NULL COMMENT '角色模板名称，如"金牌数学老师"',
    category VARCHAR(50) NOT NULL COMMENT '分类，如 education/financial/legal',
    description TEXT COMMENT '特长描述，简要说明角色擅长什么',
    system_prompt TEXT COMMENT '默认系统提示词，定义角色人格和行为',
    default_model VARCHAR(100) COMMENT '推荐使用的模型，如 qwen-max',
    default_temperature DECIMAL(2,1) DEFAULT 0.7 COMMENT '默认温度参数，0-2之间',
    default_memory_rounds INT DEFAULT 10 COMMENT '默认记忆轮数',
    avatar_url VARCHAR(500) COMMENT '默认头像URL',
    is_active BOOLEAN DEFAULT true COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category (category) COMMENT '按分类查询索引',
    INDEX idx_active (is_active) COMMENT '按启用状态查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台角色模板表';

-- 1.2 统一知识库表（平台知识库 + 用户知识库合并）- 平台库使用业务主键
CREATE TABLE knowledge_bases (
    id VARCHAR(64) PRIMARY KEY COMMENT '知识库ID，平台库如 kb_platform_math_001，用户库如 kb_user_123_001',
    name VARCHAR(200) NOT NULL COMMENT '知识库名称',
    description TEXT COMMENT '知识库描述',
    owner_type ENUM('platform', 'user') NOT NULL COMMENT '所属类型：platform-平台库，user-用户库',
    owner_id BIGINT COMMENT '所有者ID，当owner_type=user时，指向users表ID；当owner_type=platform时可为空',
    file_url VARCHAR(500) COMMENT '文件存储地址',
    vector_config JSON COMMENT '向量化配置，如分块大小、重叠等',
    is_public BOOLEAN DEFAULT false COMMENT '是否公开（仅平台库可设为true）',
    status ENUM('active', 'processing', 'failed') DEFAULT 'active' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_owner (owner_type, owner_id) COMMENT '按所有者查询索引',
    INDEX idx_public (is_public) COMMENT '公开库查询索引',
    INDEX idx_status (status) COMMENT '状态查询索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='统一知识库表（平台库+用户库）';

-- 1.3 平台技能表
CREATE TABLE platform_skills (
    id VARCHAR(64) PRIMARY KEY COMMENT '技能ID，如 skill_weather_001',
    name VARCHAR(100) NOT NULL COMMENT '技能名称',
    description TEXT COMMENT '技能描述',
    mcp_service_id VARCHAR(100) COMMENT 'MCP服务ID，如 mcp://weather/query',
    input_schema JSON COMMENT '输入参数定义',
    output_schema JSON COMMENT '输出参数定义',
    is_public BOOLEAN DEFAULT true COMMENT '是否公开',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_public (is_public) COMMENT '按公开状态查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台技能表';

-- 1.4 平台MCP服务表
CREATE TABLE platform_mcp_services (
    id VARCHAR(64) PRIMARY KEY COMMENT 'MCP服务ID，如 mcp_weather_001',
    name VARCHAR(100) NOT NULL COMMENT '服务名称',
    provider VARCHAR(50) COMMENT '提供商，如 阿里云百炼',
    endpoint VARCHAR(500) COMMENT '调用地址',
    auth_type ENUM('api_key', 'oauth', 'none') DEFAULT 'none' COMMENT '认证类型',
    config_template JSON COMMENT '配置模板，如 {"api_key": ""}',
    is_public BOOLEAN DEFAULT true COMMENT '是否公开',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_public (is_public) COMMENT '按公开状态查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台MCP服务表';

-- 1.5 模板关联知识库表
CREATE TABLE platform_template_knowledge (
    template_id VARCHAR(64) NOT NULL COMMENT '模板ID',
    knowledge_base_id VARCHAR(64) NOT NULL COMMENT '知识库ID',
    is_default BOOLEAN DEFAULT true COMMENT '是否默认启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (template_id, knowledge_base_id),
    FOREIGN KEY (template_id) REFERENCES platform_role_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    INDEX idx_knowledge (knowledge_base_id) COMMENT '知识库关联索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模板关联知识库表';

-- 1.6 模板关联技能表
CREATE TABLE platform_template_skills (
    template_id VARCHAR(64) NOT NULL COMMENT '模板ID',
    skill_id VARCHAR(64) NOT NULL COMMENT '技能ID',
    is_default BOOLEAN DEFAULT true COMMENT '是否默认启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (template_id, skill_id),
    FOREIGN KEY (template_id) REFERENCES platform_role_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES platform_skills(id) ON DELETE CASCADE,
    INDEX idx_skill (skill_id) COMMENT '技能关联索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模板关联技能表';

-- 1.7 模板关联MCP服务表
CREATE TABLE platform_template_mcp (
    template_id VARCHAR(64) NOT NULL COMMENT '模板ID',
    mcp_service_id VARCHAR(64) NOT NULL COMMENT 'MCP服务ID',
    is_default BOOLEAN DEFAULT true COMMENT '是否默认启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (template_id, mcp_service_id),
    FOREIGN KEY (template_id) REFERENCES platform_role_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (mcp_service_id) REFERENCES platform_mcp_services(id) ON DELETE CASCADE,
    INDEX idx_mcp (mcp_service_id) COMMENT 'MCP服务关联索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模板关联MCP服务表';


-- =====================================================
-- 2. 用户层表结构（使用自增ID）
-- =====================================================

-- 2.1 用户表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    email VARCHAR(255) UNIQUE NOT NULL COMMENT '登录邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(100) COMMENT '用户昵称',
    avatar_url VARCHAR(500) COMMENT '用户头像',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active' COMMENT '账号状态',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_email (email) COMMENT '邮箱登录索引',
    INDEX idx_status (status) COMMENT '状态查询索引',
    INDEX idx_created (created_at) COMMENT '注册时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2.2 用户智能体实例表
CREATE TABLE user_agents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '智能体实例ID',
    user_id BIGINT NOT NULL COMMENT '所属用户ID',
    template_id VARCHAR(64) NOT NULL COMMENT '基于哪个模板创建',
    name VARCHAR(100) NOT NULL COMMENT '用户自定义名称',
    avatar_url VARCHAR(500) COMMENT '自定义头像（覆盖模板）',
    custom_system_prompt TEXT COMMENT '自定义提示词（覆盖模板）',
    selected_model VARCHAR(100) COMMENT '用户选择的模型（覆盖模板）',
    temperature DECIMAL(2,1) DEFAULT 0.7 COMMENT '温度设置（覆盖模板）',
    memory_rounds INT DEFAULT 10 COMMENT '短期记忆轮数',
    long_term_memory TEXT COMMENT '长期记忆内容（用户画像）',
    memory_ttl INT DEFAULT 30 COMMENT '短期记忆保留天数',
    is_active BOOLEAN DEFAULT true COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES platform_role_templates(id),
    INDEX idx_user (user_id) COMMENT '按用户查询索引',
    INDEX idx_template (template_id) COMMENT '按模板查询索引',
    INDEX idx_active (is_active) COMMENT '启用状态索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户智能体实例表';

-- 2.3 用户智能体关联知识库表（支持平台库+用户库同时关联）
CREATE TABLE user_agent_knowledge (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
    agent_id BIGINT NOT NULL COMMENT '智能体ID',
    knowledge_base_id VARCHAR(64) NOT NULL COMMENT '知识库ID（统一指向knowledge_bases表）',
    is_enabled BOOLEAN DEFAULT true COMMENT '是否启用',
    enable_order INT DEFAULT 0 COMMENT '启用顺序（数值越小优先级越高）',
    custom_name VARCHAR(200) COMMENT '用户自定义显示名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (agent_id) REFERENCES user_agents(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    UNIQUE KEY unique_agent_knowledge (agent_id, knowledge_base_id) COMMENT '一个智能体不能重复关联同一个知识库',
    INDEX idx_agent_enabled (agent_id, is_enabled, enable_order) COMMENT '按智能体查询启用的知识库（带排序）',
    INDEX idx_knowledge (knowledge_base_id) COMMENT '按知识库查询使用情况'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户智能体关联知识库表';

-- 2.4 用户智能体关联技能表（用户开关）
CREATE TABLE user_agent_skills (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
    agent_id BIGINT NOT NULL COMMENT '智能体ID',
    skill_id VARCHAR(64) NOT NULL COMMENT '技能ID（平台技能）',
    is_enabled BOOLEAN DEFAULT true COMMENT '是否启用',
    custom_config JSON COMMENT '用户自定义配置（如API Key）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (agent_id) REFERENCES user_agents(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES platform_skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_agent_skill (agent_id, skill_id) COMMENT '一个智能体不能重复关联同一个技能',
    INDEX idx_agent_enabled (agent_id, is_enabled) COMMENT '按智能体查询启用的技能'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户智能体关联技能表';

-- 2.5 用户MCP服务订阅表（用户自己的MCP配置）
CREATE TABLE user_mcp_subscriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '订阅ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    mcp_service_id VARCHAR(64) NOT NULL COMMENT 'MCP服务ID',
    config JSON COMMENT '用户填写的配置（如API Key）',
    status ENUM('active', 'disabled') DEFAULT 'active' COMMENT '订阅状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (mcp_service_id) REFERENCES platform_mcp_services(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_mcp (user_id, mcp_service_id) COMMENT '一个用户不能重复订阅同一个MCP服务',
    INDEX idx_user (user_id) COMMENT '按用户查询订阅',
    INDEX idx_status (status) COMMENT '状态查询索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户MCP服务订阅表';

-- 2.6 用户智能体关联MCP服务表（关联订阅）
CREATE TABLE user_agent_mcp (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
    agent_id BIGINT NOT NULL COMMENT '智能体ID',
    mcp_subscription_id BIGINT NOT NULL COMMENT 'MCP订阅ID',
    is_enabled BOOLEAN DEFAULT true COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (agent_id) REFERENCES user_agents(id) ON DELETE CASCADE,
    FOREIGN KEY (mcp_subscription_id) REFERENCES user_mcp_subscriptions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_agent_mcp (agent_id, mcp_subscription_id) COMMENT '一个智能体不能重复关联同一个MCP订阅',
    INDEX idx_agent_enabled (agent_id, is_enabled) COMMENT '按智能体查询启用的MCP服务'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户智能体关联MCP服务表';


-- =====================================================
-- 3. 设备集成相关表（使用自增ID）
-- =====================================================

-- 3.1 用户设备表（OpenClaw/机器人/智能家居等）
CREATE TABLE user_devices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '设备ID',
    user_id BIGINT NOT NULL COMMENT '所属用户ID',
    device_type ENUM('openclaw', 'robot', 'home_assistant', 'mijia', 'huawei') NOT NULL COMMENT '设备类型',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_model VARCHAR(100) COMMENT '设备型号',
    bind_status ENUM('pending', 'online', 'offline', 'error') DEFAULT 'pending' COMMENT '绑定状态',
    bind_token VARCHAR(64) COMMENT '临时绑定令牌（用于反向绑定）',
    token_expire TIMESTAMP NULL COMMENT '令牌过期时间',
    connection_info JSON COMMENT '连接信息（IP、端口等）',
    capabilities JSON COMMENT '设备能力列表',
    last_active TIMESTAMP NULL COMMENT '最后活跃时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id) COMMENT '按用户查询',
    INDEX idx_status (bind_status) COMMENT '状态查询索引',
    INDEX idx_token (bind_token) COMMENT '绑定令牌查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户设备表';

-- 3.2 智能体可访问的设备权限表
CREATE TABLE agent_device_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '权限ID',
    agent_id BIGINT NOT NULL COMMENT '智能体ID',
    device_id BIGINT NOT NULL COMMENT '设备ID',
    permissions JSON COMMENT '权限配置（如可执行的命令列表）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (agent_id) REFERENCES user_agents(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES user_devices(id) ON DELETE CASCADE,
    UNIQUE KEY unique_agent_device (agent_id, device_id) COMMENT '一个智能体对一个设备只有一条权限记录',
    INDEX idx_agent (agent_id) COMMENT '按智能体查询权限'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='智能体设备权限表';


-- =====================================================
-- 4. 对话历史与记忆表（使用自增ID）
-- =====================================================

-- 4.1 对话会话表
CREATE TABLE conversations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '会话ID',
    agent_id BIGINT NOT NULL COMMENT '智能体ID',
    title VARCHAR(200) COMMENT '会话标题',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (agent_id) REFERENCES user_agents(id) ON DELETE CASCADE,
    INDEX idx_agent (agent_id) COMMENT '按智能体查询会话',
    INDEX idx_created (created_at) COMMENT '按创建时间查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话会话表';

-- 4.2 对话消息表
CREATE TABLE messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    conversation_id BIGINT NOT NULL COMMENT '所属会话ID',
    role ENUM('user', 'assistant', 'system') NOT NULL COMMENT '消息角色',
    content TEXT NOT NULL COMMENT '消息内容',
    metadata JSON COMMENT '元数据（如引用来源、技能调用等）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation (conversation_id, created_at) COMMENT '按会话查询消息'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话消息表';


-- =====================================================
-- 5. 系统管理表
-- =====================================================

-- 5.1 系统配置表（存储平台级配置）
CREATE TABLE system_config (
    config_key VARCHAR(100) PRIMARY KEY COMMENT '配置键',
    config_value JSON NOT NULL COMMENT '配置值',
    description VARCHAR(500) COMMENT '配置说明',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 5.2 操作日志表
CREATE TABLE operation_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    user_id BIGINT COMMENT '操作用户ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50) COMMENT '操作对象类型',
    target_id VARCHAR(64) COMMENT '操作对象ID（可能是业务ID或自增ID，存字符串统一处理）',
    details JSON COMMENT '操作详情',
    ip_address VARCHAR(45) COMMENT '操作IP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user (user_id) COMMENT '按用户查询',
    INDEX idx_time (created_at) COMMENT '按时间查询',
    INDEX idx_target (target_type, target_id) COMMENT '按对象查询'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- =====================================================
-- 初始化一些基础数据（可选）
-- =====================================================

-- 插入系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES 
('platform_settings', '{"max_memory_rounds":30, "default_model":"qwen-max"}', '平台全局设置'),
('mcp_gateway', '{"endpoint":"https://mcp.aliyun.com", "version":"1.0"}', 'MCP网关配置');

-- 插入示例角色模板
INSERT INTO platform_role_templates (id, name, category, description, system_prompt, default_model, default_temperature, avatar_url) VALUES
('tmpl_teacher_001', '金牌数学老师', 'education', '擅长K12数学辅导，耐心引导式教学', '你是一个耐心的数学老师，擅长用启发式提问帮助学生理解数学概念...', 'qwen-max', 0.7, '/avatars/teacher.png'),
('tmpl_finance_001', '资深金融分析师', 'financial', '擅长投资分析、财报解读', '你是一个专业的金融分析师，对市场趋势有独到见解...', 'deepseek-coder', 0.5, '/avatars/analyst.png'),
('tmpl_life_001', '生活助理', 'life', '日程管理、生活建议、设备控制', '你是用户的生活助理，细心体贴，帮助用户安排日常生活...', 'qwen-turbo', 0.8, '/avatars/assistant.png');

-- 插入示例平台技能
INSERT INTO platform_skills (id, name, description, mcp_service_id, input_schema, output_schema) VALUES
('skill_weather_001', '天气查询', '查询指定城市的实时天气', 'mcp://weather/query', '{"city": "string"}', '{"temperature": "number", "condition": "string"}'),
('skill_calc_001', '数学计算', '执行数学公式计算', 'mcp://calc/math', '{"expression": "string"}', '{"result": "string"}'),
('skill_map_001', '地图导航', '查询路线和位置', 'mcp://map/navigate', '{"origin": "string", "dest": "string"}', '{"distance": "number", "duration": "number"}');

-- 插入示例平台MCP服务
INSERT INTO platform_mcp_services (id, name, provider, endpoint, auth_type, config_template, is_public) VALUES
('mcp_weather_001', '高德天气', '阿里云百炼', 'https://mcp.aliyun.com/weather', 'api_key', '{"api_key": ""}', true),
('mcp_map_001', '高德地图', '阿里云百炼', 'https://mcp.aliyun.com/map', 'api_key', '{"api_key": ""}', true),
('mcp_notion_001', 'Notion', '社区', 'https://mcp.notion.com', 'oauth', '{"client_id": "", "client_secret": ""}', true);

-- 插入示例平台知识库
INSERT INTO knowledge_bases (id, name, description, owner_type, is_public, status) VALUES
('kb_platform_math_001', '高中数学题库', '包含历年高考真题和解析', 'platform', true, 'active'),
('kb_platform_physics_001', '物理公式大全', '涵盖初高中物理公式', 'platform', true, 'active'),
('kb_platform_finance_001', '投资入门指南', '基础投资知识', 'platform', true, 'active');

-- 插入示例模板关联
INSERT INTO platform_template_knowledge (template_id, knowledge_base_id) VALUES
('tmpl_teacher_001', 'kb_platform_math_001'),
('tmpl_teacher_001', 'kb_platform_physics_001'),
('tmpl_finance_001', 'kb_platform_finance_001');

INSERT INTO platform_template_skills (template_id, skill_id) VALUES
('tmpl_life_001', 'skill_weather_001'),
('tmpl_life_001', 'skill_map_001'),
('tmpl_teacher_001', 'skill_calc_001');

INSERT INTO platform_template_mcp (template_id, mcp_service_id) VALUES
('tmpl_life_001', 'mcp_weather_001'),
('tmpl_life_001', 'mcp_map_001');

-- 下面2个字段不是必须的——你完全可以在Qdrant的payload中存储MySQL的主键ID来关联。
-- 给 user_agents 增加向量ID字段（可选，用于追踪）
ALTER TABLE user_agents ADD COLUMN vector_id VARCHAR(64) COMMENT 'Qdrant中的向量ID，用于关联';

-- 给 messages 表增加向量ID（如果需要按消息召回记忆）
ALTER TABLE messages ADD COLUMN vector_id VARCHAR(64) COMMENT '消息向量ID';