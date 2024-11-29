from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 用于session加密

# 数据文件路径
USERS_FILE = 'users.json'
VEHICLES_FILE = 'vehicles.json'

# 读取用户数据
def load_users():
    if not os.path.exists(USERS_FILE):
        return {"guests": [], "staff": []}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存用户数据
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# 生成新的嘉宾ID
def generate_guest_id(users):
    guests = users.get('guests', [])
    if not guests:
        return 'G001'
    last_id = max(int(guest['guest_id'][1:]) for guest in guests)
    return f'G{str(last_id + 1).zfill(3)}'

# 读取用车数据
def load_vehicles():
    try:
        with open(VEHICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"vehicle_arrangements": []}

# 保存用车数据
def save_vehicles(data):
    with open(VEHICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 生成新的用车ID
def generate_vehicle_id():
    vehicles = load_vehicles()
    arrangements = vehicles['vehicle_arrangements']
    if not arrangements:
        return 'V001'
    last_id = max(int(v['id'][1:]) for v in arrangements)
    return f'V{str(last_id + 1).zfill(3)}'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'staff':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')

# 验证用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()
    
    if data['userType'] == 'staff':
        # 验证工作人员登录
        staff = next((s for s in users['staff'] 
                     if s['username'] == data['username'] 
                     and s['password'] == data['password']), None)
        if staff:
            # 将工作人员信息存储在session中
            session['user_type'] = 'staff'
            session['user_id'] = staff['username']
            session['role'] = staff['role']
            
            return jsonify({
                "success": True,
                "user_type": "staff",
                "role": staff['role'],
                "name": staff['name']
            })
    else:
        # 验证嘉宾登录
        guest = next((g for g in users['guests'] 
                     if g['username'] == data['username'] 
                     and g['password'] == data['password']), None)
        if guest:
            # 将嘉宾信息存储在session中
            session['user_type'] = 'guest'
            session['user_id'] = guest['guest_id']
            
            return jsonify({
                "success": True,
                "user_type": "guest",
                "guest_id": guest['guest_id'],
                "name": guest['name']
            })
    
    # 登录失败
    return jsonify({
        "success": False,
        "message": "用户名或密码错误"
    }), 401
    

# 路由：获取所有嘉宾
@app.route('/api/guests', methods=['GET'])
def get_guests():
    users = load_users()
    return jsonify(users.get('guests', []))

# 路由：添加嘉宾
@app.route('/api/guests', methods=['POST'])
def add_guest():
    try:
        guest_data = request.json
        users = load_users()
        
        # 生成新的嘉宾ID
        guest_id = generate_guest_id(users)
        
        # 创建新的嘉宾记录
        new_guest = {
            "username": guest_data['username'],
            "password": guest_data['password'],
            "guest_id": guest_id,
            "name": guest_data['name'],
            "organization": guest_data['organization'],
            "position": guest_data['position'],
            "contact": guest_data['contact']
        }
        
        users['guests'].append(new_guest)
        save_users(users)
        
        return jsonify({"success": True, "message": "嘉宾添加成功"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# 路由：根据ID获取嘉宾信息
@app.route('/api/guests/<guest_id>', methods=['GET'])
def get_guest_by_id(guest_id):
    users = load_users()
    guest = next((g for g in users['guests'] if g.get('guest_id') == guest_id), None)
    
    if guest:
        # 添加模拟的日程安排
        guest['schedule'] = [
            {
                "date": "2024-03-20",
                "time": "09:00 - 10:00",
                "activity": "开幕式",
                "location": "大会堂"
            },
            {
                "date": "2024-03-20",
                "time": "10:30 - 12:00",
                "activity": "主题演讲",
                "location": "会议室A"
            }
        ]
        # 添加模拟的接待方案
        guest['reception'] = {
            "staff": "李四",
            "contact": "987-654-3210",
            "arrangement": "嘉宾将在开幕式后由接待人员引导至会议室A进行主题演讲。"
        }
        return jsonify(guest)
    return jsonify({"error": "Guest not found"}), 404

# 路由：更新嘉宾信息
@app.route('/api/guests/<guest_id>', methods=['PUT'])
def update_guest(guest_id):
    try:
        guest_data = request.json
        users = load_users()
        
        # 查找要更新的嘉宾
        guest_index = next((index for index, g in enumerate(users['guests']) 
                          if g.get('guest_id') == guest_id), None)
        
        if guest_index is None:
            return jsonify({"success": False, "message": "嘉宾不存在"}), 404
        
        # 更新嘉宾信息
        users['guests'][guest_index].update({
            "username": guest_data['username'],
            "name": guest_data['name'],
            "organization": guest_data['organization'],
            "position": guest_data['position'],
            "contact": guest_data['contact']
        })
        
        # 如果提供了新密码，则更新密码
        if guest_data.get('password'):
            users['guests'][guest_index]['password'] = guest_data['password']
        
        save_users(users)
        return jsonify({"success": True, "message": "嘉宾信息更新成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# 路由：删除嘉宾
@app.route('/api/guests/<guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    try:
        users = load_users()
        
        # 查找要删除的嘉宾
        initial_length = len(users['guests'])
        users['guests'] = [g for g in users['guests'] if g.get('guest_id') != guest_id]
        
        if len(users['guests']) == initial_length:
            return jsonify({"success": False, "message": "嘉宾不存在"}), 404
        
        save_users(users)
        return jsonify({"success": True, "message": "嘉宾删除成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/guest_list.html')
def guest_list():
    return render_template('guest_list.html')

@app.route('/guest_detail.html')
def guest_detail():
    return render_template('guest_detail.html')

# 获取所有用车安排
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = load_vehicles()
    # 获取嘉宾信息以便展示嘉宾姓名
    users = load_users()
    guests = {g['guest_id']: g['name'] for g in users['guests']}
    
    # 为每个用车安排添加嘉宾姓名
    for arrangement in vehicles['vehicle_arrangements']:
        arrangement['guest_name'] = guests.get(arrangement['guest_id'], '未知嘉宾')
    
    return jsonify(vehicles['vehicle_arrangements'])

# 添加用车安排
@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    try:
        data = request.json
        vehicles = load_vehicles()
        
        # 验证时间格式
        try:
            datetime.strptime(data['pickup_time'], '%Y/%m/%d %H:%M')
        except ValueError:
            return jsonify({"success": False, "message": "时间格式错误"}), 400
        
        new_arrangement = {
            "id": generate_vehicle_id(),
            "guest_id": data['guest_id'],
            "vehicle_type": data['vehicle_type'],
            "pickup_time": data['pickup_time'],
            "status": "已安排"
        }
        
        vehicles['vehicle_arrangements'].append(new_arrangement)
        save_vehicles(vehicles)
        
        return jsonify({"success": True, "message": "用车安排添加成功"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# 更新用车安排
@app.route('/api/vehicles/<vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    try:
        data = request.json
        vehicles = load_vehicles()
        
        # 查找要更新的用车安排
        arrangement = next((v for v in vehicles['vehicle_arrangements'] 
                          if v['id'] == vehicle_id), None)
        
        if not arrangement:
            return jsonify({"success": False, "message": "用车安排不存在"}), 404
        
        # 验证时间格式
        try:
            datetime.strptime(data['pickup_time'], '%Y/%m/%d %H:%M')
        except ValueError:
            return jsonify({"success": False, "message": "时间格式错误"}), 400
        
        arrangement.update({
            "vehicle_type": data['vehicle_type'],
            "pickup_time": data['pickup_time'],
            "status": data['status']
        })
        
        save_vehicles(vehicles)
        return jsonify({"success": True, "message": "用车安排更新成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# 删除用车安排
@app.route('/api/vehicles/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    try:
        vehicles = load_vehicles()
        initial_length = len(vehicles['vehicle_arrangements'])
        vehicles['vehicle_arrangements'] = [v for v in vehicles['vehicle_arrangements'] 
                                          if v['id'] != vehicle_id]
        
        if len(vehicles['vehicle_arrangements']) == initial_length:
            return jsonify({"success": False, "message": "用车安排不存在"}), 404
        
        save_vehicles(vehicles)
        return jsonify({"success": True, "message": "用车安排删除成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/vehicle_management.html')
@staff_required
def vehicle_management():
    return render_template('vehicle_management.html')

# 添加管理面板路由
@app.route('/admin_dashboard.html')
@staff_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# 获取单个用车安排
@app.route('/api/vehicles/<vehicle_id>', methods=['GET'])
@staff_required
def get_vehicle_by_id(vehicle_id):
    try:
        vehicles = load_vehicles()
        # 查找指定的用车安排
        arrangement = next((v for v in vehicles['vehicle_arrangements'] 
                          if v['id'] == vehicle_id), None)
        
        if not arrangement:
            return jsonify({"success": False, "message": "用车安排不存在"}), 404
            
        # 获取嘉宾信息
        users = load_users()
        guest = next((g for g in users['guests'] 
                     if g['guest_id'] == arrangement['guest_id']), None)
        
        if guest:
            arrangement['guest_name'] = guest['name']
            
        return jsonify(arrangement)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/badge_management.html')
@staff_required
def badge_management():
    return render_template('badge_management.html')

@app.route('/api/badges/print', methods=['POST'])
@staff_required
def print_badges():
    try:
        data = request.json
        guest_ids = data.get('guest_ids', [])
        is_reprint = data.get('is_reprint', False)
        
        users = load_users()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新打印状态和历史记录
        for guest in users['guests']:
            if guest['guest_id'] in guest_ids:
                # 初始化打印历史记录列表（如果不存在）
                if 'print_history' not in guest:
                    guest['print_history'] = []
                
                # 添加新的打印记录
                print_record = {
                    'time': current_time,
                    'is_reprint': is_reprint
                }
                guest['print_history'].append(print_record)
                
                # 更新打印状态
                guest['badge_printed'] = True
                guest['last_print_time'] = current_time
        
        save_users(users)
        return jsonify({
            "success": True, 
            "message": "证件状态更新成功",
            "print_time": current_time
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/guests/permission', methods=['POST'])
@staff_required
def toggle_guest_permission():
    try:
        data = request.json
        guest_id = data.get('guest_id')
        permission_type = data.get('type')
        
        users = load_users()
        guest = next((g for g in users['guests'] if g['guest_id'] == guest_id), None)
        
        if guest:
            # 切换权限状态
            guest[permission_type] = not guest.get(permission_type, False)
            save_users(users)
            return jsonify({"success": True, "status": guest[permission_type]})
        
        return jsonify({"success": False, "message": "嘉宾不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/guests/permission/organization', methods=['POST'])
@staff_required
def toggle_organization_permission():
    try:
        data = request.json
        organization = data.get('organization')
        permission_type = data.get('type')
        
        users = load_users()
        # 获取该组织所有嘉宾的当前权限状态
        org_guests = [g for g in users['guests'] if g['organization'] == organization]
        if not org_guests:
            return jsonify({"success": False, "message": "未找到该组织的嘉宾"}), 404
            
        # 根据多数嘉宾的当前状态决定新状态
        current_status = sum(1 for g in org_guests if g.get(permission_type, False))
        new_status = current_status <= len(org_guests) / 2
        
        # 更新所有嘉宾的权限
        for guest in org_guests:
            guest[permission_type] = new_status
            
        save_users(users)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 