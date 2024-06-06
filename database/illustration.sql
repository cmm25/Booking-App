-- Creating the ADMIN table
CREATE TABLE ADMIN (
  admin_id INT NOT NULL UNIQUE PRIMARY KEY,
  admin_name VARCHAR(50) NOT NULL,
  contact_no VARCHAR(15),
  email VARCHAR(100) UNIQUE,
  username VARCHAR(100) UNIQUE,
  date_of_birth DATE,
  password VARCHAR(100)
);

-- Creating the OWNER table
CREATE TABLE OWNER (
  owner_id INT NOT NULL UNIQUE PRIMARY KEY,
  owner_name VARCHAR(50) NOT NULL,
  contact_no VARCHAR(15),
  email VARCHAR(100) UNIQUE,
  username VARCHAR(100) UNIQUE,
  date_of_birth DATE,
  password VARCHAR(100),
  admin_id INT NOT NULL,
  FOREIGN KEY (admin_id) REFERENCES ADMIN(admin_id)
);


-- Creating the OWNER_REQUEST table
CREATE TABLE OWNER_REQUEST (
  request_id INT NOT NULL UNIQUE PRIMARY KEY,
  owner_id INT NOT NULL,
  hotel_name VARCHAR(100) NOT NULL,
  address VARCHAR(200) NOT NULL,
  city VARCHAR(50) NOT NULL,
  hotel_floors INT NOT NULL,
  rooms_present INT NOT NULL,
  request_date DATE NOT NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'approved', 'declined')),
  FOREIGN KEY (owner_id) REFERENCES OWNER(owner_id)
);

-- Creating the HOTEL table
CREATE TABLE HOTEL (
  hotel_id INT NOT NULL UNIQUE PRIMARY KEY,
  owner_id INT NOT NULL,
  admin_id INT NOT NULL,
  hotel_name VARCHAR(100) NOT NULL,
  address VARCHAR(200) NOT NULL,
  city VARCHAR(50) NOT NULL,
  hotel_floors INT NOT NULL,
  rooms_present INT NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES OWNER(owner_id),
  FOREIGN KEY (admin_id) REFERENCES ADMIN(admin_id)
);

-- Creating the ROOMS table
CREATE TABLE ROOMS (
  room_id INT NOT NULL UNIQUE PRIMARY KEY,
  hotel_id INT NOT NULL,
  room_type VARCHAR(50) NOT NULL,
  room_no VARCHAR(10) NOT NULL,
  bed_type VARCHAR(20),
  price DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id),
  UNIQUE (hotel_id, room_no)
);

-- Creating the CUSTOMER table
CREATE TABLE CUSTOMER (
  customer_id INT NOT NULL UNIQUE PRIMARY KEY,
  customer_name VARCHAR(100) NOT NULL,
  contact_no VARCHAR(15) NOT NULL,
  email VARCHAR(100) UNIQUE
);

-- Creating the RESERVATIONS table
CREATE TABLE RESERVATIONS (
  reservation_id INT NOT NULL UNIQUE PRIMARY KEY,
  customer_id INT NOT NULL,
  hotel_id INT NOT NULL,
  room_id INT NOT NULL,
  check_in DATE NOT NULL,
  check_out DATE NOT NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('rented', 'available', 'completed', 'canceled')),
  FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id),
  FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id),
  FOREIGN KEY (room_id) REFERENCES ROOMS(room_id),
  CHECK (check_in < check_out)
);

-- Creating the REVIEWS table
CREATE TABLE REVIEWS (
  review_id INT NOT NULL UNIQUE PRIMARY KEY,
  reservation_id INT NOT NULL,
  customer_id INT NOT NULL,
  hotel_id INT NOT NULL,
  room_id INT NOT NULL,
  review_date DATE NOT NULL,
  rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comments TEXT,
  FOREIGN KEY (reservation_id) REFERENCES RESERVATIONS(reservation_id),
  FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id),
  FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id),
  FOREIGN KEY (room_id) REFERENCES ROOMS(room_id)
);

-- Creating the FEEDBACK table
CREATE TABLE FEEDBACK (
  feedback_id INT NOT NULL UNIQUE PRIMARY KEY,
  review_id INT NOT NULL,
  admin_id INT NOT NULL,
  feedback_date DATE NOT NULL,
  comments TEXT,
  FOREIGN KEY (review_id) REFERENCES REVIEWS(review_id),
  FOREIGN KEY (admin_id) REFERENCES ADMIN(admin_id)
);

-- Creating the PAYMENTS table
CREATE TABLE PAYMENTS (
  payment_id INT NOT NULL UNIQUE PRIMARY KEY,
  reservation_id INT NOT NULL,
  payment_date DATE NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  payment_method VARCHAR(50),
  passed_to_owner BOOLEAN DEFAULT FALSE,
  admin_id INT NOT NULL,
  FOREIGN KEY (reservation_id) REFERENCES RESERVATIONS(reservation_id),
  FOREIGN KEY (admin_id) REFERENCES ADMIN(admin_id)
);

-- Creating indexes
CREATE INDEX idx_hotel_city ON HOTEL(city);
CREATE INDEX idx_customer_contact_no ON CUSTOMER(contact_no);
CREATE INDEX idx_reservations_customer_id ON RESERVATIONS(customer_id);
CREATE INDEX idx_reservations_hotel_id ON RESERVATIONS(hotel_id);
CREATE INDEX idx_reservations_room_id ON RESERVATIONS(room_id);
CREATE INDEX idx_reservations_check_in ON RESERVATIONS(check_in);
CREATE INDEX idx_reviews_customer_id ON REVIEWS(customer_id);
CREATE INDEX idx_reviews_hotel_id ON REVIEWS(hotel_id);
CREATE INDEX idx_reviews_room_id ON REVIEWS(room_id);
CREATE INDEX idx_feedback_review_id ON FEEDBACK(review_id);
CREATE INDEX idx_feedback_admin_id ON FEEDBACK(admin_id);
CREATE INDEX idx_payments_reservation_id ON PAYMENTS(reservation_id);
CREATE INDEX idx_hotel_room ON ROOMS(hotel_id, room_no);

-- Populating the ADMIN table
INSERT INTO ADMIN (admin_id, admin_name, contact_no, email, username, date_of_birth, password)
VALUES 
(1, 'Alice Smith', '123-456-7890', 'alice@example.com', 'alice_admin', '1985-05-15', 'alice_pass123'),
(2, 'Bob Johnson', '098-765-4321', 'bob@example.com', 'bob_admin', '1979-12-20', 'bob_pass123'),
(3, 'Catherine Lee', '234-567-8901', 'catherine@example.com', 'catherine_admin', '1980-08-10', 'cat_pass123'),
(4, 'David Harris', '345-678-9012', 'david@example.com', 'david_admin', '1990-02-25', 'dave_pass123'),
(5, 'Emily Davis', '456-789-0123', 'emily@example.com', 'emily_admin', '1982-11-30', 'emily_pass123');


-- Populating the OWNER table
INSERT INTO OWNER (owner_id, owner_name, contact_no, email, username, date_of_birth, password, admin_id)
VALUES 
(1, 'Henry Ford', '111-222-3333', 'henry@example.com', 'henry_owner', '1970-01-01', 'henry_pass123', 1),
(2, 'Jane Austen', '222-333-4444', 'jane@example.com', 'jane_owner', '1980-02-02', 'jane_pass123', 2),
(3, 'Mark Twain', '333-444-5555', 'mark@example.com', 'mark_owner', '1990-03-03', 'mark_pass123', 3),
(4, 'Mary Shelley', '444-555-6666', 'mary@example.com', 'mary_owner', '2000-04-04', 'mary_pass123', 4),
(5, 'William Shakespeare', '555-666-7777', 'william@example.com', 'william_owner', '1985-05-05', 'william_pass123', 5),
(6, 'Charlotte Bronte', '666-777-8888', 'charlotte@example.com', 'charlotte_owner', '1975-06-06', 'charlotte_pass123', 1),
(7, 'Leo Tolstoy', '777-888-9999', 'leo@example.com', 'leo_owner', '1988-07-07', 'leo_pass123', 2);

-- Populating the HOTEL table
INSERT INTO HOTEL (hotel_id, owner_id, admin_id, hotel_name, address, city, hotel_floors, rooms_present)
VALUES 
(1, 1, 1, 'Grand Plaza', '123 Main St, Springfield', 'Springfield', 10, 200),
(2, 2, 2, 'Ocean View', '456 Ocean Dr, Miami', 'Miami', 8, 150),
(3, 3, 3, 'Mountain Retreat', '789 Hill St, Denver', 'Denver', 5, 100),
(4, 4, 4, 'City Center Hotel', '321 Elm St, New York', 'New York', 12, 300),
(5, 5, 5, 'Lakeside Inn', '654 Lake Dr, Chicago', 'Chicago', 7, 120),
(6, 1, 1, 'Springfield Suites', '567 Maple Ave, Springfield', 'Springfield', 6, 100),
(7, 2, 2, 'Miami Beach Resort', '789 Palm St, Miami', 'Miami', 15, 250),
(8, 3, 3, 'Rocky Mountain Lodge', '123 Hilltop Rd, Denver', 'Denver', 8, 150);


-- Populating the ROOMS table
INSERT INTO ROOMS (room_id, hotel_id, room_type, room_no, bed_type, price)
VALUES 
-- Rooms for Grand Plaza
(1, 1, 'Deluxe', '101', 'King', 150.00),
(2, 1, 'Deluxe', '102', 'King', 150.00),
(3, 1, 'Suite', '201', 'Queen', 250.00),
(4, 1, 'Suite', '202', 'Queen', 250.00),
-- Rooms for Ocean View
(5, 2, 'Standard', '301', 'Double', 100.00),
(6, 2, 'Standard', '302', 'Double', 100.00),
(7, 2, 'Suite', '401', 'King', 200.00),
(8, 2, 'Suite', '402', 'King', 200.00),
-- Rooms for Mountain Retreat
(9, 3, 'Standard', '101', 'Double', 80.00),
(10, 3, 'Standard', '102', 'Double', 80.00),
(11, 3, 'Suite', '201', 'Queen', 150.00),
(12, 3, 'Suite', '202', 'Queen', 150.00),
-- Rooms for City Center Hotel
(13, 4, 'Deluxe', '501', 'King', 200.00),
(14, 4, 'Deluxe', '502', 'King', 200.00),
(15, 4, 'Penthouse', '601', 'King', 500.00),
(16, 4, 'Penthouse', '602', 'King', 500.00),
-- Rooms for Lakeside Inn
(17, 5, 'Standard', '301', 'Double', 110.00),
(18, 5, 'Standard', '302', 'Double', 110.00),
(19, 5, 'Suite', '401', 'King', 210.00),
(20, 5, 'Suite', '402', 'King', 210.00),
-- Rooms for Springfield Suites
(21, 6, 'Standard', '101', 'Double', 90.00),
(22, 6, 'Standard', '102', 'Double', 90.00),
(23, 6, 'Suite', '201', 'King', 180.00),
(24, 6, 'Suite', '202', 'King', 180.00),
-- Rooms for Miami Beach Resort
(25, 7, 'Standard', '301', 'Double', 120.00),
(26, 7, 'Standard', '302', 'Double', 120.00),
(27, 7, 'Suite', '401', 'King', 220.00),
(28, 7, 'Suite', '402', 'King', 220.00),
-- Rooms for Rocky Mountain Lodge
(29, 8, 'Standard','101', 'Double', 100.00),
(30, 8, 'Standard', '102', 'Double', 100.00),
(31, 8, 'Suite', '201', 'Queen', 180.00),
(32, 8, 'Suite', '202', 'Queen', 180.00);


-- Populating the CUSTOMER table
INSERT INTO CUSTOMER (customer_id, customer_name, contact_no, email)
VALUES 
(1, 'Charlie Brown', '555-123-4567', 'charlie@example.com'),
(2, 'Diana Prince', '555-234-5678', 'diana@example.com'),
(3, 'Ethan Hunt', '555-345-6789', 'ethan@example.com'),
(4, 'Fiona Gallagher', '555-456-7890', 'fiona@example.com'),
(5, 'George Martin', '555-567-8901', 'george@example.com');

-- Populating the RESERVATIONS table
INSERT INTO RESERVATIONS (reservation_id, customer_id, hotel_id, room_id, check_in, check_out, status)
VALUES 
(1, 1, 1, 1, '2024-06-01', '2024-06-05', 'completed'),
(2, 2, 2, 5, '2024-06-10', '2024-06-15', 'rented'),
(3, 3, 3, 9, '2024-07-01', '2024-07-07', 'available'),
(4, 4, 4, 13, '2024-08-05', '2024-08-10', 'completed'),
(5, 5, 5, 17, '2024-09-01', '2024-09-05', 'canceled');


-- Populating the REVIEWS table
INSERT INTO REVIEWS (review_id, reservation_id, customer_id, hotel_id, room_id, review_date, rating, comments)
VALUES 
(1, 1, 1, 1, 1, '2024-06-06', 5, 'Excellent stay, very comfortable and clean.'),
(2, 2, 2, 2, 3, '2024-06-16', 4, 'Great location, friendly staff.'),
(3, 3, 3, 3, 5, '2024-06-26', 3, 'Average experience, room could be cleaner.'),
(4, 4, 4, 4, 7, '2024-07-06', 5, 'Fantastic service and amenities.'),
(5, 5, 5, 5, 9, '2024-07-16', 2, 'Disappointing stay, issues with cleanliness.');

-- Populating the FEEDBACK table
INSERT INTO FEEDBACK (feedback_id, review_id, admin_id, feedback_date, comments)
VALUES 
(1, 1, 1, '2024-06-07', 'Thank you for your feedback! We hope to see you again soon.'),
(2, 2, 2, '2024-06-17', 'We appreciate your comments and are glad you enjoyed your stay.'),
(3, 3, 3, '2024-06-27', 'Thank you for the review. We will work on improving cleanliness.'),
(4, 4, 4, '2024-07-07', 'We are thrilled you had a great experience. Thank you!'),
(5, 5, 5, '2024-07-17', 'We apologize for the issues you faced. Your feedback is important.');

-- Populating the PAYMENTS table
INSERT INTO PAYMENTS (payment_id, reservation_id, payment_date, amount, payment_method, passed_to_owner, admin_id)
VALUES 
(1, 1, '2024-06-05', 750.00, 'Credit Card', TRUE, 1),
(2, 2, '2024-06-15', 500.00, 'Credit Card', TRUE, 2),
(3, 3, '2024-06-25', 400.00, 'Debit Card', FALSE, 3),
(4, 4, '2024-07-05', 1000.00, 'PayPal', TRUE, 4),
(5, 5, '2024-07-15', 550.00, 'Credit Card', FALSE, 5);

-- all hotels an owner has
SELECT o.owner_name, h.hotel_name
FROM OWNER o
JOIN HOTEL h ON o.owner_id = h.owner_id;

-- customer reviews from each hotel
SELECT a.admin_name, h.hotel_name, r.rating, r.comments
FROM ADMIN a
JOIN HOTEL h ON a.admin_id = h.admin_id
JOIN REVIEWS r ON h.hotel_id = r.hotel_id;

--approved payments
SELECT a.admin_name, p.payment_id, p.payment_date, p.amount
FROM ADMIN a
JOIN PAYMENTS p ON a.admin_id = p.admin_id
WHERE p.passed_to_owner = TRUE;
