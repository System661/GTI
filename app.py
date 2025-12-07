"""
Railway部署包装器
这个文件导入您的原始ccc.py应用
完全不需要修改ccc.py源代码
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # 导入您的原始应用
    from ccc import app
    
    print("✅ 成功导入ccc.py中的Flask应用")
    print(f"📦 应用名称: {app.name}")
    
except ImportError as e:
    print(f"❌ 导入ccc.py失败: {e}")
    print("💡 请确保:")
    print("   1. ccc.py在同一目录")
    print("   2. ccc.py中有 app = Flask(__name__)")
    
    # 创建临时应用作为备选
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return """
        <h1>⚠️ 导入原应用失败</h1>
        <p>请检查ccc.py文件是否存在且包含Flask应用。</p>
        """

# Railway会自动使用这个app对象
# 不需要修改ccc.py的任何代码！
