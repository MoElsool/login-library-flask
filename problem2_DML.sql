USE library;

INSERT INTO AUTHOR (author_id, name, country) VALUES
(1, 'Naguib Mahfouz', 'Egypt'),
(2, 'Agatha Christie', 'United Kingdom'),
(3, 'Gabriel Garcia Marquez', 'Colombia'),
(4, 'Paulo Coelho', 'Brazil'),
(5, 'Taha Hussein', 'Egypt'),
(6, 'George Orwell', 'United Kingdom'),
(7, 'Fyodor Dostoevsky', 'Russia'),
(8, 'Jane Austen', 'United Kingdom'),
(9, 'Haruki Murakami', 'Japan');

INSERT INTO BOOK (book_id, title, price, author_id, pages) VALUES
(1, 'Palace Walk', 12.50, 1, 498),
(2, 'Midaq Alley', 9.99, 1, 243),
(3, 'The Thief and the Dogs', 8.75, 1, 160),
(4, 'Murder on the Orient Express', 11.00, 2, 256),
(5, 'And Then There Were None', 10.50, 2, 272),
(6, 'One Hundred Years of Solitude', 14.25, 3, 417),
(7, 'Love in the Time of Cholera', 13.00, 3, 348),
(8, 'The Alchemist', 9.50, 4, 208),
(9, 'The Days', 8.50, 5, 320),
(10, 'The Tree of Misery', 9.00, 5, 192),
(11, 'Nineteen Eighty-Four', 10.99, 6, 328),
(12, 'Animal Farm', 7.99, 6, 112),
(13, 'Crime and Punishment', 12.00, 7, 545),
(14, 'The Brothers Karamazov', 14.50, 7, 796),
(15, 'Pride and Prejudice', 8.99, 8, 279),
(16, 'Emma', 9.25, 8, 474),
(17, 'Norwegian Wood', 11.50, 9, 296),
(18, 'Kafka on the Shore', 13.75, 9, 505);
