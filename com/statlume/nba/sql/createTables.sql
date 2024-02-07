CREATE TABLE IF NOT EXISTS Schedule (
    GameID int NOT NULL AUTO_INCREMENT,
    GameDate date NOT NULL,
    Home varchar(255) NOT NULL REFERENCES Teams(TeamName),
    Visitor varchar(255) NOT NULL REFERENCES Teams(TeamName),
    PRIMARY KEY (GameID)
);

CREATE TABLE IF NOT EXISTS PlayerStats (
    PlayerID int NOT NULL AUTO_INCREMENT,
    FullName varchar(255) NOT NULL,
    TeamID int NOT NULL,
    TeamName varchar(255),
    MinutesPlayed decimal(3, 1) NOT NULL,
    PointsPerGame decimal(3, 1) NOT NULL,
    Rebounds decimal(3, 1) NOT NULL,
    Assists decimal(3, 1) NOT NULL,
    Steals decimal(3, 1) NOT NULL,
    Blocks decimal(3, 1) NOT NULL,
    Turnovers decimal(3, 1) NOT NULL,
    PRIMARY KEY (PlayerID),
    FOREIGN KEY (TeamID) REFERENCES Teams(id)
);

CREATE TABLE IF NOT EXISTS TeamStats (
    TeamID int NOT NULL,
    TeamName varchar(255) NOT NULL,
    Abbreviation varchar(3) NOT NULL,
    OppFGPercent decimal(3, 3) NOT NULL,
    OppOffReboundsPerGame decimal(3, 1) NOT NULL,
    OppDefReboundsPerGame decimal(3, 1) NOT NULL,
    OppReboundsPerGame decimal(3, 1) NOT NULL,
    OppAssistsPerGame decimal(3, 1) NOT NULL,
    OppStealsPerGame decimal(3, 1) NOT NULL,
    OppBlocksPerGame decimal(3, 1) NOT NULL,
    OppPointsPerGame decimal(4, 1) NOT NULL,
    TurnoversPerGame decimal(3, 1) NOT NULL,
    FOREIGN KEY (TeamID) REFERENCES Teams(id)
);