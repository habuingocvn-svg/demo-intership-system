from datetime import datetime
from backend import db


class User(db.Model):
    __tablename__ = "user"
    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20),  nullable=False)   # student | company | admin
    avatar_url    = db.Column(db.Text)
    is_banned     = db.Column(db.Boolean, default=False)
    is_verified   = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    student       = db.relationship("Student", back_populates="user", uselist=False)
    company       = db.relationship("Company", back_populates="user", uselist=False)
    notifications = db.relationship("Notification", back_populates="user")
    system_logs   = db.relationship("SystemLog", back_populates="admin_user")


class Student(db.Model):
    __tablename__ = "student"
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    phone    = db.Column(db.String(20))
    location = db.Column(db.String(100))
    bio      = db.Column(db.Text)
    cv_url   = db.Column(db.Text)

    user         = db.relationship("User", back_populates="student")
    educations   = db.relationship("Education",   back_populates="student", cascade="all, delete")
    projects     = db.relationship("Project",     back_populates="student", cascade="all, delete")
    certificates = db.relationship("Certificate", back_populates="student", cascade="all, delete")
    skills       = db.relationship("StudentSkill", back_populates="student", cascade="all, delete")
    applications = db.relationship("Application",  back_populates="student", cascade="all, delete")
    saved        = db.relationship("SavedInternship", back_populates="student", cascade="all, delete")


class Company(db.Model):
    __tablename__ = "company"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    description  = db.Column(db.Text)
    website      = db.Column(db.Text)
    location     = db.Column(db.String(100))
    is_verified  = db.Column(db.Boolean, default=False)

    user        = db.relationship("User", back_populates="company")
    internships = db.relationship("Internship", back_populates="company", cascade="all, delete")


class Education(db.Model):
    __tablename__ = "education"
    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    school_name    = db.Column(db.String(150), nullable=False)
    degree         = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    start_date     = db.Column(db.Date)
    end_date       = db.Column(db.Date)

    student = db.relationship("Student", back_populates="educations")


class Skill(db.Model):
    __tablename__ = "skill"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    student_skills    = db.relationship("StudentSkill",    back_populates="skill")
    internship_skills = db.relationship("InternshipSkill", back_populates="skill")


class StudentSkill(db.Model):
    __tablename__ = "student_skill"
    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), primary_key=True)
    skill_id   = db.Column(db.Integer, db.ForeignKey("skill.id",   ondelete="CASCADE"), primary_key=True)
    level      = db.Column(db.String(20))   # beginner | intermediate | advanced

    student = db.relationship("Student", back_populates="skills")
    skill   = db.relationship("Skill",   back_populates="student_skills")


class Project(db.Model):
    __tablename__ = "project"
    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    title       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    url         = db.Column(db.Text)
    start_date  = db.Column(db.Date)
    end_date    = db.Column(db.Date)

    student = db.relationship("Student", back_populates="projects")


class Certificate(db.Model):
    __tablename__ = "certificate"
    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    title       = db.Column(db.String(150), nullable=False)
    issuer      = db.Column(db.String(150))
    issued_date = db.Column(db.Date)
    url         = db.Column(db.Text)

    student = db.relationship("Student", back_populates="certificates")


class Internship(db.Model):
    __tablename__ = "internship"
    id          = db.Column(db.Integer, primary_key=True)
    company_id  = db.Column(db.Integer, db.ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    title       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location    = db.Column(db.String(100))
    status      = db.Column(db.String(20), default="open")   # open | closed | removed
    posted_at   = db.Column(db.DateTime, default=datetime.utcnow)
    deadline    = db.Column(db.DateTime)
    closed_at   = db.Column(db.DateTime)

    company      = db.relationship("Company", back_populates="internships")
    skills       = db.relationship("InternshipSkill", back_populates="internship", cascade="all, delete")
    applications = db.relationship("Application",     back_populates="internship", cascade="all, delete")
    saved_by     = db.relationship("SavedInternship", back_populates="internship", cascade="all, delete")
    reports      = db.relationship("Report",          back_populates="internship", cascade="all, delete")


class InternshipSkill(db.Model):
    __tablename__ = "internship_skill"
    internship_id = db.Column(db.Integer, db.ForeignKey("internship.id", ondelete="CASCADE"), primary_key=True)
    skill_id      = db.Column(db.Integer, db.ForeignKey("skill.id",      ondelete="CASCADE"), primary_key=True)

    internship = db.relationship("Internship", back_populates="skills")
    skill      = db.relationship("Skill",      back_populates="internship_skills")


class Application(db.Model):
    __tablename__ = "application"
    __table_args__ = (db.UniqueConstraint("student_id", "internship_id"),)
    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey("student.id",    ondelete="CASCADE"), nullable=False)
    internship_id   = db.Column(db.Integer, db.ForeignKey("internship.id", ondelete="CASCADE"), nullable=False)
    status          = db.Column(db.String(20), default="pending")  # pending | accepted | rejected | withdrawn
    cv_snapshot_url = db.Column(db.Text)
    applied_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student    = db.relationship("Student",    back_populates="applications")
    internship = db.relationship("Internship", back_populates="applications")


class SavedInternship(db.Model):
    __tablename__ = "saved_internship"
    student_id    = db.Column(db.Integer, db.ForeignKey("student.id",    ondelete="CASCADE"), primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internship.id", ondelete="CASCADE"), primary_key=True)
    saved_at      = db.Column(db.DateTime, default=datetime.utcnow)

    student    = db.relationship("Student",    back_populates="saved")
    internship = db.relationship("Internship", back_populates="saved_by")


class Report(db.Model):
    __tablename__ = "report"
    id            = db.Column(db.Integer, primary_key=True)
    reporter_id   = db.Column(db.Integer, db.ForeignKey("user.id",       ondelete="CASCADE"), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey("internship.id", ondelete="CASCADE"), nullable=False)
    reason        = db.Column(db.Text, nullable=False)
    status        = db.Column(db.String(20), default="pending")  # pending | resolved | dismissed
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    internship = db.relationship("Internship", back_populates="reports")


class Notification(db.Model):
    __tablename__ = "notification"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    type       = db.Column(db.String(50), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_token"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token      = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemLog(db.Model):
    __tablename__ = "system_log"
    id            = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    action        = db.Column(db.String(100), nullable=False)
    target_type   = db.Column(db.String(50))
    target_id     = db.Column(db.Integer)
    note          = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    admin_user = db.relationship("User", back_populates="system_logs")
