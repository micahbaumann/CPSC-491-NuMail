PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

CREATE TABLE Users (
    UserId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Username VARCHAR(30) NOT NULL UNIQUE,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    DisplayName VARCHAR(100) NOT NULL,
    Password VARCHAR(1000) NOT NULL
);

-- CREATE TABLE Classes (
--     ClassID INT NOT NULL UNIQUE,
--     CourseCode VARCHAR(15) NOT NULL DEFAULT 'XXX 001',
--     SectionNumber INT NOT NULL,
--     Name VARCHAR(100) DEFAULT "Class",
--     MaximumEnrollment INT DEFAULT 30,
--     WaitlistCount INT DEFAULT 0,
--     WaitlistMaximum INT DEFAUlT 15,
--     PRIMARY KEY (ClassID, SectionNumber)
-- );

CREATE TABLE UserSettings (
    UserSettingsId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    FOREIGN KEY (UserSettingsId) REFERENCES Users(UserId)
);

CREATE TABLE Mailboxes (
    MailboxId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    MBType INTEGER NOT NULL DEFAULT 0,
    MBSend BOOLEAN NOT NULL DEFAULT 1,
    MBReceive BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (MailboxId) REFERENCES Users(UserId)
);

CREATE TABLE Messages (
    MessageId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    MessageTimestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    MessageType INTEGER NOT NULL DEFAULT 0,
    IsSent BOOLEAN NOT NULL DEFAULT 0, -- 0 means you received the message
    MessageFrom VARCHAR(100) NOT NULL,
    MessageTo VARCHAR(100) NOT NULL,
    MessageContent TEXT NOT NULL,
    DeliveryConfirm BOOLEAN NOT NULL DEFAULT 1,
    ReadConfirm BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (MessageId) REFERENCES Mailboxes(MailboxId)
);

CREATE TABLE Attachments (
    AttachmentId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    FOREIGN KEY (AttachmentId) REFERENCES Messages(MessageId)
);

-- CREATE TABLE Enrollments (
--     EnrollmentID INTEGER         NOT NULL PRIMARY KEY AUTOINCREMENT,
--     StudentID INT                NOT NULL,
--     ClassID INT                  NOT NULL,
--     SectionNumber INT            NOT NULL,
--     EnrollmentStatus VARCHAR(25) NOT NULL DEFAULT "ENROLLED",
--     FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
--     FOREIGN KEY (ClassID, SectionNumber) REFERENCES Classes(ClassID, SectionNumber)
-- );

-- CREATE TABLE Instructors (
--     InstructorID INTEGER PRIMARY KEY NOT NULL UNIQUE,
--     FOREIGN KEY (InstructorID) REFERENCES Users(UserId)
-- );

-- CREATE TABLE InstructorClasses (
--     InstructorClassesID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
--     InstructorID INT            NOT NULL,
--     ClassID INT                 NOT NULL,
--     SectionNumber INT           NOT NULL,
--     FOREIGN KEY (InstructorID) REFERENCES Instructors(InstructorID),
--     FOREIGN KEY (ClassID, SectionNumber) REFERENCES Classes(ClassID, SectionNumber)
-- );

-- CREATE TABLE Waitlists (
--     WaitlistID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
--     StudentID INT      NOT NULL,
--     ClassID INT        NOT NULL,
--     SectionNumber INT  NOT NULL,
--     Position INT       NOT NULL,
--     FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
--     FOREIGN KEY (ClassID, SectionNumber) REFERENCES Classes(ClassID, SectionNumber)
-- );

-- CREATE TABLE Freeze (
--     IsFrozen BOOLEAN DEFAULT 0
-- );

-- INSERT INTO Freeze VALUES (0);

COMMIT;