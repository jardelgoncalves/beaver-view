CREATE USER 'beaver_user'@'localhost' IDENTIFIED BY 'JNFBEEzXp397';
CREATE DATABASE beaver_db;
GRANT ALL PRIVILEGES ON beaver_db.* TO 'beaver_user'@'localhost';
FLUSH PRIVILEGES;
