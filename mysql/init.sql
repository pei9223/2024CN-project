CREATE DATABASE IF NOT EXISTS labapp;
USE labapp;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;

-- SET GLOBAL time_zone = 'Asia/Taipei';
-- SET system_time_zone = CST
-- SET SQL_MODE='ALLOW_INVALID_DATES';
SET explicit_defaults_for_timestamp=ON;


CREATE TABLE orders (
  serialNo INT NOT NULL AUTO_INCREMENT,
  serialString VARCHAR(50) NOT NULL,
  priority ENUM('regular', 'urgent', 'emergency') NOT NULL,
  factory ENUM('Fab A', 'Fab B', 'Fab C') NOT NULL,
  lab ENUM('chemical', 'surface', 'composition') NOT NULL,
  status ENUM('Issued', 'Approved', 'Completed', 'Rejected') NOT NULL,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  createdBy VARCHAR(50) NOT NULL,
  filePath VARCHAR(255) DEFAULT NULL,
  approvedAt TIMESTAMP DEFAULT NULL,
  approvedBy VARCHAR(50) DEFAULT NULL,
  completedAt TIMESTAMP DEFAULT NULL,
  completedBy VARCHAR(50) DEFAULT NULL,
  description VARCHAR(1000) DEFAULT NULL,
  PRIMARY KEY (serialNo)
);

CREATE TABLE users (
  userID VARCHAR(50) NOT NULL,
  userPassword VARCHAR(255) NOT NULL,
  dep ENUM('Fab A', 'Fab B', 'Fab C', 'chemical', 'surface', 'composition') NOT NULL,
  email VARCHAR(255) NOT NULL,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (userID)
);

-- Insert default users
INSERT INTO users (userID, userPassword, dep, email) VALUES 
('user_fabA', 'password', 'Fab A', 'tonywon.cs08@nycu.edu.tw'),
('user_fabB', 'password', 'Fab B', 'tonywon.cs08@nycu.edu.tw'),
('user_fabC', 'password', 'Fab C', 'tonywon.cs08@nycu.edu.tw'),
('user_chemical', 'password', 'chemical', 'tonywon.cs08@nycu.edu.tw'),
('user_surface', 'password', 'surface', 'tonywon.cs08@nycu.edu.tw'),
('user_composition', 'password', 'composition', 'tonywon.cs08@nycu.edu.tw');