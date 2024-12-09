PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

CREATE TABLE Users (
    userId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    userName VARCHAR(100) NOT NULL UNIQUE,
    firstName VARCHAR(100) DEFAULT NULL,
    lastName VARCHAR(100) DEFAULT NULL,
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

CREATE TABLE UserSettings (
    userSettingsId INTEGER PRIMARY KEY NOT NULL UNIQUE,
    FOREIGN KEY (userSettingsId) REFERENCES Users(userId)
);

CREATE TABLE Mailboxes (
    mailboxId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    mbUser INTEGER NOT NULL,
    mbName VARCHAR(100) NOT NULL UNIQUE,
    mbType INTEGER NOT NULL DEFAULT 0,
    mbSend BOOLEAN NOT NULL DEFAULT 1,
    mbReceive BOOLEAN NOT NULL DEFAULT 1,
    mbReadConf BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (mbUser) REFERENCES Users(userId)
);

CREATE TABLE Messages (
    messageId VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
    receiverId VARCHAR(255) DEFAULT NULL,
    messageMailbox INTEGER NOT NULL,
    messageTimestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    messageType INTEGER NOT NULL DEFAULT 0,
    isSent BOOLEAN NOT NULL DEFAULT 0, -- 0 means you received the message
    messageFrom VARCHAR(100) NOT NULL,
    messageTo VARCHAR(100) NOT NULL,
    messageContent TEXT NOT NULL,
    readConfirm BOOLEAN NOT NULL DEFAULT 0,
    messageSent BOOLEAN NOT NULL DEFAULT 0,
    messageAttachments TEXT DEFAULT NULL,
    messageUnsubscribe VARCHAR(255) DEFAULT NULL,
    messageRead BOOLEAN DEFAULT NULL,
    FOREIGN KEY (messageMailbox) REFERENCES Mailboxes(mailboxId)
);

CREATE TABLE Attachments (
    attachmentId VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
    attachmentIdReceive VARCHAR(255) DEFAULT NULL,
    attachmentMessage VARCHAR(255) NOT NULL,
    attachmentLocation VARCHAR(255),
    attachmentExpire INTEGER DEFAULT NULL,
    attachmentExpireRet BOOLEAN NOT NULL DEFAULT 1,
    attachmentName VARCHAR(255) NOT NULL,
    attachmentRetrieved BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (attachmentMessage) REFERENCES Messages(messageId)
);

INSERT INTO Users(userName, displayName, password, isAdmin) VALUES ("admin", "Admin", "$2b$12$Xoo6simQ/GCzqV9j.HGyCu35SDyQpKT0JtpJOhWCJcc60b12oe5y.", 1);

COMMIT;