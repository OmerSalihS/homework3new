CREATE TABLE feedback (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    comment TEXT NOT NULL
);
