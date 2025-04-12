CREATE TABLE feedback (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    email VARCHAR(255),
    comment TEXT NOT NULL
);
