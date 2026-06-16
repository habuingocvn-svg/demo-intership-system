from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend import db, bcrypt
from backend.models.models import User, Student, Company

auth_bp = Blueprint("auth", __name__)


def serialize_user(user):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_verified": user.is_verified,
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not full_name or not email or not password or not role:
        return jsonify({"message": "Vui lòng điền đầy đủ thông tin"}), 400

    if role not in ("student", "company"):
        return jsonify({"message": "Vai trò không hợp lệ"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email đã được sử dụng"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        full_name=full_name,
        email=email,
        password_hash=password_hash,
        role=role,
        is_verified=(role == "student"),  # students don't need verification, companies do
    )
    db.session.add(user)
    db.session.flush()  # get user.id without full commit

    if role == "student":
        profile = Student(user_id=user.id)
        db.session.add(profile)
    elif role == "company":
        company_name = data.get("company_name") or full_name
        profile = Company(user_id=user.id, company_name=company_name, is_verified=False)
        db.session.add(profile)

    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": serialize_user(user)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Vui lòng điền đầy đủ thông tin"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Email hoặc mật khẩu không đúng"}), 401

    if user.is_banned:
        return jsonify({"message": "Tài khoản của bạn đã bị khóa"}), 403

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": serialize_user(user)}), 200
