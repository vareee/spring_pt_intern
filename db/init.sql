CREATE TABLE if NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE if NOT EXISTS phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL
);

INSERT INTO emails (email) VALUES ('example1@example.com');
INSERT INTO emails (email) VALUES ('test1@test.com');

INSERT INTO phone_numbers (phone_number) VALUES ('89325678912');
INSERT INTO phone_numbers (phone_number) VALUES ('+79123456789');

