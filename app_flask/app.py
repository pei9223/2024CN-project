from flask import Flask, request, jsonify, url_for, request, redirect, flash, render_template, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
from sqlalchemy.dialects.postgresql import ARRAY
import flask_login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import subprocess
import re
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager


app = Flask(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rootpassword@db/labapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # file max 16MB
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])

# flask login
# login_manager = Login

app.config["JWT_SECRET_KEY"] = "secretkey"
jwt = JWTManager(app)


class Orders(db.Model):
    __tablename__ = 'orders'
    serialNo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serialString = db.Column(db.String(50), nullable=False)
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
    __tablename__ = 'users'
    userID = db.Column(db.String(50), primary_key=True)
    userPassword = db.Column(db.String(255), nullable=False)
    dep = db.Column(db.Enum('Fab A', 'Fab B', 'Fab C', 'chemical', 'surface', 'composition'), nullable=False)
    createdAt = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    def get_id(self):
        return self.userID
    
# check file extension    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# get all file paths in the folder
def get_alll_file_paths(folder_path):
    if folder_path and os.path.isdir(folder_path):
        return [os.path.join(folder_path, x) for x in os.listdir(folder_path)]
    else: return None

    
# login user data
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)

# create user
@app.route('/api/register', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        app.logger.info('get request')
        data = request.json

        id = data.get('userID')
        pswd = data.get('userPassword')
        dep = data.get('dep')

        # check if ID existed
        existing_user = User.query.filter_by(userID=id).first()
        if existing_user:
            return jsonify({'error': 'User ID already exists'}), 400
        
        # create user
        user = User(
            userID=id,
            userPassword=pswd,
            dep=dep,
            # displayName=name,
            createdAt=db.func.current_timestamp(),
            # approvedList={}
        )

        # add order to db
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201


# login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # print(request.headers['Cookie'], flush=True)
    app.logger.info('Received data from frontend: %s', data)
    
    if not data:
        return jsonify({'message': 'Missing JSON data in request'}), 400
    
    user_id = data.get('userID', '').strip()
    user_password = data.get('userPassword', '').strip()

    if not user_id or not user_password:
        return jsonify({'message': 'User ID or password missing in request'}), 400

    user = User.query.filter_by(userID=user_id).first()
    if user and user.userPassword == user_password:
        # login_user(user, remember=True)

        # set cookie
        # response = make_response('User login successfully', 200)
        # response.headers['Content-Type'] = 'application/json'
        # response.set_cookie('remember_token', request.cookies.get('remember_token'))
        # response.set_cookie('session', request.cookies.get('session'))

        # return response
        access_token = create_access_token(identity=user_id)
        return jsonify(access_token=access_token)
        # return jsonify({'message': 'User login successfully'}), 200
    else:
        return jsonify({'message': 'Invalid user ID or password'}), 401


# logout
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        current_user = get_jwt_identity()
        app.logger.info(f"Logging out user: {current_user}")
        # logout_user()
        return jsonify({'message': 'User logout successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error during logout: {e}")
        return jsonify({'message': 'An error occurred during logout', 'error': str(e)}), 500



# add and get order
@app.route('/api/orders', methods=['GET', 'POST'])
@jwt_required()
def manage_items():
    if request.method == 'POST':
        return add_order()
    return get_orders()

def add_order():
    print(request.form.to_dict(), flush=True)
    
    # system created values
    status = 'Issued'
    createdAt = db.func.current_timestamp()
    createdBy = get_jwt_identity()

    # create serial string
    time_label = str(datetime.today().year)[2:] + str(datetime.today().month).zfill(2) + str(datetime.today().day).zfill(2)

    latest_order_id = Orders.query.order_by(Orders.serialNo.desc()).first()
    if latest_order_id:
        latest_order_id = int(latest_order_id.serialNo) + 1
    else:
        latest_order_id = 1

    serialString = f"{request.form['lab'][:3].upper()}-{time_label}-{str(latest_order_id).zfill(3)}"

    # check approvedBy
    approvedBy=request.form.get('approvedBy')
    if approvedBy and not User.query.filter_by(userID=approvedBy).first():
        return jsonify({'error': 'approvedBy user not found'}), 404

    # file upload
    filePath = None
    files = request.files.getlist("file")
    if len(files):                              # there are files uploded
        filePath = 'uploads/' + serialString
        print('====', filePath, flush=True)
        if not os.path.isdir(filePath):
            os.mkdir(filePath)

        for file in files:
            print(file, flush=True)
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(filePath, filename)
                file.save(file_path)
            else:
                return jsonify({'error': 'File not allowed'}), 403
    
    # create order
    order = Orders(
        serialString=serialString,
        priority=request.form['priority'],
        factory=request.form['factory'],
        lab=request.form['lab'],
        status=status,
        createdAt=createdAt,
        createdBy=createdBy,
        filePath=filePath,
        approvedAt=None,
        approvedBy=request.form.get('approvedBy'),
        completedAt=None,
        completedBy=None 
    )

    # add order to db
    db.session.add(order)
    db.session.commit()
    
    return jsonify({'message': 'Order created successfully'}), 201


def get_orders():
    # get sorting method
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
                    'serialString': order.serialString,
                    'priority': order.priority,
                    'factory': order.factory,
                    'lab': order.lab,
                    'status': order.status,
                    'createdAt': order.createdAt,
                    'createdBy': order.createdBy,
                    'filePath': order.filePath,
                    'allFilePaths': get_alll_file_paths(order.filePath),
                    'approvedAt': order.approvedAt,
                    'approvedBy': order.approvedBy,
                    'completedAt': order.completedAt,
                    'completedBy': order.completedBy} for order in orders]
    return jsonify(orders_json), 200


# get order with id
@app.route('/api/orders/<int:id>', methods=['GET'])
@jwt_required()
def get_order_with_id(id):
    order = Orders.query.get_or_404(id)

    order_json = {'serialNo': order.serialNo,
                    'serialString': order.serialString,
                    'priority': order.priority,
                    'factory': order.factory,
                    'lab': order.lab,
                    'status': order.status,
                    'createdAt': order.createdAt,
                    'createdBy': order.createdBy,
                    'filePath': order.filePath,
                    'allFilePaths': get_alll_file_paths(order.filePath),
                    'approvedAt': order.approvedAt,
                    'approvedBy': order.approvedBy,
                    'completedAt': order.completedAt,
                    'completedBy': order.completedBy}
    return jsonify(order_json), 200


# modify order priority
@app.route('/api/orders/<int:id>', methods=['PUT'])
@jwt_required()
def adjust_order_priority(id):
    order = Orders.query.get_or_404(id)

    current_user = get_jwt_identity()
    print(order.createdBy, current_user, flush=True)
    # check user
    if order.createdBy != current_user:
        return jsonify({'error': 'Peimission denied'}), 400
    
    new_priority = request.json['priority']
    order.priority = new_priority
    db.session.commit()
    return jsonify({'message': 'Order updated'}), 200


# delete order
@app.route('/api/orders/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_order(id):
    order = Orders.query.get_or_404(id)

    # check user
    current_user = get_jwt_identity()
    if order.createdBy != current_user:
        return jsonify({'error': 'Peimission denied'}), 400
    
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted'}), 200


# get orders waiting for user to approve
@app.route('/api/get_approve_order', methods=['GET'])
@jwt_required()
def get_approve_order():
    current_user = get_jwt_identity()
    approve_orders = Orders.query.filter_by(approvedBy=current_user, status='Issued').all()

    orders_json = [{'serialNo': order.serialNo,
                    'serialString': order.serialString,
                    'priority': order.priority,
                    'factory': order.factory,
                    'lab': order.lab,
                    'status': order.status,
                    'createdAt': order.createdAt,
                    'createdBy': order.createdBy,
                    'filePath': order.filePath,
                    'allFilePaths': get_alll_file_paths(order.filePath),
                    'approvedAt': order.approvedAt,
                    'approvedBy': order.approvedBy,
                    'completedAt': order.completedAt,
                    'completedBy': order.completedBy} for order in approve_orders]
    return jsonify(orders_json), 200


# approve order
@app.route('/api/approve_order/<int:id>', methods=['POST'])
@jwt_required()
def approve_order(id):
    order = Orders.query.get_or_404(id)
    print("order: ", order, flush=True)
    current_user = get_jwt_identity()

    if order is None:
        return jsonify({"error": "Order not found"}), 404
    elif order.approvedBy != current_user:
        return jsonify({"error": "Only approver can approve orders"}), 403
    
    if request.json.get("action") == "Approve":
        order.status = "Approved"
        order.approvedAt = db.func.current_timestamp()
    elif request.json.get("action") == "Reject":
        order.status = "Rejected"
        order.approvedAt = db.func.current_timestamp()

    db.session.commit()
    
    return jsonify({"message": "Order updated successfully"}), 200


# complete order
@app.route('/api/complete_order/<int:id>', methods=['POST'])
@jwt_required()
def complete_order(id):
    order = Orders.query.get_or_404(id)
    current_user = get_jwt_identity()

    if order is None:
        return jsonify({"error": "Order not found"}), 404
    # check user dep
    current_user_dept = User.query.filter_by(userID=get_jwt_identity()).first()
    if order.lab != current_user_dept:
        return jsonify({"error": "User department does not match order lab"}), 403
    
    # check status
    if order.approvedBy:
        if order.status != "Approved":
            return jsonify({"error": "Order must be approved to complete"}), 403
    else:
        if order.status != "Issued":
            return jsonify({"error": "Order must be issued to complete"}), 403
    
    # complete
    order.status = "Completed"
    order.completedBy = current_user
    order.completedAt = db.func.current_timestamp()

    db.session.commit()
    
    return jsonify({"message": "Order updated successfully"}), 200


# download file
@app.route('/api/download', methods=['POST'])
@jwt_required()
def download_file():
    file_path = request.json.get('filePath')
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)

# get order count (by status)
@app.route('/api/count_order_by_status', methods=['GET'])
@jwt_required()
def count_order_by_status():
    result = {}
    for status in ['Issued', 'Approved', 'Completed', 'Rejected']:
        status_counts = Orders.query.filter_by(**{'status': status}).count()
        result[status] = status_counts

    return jsonify(result), 200


# get order count (by type)
@app.route('/api/count_order_by_type', methods=['GET'])
@jwt_required()
def count_order_by_type():
    result = []

    combinations = [
        {'attribute': 'priority', 'values': ['regular', 'urgent', 'emergency']},
        {'attribute': 'factory', 'values': ['Fab A', 'Fab B', 'Fab C']},
        {'attribute': 'lab', 'values': ['chemical', 'surface', 'composition']}
    ]

    for combination in combinations:
        attribute = combination['attribute']
        for value in combination['values']:
            attribute_count = {attribute: value, 'count': {}}
            for status in ['Issued', 'Approved', 'Completed', 'Rejected']:
                count = Orders.query.filter_by(**{attribute: value, 'status': status}).count()
                attribute_count['count'][status] = count
            result.append(attribute_count)

    return jsonify(result), 200


@app.route('/api/used_space', methods=['GET'])
@jwt_required()
def used_space():
    output = subprocess.check_output(["du", "-s", 'uploads'])
    subprocess_output = output.decode("utf-8")
    print(subprocess_output, flush=True)
    used  = subprocess_output.split('\t')[0]

    return jsonify({'used': used}), 200


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)