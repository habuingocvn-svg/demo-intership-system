-- ============================================================
--  Internship Connection System — Database Schema
-- ============================================================

-- ----------------------
--  USER
-- ----------------------
CREATE TABLE "user" (
    id               SERIAL PRIMARY KEY,
    full_name        VARCHAR(100)        NOT NULL,
    email            VARCHAR(255)        NOT NULL UNIQUE,
    password_hash    VARCHAR(255)        NOT NULL,
    role             VARCHAR(20)         NOT NULL CHECK (role IN ('student', 'company', 'admin')),
    avatar_url       TEXT,
    is_banned        BOOLEAN             NOT NULL DEFAULT FALSE,
    is_verified      BOOLEAN             NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMP           NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_email  ON "user" (email);
CREATE INDEX idx_user_role   ON "user" (role);


-- ----------------------
--  STUDENT
-- ----------------------
CREATE TABLE student (
    id          SERIAL PRIMARY KEY,
    user_id     INT             NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    phone       VARCHAR(20),
    location    VARCHAR(100),
    bio         TEXT,
    cv_url      TEXT
);


-- ----------------------
--  COMPANY
-- ----------------------
CREATE TABLE company (
    id              SERIAL PRIMARY KEY,
    user_id         INT             NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    company_name    VARCHAR(150)    NOT NULL,
    description     TEXT,
    website         TEXT,
    location        VARCHAR(100),
    is_verified     BOOLEAN         NOT NULL DEFAULT FALSE
);


-- ----------------------
--  EDUCATION
-- ----------------------
CREATE TABLE education (
    id              SERIAL PRIMARY KEY,
    student_id      INT             NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    school_name     VARCHAR(150)    NOT NULL,
    degree          VARCHAR(100),
    field_of_study  VARCHAR(100),
    start_date      DATE,
    end_date        DATE
);

CREATE INDEX idx_education_student ON education (student_id);


-- ----------------------
--  SKILL
-- ----------------------
CREATE TABLE skill (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) NOT NULL UNIQUE
);


-- ----------------------
--  STUDENT_SKILL  (many-to-many)
-- ----------------------
CREATE TABLE student_skill (
    student_id  INT         NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    skill_id    INT         NOT NULL REFERENCES skill(id)   ON DELETE CASCADE,
    level       VARCHAR(20) CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    PRIMARY KEY (student_id, skill_id)
);


-- ----------------------
--  PROJECT
-- ----------------------
CREATE TABLE project (
    id          SERIAL PRIMARY KEY,
    student_id  INT     NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    title       VARCHAR(150) NOT NULL,
    description TEXT,
    url         TEXT,
    start_date  DATE,
    end_date    DATE
);

CREATE INDEX idx_project_student ON project (student_id);


-- ----------------------
--  CERTIFICATE
-- ----------------------
CREATE TABLE certificate (
    id           SERIAL PRIMARY KEY,
    student_id   INT          NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    title        VARCHAR(150) NOT NULL,
    issuer       VARCHAR(150),
    issued_date  DATE,
    url          TEXT
);

CREATE INDEX idx_certificate_student ON certificate (student_id);


-- ----------------------
--  INTERNSHIP
-- ----------------------
CREATE TABLE internship (
    id           SERIAL PRIMARY KEY,
    company_id   INT          NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    title        VARCHAR(150) NOT NULL,
    description  TEXT,
    location     VARCHAR(100),
    status       VARCHAR(20)  NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'removed')),
    posted_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    deadline     TIMESTAMP,
    closed_at    TIMESTAMP
);

CREATE INDEX idx_internship_company ON internship (company_id);
CREATE INDEX idx_internship_status  ON internship (status);
CREATE INDEX idx_internship_posted  ON internship (posted_at DESC);


-- ----------------------
--  INTERNSHIP_SKILL  (many-to-many)
-- ----------------------
CREATE TABLE internship_skill (
    internship_id   INT NOT NULL REFERENCES internship(id) ON DELETE CASCADE,
    skill_id        INT NOT NULL REFERENCES skill(id)      ON DELETE CASCADE,
    PRIMARY KEY (internship_id, skill_id)
);


-- ----------------------
--  APPLICATION
-- ----------------------
CREATE TABLE application (
    id                  SERIAL PRIMARY KEY,
    student_id          INT         NOT NULL REFERENCES student(id)    ON DELETE CASCADE,
    internship_id       INT         NOT NULL REFERENCES internship(id) ON DELETE CASCADE,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn')),
    cv_snapshot_url     TEXT,
    applied_at          TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP   NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, internship_id)   -- prevent duplicate applications
);

CREATE INDEX idx_application_student    ON application (student_id);
CREATE INDEX idx_application_internship ON application (internship_id);
CREATE INDEX idx_application_status     ON application (status);


-- ----------------------
--  SAVED_INTERNSHIP  (student bookmarks)
-- ----------------------
CREATE TABLE saved_internship (
    student_id      INT         NOT NULL REFERENCES student(id)    ON DELETE CASCADE,
    internship_id   INT         NOT NULL REFERENCES internship(id) ON DELETE CASCADE,
    saved_at        TIMESTAMP   NOT NULL DEFAULT NOW(),
    PRIMARY KEY (student_id, internship_id)
);


-- ----------------------
--  REPORT  (flag fake/inappropriate internships)
-- ----------------------
CREATE TABLE report (
    id              SERIAL PRIMARY KEY,
    reporter_id     INT         NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    internship_id   INT         NOT NULL REFERENCES internship(id) ON DELETE CASCADE,
    reason          TEXT        NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'resolved', 'dismissed')),
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_report_internship ON report (internship_id);


-- ----------------------
--  NOTIFICATION
-- ----------------------
CREATE TABLE notification (
    id          SERIAL PRIMARY KEY,
    user_id     INT         NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    type        VARCHAR(50) NOT NULL,
    message     TEXT        NOT NULL,
    is_read     BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notification_user   ON notification (user_id);
CREATE INDEX idx_notification_unread ON notification (user_id) WHERE is_read = FALSE;


-- ----------------------
--  PASSWORD_RESET_TOKEN
-- ----------------------
CREATE TABLE password_reset_token (
    id          SERIAL PRIMARY KEY,
    user_id     INT         NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMP   NOT NULL,
    used        BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);


-- ----------------------
--  SYSTEM_LOG  (admin audit trail)
-- ----------------------
CREATE TABLE system_log (
    id              SERIAL PRIMARY KEY,
    admin_user_id   INT         NOT NULL REFERENCES "user"(id) ON DELETE SET NULL,
    action          VARCHAR(100) NOT NULL,
    target_type     VARCHAR(50),
    target_id       INT,
    note            TEXT,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_system_log_admin  ON system_log (admin_user_id);
CREATE INDEX idx_system_log_time   ON system_log (created_at DESC);
