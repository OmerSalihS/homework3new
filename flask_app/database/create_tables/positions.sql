CREATE TABLE IF NOT EXISTS positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inst_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    responsibilities VARCHAR(500) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE DEFAULT NULL,
    FOREIGN KEY (inst_id) REFERENCES institutions(inst_id)
);