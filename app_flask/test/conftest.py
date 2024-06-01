import os
import pytest
import sqlalchemy as sa
from app import app, db

@pytest.fixture(scope='session')
def app_instance():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rootpassword@db/labapp'
    return app

@pytest.fixture(scope='session')
def client(app_instance):
    with app_instance.app_context():
        with app_instance.test_client() as client:
            yield client

@pytest.fixture(scope='session')
def init_database(app_instance):
    with app_instance.app_context():
        db.drop_all()
        db.create_all()

        # 執行 init.sql 文件
        sql_file_path = os.path.join(os.path.dirname(__file__), 'init.sql')
        with open(sql_file_path, 'r') as file:
            init_sql = file.read()
        db.session.execute(sa.text(init_sql))
        db.session.commit()

        yield db

        # Clean up after test
        db.session.remove()
        db.drop_all()

        # 重新初始化資料庫
        db.create_all()
        with open(sql_file_path, 'r') as file:
            init_sql = file.read()
        db.session.execute(sa.text(init_sql))
        db.session.commit()
