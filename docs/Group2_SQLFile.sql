CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    telephone VARCHAR(20),
    password VARCHAR(255)
);

CREATE TABLE Lodge (
    lodge_id INT PRIMARY KEY,
    lodge_name VARCHAR(100),
    lodge_description VARCHAR(500),
	lodge_image VARCHAR(100)
);

CREATE TABLE Room_Type (
    room_type_id INT PRIMARY KEY,
    room_size VARCHAR(50),
    nightly_rate DECIMAL(6,2)
);

CREATE TABLE Reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    lodge_id INT,
    room_type_id INT,
    number_of_guests INT,
    check_in_date DATE,
    check_out_date DATE,
    total_cost DECIMAL(8,2),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (lodge_id) REFERENCES Lodge(lodge_id),
    FOREIGN KEY (room_type_id) REFERENCES Room_Type(room_type_id)
);

INSERT INTO Customer
    (customer_id, first_name, last_name, email, telephone, password)
VALUES
    (1, 'Olivia', 'Carter', 'olivia.carter@example.com', '314-555-0101', 'OliviaPass123'),
    (2, 'Liam', 'Bennett', 'liam.bennett@example.com', '636-555-0102', 'LiamPass456'),
    (3, 'Sophia', 'Mitchell', 'sophia.mitchell@example.com', '573-555-0103', 'SophiaPass789');

INSERT INTO Lodge
    (lodge_id, lodge_name, lodge_description, lodge_image)
VALUES
    (1, 'Cedar Hollow Lodge', "Tucked beneath old-growth cedars just a short walk from the pool, "
                    "this lodge blends rustic timber charm with modern comfort. "
                    "Wood-burning fireplaces, wraparound porches, and a view of the "
                    "strait make this the island's coziest retreat.",
		'/images/CedarStrait.png'),
    (2, 'Whistling Strait Inn', "Perched on the bluffs overlooking Joviedsa's windswept northern "
                    "coast, this inn is known for its floor-to-ceiling windows and "
                    "front-row seats to passing orcas. Perfect for early risers who "
                    "don't mind a stiff sea breeze.",
		'/images/WhistlingStrait.png'),
    (3, 'Fembrook Retreat', "Surrounded by moss-draped forest trails and a quiet freshwater "
                    "creek, Fembrook is the island's go-to for hikers and hammock "
                    "campers alike. Each cabin comes with its own outdoor cooking "
                    "tub.",
		'/images/Fembrook.png'),
	(4, 'Harbor Light Lodge', "Set right in Joviedsa's small fishing village, this lodge puts "
                    "guests steps from the docks, local seafood shacks, and the weekly "
                    "farmers market. Rooms feature nautical decor and views of the "
                    "working harbor.",
		'/images/HarborLight.png'),
	(5, 'Ravenwood Lodge', "A dark, moodier option nestled deep in the island's interior "
                    "forest, Ravenwood leans into rustic-luxury with stone fireplaces, "
                    "exposed timber beams, and a reputation for spotting the resident "
                    "raven flock at dusk.",
		'/images/Ravenwood.png'),
	(6, 'Tidepool Bluff Cottages', "A cluster of small, private cottages along the southern shoreline, "
                    "each with a private path down to tide pools teeming with starfish "
                    "and anemones. Popular with families and low-key beach lovers.",
		'/images/TidepoolBluff.png');

INSERT INTO Room_Type
    (room_type_id, room_size, nightly_rate)
VALUES
    (1, 'double full beds', 120.00),
    (2, 'queen', 135.00),
    (3, 'double queen beds', 150.00),
    (4, 'king', 160.00);

INSERT INTO Reservation
    (reservation_id, customer_id, lodge_id, room_type_id, number_of_guests,
     check_in_date, check_out_date, total_cost)
VALUES
    (1, 1, 1, 1, 2, '2026-10-10', '2026-10-13', 360.00),
    (2, 2, 2, 2, 3, '2026-11-05', '2026-11-08', 405.00),
    (3, 3, 3, 3, 4, '2026-12-20', '2026-12-22', 300.00);
