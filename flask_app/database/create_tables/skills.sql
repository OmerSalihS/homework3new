CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    experience_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    skill_level INTEGER CHECK (skill_level BETWEEN 1 AND 10),
    FOREIGN KEY (experience_id) REFERENCES experiences(experience_id) ON DELETE CASCADE
);
