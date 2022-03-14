PREPARE CREATE_SERVER (VARCHAR, VARCHAR) AS
    INSERT INTO SERVER VALUES($1, $2);
PREPARE CREATE_STARBOARD (INTEGER, VARCHAR, VARCHAR) AS
    INSERT INTO STARBOARD VALUES($1, $2, $3);
PREPARE CREATE_STAR_MESSAGE (VARCHAR, INTEGER, VARCHAR) AS
    INSERT INTO STAR_MESSAGE VALUES($1, $2, $3);
PREPARE CREATE_CLASS (VARCHAR, VARCHAR, VARCHAR, VARCHAR) AS
    INSERT INTO CLASS VALUES($1, $2, $3, $4);
PREPARE CREATE_CLASS_GROUP (INTEGER, VARCHAR) AS
    INSERT INTO CLASS_GROUP VALUES($1, $2);
PREPARE CREATE_CLASS_IN_GROUP_RELATION (VARCHAR, VARCHAR, INTEGER) AS
    INSERT INTO CLASS_IN_GROUP_RELATION VALUES($1, $2, $3);
PREPARE CREATE_I_ROLE (VARCHAR) AS
    INSERT INTO I_ROLE VALUES($1);
PREPARE CREATE_ROLE_ENTRY (VARCHAR, VARCHAR) AS
    INSERT INTO ROLE_ENTRY VALUES($1, $2);
PREPARE CREATE_CLASS_ROLE (VARCHAR, VARCHAR, VARCHAR, VARCHAR) AS
    INSERT INTO CLASS_ROLE VALUES($1, $2, $3, $4);
PREPARE CREATE_ROLE_GROUP (VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) AS
    INSERT INTO ROLE_GROUP VALUES($1, $2, $3, $4, $5, $6);
PREPARE CREATE_ROLE_MENU (VARCHAR, VARCHAR, VARCHAR, VARCHAR) AS
    INSERT INTO ROLE_MENU VALUES($1, $2, $3, $4);