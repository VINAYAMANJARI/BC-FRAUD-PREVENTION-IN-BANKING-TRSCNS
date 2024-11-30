# app.py   --- with in-memory storage.
# from flask import Flask, render_template, redirect, url_for, request, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import (
#     LoginManager,
#     login_user,
#     login_required,
#     logout_user,
#     UserMixin,
#     current_user,
# )
# from blockchain import Blockchain
# from werkzeug.security import generate_password_hash, check_password_hash
# import os
# import time

# app = Flask(__name__)
# app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_default_secret_key")  # Use environment variable for security
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # Initialize Blockchain in-memory
# blockchain = Blockchain()

# # User Model
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(150), nullable=False)

# # Create the database
# with app.app_context():
#     db.create_all()

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # Routes
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         # Check if user exists
#         user = User.query.filter_by(username=username).first()
#         if user:
#             flash("Username already exists", "danger")
#             return redirect(url_for("signup"))

#         # Create new user with hashed password
#         new_user = User(
#             username=username,
#             password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=16),
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash("Account created! Please log in.", "success")
#         return redirect(url_for("login"))
#     return render_template("signup.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         user = User.query.filter_by(username=username).first()
#         if not user or not check_password_hash(user.password, password):
#             flash("Invalid credentials", "danger")
#             return redirect(url_for("login"))

#         login_user(user)
#         return redirect(url_for("dashboard"))
#     return render_template("login.html")

# @app.route("/dashboard", methods=["GET", "POST"])
# @login_required
# def dashboard():
#     if request.method == "POST":
#         transaction = request.form.get("transaction")

#         if blockchain.add_block(transaction, current_user.id):
#             flash("Transaction added to the blockchain!", "success")
#         else:
#             flash("This transaction already exists!", "warning")
#         return redirect(url_for("dashboard"))

#     # Retrieve all transactions for the current user
#     user_transactions = [block for block in blockchain.chain if block.user_id == current_user.id]
#     return render_template("dashboard.html", transactions=user_transactions)

# @app.route("/history")
# @login_required
# def history():
#     # Include blocks that belong to the user or the genesis block
#     user_transactions = [
#         block for block in blockchain.chain
#         if block.user_id == current_user.id or block.index == 0
#     ]

#     # Prepare data for rendering
#     chain_data = []
#     for block in user_transactions:
#         chain_data.append(
#             {
#                 "index": block.index,
#                 "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block.timestamp)),
#                 "data": block.data,
#                 "hash": block.hash,
#                 "previous_hash": block.previous_hash,
#             }
#         )

#     return render_template("history.html", chain=chain_data)

# @app.route("/about")
# def about():
#     return render_template("about.html")

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("index"))

# # Error Handlers
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template("404.html"), 404

# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template("500.html"), 500

# # Run the app
# if __name__ == "__main__":
#     app.run(debug=True)


# app.py  -- database created with SQL and data remains in the DB even after stop running the server.
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    UserMixin,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_default_secret_key")  # Use environment variable for security
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blockchain.db"  # Updated database name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Block Model
class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    data = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Set nullable=True
    hash = db.Column(db.String(64), nullable=False)
    previous_hash = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<Block {self.index}>"

# Initialize the database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Blockchain:
    def __init__(self):
        self.create_genesis_block()

    def create_genesis_block(self):
        # Check if a genesis block already exists
        genesis_block = Block.query.filter_by(index=0).first()
        if not genesis_block:
            genesis_block = Block(
                index=0,
                timestamp=time.time(),
                data="Genesis Block",
                user_id=None,  # Set to None since it doesn't belong to any user
                previous_hash='0',
                hash=self.calculate_hash(0, time.time(), "Genesis Block", None, '0')
            )
            db.session.add(genesis_block)
            db.session.commit()

    def get_latest_block(self, user_id):
        return Block.query.filter_by(user_id=user_id).order_by(Block.index.desc()).first()

    def add_block(self, data, user_id):
        latest_block = self.get_latest_block(user_id)
        if latest_block:
            previous_hash = latest_block.hash
            index = latest_block.index + 1
        else:
            previous_hash = '0'
            index = 1  ## index value updated.

        # Check for duplicate transaction for the user
        existing_block = Block.query.filter_by(data=data, user_id=user_id).first()
        if existing_block:
            return False  # Duplicate transaction

        # Calculate hash for the new block
        new_hash = self.calculate_hash(index, time.time(), data, user_id, previous_hash)
        new_block = Block(
            index=index,
            timestamp=time.time(),
            data=data,
            user_id=user_id,
            previous_hash=previous_hash,
            hash=new_hash
        )
        db.session.add(new_block)
        db.session.commit()
        return True

    def calculate_hash(self, index, timestamp, data, user_id, previous_hash):
        user_id_str = str(user_id) if user_id is not None else 'None'
        sha = hashlib.sha256()
        sha.update(
            str(index).encode('utf-8') +
            str(timestamp).encode('utf-8') +
            str(data).encode('utf-8') +
            user_id_str.encode('utf-8') +
            str(previous_hash).encode('utf-8')
        )
        return sha.hexdigest()

    def is_chain_valid(self, user_id):
        # Fetch all blocks for the user
        user_blocks = Block.query.filter_by(user_id=user_id).order_by(Block.index).all()
        if not user_blocks:
            return False
        # Check the genesis block
        genesis = Block.query.filter_by(index=0).first()
        if genesis is None or genesis.data != "Genesis Block" or genesis.previous_hash != '0':
            return False
        # Check the user's blocks
        for i in range(len(user_blocks)):
            current = user_blocks[i]
            if current.index == 0:
                continue  # Skip genesis block
            if i == 0:
                # The first user block should link to the genesis block
                if current.previous_hash != genesis.hash:
                    return False
            else:
                prev = user_blocks[i - 1]
                if current.previous_hash != prev.hash:
                    return False
            # Recalculate the hash and compare
            expected_hash = self.calculate_hash(current.index, current.timestamp, current.data, current.user_id, current.previous_hash)
            if current.hash != expected_hash:
                return False
        return True

# Initialize the Blockchain within an application context
with app.app_context():
    blockchain = Blockchain()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Input validation
        if not username or not password:
            flash("Username and password are required!", "danger")
            return redirect(url_for("signup"))

        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists", "danger")
            return redirect(url_for("signup"))

        # Create new user with hashed password
        new_user = User(
            username=username,
            password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=16),
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Input validation
        if not username or not password:
            flash("Username and password are required!", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        transaction = request.form.get("transaction")

        # Input validation
        if not transaction:
            flash("Transaction data cannot be empty!", "danger")
            return redirect(url_for("dashboard"))

        if blockchain.add_block(transaction, current_user.id):
            flash("Transaction added to the blockchain!", "success")
        else:
            flash("This transaction already exists!", "warning")
        return redirect(url_for("dashboard"))

    # Fetch all blocks for the current user
    user_blocks = Block.query.filter_by(user_id=current_user.id).order_by(Block.index).all()

    # Prepare data for rendering
    transactions = []
    for block in user_blocks:
        transactions.append(
            {
                "index": block.index,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block.timestamp)),
                "data": block.data,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
            }
        )

    return render_template("dashboard.html", transactions=transactions)

@app.route("/history")
@login_required
def history():
    # Fetch the genesis block
    genesis_block = Block.query.filter_by(index=0).first()

    # Fetch all blocks for the current user
    user_blocks = Block.query.filter_by(user_id=current_user.id).order_by(Block.index).all()

    # Combine genesis block with user-specific blocks
    blocks_to_show = []
    if genesis_block:
        blocks_to_show.append(genesis_block)
    blocks_to_show.extend(user_blocks)

    # Prepare data for rendering
    chain_data = []
    for block in blocks_to_show:
        chain_data.append(
            {
                "index": block.index,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block.timestamp)),
                "data": block.data,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
            }
        )

    return render_template("history.html", chain=chain_data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# Add custom filter
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format, time.localtime(value))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)





