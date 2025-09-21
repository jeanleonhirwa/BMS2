-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS `bms_db`;

-- Use the newly created database
USE `bms_db`;

-- A table to define the spending/income categories
-- We create this first as other tables depend on it
CREATE TABLE `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE
);

-- A table to hold all your income and expense records
CREATE TABLE `transactions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `transaction_date` DATE NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL,
    `type` VARCHAR(7) NOT NULL, -- 'income' or 'expense'
    `category_id` INT,
    `description` VARCHAR(255),
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`)
);

-- A table to manage your monthly budgets per category
CREATE TABLE `budgets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category_id` INT,
    `amount` DECIMAL(10, 2) NOT NULL,
    `month` INT NOT NULL,
    `year` INT NOT NULL,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`),
    UNIQUE(`category_id`, `month`, `year`) -- Ensures one budget per category per month
);

-- A table to track your savings goals
CREATE TABLE `savings_goals` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `target_amount` DECIMAL(10, 2) NOT NULL,
    `current_amount` DECIMAL(10, 2) DEFAULT 0.00
);

-- Insert some default categories to get you started
INSERT INTO `categories` (`name`) VALUES
('Parental Money'),
('Canteen/Food'),
('Internet'),
('Savings'),
('Other');
