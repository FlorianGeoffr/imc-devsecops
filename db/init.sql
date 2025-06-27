CREATE DATABASE IF NOT EXISTS imc_db;
USE imc_db;

CREATE TABLE IF NOT EXISTS imc_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    poids FLOAT,
    taille FLOAT,
    imc FLOAT
);
