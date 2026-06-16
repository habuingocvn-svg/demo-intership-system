from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.models import (
    Student, Education, Skill, StudentSkill, Project, Certificate,
    SavedInternship, Notification, Internship
)

students_bp = Blueprint("students", __name__)


def get_current_student():
    user_id = get_jwt_identity()
    return Student.query.filter_by(user_id=user_id).first()


# ===== PROFILE =====
@students_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404
    return jsonify({
        "full_name": student.user.full_name,
        "email": student.user.email,
        "phone": student.phone,
        "location": student.location,
        "bio": student.bio,
        "cv_url": student.cv_url,
    }), 200


@students_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    data = request.get_json() or {}
    if data.get("full_name"):
        student.user.full_name = data["full_name"]
    student.phone = data.get("phone", student.phone)
    student.location = data.get("location", student.location)
    student.bio = data.get("bio", student.bio)
    student.cv_url = data.get("cv_url", student.cv_url)

    db.session.commit()
    return jsonify({"message": "Cập nhật thành công"}), 200


# ===== SKILLS =====
@students_bp.route("/skills", methods=["GET"])
@jwt_required()
def get_skills():
    student = get_current_student()
    if not student:
        return jsonify({"skills": []}), 200
    skills = [{"skill_id": s.skill_id, "name": s.skill.name, "level": s.level} for s in student.skills]
    return jsonify({"skills": skills}), 200


@students_bp.route("/skills", methods=["POST"])
@jwt_required()
def add_skill():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    data = request.get_json() or {}
    name = data.get("name")
    level = data.get("level", "beginner")
    if not name:
        return jsonify({"message": "Tên kỹ năng là bắt buộc"}), 400

    skill = Skill.query.filter_by(name=name).first()
    if not skill:
        skill = Skill(name=name)
        db.session.add(skill)
        db.session.flush()

    existing = StudentSkill.query.filter_by(student_id=student.id, skill_id=skill.id).first()
    if existing:
        existing.level = level
    else:
        db.session.add(StudentSkill(student_id=student.id, skill_id=skill.id, level=level))

    db.session.commit()
    return jsonify({"message": "Đã thêm kỹ năng"}), 201


@students_bp.route("/skills/<int:skill_id>", methods=["DELETE"])
@jwt_required()
def remove_skill(skill_id):
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    StudentSkill.query.filter_by(student_id=student.id, skill_id=skill_id).delete()
    db.session.commit()
    return jsonify({"message": "Đã xóa kỹ năng"}), 200


# ===== EDUCATION =====
@students_bp.route("/education", methods=["GET"])
@jwt_required()
def get_education():
    student = get_current_student()
    if not student:
        return jsonify({"education": []}), 200
    edu = [{
        "id": e.id, "school_name": e.school_name, "degree": e.degree,
        "field_of_study": e.field_of_study,
        "start_date": e.start_date.isoformat() if e.start_date else None,
        "end_date": e.end_date.isoformat() if e.end_date else None,
    } for e in student.educations]
    return jsonify({"education": edu}), 200


@students_bp.route("/education", methods=["POST"])
@jwt_required()
def add_education():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    data = request.get_json() or {}
    if not data.get("school_name"):
        return jsonify({"message": "Tên trường là bắt buộc"}), 400

    edu = Education(
        student_id=student.id,
        school_name=data.get("school_name"),
        degree=data.get("degree"),
        field_of_study=data.get("field_of_study"),
        start_date=data.get("start_date") or None,
        end_date=data.get("end_date") or None,
    )
    db.session.add(edu)
    db.session.commit()
    return jsonify({"message": "Đã thêm học vấn"}), 201


@students_bp.route("/education/<int:edu_id>", methods=["DELETE"])
@jwt_required()
def delete_education(edu_id):
    student = get_current_student()
    edu = Education.query.get_or_404(edu_id)
    if not student or edu.student_id != student.id:
        return jsonify({"message": "Không có quyền"}), 403
    db.session.delete(edu)
    db.session.commit()
    return jsonify({"message": "Đã xóa"}), 200


# ===== PROJECTS =====
@students_bp.route("/projects", methods=["GET"])
@jwt_required()
def get_projects():
    student = get_current_student()
    if not student:
        return jsonify({"projects": []}), 200
    projects = [{
        "id": p.id, "title": p.title, "description": p.description, "url": p.url,
    } for p in student.projects]
    return jsonify({"projects": projects}), 200


@students_bp.route("/projects", methods=["POST"])
@jwt_required()
def add_project():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"message": "Tên dự án là bắt buộc"}), 400

    project = Project(
        student_id=student.id,
        title=data.get("title"),
        description=data.get("description"),
        url=data.get("url"),
        start_date=data.get("start_date") or None,
        end_date=data.get("end_date") or None,
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"message": "Đã thêm dự án"}), 201


@students_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    student = get_current_student()
    project = Project.query.get_or_404(project_id)
    if not student or project.student_id != student.id:
        return jsonify({"message": "Không có quyền"}), 403
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Đã xóa"}), 200


# ===== CERTIFICATES =====
@students_bp.route("/certificates", methods=["GET"])
@jwt_required()
def get_certificates():
    student = get_current_student()
    if not student:
        return jsonify({"certificates": []}), 200
    certs = [{
        "id": c.id, "title": c.title, "issuer": c.issuer,
        "issued_date": c.issued_date.isoformat() if c.issued_date else None, "url": c.url,
    } for c in student.certificates]
    return jsonify({"certificates": certs}), 200


@students_bp.route("/certificates", methods=["POST"])
@jwt_required()
def add_certificate():
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"message": "Tên chứng chỉ là bắt buộc"}), 400

    cert = Certificate(
        student_id=student.id,
        title=data.get("title"),
        issuer=data.get("issuer"),
        issued_date=data.get("issued_date") or None,
        url=data.get("url"),
    )
    db.session.add(cert)
    db.session.commit()
    return jsonify({"message": "Đã thêm chứng chỉ"}), 201


@students_bp.route("/certificates/<int:cert_id>", methods=["DELETE"])
@jwt_required()
def delete_certificate(cert_id):
    student = get_current_student()
    cert = Certificate.query.get_or_404(cert_id)
    if not student or cert.student_id != student.id:
        return jsonify({"message": "Không có quyền"}), 403
    db.session.delete(cert)
    db.session.commit()
    return jsonify({"message": "Đã xóa"}), 200


# ===== SAVED INTERNSHIPS =====
@students_bp.route("/saved", methods=["GET"])
@jwt_required()
def get_saved():
    student = get_current_student()
    if not student:
        return jsonify({"saved": []}), 200
    saved = [{
        "internship_id": s.internship_id,
        "title": s.internship.title,
        "company_name": s.internship.company.company_name if s.internship.company else None,
        "location": s.internship.location,
    } for s in student.saved]
    return jsonify({"saved": saved}), 200


@students_bp.route("/saved/<int:internship_id>", methods=["POST"])
@jwt_required()
def save_internship(internship_id):
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404

    existing = SavedInternship.query.filter_by(student_id=student.id, internship_id=internship_id).first()
    if existing:
        return jsonify({"message": "Đã lưu trước đó"}), 200

    db.session.add(SavedInternship(student_id=student.id, internship_id=internship_id))
    db.session.commit()
    return jsonify({"message": "Đã lưu vị trí"}), 201


@students_bp.route("/saved/<int:internship_id>", methods=["DELETE"])
@jwt_required()
def unsave_internship(internship_id):
    student = get_current_student()
    if not student:
        return jsonify({"message": "Không tìm thấy hồ sơ"}), 404
    SavedInternship.query.filter_by(student_id=student.id, internship_id=internship_id).delete()
    db.session.commit()
    return jsonify({"message": "Đã bỏ lưu"}), 200


# ===== NOTIFICATIONS =====
@students_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify({"notifications": [{
        "id": n.id, "type": n.type, "message": n.message,
        "is_read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else None,
    } for n in notifs]}), 200


# ===== RECOMMENDATIONS (based on student skills) =====
@students_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations():
    student = get_current_student()
    if not student or not student.skills:
        return jsonify({"internships": []}), 200

    skill_ids = [s.skill_id for s in student.skills]
    from backend.models.models import InternshipSkill
    internship_ids = db.session.query(InternshipSkill.internship_id).filter(
        InternshipSkill.skill_id.in_(skill_ids)
    ).distinct().subquery()

    internships = Internship.query.filter(
        Internship.id.in_(internship_ids), Internship.status == "open"
    ).order_by(Internship.posted_at.desc()).limit(10).all()

    result = [{
        "id": i.id, "title": i.title, "location": i.location,
        "company_name": i.company.company_name if i.company else None,
        "skills": [s.skill.name for s in i.skills],
    } for i in internships]

    return jsonify({"internships": result}), 200
