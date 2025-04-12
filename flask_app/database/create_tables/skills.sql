CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    experience_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    skill_level INT CHECK (skill_level BETWEEN 1 AND 10),
    FOREIGN KEY (experience_id) REFERENCES experiences(experience_id) ON DELETE CASCADE
);
