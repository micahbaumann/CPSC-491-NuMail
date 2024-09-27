PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

INSERT INTO Users(userName, firstName, lastName, displayName, company, password, isAdmin) VALUES
('micahbaumann', 'Micah', 'Baumann', 'Micah Baumann', 'Ruts Technologies', "pbkdf2_sha256$600000$c9fc625a0e406cec90594958016ac631$5iDVmwSTF6K9K110LWBxH/xi0ZvwpgKt3y8gAMz0GzQ=", 1),
('usertwo', 'User', 'Two', 'User Two', 'U2, inc', "pbkdf2_sha256$600000$c9fc625a0e406cec90594958016ac631$5iDVmwSTF6K9K110LWBxH/xi0ZvwpgKt3y8gAMz0GzQ=", 0),
('userthree', 'User', 'Three', 'User Three', 'U3, inc', "pbkdf2_sha256$600000$c9fc625a0e406cec90594958016ac631$5iDVmwSTF6K9K110LWBxH/xi0ZvwpgKt3y8gAMz0GzQ=", 0),
('userfour', 'User', 'Four', 'User Four', 'U4, inc', "pbkdf2_sha256$600000$c9fc625a0e406cec90594958016ac631$5iDVmwSTF6K9K110LWBxH/xi0ZvwpgKt3y8gAMz0GzQ=", 0),
('userfive', 'User', 'Five', 'User Five', 'U5, inc', "pbkdf2_sha256$600000$c9fc625a0e406cec90594958016ac631$5iDVmwSTF6K9K110LWBxH/xi0ZvwpgKt3y8gAMz0GzQ=", 0);



COMMIT;