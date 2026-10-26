USE company;

INSERT INTO EMPLOYEE (ssn, fname, lname, bdate, address, gender, salary, Dno) VALUES
('123456789', 'Ahmed', 'Hassan', '1985-03-12', '12 Fouad St, Alexandria', 'M', 12000.00, NULL),
('987654321', 'Sara', 'Mostafa', '1990-07-25', '5 Tahrir Sq, Cairo', 'F', 9500.00, NULL),
('456789123', 'Omar', 'Khaled', '1988-11-02', '30 Pyramids Rd, Giza', 'M', 8200.50, NULL),
('321654987', 'Mona', 'Adel', '1992-01-18', '8 Corniche, Alexandria', 'F', 7000.00, NULL),
('654987321', 'Youssef', 'Nabil', '1983-09-30', '21 El Gomhoria St, Mansoura', 'M', 15000.00, NULL);

INSERT INTO DEPARTMENT (Dnumber, Dname, mgr_ssn, mgr_start_date) VALUES
(1, 'Engineering', '123456789', '2018-01-01'),
(2, 'Marketing', '987654321', '2020-06-15'),
(3, 'Finance', '654987321', '2019-09-01');

UPDATE EMPLOYEE SET Dno = 1 WHERE ssn IN ('123456789', '456789123');
UPDATE EMPLOYEE SET Dno = 2 WHERE ssn IN ('987654321', '321654987');
UPDATE EMPLOYEE SET Dno = 3 WHERE ssn = '654987321';

INSERT INTO PROJECT (Pnumber, Pname, Plocation, Dno) VALUES
(10, 'Website Redesign', 'Alexandria', 1),
(20, 'Ad Campaign', 'Cairo', 2),
(30, 'Budget Audit', 'Giza', 3),
(40, 'Mobile App', 'Alexandria', 1);
