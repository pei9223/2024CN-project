import unittest
import json
from app import app, db, Orders

class TestOrdersAPI(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rootpassword@db/testdb'  # 使用測試數據庫URI
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.ctx = app.app_context()  # 建立應用程式上下文
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()  # 彈出應用程式上下文

    def test_create_order(self):
        # 發送POST請求到創建order的API端點
        response = self.app.post('/api/orders', 
                                 data=json.dumps({'priority': 'regular',
                                                  'factory': 'Fab A',
                                                  'lab': 'chemical',
                                                  'approvedBy': 'aaa'}),
                                 content_type='application/json')

        # 驗證回應
        self.assertEqual(response.status_code, 201)  # 確保回應狀態碼為201表示成功創建
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Order created successfully')  # 確保回應消息正確

        # 檢查數據庫中是否成功添加了一條新的order
        orders_count = Orders.query.count()
        self.assertEqual(orders_count, 1)

    def test_get_orders(self):
        # 在測試數據庫中創建一些假訂單數據
        order1 = Orders(priority='regular', factory='Fab A', lab='chemical', status='Issued', createdBy='System')
        order2 = Orders(priority='urgent', factory='Fab B', lab='surface', status='Approved', createdBy='User1')
        db.session.add(order1)
        db.session.add(order2)
        db.session.commit()

        # 發送GET請求到獲取所有orders的API端點
        response = self.app.get('/api/orders')

        # 驗證回應
        self.assertEqual(response.status_code, 200)  # 確保回應狀態碼為200表示成功
        data = json.loads(response.data)
        print("-------test_get_orders-------")
        print(data)
        self.assertEqual(len(data), 2)  # 確保返回的數據中有兩個訂單

    def test_get_order_with_id(self):
        # 在測試數據庫中創建一個假訂單數據
        order = Orders(priority='regular', factory='Fab A', lab='chemical', status='Issued', createdBy='System')
        db.session.add(order)
        db.session.commit()

        # 發送GET請求到獲取單個order的API端點
        response = self.app.get(f'/api/orders/{order.serialNo}')

        # 驗證回應
        self.assertEqual(response.status_code, 200)  # 確保回應狀態碼為200表示成功
        data = json.loads(response.data)
        print("-------test_get_order_with_id-------")
        print(data)
        self.assertEqual(data['priority'], 'regular')  # 確保返回的數據中包含正確的優先順序

    def test_edit_order(self):
        # 在測試數據庫中創建一個假訂單數據
        order = Orders(priority='regular', factory='Fab A', lab='chemical', status='Issued', createdBy='System')
        db.session.add(order)
        db.session.commit()

        # 發送PUT請求到編輯order的API端點
        new_priority = 'emergency'
        response = self.app.put(f'/api/orders/{order.serialNo}',
                                data=json.dumps({'priority': new_priority}),
                                content_type='application/json')

        # 驗證回應
        self.assertEqual(response.status_code, 200)  # 確保回應狀態碼為200表示成功
        data = json.loads(response.data)
        print("-------test_edit_order-------")
        print(data)
        self.assertEqual(data['message'], 'Item updated')  # 確保返回的消息正確

        # 檢查數據庫中的order是否已經更新
        updated_order = Orders.query.get(order.serialNo)
        print("updated_order", updated_order.priority)
        self.assertEqual(updated_order.priority, new_priority)


class LoginTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_required_redirect(self):
        # 发送未经身份验证的请求到受保护的端点
        response = self.app.get('/')
        # 检查是否被重定向到登录页面
        self.assertEqual(response.status_code, 302)  # 302 是重定向状态码
        self.assertTrue('/api/login' in response.location)

if __name__ == '__main__':
    unittest.main()
