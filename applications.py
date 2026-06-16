from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend import db
from backend.models.models import Application, Student, Internship, Notification

applications_bp = Blueprint("applications", __name__)


def serialize_application(a):
    return {
        "id": a.id,
        "internship_id": a.internship_id,
        "internship_title": a.internship.title,
        "company_name": a.internship.company.company_name if a.internship.company else None,
        "status": a.status,
        "applied_at": a.applied_at.isoformat() if a.applied_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }


@applications_bp.route("", methods=["POST"])
@jwt_required()
def apply():
    claims = get_jwt()
    if claims.get("role") != "student":
        return jsonify({"message": "Chỉ sinh viên mới có thể ứng tuyển"}), 403

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ sinh viên"}), 404

    data = request.get_json() or {}
    internship_id = data.get("internship_id")
    internship = Internship.query.get(internship_id)
    if not internship:
        return jsonify({"message": "Không tìm thấy vị trí thực tập"}), 404

    if internship.status != "open":
        return jsonify({"message": "Vị trí này đã đóng, không thể ứng tuyển"}), 400

    existing = Application.query.filter_by(student_id=student.id, internship_id=internship_id).first()
    if existing:
        return jsonify({"message": "Bạn đã ứng tuyển vị trí này rồi"}), 409

    application = Application(
        student_id=student.id,
        internship_id=internship_id,
        cv_snapshot_url=student.cv_url,
        status="pending",
    )
    db.session.add(application)

    if internship.company:
        notif = Notification(
            user_id=internship.company.user_id,
            type="new_application",
            message=f"Có ứng viên mới cho vị trí '{internship.title}'",
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify(serialize_application(application)), 201


@applications_bp.route("/my", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"applications": []}), 200

    apps = Application.query.filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()
    return jsonify({"applications": [serialize_application(a) for a in apps]}), 200


@applications_bp.route("/<int:application_id>", methods=["PATCH"])
@jwt_required()
def update_application(application_id):
    claims = get_jwt()
    user_id = get_jwt_identity()
    application = Application.query.get_or_404(application_id)
    data = request.get_json() or {}
    new_status = data.get("status")

    role = claims.get("role")

    if role == "student":
        student = Student.query.filter_by(user_id=user_id).first()
        if not student or application.student_id != student.id:
            return jsonify({"message": "Bạn không có quyền"}), 403
        if new_status != "withdrawn":
            return jsonify({"message": "Sinh viên chỉ có thể rút đơn"}), 400

    elif role == "company":
        from backend.models.models import Company
        company = Company.query.filter_by(user_id=user_id).first()
        if not company or application.internship.company_id != company.id:
            return jsonify({"message": "Bạn không có quyền"}), 403
        if new_status not in ("accepted", "rejected"):
            return jsonify({"message": "Trạng thái không hợp lệ"}), 400

        notif = Notification(
            user_id=application.student.user_id,
            type="application_status",
            message=f"Đơn ứng tuyển '{application.internship.title}' đã được {'chấp nhận' if new_status == 'accepted' else 'từ chối'}",
        )
        db.session.add(notif)
    else:
        return jsonify({"message": "Không có quyền"}), 403

    application.status = new_status
    db.session.commit()
    return jsonify(serialize_application(application)), 200
