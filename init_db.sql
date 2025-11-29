CREATE DATABASE IF NOT EXISTS fashionista CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fashionista;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  name VARCHAR(255),
  is_admin TINYINT(1) DEFAULT 0
);

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  brand VARCHAR(100),
  price DECIMAL(10,2),
  image VARCHAR(255),
  description TEXT,
  sizes VARCHAR(255),
  colors VARCHAR(255)
);

INSERT INTO users (email, password, name, is_admin) VALUES ('admin@fashionista.test', 'adminpass', 'Admin', 1);

INSERT INTO products (name, brand, price, image, description, sizes, colors) VALUES
('Rosy Satin Dress', 'Petal & Co', 49.99, 'rosy_satin.svg', 'Elegant rosy satin mini dress — perfect for parties.', 'S,M,L', 'pink'),
('Sunset Maxi', 'Amber Lane', 69.00, 'sunset_maxi.svg', 'Flowy maxi with warm orange tones.', 'M,L', 'orange,peach'),
('Candy Crop Top', 'SugarPop', 19.50, 'candy_top.svg', 'Playful crop top in bubblegum pink.', 'XS,S,M', 'pink'),
('Blush Trench', 'UrbanChic', 89.99, 'blush_trench.svg', 'Lightweight trench coat in blush pink.', 'M,L,XL', 'blush'),
('Coral Knit', 'Knit&Co', 39.00, 'coral_knit.svg', 'Cozy coral knit sweater for cool evenings.', 'S,M,L,XL', 'coral');
