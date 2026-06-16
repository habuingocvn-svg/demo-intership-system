from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_
from backend import db
from backend.models.models import Internship, Company, InternshipSkill, Skill, Application

internships_bp = Blueprint("internships", __name__)


def serialize_internship(i, with_company=True):
    data = {
        "id": i.id,
        "title": i.title,
        "description": i.description,
        "location": i.location,
        "status": i.status,
        "posted_at": i.posted_at.isoformat() if i.posted_at else None,
        "deadline": i.deadline.isoformat() if i.deadline else None,
        "skills": [{"id": s.skill.id, "name": s.skill.name} for s in i.skills],
        "application_count": len(i.applications),
    }
    if with_company and i.company:
        data["company_id"] = i.company.id
        data["company_name"] = i.company.company_name
        data["company_location"] = i.company.location
    return data


@internships_bp.route("", methods=["GET"])
def list_internships():
    query = Internship.query.filter(Internship.status != "removed")

    q = request.args.get("q")
    location = request.args.get("location")
    skill = request.args.get("skill")
    company_name = request.args.get("company")
    sort = request.args.get("sort", "newest")

    if q:
        query = query.filter(Internship.title.ilike(f"%{q}%"))
    if location:
        query = query.filter(Internship.location.ilike(f"%{location}%"))
    if company_name:
        query = query.join(Company).filter(Company.company_name.ilike(f"%{company_name}%"))
    if skill:
        query = query.join(InternshipSkill).join(Skill).filter(Skill.name.ilike(f"%{skill}%"))

    if sort == "oldest":
        query = query.order_by(Internship.posted_at.asc())
    else:
        query = query.order_by(Internship.posted_at.desc())

    internships = query.all()
    return jsonify({
        "internships": [serialize_internship(i) for i in internships],
        "total": len(internships),
    }), 200


@internships_bp.route("/<int:internship_id>", methods=["GET"])
def get_internship(internship_id):
    i = Internship.query.get_or_404(internship_id)
    return jsonify(serialize_internship(i)), 200


@internships_bp.route("", methods=["POST"])
@jwt_required()
def create_internship():
    claims = get_jwt()
    if claims.get("role") != "company":
        return jsonify({"message": "Chỉ công ty mới được đăng tin"}), 403

    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Không tìm thấy hồ sơ công ty"}), 404

    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"message": "Tiêu đề là bắt buộc"}), 400

    internship = Internship(
        company_id=company.id,
        title=title,
        description=data.get("description"),
        location=data.get("location"),
        deadline=data.get("deadline"),
        status="open",
    )
    db.session.add(internship)
    db.session.flush()

    skill_names = data.get("skills", [])
    for name in skill_names:
        skill = Skill.query.filter_by(name=name).first()
        if not skill:
            skill = Skill(name=name)
            db.session.add(skill)
            db.session.flush()
        db.session.add(InternshipSkill(internship_id=internship.id, skill_id=skill.id))

    db.session.commit()
    return jsonify(serialize_internship(internship)), 201


@internships_bp.route("/<int:internship_id>", methods=["PUT"])
@jwt_required()
def update_internship(internship_id):
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    internship = Internship.query.get_or_404(internship_id)

    if not company or internship.company_id != company.id:
        return jsonify({"message": "Bạn không có quyền sửa tin này"}), 403

    data = request.get_json() or {}
    internship.title = data.get("title", internship.title)
    internship.description = data.get("description", internship.description)
    internship.location = data.get("location", internship.location)
    internship.deadline = data.get("deadline", internship.deadline)

    db.session.commit()
    return jsonify(serialize_internship(internship)), 200


@internships_bp.route("/<int:internship_id>/close", methods=["PATCH"])
@jwt_required()
def close_internship(internship_id):
    from datetime import datetime
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    internship = Internship.query.get_or_404(internship_id)

    if not company or internship.company_id != company.id:
        return jsonify({"message": "Bạn không có quyền"}), 403

    internship.status = "closed"
    internship.closed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Đã đóng tin tuyển dụng"}), 200


@internships_bp.route("/<int:internship_id>/applicants", methods=["GET"])
@jwt_required()
def get_applicants(internship_id):
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    internship = Internship.query.get_or_404(internship_id)

    if not company or internship.company_id != company.id:
        return jsonify({"message": "Bạn không có quyền xem"}), 403

    applicants = []
    for app in internship.applications:
        s = app.student
        applicants.append({
            "application_id": app.id,
            "student_id": s.id,
            "full_name": s.user.full_name,
            "email": s.user.email,
            "phone": s.phone,
            "cv_url": s.cv_url,
            "status": app.status,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None,
        })

    return jsonify({"applicants": applicants}), 200
