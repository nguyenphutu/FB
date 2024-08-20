-- setup_database.sql
CREATE DATABASE IF NOT EXISTS fb_db;

USE fb_db;

CREATE TABLE IF NOT EXISTS groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255),
    group_info VARCHAR(255),
    group_link VARCHAR(255),
    group_member VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_name VARCHAR(255),
    post_user_name VARCHAR(255),
    post_user_link VARCHAR(255),
    post_info VARCHAR(255),
    post_link VARCHAR(255),
    post_like VARCHAR(255),
    post_share VARCHAR(255),
    post_comment VARCHAR(255),
    post_media TEXT
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_info TEXT,
    comment_link VARCHAR(255),
    comment_user_name VARCHAR(255),
    comment_user_link VARCHAR(255)
);