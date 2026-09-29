-- IaaS database schema.
--
-- Create the database first (or edit the USE statement below), then run:
--   mysql -u root -p < DB/schema.sql
--
-- The users table stores an RSA-2048 public key in plaintext (it is public by
-- definition) and the matching private key still wrapped by AWS KMS, so the
-- application never persists an unwrapped private key.

CREATE DATABASE IF NOT EXISTS iaas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE iaas;

CREATE TABLE IF NOT EXISTS users (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    username              VARCHAR(100) NOT NULL UNIQUE,
    -- The user's password, RSA-OAEP encrypted with their own public key.
    password              BLOB NOT NULL,
    full_name             VARCHAR(100) NOT NULL,
    -- PEM-encoded RSA-2048 public key.
    public_key            BLOB NOT NULL,
    -- The same private key, still encrypted by AWS KMS.
    cyphered_private_key  BLOB NOT NULL,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
