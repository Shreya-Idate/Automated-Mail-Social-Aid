drop table registered
create table registered(
prn varchar(7) PRIMARY KEY NOT NULL,
name varchar NOT NULL,
birth_day int NOT NULL,
birth_month int NOT NULL,
birth_year int NOT NULL,
email varchar (40) NOT NULL)

insert into registered(prn,name,birth_day,birth_month,birth_year,email) values (1,'Parag',18,3,2001,'paragdudhmal9177@gmail.com'),
(2,'Rayan',10,2,2000,'ryanbranwen4572@gmail.com'),(3,'Sneha',2,3,2002,'baitalsneha@gmail.com'),
(4,'Shreya',24,3,2002,'shreya.idate2002@gmail.com');

select * from registered