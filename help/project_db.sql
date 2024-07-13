-- факультеты
CREATE TABLE faculties (
    `id` TINYINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(7) NOT NULL UNIQUE
);

-- кафедры
CREATE TABLE departments (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(7) NOT NULL UNIQUE,
    `faculty` TINYINT NOT NULL,
    FOREIGN KEY (`faculty`) REFERENCES faculties(`id`)
);

-- специальности
CREATE TABLE specialities (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(35) NOT NULL UNIQUE,
    `department` INT NOT NULL,
    FOREIGN KEY (`department`) REFERENCES departments(`id`)
);

-- группы
CREATE TABLE `groups` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(7) NOT NULL UNIQUE,
    `students_count` TINYINT NOT NULL,
    `speciality` INT NOT NULL,
    FOREIGN KEY (`speciality`) REFERENCES specialities(`id`)
);

-- преподаватели
CREATE TABLE teachers (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(35) NOT NULL UNIQUE,
    `department` INT NOT NULL,
    FOREIGN KEY (`department`) REFERENCES departments(`id`)
);

-- аудитории
CREATE TABLE classrooms (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `number` VARCHAR(7) NOT NULL UNIQUE,
    `size` TINYINT NOT NULL,
    `faculty` TINYINT NOT NULL,
    `department` INT,
    FOREIGN KEY (`faculty`) REFERENCES faculties(`id`),
    FOREIGN KEY (`department`) REFERENCES departments(`id`)
);

-- предметы
CREATE TABLE subjects (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(35) NOT NULL,
    `hours` INT NULL,
    `department` INT NOT NULL,
    `main_teacher` INT NOT NULL,
    `second_teacher` INT,
    `group` INT NOT NULL,
    FOREIGN KEY (`main_teacher`) REFERENCES teachers(`id`),
    FOREIGN KEY (`second_teacher`) REFERENCES teachers(`id`),
    FOREIGN KEY (`group`) REFERENCES `groups`(`id`),
    FOREIGN KEY (`department`) REFERENCES departments(`id`)
);

ALTER TABLE subjects ADD COLUMN `short_name` VARCHAR(10) NOT NULL;

-- ячейка расписания
CREATE TABLE schedule (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `week` BOOLEAN NOT NULL,
    `pair_number` TINYINT NOT NULL,
    `day_number` TINYINT NOT NULL,
    `group` INT NOT NULL,
    `classroom` INT NOT NULL,
    `subject` INT NOT NULL,
    FOREIGN KEY (`group`) REFERENCES `groups`(`id`),
    FOREIGN KEY (`classroom`) REFERENCES classrooms(`id`),
    FOREIGN KEY (`subject`) REFERENCES subjects(`id`)
);