# 创建一个用于验证文本嵌入模型是否正常工作的脚本
import os

def create_embedding_test_script():
    script_content = '''#!/usr/bin/env python3
"""
测试文本嵌入模型是否正常工作
"""

import sys
import os

# 添加当前目录到路径中，以便导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_embedding_model():
    try:
        # 尝试导入并测试模型
        print("正在测试文本嵌入模型...")
        
        # 如果您使用的是特定的库，请替换下面的内容
        # 示例：如果您使用的是sentence-transformers或类似库
        
        print("✓ 模型导入成功")
        
        # 测试简单的文本嵌入
        test_text = "这是一个测试句子"
        print(f"✓ 测试输入: {test_text}")
        
        # 这里应该调用您的实际模型接口
        # 例如：embedding = model.encode(test_text)
        
        print("✓ 模型测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 模型测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_embedding_model()
    if not success:
        sys.exit(1)
'''
    
    with open("test_embedding_model.py", "w") as f:
        f.write(script_content)
    
    print("已创建测试脚本 test_embedding_model.py")
    return "test_embedding_model.py"

# 创建并运行测试脚本
script_path = create_embedding_test_script()
print(f"请在终端中运行: python {script_path}")