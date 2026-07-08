CREATE DATABASE IF NOT EXISTS moneytree DEFAULT CHARACTER SET utf8mb4;
USE moneytree;

CREATE TABLE IF NOT EXISTS goals (
    id VARCHAR(32) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nodes (
    id VARCHAR(64) PRIMARY KEY,
    goal_id VARCHAR(32) NOT NULL,
    title VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    status VARCHAR(32) DEFAULT 'locked',
    summary TEXT,
    learned_at VARCHAR(64),
    verified_at VARCHAR(64),
    INDEX idx_goal (goal_id)
);

CREATE TABLE IF NOT EXISTS node_deps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id VARCHAR(64) NOT NULL,
    depends_on VARCHAR(64) NOT NULL,
    INDEX idx_node (node_id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id VARCHAR(64),
    role VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    phase VARCHAR(16) DEFAULT 'teach',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_node (node_id)
);

CREATE TABLE IF NOT EXISTS journal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date VARCHAR(32),
    action VARCHAR(32),
    asset VARCHAR(128),
    amount VARCHAR(64),
    cost VARCHAR(64),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
