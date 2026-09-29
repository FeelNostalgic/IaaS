USE test_db;
drop table users;

CREATE TABLE IF NOT EXISTS users (
     id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password BLOB NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    public_key BLOB NOT NULL,
    cyphered_private_key BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, full_name, public_key, cyphered_private_key) 
VALUES ('test1',
 'test1',
 'test 1',
 '0',
 '0');
                       
delete from users where username = 'JohnD';

select * from users;