CREATE DATABASE AwsFinalProject;

CREATE TABLE Accounts(
    user_id BIGINT NULL AUTO_INCREMENT,
    user_name VARCHAR(20) NULL,
    user_password VARCHAR(100) NULL,
    PRIMARY KEY (user_id)
);
