-- seed_destinations.sql
-- Tabla: Destination
INSERT INTO app_destination (id, name) VALUES
(1, 'Bariloche'),
(2, 'Madrid'),
(3, 'Buenos Aires'),
(4, 'Roma'),
(5, 'Tokio'),
(6, 'Nueva York'),
(7, 'Sydney'),
(8, 'Londres'),
(9, 'París'),
(10, 'El Calafate');

-- Tabla: DestinationImage
INSERT INTO app_destinationimage (id, destination_id, image_url) VALUES
(1, 1, 'https://flydestinations.s3.us-east-2.amazonaws.com/bariloche.jpg'),
(2, 2, 'https://flydestinations.s3.us-east-2.amazonaws.com/madrid.jpg'),
(3, 3, 'https://flydestinations.s3.us-east-2.amazonaws.com/buenos_aires.jpg'),
(4, 4, 'https://flydestinations.s3.us-east-2.amazonaws.com/roma.jpg'),
(5, 5, 'https://flydestinations.s3.us-east-2.amazonaws.com/tokio.jpg'),
(6, 6, 'https://flydestinations.s3.us-east-2.amazonaws.com/nueva_york.jpg'),
(7, 7, 'https://flydestinations.s3.us-east-2.amazonaws.com/sydney.jpg'),
(8, 8, 'https://flydestinations.s3.us-east-2.amazonaws.com/londres.jpg'),
(9, 9, 'https://flydestinations.s3.us-east-2.amazonaws.com/paris.jpg'),
(10, 10, 'https://flydestinations.s3.us-east-2.amazonaws.com/calafate.jpg');
