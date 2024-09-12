PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

CREATE TABLE Users (
    userId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    userName VARCHAR(30) NOT NULL UNIQUE,
    firstName VARCHAR(100),
    lastName VARCHAR(100),
    displayName VARCHAR(100) NOT NULL,
    company VARCHAR(100) DEFAULT NULL,
    password TEXT NOT NULL,
    isAdmin BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE Permissions (
    permissionsId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    permissionName VARCHAR(100) NOT NULL
);

CREATE TABLE UserPermissions (
    userPermissionsId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    permission INTEGER NOT NULL DEFAULT 0,
    permissionUser INTEGER NOT NULL DEFAULT 0,
    appliesToUser INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (permissionUser) REFERENCES Users(userId),
    FOREIGN KEY (appliesToUser) REFERENCES Users(userId),
    FOREIGN KEY (permission) REFERENCES Permissions(permissionsId)
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
    userSettingsId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    FOREIGN KEY (userSettingsId) REFERENCES Users(userId)
);

CREATE TABLE Mailboxes (
    mailboxId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    mbType INTEGER NOT NULL DEFAULT 0,
    mbSend BOOLEAN NOT NULL DEFAULT 1,
    mbReceive BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (mailboxId) REFERENCES Users(userId)
);

CREATE TABLE Messages (
    messageId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    messageTimestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    messageType INTEGER NOT NULL DEFAULT 0,
    isSent BOOLEAN NOT NULL DEFAULT 0, -- 0 means you received the message
    messageFrom VARCHAR(100) NOT NULL,
    messageTo VARCHAR(100) NOT NULL,
    messageContent TEXT NOT NULL,
    deliveryConfirm BOOLEAN NOT NULL DEFAULT 1,
    readConfirm BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (messageId) REFERENCES Mailboxes(mailboxId)
);

CREATE TABLE Attachments (
    attachmentId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    FOREIGN KEY (attachmentId) REFERENCES Messages(messageId)
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