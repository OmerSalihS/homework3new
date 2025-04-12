CREATE TABLE experiences (
    experience_id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    hyperlink VARCHAR(500),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE CASCADE
);
