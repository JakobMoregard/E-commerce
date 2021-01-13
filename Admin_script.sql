CREATE TABLE IF NOT EXISTS D0018E.Administrator
	   (AID			INT		NOT NULL,
		AFName		VARCHAR(16)		NOT NULL,
        ALName		VARCHAR(24)		NOT NULL,
        AMail		VARCHAR(32)		NOT NULL,
        APassword	VARCHAR(32)		NOT NULL,
        PRIMARY KEY(AID),
        UNIQUE(AID),
        UNIQUE(AMail));