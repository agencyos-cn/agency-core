"""示例：如何使用角色系统创建专业AI助手团队"""

import asyncio
from src.core.runtime import AgentRuntime, RuntimeContext
from src.core.character import CharacterRoleType


async def main():
    """演示如何使用角色系统"""
    # 创建运行时实例
    runtime = AgentRuntime()
    await runtime.initialize()
    
    # 假设用户ID
    user_id = "user_12345"
    
    print("=== 欢迎使用多角色AI助手系统 ===\n")
    
    # 1. 创建教师角色
    print("1. 创建教师角色...")
    teacher = runtime.create_character(
        user_id=user_id,
        name="李老师",
        role_type="teacher",
        description="资深教育专家，擅长课程辅导和学习规划",
        expertise_areas=["数学", "物理", "化学"],
        personality_traits=["耐心", "细致", "循序渐进"],
        llm_config={
            "llm": {
                "local_model_enabled": False,
                "local_model_name": "llama2-education",  # 教育专用模型
                "providers": {
                    "openai": {
                        "api_key": "your-education-openai-key",
                        "model": "gpt-4-turbo-2024-04-09"
                    }
                }
            }
        }
    )
    print(f"   ✓ 成功创建教师角色: {teacher.name}\n")
    
    # 2. 创建律师角色
    print("2. 创建律师角色...")
    lawyer = runtime.create_character(
        user_id=user_id,
        name="王律师",
        role_type="lawyer",
        description="专业法律顾问，擅长民法和商法",
        expertise_areas=["合同法", "知识产权", "劳动法"],
        personality_traits=["严谨", "客观", "逻辑性强"],
        llm_config={
            "llm": {
                "local_model_enabled": False,
                "local_model_name": "llama2-law",  # 法律专用模型
                "providers": {
                    "anthropic": {
                        "api_key": "your-law-anthropic-key",
                        "model": "claude-3-opus-20240229"
                    }
                }
            }
        }
    )
    print(f"   ✓ 成功创建律师角色: {lawyer.name}\n")
    
    # 3. 创建金融顾问角色
    print("3. 创建金融顾问角色...")
    financial_advisor = runtime.create_character(
        user_id=user_id,
        name="张金融师",
        role_type="financial_advisor",
        description="资深投资顾问，擅长财富管理和风险控制",
        expertise_areas=["股票投资", "基金理财", "保险规划"],
        personality_traits=["稳健", "前瞻", "风险意识强"],
        llm_config={
            "llm": {
                "local_model_enabled": False,
                "local_model_name": "llama2-finance",  # 金融专用模型
                "providers": {
                    "google": {
                        "api_key": "your-finance-google-key",
                        "model": "gemini-pro"
                    }
                }
            }
        }
    )
    print(f"   ✓ 成功创建金融顾问角色: {financial_advisor.name}\n")
    
    # 4. 创建个人助理角色
    print("4. 创建个人助理角色...")
    assistant = runtime.create_character(
        user_id=user_id,
        name="小助手",
        role_type="assistant",
        description="智能家居控制和个人事务助理",
        expertise_areas=["设备控制", "日程管理", "生活助手"],
        personality_traits=["贴心", "高效", "细心"],
        llm_config={
            "llm": {
                "local_model_enabled": True,
                "local_model_name": "llama2-home",  # 本地家庭助手模型
                "local_api_base": "http://localhost:11434/v1"
            }
        }
    )
    print(f"   ✓ 成功创建个人助理角色: {assistant.name}\n")
    
    # 5. 列出用户的所有角色
    print("5. 您的角色团队:")
    characters = runtime.get_user_characters(user_id)
    for i, char in enumerate(characters, 1):
        print(f"   {i}. {char.name} ({char.role_type.value}) - {char.description}")
    print()
    
    # 6. 演示如何切换角色并处理请求
    print("6. 演示角色切换和请求处理:")
    
    # 切换到教师角色并提问
    print(f"   切换到 {teacher.name} 角色...")
    runtime.switch_character(user_id, teacher.id)
    
    context = RuntimeContext(
        user_id=user_id,
        session_id="session_teacher_1",
        character_id=teacher.id
    )
    
    result = await runtime.process("请帮我解释一下牛顿第二定律", context)
    print(f"   教师回答: {result['answer']}\n")
    
    # 切换到助理角色并提问
    print(f"   切换到 {assistant.name} 角色...")
    runtime.switch_character(user_id, assistant.id)
    
    context = RuntimeContext(
        user_id=user_id,
        session_id="session_assistant_1",
        character_id=assistant.id
    )
    
    result = await runtime.process("请打开客厅的灯", context)
    print(f"   助理响应: {result['answer']}\n")
    
    # 切换到金融顾问角色并提问
    print(f"   切换到 {financial_advisor.name} 角色...")
    runtime.switch_character(user_id, financial_advisor.id)
    
    context = RuntimeContext(
        user_id=user_id,
        session_id="session_financial_1",
        character_id=financial_advisor.id
    )
    
    result = await runtime.process("最近有什么值得关注的投资机会?", context)
    print(f"   金融顾问建议: {result['answer']}\n")
    
    print("=== 角色系统演示完成 ===")


if __name__ == "__main__":
    asyncio.run(main())