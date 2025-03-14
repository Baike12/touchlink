-- 创建用户数据库
CREATE DATABASE IF NOT EXISTS user_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用用户数据库
USE user_database;

-- 创建用户表信息表，用于记录用户创建的表
CREATE TABLE IF NOT EXISTS user_table_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建表字段信息表，用于记录用户创建的表的字段信息
CREATE TABLE IF NOT EXISTS user_table_column (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    column_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_name) REFERENCES user_table_info(table_name) ON DELETE CASCADE,
    UNIQUE KEY (table_name, column_name)
); 