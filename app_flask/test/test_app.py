import json
import pytest
from app import db, User, Orders

def user_fabA_login(client):
    response = client.post('/api/login', json={
        'userID': 'user_fabA',
        'userPassword': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'User login successfully'
    assert 'access_token' in data
    return data['access_token']

def user_fabB_login(client):
    response = client.post('/api/login', json={
        'userID': 'user_fabB',
        'userPassword': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'User login successfully'
    assert 'access_token' in data
    return data['access_token']

def user_fabC_login(client):
    response = client.post('/api/login', json={
        'userID': 'user_fabC',
        'userPassword': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'User login successfully'
    assert 'access_token' in data
    return data['access_token']

def user_chemical_login(client):
    response = client.post('/api/login', json={
        'userID': 'user_chemical',
        'userPassword': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'User login successfully'
    assert 'access_token' in data
    return data['access_token']

def user_logout(client, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = client.post('/api/logout', headers=headers)
    assert response.status_code == 200





def test_create_order(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }

    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description'
    }

    response = client.post('/api/orders', data=data, headers=headers)
    
    print(response.data.decode(), flush=True)  # 添加調試信息以檢查響應內容
    assert response.status_code == 201
    data = json.loads(response.data.decode())
    assert data['message'] == 'Order created successfully'

def test_get_orders(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/api/orders', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert isinstance(data, list)

def test_approve_order(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }

    # 首先創建一個訂單
    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description',
        'approvedBy': 'user_fabC'
    }

    response = client.post('/api/orders', data=data, headers=headers)
    print(response.data.decode(), flush=True)  # 添加調試信息以檢查響應內容
    assert response.status_code == 201
    order_id = Orders.query.order_by(Orders.serialNo.desc()).first().serialNo

    # 登出並以 approver 身份登入
    user_logout(client, access_token)
    access_token = user_fabC_login(client)
    headers['Authorization'] = f'Bearer {access_token}'
    headers.pop('Content-Type', None)  # 移除 Content-Type

    response = client.post(f'/api/approve_order/{order_id}', json={'action': 'Approve'}, headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'Order updated successfully'

def test_complete_order(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }

    # 首先創建並批准一個訂單
    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description',
        'approvedBy': 'user_fabC'
    }

    response = client.post('/api/orders', data=data, headers=headers)
    print(response.data.decode(), flush=True)  # 添加調試信息以檢查響應內容
    assert response.status_code == 201
    order_id = Orders.query.order_by(Orders.serialNo.desc()).first().serialNo

    # 登出並以 approver 身份登入批准
    user_logout(client, access_token)
    access_token = user_fabC_login(client)
    headers['Authorization'] = f'Bearer {access_token}'
    headers.pop('Content-Type', None)  # 移除 Content-Type
    client.post(f'/api/approve_order/{order_id}', json={'action': 'Approve'}, headers=headers)

    # 登出並以相應部門用戶身份登入完成訂單
    user_logout(client, access_token)
    access_token = user_chemical_login(client)
    headers['Authorization'] = f'Bearer {access_token}'
    headers.pop('Content-Type', None)  # 移除 Content-Type

    response = client.post(f'/api/complete_order/{order_id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'Order updated successfully'

def test_delete_order(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }

    # 首先創建一個訂單
    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description'
    }

    response = client.post('/api/orders', data=data, headers=headers)
    print(response.data.decode(), flush=True)  # 添加調試信息以檢查響應內容
    assert response.status_code == 201
    order_id = Orders.query.order_by(Orders.serialNo.desc()).first().serialNo

    response = client.delete(f'/api/orders/{order_id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'Order deleted'

def test_register_user(client, init_database):

    # 重複的 User ID
    response = client.post('/api/register', json={
        'userID': 'user_fabA',
        'userPassword': 'password',
        'dep': 'Fab A',
        'email': 'tonywon.cs08@nycu.edu.tw'
    })
    assert response.status_code == 400
    data = json.loads(response.data.decode())
    assert 'error' in data and data['error'] == 'User ID already exists'

    # 錯誤的 email 格式
    response = client.post('/api/register', json={
        'userID': 'another_user',
        'userPassword': 'password',
        'dep': 'Fab A',
        'email': 'invalid_email_format'
    })
    assert response.status_code == 400
    data = json.loads(response.data.decode())
    assert 'error' in data and data['error'] == 'Invalid email format'

def test_login_user(client, init_database):
    # 成功登入
    response = client.post('/api/login', json={
        'userID': 'user_fabA',
        'userPassword': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'User login successfully'

    # 缺少 userID 或 password
    response = client.post('/api/login', json={
        'userID': '',
        'userPassword': 'password'
    })
    assert response.status_code == 400
    data = json.loads(response.data.decode())
    assert 'message' in data and data['message'] == 'User ID or password missing in request'

    # 錯誤的 userID 或 password
    response = client.post('/api/login', json={
        'userID': 'invalid_user',
        'userPassword': 'wrong_password'
    })
    assert response.status_code == 401
    data = json.loads(response.data.decode())
    assert 'message' in data and data['message'] == 'Invalid user ID or password'

def test_logout_user(client, init_database):
    access_token = user_fabA_login(client)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = client.post('/api/logout', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['message'] == 'User logout successfully'

def test_create_order_unauthorized(client, init_database):
    access_token = user_chemical_login(client)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }
    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description'
    }
    response = client.post('/api/orders', data=data, headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data.decode())
    assert 'error' in data and data['error'] == 'The user is not allowed to create order'

def test_modify_order_priority_unauthorized(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }

    # 創建訂單
    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description'
    }
    response = client.post('/api/orders', data=data, headers=headers)
    assert response.status_code == 201
    order_id = Orders.query.order_by(Orders.serialNo.desc()).first().serialNo

    # 其他用戶登入
    user_logout(client, access_token)
    access_token = user_fabC_login(client)
    headers['Authorization'] = f'Bearer {access_token}'
    headers.pop('Content-Type', None)

    response = client.put(f'/api/orders/{order_id}', json={'priority': 'urgent'}, headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data.decode())
    assert 'error' in data and data['error'] == 'Peimission denied'

def test_complete_order_unauthorized(client, init_database):
    access_token = user_fabA_login(client)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'multipart/form-data'
    }

    # 創建並批准訂單
    data = {
        'priority': 'regular',
        'factory': 'Fab A',
        'lab': 'chemical',
        'description': 'Test order description',
        'approvedBy': 'user_fabC'
    }
    response = client.post('/api/orders', data=data, headers=headers)
    assert response.status_code == 201
    order_id = Orders.query.order_by(Orders.serialNo.desc()).first().serialNo

    user_logout(client, access_token)
    access_token = user_fabC_login(client)
    headers['Authorization'] = f'Bearer {access_token}'
    headers.pop('Content-Type', None)
    client.post(f'/api/approve_order/{order_id}', json={'action': 'Approve'}, headers=headers)

    # 其他用戶登入
    user_logout(client, access_token)
    access_token = user_fabB_login(client)
    headers['Authorization'] = f'Bearer {access_token}'
    headers.pop('Content-Type', None)

    response = client.post(f'/api/complete_order/{order_id}', headers=headers)
    assert response.status_code == 403
    data = json.loads(response.data.decode())
    assert 'error' in data and data['error'] == 'User department does not match order lab'

def test_get_orders_by_status(client, init_database):
    access_token = user_fabA_login(client)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = client.get('/api/count_order_by_status', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert 'Issued' in data
    assert 'Approved' in data
    assert 'Completed' in data
    assert 'Rejected' in data

def test_download_file_not_found(client, init_database):
    access_token = user_fabA_login(client)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = client.post('/api/download', json={'filePath': 'nonexistent/file/path'}, headers=headers)
    assert response.status_code == 404
    data = json.loads(response.data.decode())
    assert 'error' in data and data['error'] == 'File not found'


