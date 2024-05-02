from flask import Flask, request, jsonify, url_for, request, redirect, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
import flask_login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rootpassword@db/labapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.login_message = "Please login first"


class Orders(db.Model):
    __tablename__ = 'orders'
    serialNo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    priority = db.Column(db.Enum('regular', 'urgent', 'emergency'), nullable=False)
    factory = db.Column(db.Enum('Fab A', 'Fab B', 'Fab C'), nullable=False)
    lab = db.Column(db.Enum('chemical', 'surface', 'composition'), nullable=False)
    status = db.Column(db.Enum('Issued', 'Approved', 'Completed', 'Rejected'), nullable=False)
    createdAt = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    createdBy = db.Column(db.String(50), nullable=False)
    filePath = db.Column(db.String(255))
    approvedAt = db.Column(db.TIMESTAMP)
    approvedBy = db.Column(db.String(50))
    completedAt = db.Column(db.TIMESTAMP)
    completedBy = db.Column(db.String(50))

class User(UserMixin, db.Model):
# class User(db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.String(50), primary_key=True)
    userPassword = db.Column(db.String(255), nullable=False)
    displayName = db.Column(db.String(100), nullable=False)
    createdAt = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    approvedList = db.Column(db.JSON, nullable=False)

    def get_id(self):
        return self.userID
    
    
# login user data
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# create user
@app.route('/api/register', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        app.logger.info('get request')
        data = request.json

        id = data.get('userID')
        pswd = data.get('userPassword')
        name = data.get('displayName')

        # check if ID existed
        existing_user = User.query.filter_by(userID=id).first()
        if existing_user:
            return jsonify({'error': 'User ID already exists'}), 400

        
        # create user
        user = User(
            userID=id,
            userPassword=pswd,
            displayName=name,
            createdAt=db.func.current_timestamp(),
            approvedList={}
        )

        # add order to db
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Order created successfully'}), 201


# login
@app.route('/api/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        data = request.form.to_dict()
        print(data, flush=True)
        user_id = data['userID'].strip()
        user_password = data['userPassword'].strip()

        user = User.query.filter_by(userID=user_id).first()
        if user and user.userPassword == user_password:
            login_user(user)
            print("current user: ", current_user, flush=True)
            return redirect(url_for('index'))
        else:
            return 'Invalid user ID or password'
    else:
        return render_template('login.html')
        # return """<form method=post>
        # Name: <input name="name"><br>
        # Password: <input name="password" type=password><br>
        # <button>Log In</button>
        # </form>"""

# logout
@app.route('/api/logout')
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('index'))

# home
@app.route('/')
@login_required
def index():
    return f'Hello, {current_user.displayName}! <a href="/logout">Logout</a>'


@app.route('/api/orders', methods=['GET', 'POST'])
@login_required
def manage_items():
    if request.method == 'POST':
        return add_order()
    return get_orders()

def add_order():
    # data = request.json
    # data = request.form
    print(request.form.to_dict(), flush=True)

    # file upload
    filePath = None
    if 'file' in request.files:
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads/', filename)
            file.save(file_path)
            filePath = file_path
        # else:
        #     return jsonify({'error': 'No file selected'}), 400
    
    # system created values
    status = 'Issued'
    createdAt = db.func.current_timestamp()
    createdBy = current_user.userID
    
    # create order
    order = Orders(
        priority=request.form['priority'],
        factory=request.form['factory'],
        lab=request.form['lab'],
        status=status,
        createdAt=createdAt,
        createdBy=createdBy,
        filePath=filePath,
        approvedAt=None,
        approvedBy=None,
        completedAt=None,
        completedBy=None 
    )

    # add order to db
    db.session.add(order)
    db.session.commit()
    
    return jsonify({'message': 'Order created successfully'}), 201

def get_orders():

    # get order method
    sort_by = request.args.get('sort_by', 'priority')  # deafult:priority
    if sort_by == 'createdAt':
        orders = Orders.query.order_by(Orders.createdAt.desc()).all()
    elif sort_by == 'priority':
        orders = Orders.query.order_by(
            Orders.status != 'Completed', 
            Orders.status != 'Rejected', 
            case(
                (Orders.priority == 'emergency', 0),
                (Orders.priority == 'urgent', 1),
                (Orders.priority == 'regular', 2),
                else_=3
            ),
            Orders.createdAt.desc()).all()

    orders_json = [{'serialNo': order.serialNo,
                    'priority': order.priority,
                    'factory': order.factory,
                    'lab': order.lab,
                    'status': order.status,
                    'createdAt': order.createdAt,
                    'createdBy': order.createdBy,
                    'filePath': order.filePath,
                    'approvedAt': order.approvedAt,
                    'approvedBy': order.approvedBy,
                    'completedAt': order.completedAt,
                    'completedBy': order.completedBy} for order in orders]
    return jsonify(orders_json), 200


@app.route('/api/orders/<int:id>', methods=['GET'])
@login_required
def get_order_with_id(id):
    order = Orders.query.get_or_404(id)

    order_json = {'serialNo': order.serialNo,
                    'priority': order.priority,
                    'factory': order.factory,
                    'lab': order.lab,
                    'status': order.status,
                    'createdAt': order.createdAt,
                    'createdBy': order.createdBy,
                    'filePath': order.filePath,
                    'approvedAt': order.approvedAt,
                    'approvedBy': order.approvedBy,
                    'completedAt': order.completedAt,
                    'completedBy': order.completedBy}
    return jsonify(order_json), 200


@app.route('/api/orders/<int:id>', methods=['PUT'])
@login_required
def edit_item(id):
    order = Orders.query.get_or_404(id)

    print(order.createdBy, current_user.userID, flush=True)
    # check user
    if order.createdBy != current_user.userID:
        return jsonify({'error': 'Peimission denied'}), 400
    
    new_priority = request.json['priority']
    order.priority = new_priority
    db.session.commit()
    return jsonify({'message': 'Item updated'}), 200


# @app.route('/api/items/<int:id>', methods=['DELETE'])
# def delete_item(id):
#     item = Item.query.get_or_404(id)
#     db.session.delete(item)
#     db.session.commit()
#     return jsonify({'message': 'Item deleted'}), 200



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)