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
