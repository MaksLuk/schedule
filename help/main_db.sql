create database if not exists `pgu_project` default character set utf8 collate utf8_general_ci;
CREATE USER 'pgu_admin'@'localhost'
  IDENTIFIED BY 'adminpass' PASSWORD EXPIRE;
ALTER USER `pgu_admin`@`localhost` IDENTIFIED BY 'new_password', `pgu_admin`@`localhost` PASSWORD EXPIRE NEVER;
GRANT ALL PRIVILEGES ON *.* TO 'pgu_admin'@'localhost' WITH GRANT OPTION;
USE pgu_project;

CREATE TABLE user_types (
    `id` TINYINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(5) NOT NULL UNIQUE,
    `full_name` VARCHAR(30) NOT NULL UNIQUE
);
INSERT INTO user_types(name, full_name) VALUES ('user', 'Пользователь'), ('admin', 'Администратор'), ('block', 'Заблокирован');

CREATE TABLE users (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email_address` VARCHAR(35) NOT NULL UNIQUE,
    `full_name` VARCHAR(55) NOT NULL,
    `password` VARCHAR(30) NOT NULL,
    `user_type` TINYINT NOT NULL DEFAULT 1,
    FOREIGN KEY (`user_type`) REFERENCES user_types(`id`)
);

CREATE TABLE projects (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(30) NOT NULL,
    `admin_id` INT NOT NULL,
    `db_name` VARCHAR(20) NOT NULL UNIQUE,
    `db_user` VARCHAR(20) NOT NULL DEFAULT 'pgu_admin',
    `db_pass` VARCHAR(30) NOT NULL DEFAULT 'new_password',
    `db_host` VARCHAR(40) NOT NULL DEFAULT 'localhost',
    FOREIGN KEY (`admin_id`) REFERENCES users(`id`)
);

CREATE TABLE project_workers (
    `user_id` INT NOT NULL,
    `project_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES users(`id`),
    FOREIGN KEY (`project_id`) REFERENCES projects(`id`)
);

-- INSERT INTO users(`email_address`, `full_name`, `password`, `user_type`) VALUES ('admin@gmail.com', 'admin', 'pass', 2);