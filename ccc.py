from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import uuid
from datetime import datetime
import os
import logging
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 数据文件路径
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
DOCUMENTS_FILE = os.path.join(DATA_DIR, "documents.json")
AUDIT_LOGS_FILE = os.path.join(DATA_DIR, "audit_logs.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

def load_data(file_path, default_data):
    """从文件加载数据，如果文件不存在则使用默认数据"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载数据文件 {file_path} 失败: {e}")
    return default_data.copy() if hasattr(default_data, 'copy') else default_data

def save_data(file_path, data):
    """保存数据到文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存数据到 {file_path} 失败: {e}")
        return False

# 默认用户数据
DEFAULT_USERS = [
    # 2个特殊用户
    {"id": "1", "username": "special_user1", "password": "special_password1", "permission": "special", "can_upgrade": True},
    {"id": "2", "username": "special_user2", "password": "special_password2", "permission": "special", "can_upgrade": True},
    
    # 3个绝密用户
    {"id": "3", "username": "ts_user1", "password": "ts_password1", "permission": "top_secret", "can_upgrade": True},
    {"id": "4", "username": "ts_user2", "password": "ts_password2", "permission": "top_secret", "can_upgrade": True},
    {"id": "5", "username": "ts_user3", "password": "ts_password3", "permission": "top_secret", "can_upgrade": True},
    
    # 12个机密用户
    {"id": "6", "username": "c_user1", "password": "c_password1", "permission": "confidential", "can_upgrade": False},
    {"id": "7", "username": "c_user2", "password": "c_password2", "permission": "confidential", "can_upgrade": False},
    {"id": "8", "username": "c_user3", "password": "c_password3", "permission": "confidential", "can_upgrade": False},
    {"id": "9", "username": "c_user4", "password": "c_password4", "permission": "confidential", "can_upgrade": False},
    {"id": "10", "username": "c_user5", "password": "c_password5", "permission": "confidential", "can_upgrade": False},
    {"id": "11", "username": "c_user6", "password": "c_password6", "permission": "confidential", "can_upgrade": False},
    {"id": "12", "username": "c_user7", "password": "c_password7", "permission": "confidential", "can_upgrade": False},
    {"id": "13", "username": "c_user8", "password": "c_password8", "permission": "confidential", "can_upgrade": False},
    {"id": "14", "username": "c_user9", "password": "c_password9", "permission": "confidential", "can_upgrade": False},
    {"id": "15", "username": "c_user10", "password": "c_password10", "permission": "confidential", "can_upgrade": False},
    {"id": "16", "username": "c_user11", "password": "c_password11", "permission": "confidential", "can_upgrade": False},
    {"id": "17", "username": "c_user12", "password": "c_password12", "permission": "confidential", "can_upgrade": False},
    
    # 9个普通用户
    {"id": "18", "username": "normal_user1", "password": "normal_password1", "permission": "normal", "can_upgrade": False},
    {"id": "19", "username": "normal_user2", "password": "normal_password2", "permission": "normal", "can_upgrade": False},
    {"id": "20", "username": "normal_user3", "password": "normal_password3", "permission": "normal", "can_upgrade": False},
    {"id": "21", "username": "normal_user4", "password": "normal_password4", "permission": "normal", "can_upgrade": False},
    {"id": "22", "username": "normal_user5", "password": "normal_password5", "permission": "normal", "can_upgrade": False},
    {"id": "23", "username": "normal_user6", "password": "normal_password6", "permission": "normal", "can_upgrade": False},
    {"id": "24", "username": "normal_user7", "password": "normal_password7", "permission": "normal", "can_upgrade": False},
    {"id": "25", "username": "normal_user8", "password": "normal_password8", "permission": "normal", "can_upgrade": False},
    {"id": "26", "username": "normal_user9", "password": "normal_password9", "permission": "normal", "can_upgrade": False}
]

# 默认文档数据
DEFAULT_DOCUMENTS = [
    {
        "id": "1",
        "filename": "普通通知.txt",
        "permission": "normal", 
        "content": "这是一份普通通知文档，所有用户都可以查看。\n\n主要内容：\n1. 系统使用说明\n2. 权限管理规则\n3. 安全操作指南",
        "created_at": "2024-01-01",
        "created_by": "system"
    },
    {
        "id": "2",
        "filename": "部门会议纪要.docx", 
        "permission": "confidential",
        "content": "机密会议纪要内容，包含重要商业决策。\n\n会议主题：2024年战略规划\n参会人员：管理层全体\n决议事项：\n1. 新产品开发计划\n2. 市场拓展策略\n3. 预算分配方案",
        "created_at": "2024-01-01",
        "created_by": "system"
    },
    {
        "id": "3",
        "filename": "公司战略规划.pdf",
        "permission": "top_secret", 
        "content": "绝密战略规划文档，包含公司未来5年发展规划。\n\n核心内容：\n1. 技术研发路线图\n2. 市场竞争分析\n3. 投资并购计划\n4. 风险控制策略\n5. 应急预案",
        "created_at": "2024-01-01", 
        "created_by": "system"
    },
    {
        "id": "4",
        "filename": "国家安全级别文档.sec",
        "permission": "special", 
        "content": "特殊权限文档，包含最高级别机密信息。\n\n访问限制：\n- 仅限特殊权限用户访问\n- 包含国家级安全信息\n- 严格审计追踪\n\n内容分类：\n1. 国家安全战略\n2. 关键基础设施保护\n3. 紧急响应预案",
        "created_at": "2024-01-01", 
        "created_by": "system"
    },
    {
        "id": "5",
        "filename": "技术研发白皮书.pdf",
        "permission": "confidential",
        "content": "机密技术研发文档。\n\n研发方向：\n1. 人工智能算法优化\n2. 量子计算研究\n3. 网络安全防护\n4. 数据加密技术",
        "created_at": "2024-01-01",
        "created_by": "system"
    }
]

# 加载数据
users = load_data(USERS_FILE, DEFAULT_USERS)
documents = load_data(DOCUMENTS_FILE, DEFAULT_DOCUMENTS)
audit_logs = load_data(AUDIT_LOGS_FILE, [])

# 会话管理（内存中，重启会丢失）
user_sessions = {}

def create_session(user):
    """创建用户会话"""
    session_id = str(uuid.uuid4())
    user_sessions[session_id] = {
        'user_id': user['id'],
        'username': user['username'],
        'permission': user['permission'],
        'can_upgrade': user.get('can_upgrade', False),
        'created_at': datetime.now().isoformat()
    }
    return session_id

def get_session(session_id):
    """获取会话信息"""
    return user_sessions.get(session_id)

def get_permission_level(permission):
    """获取权限等级数值"""
    levels = {"normal": 1, "confidential": 2, "top_secret": 3, "special": 4}
    return levels.get(permission, 0)

def get_permission_text(permission):
    """获取权限文本描述"""
    texts = {
        "normal": "普通",
        "confidential": "机密", 
        "top_secret": "绝密",
        "special": "特殊"
    }
    return texts.get(permission, permission)

def hash_password(password):
    """哈希密码（可选，当前系统使用明文）"""
    return hashlib.sha256(password.encode()).hexdigest()

def log_audit(username, action, details):
    """记录审计日志并保存到文件"""
    audit_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "action": action,
        "details": details,
        "ip": request.remote_addr if request else "0.0.0.0"
    }
    audit_logs.append(audit_entry)
    
    # 只保留最近1000条日志
    if len(audit_logs) > 1000:
        audit_logs.pop(0)
    
    # 异步保存审计日志
    save_data(AUDIT_LOGS_FILE, audit_logs)
    
    logger.info(f"审计日志: {username} - {action}")

def save_users():
    """保存用户数据"""
    return save_data(USERS_FILE, users)

def save_documents():
    """保存文档数据"""
    return save_data(DOCUMENTS_FILE, documents)

# ==================== API路由 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "安全文档库系统",
        "version": "3.1",
        "user_count": len(users),
        "document_count": len(documents),
        "audit_log_count": len(audit_logs),
        "data_persistence": True,
        "permission_levels": ["特殊", "绝密", "机密", "普通"]
    })

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400

        user = next((u for u in users if u['username'] == username), None)
        
        if not user:
            return jsonify({"error": "用户名或密码错误"}), 401

        # 直接比较明文密码
        if user['password'] != password:
            return jsonify({"error": "用户名或密码错误"}), 401

        # 创建会话
        session_id = create_session(user)

        # 记录登录日志
        log_audit(username, "用户登录", "成功登录系统")

        return jsonify({
            "session_id": session_id,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "permission": user['permission'],
                "can_upgrade": user.get('can_upgrade', False)
            }
        })
    except Exception as e:
        logger.error(f"登录处理异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/emergency-upgrade', methods=['POST'])
def emergency_upgrade():
    """紧急权限升级"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        emergency_password = data.get('emergency_password')
        
        if emergency_password != 'hello':
            return jsonify({"error": "紧急升级密码错误"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        # 找到用户并升级权限
        user = next((u for u in users if u['id'] == session['user_id']), None)
        if not user:
            return jsonify({"error": "用户不存在"}), 404

        old_permission = user['permission']
        user['permission'] = 'special'  # 紧急升级到特殊权限
        user['can_upgrade'] = True

        # 更新会话
        session['permission'] = 'special'
        session['can_upgrade'] = True

        # 保存用户数据
        save_users()

        log_audit(session['username'], "紧急权限升级", f"从 {old_permission} 升级到 special")

        return jsonify({
            "message": "紧急权限升级成功！您现在拥有特殊权限。",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "permission": user['permission'],
                "can_upgrade": user['can_upgrade']
            }
        })
    except Exception as e:
        logger.error(f"紧急升级处理异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """获取文档列表（根据权限过滤）"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        user_level = get_permission_level(session['permission'])
        
        accessible_docs = [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "permission": doc["permission"],
                "permission_text": get_permission_text(doc["permission"]),
                "created_at": doc["created_at"],
                "created_by": doc["created_by"]
            }
            for doc in documents 
            if user_level >= get_permission_level(doc['permission'])
        ]

        return jsonify(accessible_docs)
    except Exception as e:
        logger.error(f"获取文档列表异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document_content(document_id):
    """获取单个文档内容"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        document = next((doc for doc in documents if doc['id'] == document_id), None)
        if not document:
            return jsonify({"error": "文档不存在"}), 404

        user_level = get_permission_level(session['permission'])
        doc_level = get_permission_level(document['permission'])
        
        if user_level < doc_level:
            return jsonify({"error": "权限不足"}), 403

        log_audit(session['username'], "查看文档", f"查看文档: {document['filename']}")

        return jsonify(document)
    except Exception as e:
        logger.error(f"获取文档内容异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """删除文档"""
    try:
        global documents  # 将 global 声明移到函数最开头
        
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        # 找到要删除的文档
        document = next((doc for doc in documents if doc['id'] == document_id), None)
        if not document:
            return jsonify({"error": "文档不存在"}), 404

        # 权限检查：只有文档创建者或特殊权限用户可以删除
        user_can_delete = (
            session['username'] == document['created_by'] or  # 文档创建者
            session['permission'] == 'special' or  # 特殊权限用户
            (session['permission'] == 'top_secret' and document['permission'] != 'special')  # 绝密用户可以删除非特殊文档
        )
        
        if not user_can_delete:
            return jsonify({"error": "权限不足，无法删除此文档"}), 403

        # 从文档列表中移除
        original_length = len(documents)
        documents = [doc for doc in documents if doc['id'] != document_id]
        
        if len(documents) == original_length:
            return jsonify({"error": "删除失败，文档不存在"}), 404

        # 保存文档数据
        save_documents()

        log_audit(session['username'], "删除文档", f"删除文档: {document['filename']} (ID: {document_id})")

        return jsonify({
            "message": "文档删除成功",
            "deleted_document": {
                "id": document_id,
                "filename": document['filename']
            }
        })
    except Exception as e:
        logger.error(f"删除文档异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/documents', methods=['POST'])
def add_document():
    """添加新文档"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        # 只有特殊和绝密用户可以添加文档
        if session['permission'] not in ['special', 'top_secret']:
            return jsonify({"error": "权限不足，只有特殊和绝密用户可以添加文档"}), 403

        data = request.get_json()
        if not data.get('filename') or not data.get('content'):
            return jsonify({"error": "文档名称和内容不能为空"}), 400

        # 特殊用户可创建所有权限文档，绝密用户只能创建机密和普通文档
        user_permission = session['permission']
        doc_permission = data.get('permission', 'normal')
        
        if user_permission == 'top_secret' and doc_permission in ['special', 'top_secret']:
            return jsonify({"error": "绝密用户只能创建机密和普通权限文档"}), 403

        new_doc = {
            "id": str(uuid.uuid4()),
            "filename": data['filename'],
            "permission": doc_permission,
            "content": data['content'],
            "created_at": datetime.now().strftime('%Y-%m-%d'),
            "created_by": session['username']
        }

        documents.append(new_doc)

        # 保存文档数据
        save_documents()

        log_audit(session['username'], "添加文档", f"添加文档: {data['filename']}, 权限: {doc_permission}")

        return jsonify(new_doc)
    except Exception as e:
        logger.error(f"添加文档异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表（特殊权限用户可见）"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        if not session.get('can_upgrade', False):
            return jsonify({"error": "权限不足"}), 403

        other_users = [
            {
                "id": u["id"],
                "username": u["username"],
                "permission": u["permission"],
                "permission_text": get_permission_text(u["permission"]),
                "can_upgrade": u.get("can_upgrade", False)
            }
            for u in users if u['id'] != session['user_id']
        ]
        return jsonify(other_users)
    except Exception as e:
        logger.error(f"获取用户列表异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/users/<user_id>/permission', methods=['PUT'])
def update_user_permission(user_id):
    """更新用户权限"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        if not session.get('can_upgrade', False):
            return jsonify({"error": "权限不足"}), 403

        data = request.get_json()
        new_permission = data.get('permission')
        
        if new_permission not in ['normal', 'confidential', 'top_secret', 'special']:
            return jsonify({"error": "无效的权限等级"}), 400

        target_user = next((u for u in users if u['id'] == user_id), None)
        if not target_user:
            return jsonify({"error": "用户不存在"}), 404

        old_permission = target_user['permission']
        target_user['permission'] = new_permission
        
        # 特殊权限用户才能管理其他用户权限
        if new_permission == 'special':
            target_user['can_upgrade'] = True
        else:
            target_user['can_upgrade'] = False

        # 保存用户数据
        save_users()

        log_audit(session['username'], "权限变更", f"将用户 {target_user['username']} 从 {old_permission} 改为 {new_permission}")

        return jsonify({
            "id": target_user['id'],
            "username": target_user['username'],
            "permission": target_user['permission'],
            "permission_text": get_permission_text(target_user['permission']),
            "can_upgrade": target_user.get('can_upgrade', False)
        })
    except Exception as e:
        logger.error(f"更新用户权限异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/audit-logs', methods=['GET'])
def get_audit_logs():
    """获取审计日志"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        if session['permission'] not in ['special', 'top_secret']:
            return jsonify({"error": "权限不足"}), 403

        return jsonify(audit_logs[-100:])  # 返回最近100条日志
    except Exception as e:
        logger.error(f"获取审计日志异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """修改用户密码"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([old_password, new_password, confirm_password]):
            return jsonify({"error": "所有字段都必须填写"}), 400

        if new_password != confirm_password:
            return jsonify({"error": "新密码和确认密码不匹配"}), 400

        if len(new_password) < 6:
            return jsonify({"error": "新密码至少需要6个字符"}), 400

        # 找到当前用户
        user = next((u for u in users if u['id'] == session['user_id']), None)
        if not user:
            return jsonify({"error": "用户不存在"}), 404

        # 验证旧密码
        if user['password'] != old_password:
            return jsonify({"error": "旧密码不正确"}), 401

        # 更新密码
        user['password'] = new_password
        
        # 保存用户数据
        save_users()

        log_audit(session['username'], "更改密码", "密码已更新")

        return jsonify({
            "message": "密码修改成功"
        })
    except Exception as e:
        logger.error(f"修改密码异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/backup', methods=['GET'])
def backup_data():
    """备份所有数据（特殊权限用户可用）"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        if session['permission'] != 'special':
            return jsonify({"error": "需要特殊权限"}), 403

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "users": users,
            "documents": documents,
            "audit_logs": audit_logs[-500:]  # 只备份最近500条日志
        }

        # 保存备份文件
        backup_file = os.path.join(DATA_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        log_audit(session['username'], "数据备份", f"创建备份文件: {backup_file}")

        return jsonify({
            "message": "数据备份成功",
            "backup_file": backup_file,
            "backup_time": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"数据备份异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计信息"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({"error": "未授权"}), 401

        session = get_session(session_id)
        if not session:
            return jsonify({"error": "会话无效"}), 401

        # 统计各权限用户数量
        permission_counts = {
            "special": 0,
            "top_secret": 0,
            "confidential": 0,
            "normal": 0
        }
        
        for user in users:
            if user['permission'] in permission_counts:
                permission_counts[user['permission']] += 1

        # 统计各权限文档数量
        doc_counts = {
            "special": 0,
            "top_secret": 0,
            "confidential": 0,
            "normal": 0
        }
        
        for doc in documents:
            if doc['permission'] in doc_counts:
                doc_counts[doc['permission']] += 1

        return jsonify({
            "user_stats": {
                "total": len(users),
                "by_permission": permission_counts
            },
            "document_stats": {
                "total": len(documents),
                "by_permission": doc_counts
            },
            "audit_logs": len(audit_logs),
            "data_files": {
                "users": os.path.getsize(USERS_FILE) if os.path.exists(USERS_FILE) else 0,
                "documents": os.path.getsize(DOCUMENTS_FILE) if os.path.exists(DOCUMENTS_FILE) else 0,
                "audit_logs": os.path.getsize(AUDIT_LOGS_FILE) if os.path.exists(AUDIT_LOGS_FILE) else 0
            }
        })
    except Exception as e:
        logger.error(f"获取统计信息异常: {e}")
        return jsonify({"error": "服务器内部错误"}), 500

# ==================== 前端页面路由 ====================

@app.route('/')
def index():
    """返回前端页面"""
    try:
        # 尝试返回前端页面
        return send_file('index.html')
    except:
        # 如果前端文件不存在，返回简单的信息页面
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>安全文档库管理系统</title>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                h1 { color: #333; text-align: center; }
                .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .endpoints { background: #f0f0f0; padding: 15px; border-radius: 5px; }
                .permission-levels { display: flex; justify-content: space-between; margin: 20px 0; }
                .level { text-align: center; padding: 10px; border-radius: 5px; flex: 1; margin: 0 5px; }
                .special { background: #8e44ad; color: white; }
                .top-secret { background: #c0392b; color: white; }
                .confidential { background: #f39c12; color: white; }
                .normal { background: #27ae60; color: white; }
                .api-list { background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0; }
                .api-list code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
                .data-info { background: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>安全文档库管理系统 v3.1</h1>
                <div class="data-info">
                    <h3>✅ 数据持久化已启用</h3>
                    <p>数据已保存到 <strong>data/</strong> 目录</p>
                    <p>服务器重启后数据不会丢失</p>
                </div>
                
                <div class="info">
                    <p>服务器运行在: <strong>localhost:5000</strong></p>
                    <p>数据目录: <strong>data/</strong> (包含 users.json, documents.json, audit_logs.json)</p>
                    <p>✅ 后端API服务正常运行中</p>
                </div>
                
                <div class="permission-levels">
                    <div class="level special">
                        <h3>特殊权限</h3>
                        <p>2个用户</p>
                        <p>最高访问级别</p>
                    </div>
                    <div class="level top-secret">
                        <h3>绝密权限</h3>
                        <p>3个用户</p>
                        <p>高级访问权限</p>
                    </div>
                    <div class="level confidential">
                        <h3>机密权限</h3>
                        <p>12个用户</p>
                        <p>中级访问权限</p>
                    </div>
                    <div class="level normal">
                        <h3>普通权限</h3>
                        <p>9个用户</p>
                        <p>基础访问权限</p>
                    </div>
                </div>
                
                <h3>可用API端点:</h3>
                <div class="api-list">
                    <p><strong>健康检查:</strong> <code>GET /api/health</code></p>
                    <p><strong>用户登录:</strong> <code>POST /api/login</code></p>
                    <p><strong>获取文档列表:</strong> <code>GET /api/documents</code></p>
                    <p><strong>查看文档内容:</strong> <code>GET /api/documents/&lt;id&gt;</code></p>
                    <p><strong>删除文档:</strong> <code>DELETE /api/documents/&lt;id&gt;</code></p>
                    <p><strong>添加文档:</strong> <code>POST /api/documents</code></p>
                    <p><strong>获取用户列表:</strong> <code>GET /api/users</code></p>
                    <p><strong>更新用户权限:</strong> <code>PUT /api/users/&lt;id&gt;/permission</code></p>
                    <p><strong>修改密码:</strong> <code>POST /api/change-password</code></p>
                    <p><strong>紧急权限升级:</strong> <code>POST /api/emergency-upgrade</code></p>
                    <p><strong>审计日志:</strong> <code>GET /api/audit-logs</code></p>
                    <p><strong>系统统计:</strong> <code>GET /api/stats</code></p>
                    <p><strong>数据备份:</strong> <code>GET /api/backup</code> (特殊权限)</p>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
                    <h3>测试账户:</h3>
                    <p><strong>特殊用户:</strong> special_user1 / special_password1</p>
                    <p><strong>绝密用户:</strong> ts_user1 / ts_password1</p>
                    <p><strong>机密用户:</strong> c_user1 / c_password1</p>
                    <p><strong>普通用户:</strong> normal_user1 / normal_password1</p>
                    <p><strong>紧急升级密码:</strong> hello</p>
                </div>
                
                <div style="margin-top: 20px; color: #666; font-size: 14px;">
                    <p>当前版本包含功能：登录认证、权限管理、文档CRUD、用户管理、审计日志、紧急升级、数据持久化</p>
                    <p>数据保存位置: data/users.json, data/documents.json, data/audit_logs.json</p>
                </div>
            </div>
        </body>
        </html>
        """

# ==================== 启动应用 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("安全文档库系统 v3.1 (数据持久化版) 启动中...")
    print("=" * 60)
    print(f"📍 本地访问: http://localhost:5000")
    print(f"📁 数据目录: {DATA_DIR}/")
    print(f"📊 用户数据: {len(users)} 个用户")
    print(f"📄 文档数据: {len(documents)} 个文档") 
    print(f"📋 审计日志: {len(audit_logs)} 条记录")
    print("=" * 60)
    print("权限等级 (从高到低):")
    print("🔮 特殊权限: 2个用户 (最高权限)")
    print("🔴 绝密权限: 3个用户") 
    print("🟡 机密权限: 12个用户")
    print("🟢 普通权限: 9个用户")
    print("=" * 60)
    print("数据持久化:")
    print("✓ 用户数据自动保存到 users.json")
    print("✓ 文档数据自动保存到 documents.json")
    print("✓ 审计日志自动保存到 audit_logs.json")
    print("✓ 服务器重启后数据不会丢失")
    print("=" * 60)
    print("API功能:")
    print("✓ 用户登录认证")
    print("✓ 文档增删改查 (持久化)")
    print("✓ 用户权限管理 (持久化)")
    print("✓ 审计日志记录 (持久化)")
    print("✓ 紧急权限升级 (持久化)")
    print("✓ 密码修改功能 (持久化)")
    print("✓ 数据备份功能")
    print("✓ 系统统计信息")
    print("=" * 60)
    print("启动完成，等待请求...")
    print("=" * 60)
    
    # 监听所有接口
    app.run(host='0.0.0.0', port=5000, debug=False)
