-- ============================================================
-- Smart Waste Management System — SQL Queries
-- CS 331 Database Systems | NJIT
-- Author: Pruthul Patel
-- Database: MySQL | Tables: 18 | Records: 49,932+
-- ============================================================

-- HOW TO USE:
-- 1. Load the schema file first in MySQL or db-fiddle.com
-- 2. Select MySQL 8.0 on db-fiddle.com
-- 3. Run queries one by one on the right side

-- ============================================================
-- BEGINNER QUERIES
-- ============================================================

-- Query 1: Find names of users who used a bin between 2-3pm
-- Joins: User → LocationSensor → LocationObservation
-- Result: 75 users found

SELECT DISTINCT u.name
FROM User u, LocationSensor ls, LocationObservation lo
WHERE u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp >= '2019-10-26 14:00:00'
AND lo.timestamp <= '2019-10-26 15:00:00';


-- Query 2: Find inside bins used by Visitors between 2-3pm
-- "Inside" means bin X,Y coordinates fall within building boundaries
-- Result: 22 bins found

SELECT DISTINCT wb.waste_bin_id, wb.X, wb.Y
FROM WasteBin wb, Building b,
     ObjectRecognitionSensor ors,
     ObjectRecognitionObservation oro,
     LocationObservation lo,
     LocationSensor ls,
     Visitor v
WHERE wb.X >= b.boxLowX AND wb.X <= b.boxUpperX
AND wb.Y >= b.boxLowY AND wb.Y <= b.boxUpperY
AND wb.waste_bin_id = ors.Waste_bin_id
AND ors.sensor_id = oro.sensor_id
AND lo.timestamp = oro.timestamp
AND lo.sensor_id = ls.sensor_id
AND ls.User_id = v.user_id
AND oro.timestamp >= '2019-10-26 14:00:00'
AND oro.timestamp <= '2019-10-26 15:00:00';


-- Query 3: Find students who put wrong trash in recycling bin
-- Wrong = trash type is NOT 'Recycle' but bin IS a RecycleBin
-- Result: 13 students found

SELECT DISTINCT u.name
FROM User u, Student s,
     LocationSensor ls,
     LocationObservation lo,
     ObjectRecognitionObservation oro,
     ObjectRecognitionSensor ors,
     RecycleBin rb
WHERE u.user_id = s.user_id
AND u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp = oro.timestamp
AND oro.sensor_id = ors.sensor_id
AND ors.Waste_bin_id = rb.waste_bin_id
AND oro.Trash_type != 'Recycle'
AND oro.timestamp >= '2019-10-26 14:00:00'
AND oro.timestamp <= '2019-10-26 15:00:00';


-- Query 4: Find users with more than 100 landfill disposal events
-- Uses GROUP BY + HAVING (HAVING filters after grouping, not before)
-- Result: 144 users found | Top user: Cora with 3,063 events

SELECT u.user_id, u.name, COUNT(*) AS total_events
FROM User u, LocationSensor ls,
     LocationObservation lo,
     ObjectRecognitionObservation oro,
     ObjectRecognitionSensor ors,
     LandfillBin lb
WHERE u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp = oro.timestamp
AND oro.sensor_id = ors.sensor_id
AND ors.Waste_bin_id = lb.waste_bin_id
GROUP BY u.user_id, u.name
HAVING total_events > 100
ORDER BY total_events DESC;


-- ============================================================
-- INTERMEDIATE QUERIES
-- ============================================================

-- Query 5: Top 10 users by total compost weight WITH rank number
-- Uses RANK() window function and subquery
-- Result: User 55 (Cora) ranked #1 with highest compost weight

SELECT user_id,
       ROUND(total_weight, 0) AS total_weight,
       RANK() OVER (ORDER BY total_weight DESC) AS user_rank
FROM (
    SELECT u.user_id, SUM(lob.Weight) AS total_weight
    FROM User u, LocationSensor ls,
         LocationObservation lo,
         ObjectRecognitionObservation oro,
         ObjectRecognitionSensor ors,
         CompostBin cb,
         LoadSensor lsen,
         LoadObservation lob
    WHERE u.user_id = ls.User_id
    AND ls.sensor_id = lo.sensor_id
    AND lo.timestamp = oro.timestamp
    AND oro.sensor_id = ors.sensor_id
    AND ors.Waste_bin_id = cb.waste_bin_id
    AND cb.waste_bin_id = lsen.Waste_bin_id
    AND lsen.sensor_id = lob.sensor_id
    GROUP BY u.user_id
) AS ranked_users
ORDER BY user_rank
LIMIT 10;


-- ============================================================
-- VIEWS — Role-Based Access Control (RBAC)
-- ============================================================

-- Query 6: App Users View
-- Shows only bins that are: inside a building AND not currently full
-- Current time assumed: 2019-10-26 13:00:00
-- Run this: SELECT * FROM App_Users;

CREATE VIEW App_Users AS
SELECT wb.waste_bin_id AS waste_bin_id,
       wb.X AS x,
       wb.Y AS y,
       CASE
           WHEN rb.waste_bin_id IS NOT NULL THEN 'Recycle'
           WHEN lb.waste_bin_id IS NOT NULL THEN 'LandFill'
           WHEN cb.waste_bin_id IS NOT NULL THEN 'Compost'
       END AS type_of_bin
FROM WasteBin wb, Building b
LEFT JOIN RecycleBin rb ON wb.waste_bin_id = rb.waste_bin_id
LEFT JOIN LandfillBin lb ON wb.waste_bin_id = lb.waste_bin_id
LEFT JOIN CompostBin cb ON wb.waste_bin_id = cb.waste_bin_id
WHERE wb.X >= b.boxLowX AND wb.X <= b.boxUpperX
AND wb.Y >= b.boxLowY AND wb.Y <= b.boxUpperY
AND wb.waste_bin_id IN (
    SELECT lsen.Waste_bin_id
    FROM LoadSensor lsen, LoadObservation lob
    WHERE lsen.sensor_id = lob.sensor_id
    AND lob.Weight < wb.capacity
    AND lob.timestamp <= '2019-10-26 13:00:00'
);

SELECT * FROM App_Users;


-- Query 7: Sustainability Analysts View
-- Shows bin location + department + total weight
-- NO student names, NO trash types (privacy protection)
-- Run this: SELECT * FROM Sustainability_Analysts;

CREATE VIEW Sustainability_Analysts AS
SELECT wb.waste_bin_id AS waste_bin_id,
       wb.X AS x,
       wb.Y AS y,
       s.dept_name AS Department,
       SUM(lob.Weight) AS total_weight
FROM WasteBin wb, ObjectRecognitionSensor ors,
     ObjectRecognitionObservation oro,
     LocationObservation lo,
     LocationSensor ls,
     Student s,
     LoadSensor lsen,
     LoadObservation lob
WHERE wb.waste_bin_id = ors.Waste_bin_id
AND ors.sensor_id = oro.sensor_id
AND lo.timestamp = oro.timestamp
AND lo.sensor_id = ls.sensor_id
AND ls.User_id = s.user_id
AND wb.waste_bin_id = lsen.Waste_bin_id
AND lsen.sensor_id = lob.sensor_id
GROUP BY wb.waste_bin_id, wb.X, wb.Y, s.dept_name;

SELECT * FROM Sustainability_Analysts;


-- Query 8: Facility Managers View
-- Shows each user, each day, how many times they used each bin type
-- Uses CASE WHEN inside SUM() to count by bin type
-- Run this: SELECT * FROM Facility_Managers;

CREATE VIEW Facility_Managers AS
SELECT u.name AS Name,
       DATE(oro.timestamp) AS Day,
       SUM(CASE WHEN cb.waste_bin_id IS NOT NULL THEN 1 ELSE 0 END) AS Compost_Bin,
       SUM(CASE WHEN lb.waste_bin_id IS NOT NULL THEN 1 ELSE 0 END) AS LandFill_Bin,
       SUM(CASE WHEN rb.waste_bin_id IS NOT NULL THEN 1 ELSE 0 END) AS Recycle_Bin
FROM User u, LocationSensor ls,
     LocationObservation lo,
     ObjectRecognitionObservation oro,
     ObjectRecognitionSensor ors
LEFT JOIN CompostBin cb ON ors.Waste_bin_id = cb.waste_bin_id
LEFT JOIN LandfillBin lb ON ors.Waste_bin_id = lb.waste_bin_id
LEFT JOIN RecycleBin rb ON ors.Waste_bin_id = rb.waste_bin_id
WHERE u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp = oro.timestamp
AND oro.sensor_id = ors.sensor_id
GROUP BY u.name, DATE(oro.timestamp);

SELECT * FROM Facility_Managers;


-- ============================================================
-- TRIGGERS
-- ============================================================

-- Query 9: Replace bad sensor readings with NULL automatically
-- Fires BEFORE every INSERT on LoadObservation
-- Bad reading = jumps more than 1000 units within 24 hours
--            OR sensor already has a NULL reading recorded

DELIMITER //

CREATE TRIGGER check_erroneous_load
BEFORE INSERT ON LoadObservation
FOR EACH ROW
BEGIN
    DECLARE last_weight INT;
    DECLARE last_time DATETIME;
    DECLARE has_null INT;

    -- check if this sensor already has any null reading
    SELECT COUNT(*) INTO has_null
    FROM LoadObservation
    WHERE sensor_id = NEW.sensor_id
    AND Weight IS NULL;

    -- get the most recent reading for this sensor
    SELECT Weight, timestamp INTO last_weight, last_time
    FROM LoadObservation
    WHERE sensor_id = NEW.sensor_id
    ORDER BY timestamp DESC
    LIMIT 1;

    -- rule b: already has a null reading → set new one null too
    IF has_null > 0 THEN
        SET NEW.Weight = NULL;

    -- rule a: value jumps more than 1000 within 24 hours → bad reading
    ELSEIF last_weight IS NOT NULL
        AND DATEDIFF(NEW.timestamp, last_time) <= 1
        AND ABS(NEW.Weight - last_weight) > 1000 THEN
        SET NEW.Weight = NULL;
    END IF;

END //

DELIMITER ;

-- Test it with these inserts:
INSERT INTO LoadObservation(sensor_id, oid, Weight, timestamp)
VALUES (350, 50001, 15000, '2017-07-07 20:00:55');

INSERT INTO LoadObservation(sensor_id, oid, Weight, timestamp)
VALUES (350, 50002, 15500, '2017-07-17 22:00:55');

INSERT INTO LoadObservation(sensor_id, oid, Weight, timestamp)
VALUES (350, 50003, 17000, '2017-07-18 20:45:55');

INSERT INTO LoadObservation(sensor_id, oid, Weight, timestamp)
VALUES (350, 50004, 17500, '2017-07-20 20:50:55');

-- Check results (expect: row 1 = 15000, rows 2,3,4 = NULL):
SELECT * FROM LoadObservation
WHERE sensor_id = 350 AND oid > 50000;


-- Query 10: Auto-log trash violations when wrong trash is thrown
-- First create the violations table, then create the trigger
-- Fires AFTER every INSERT on ObjectRecognitionObservation

-- Step 1: Create violations table
CREATE TABLE TrashViolations (
    TVID INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    timestamp DATETIME,
    waste_bin_id INT,
    trash_type VARCHAR(30)
);

-- Step 2: Create the trigger
DELIMITER //

CREATE TRIGGER record_trash_violation
AFTER INSERT ON ObjectRecognitionObservation
FOR EACH ROW
BEGIN
    DECLARE bin_id INT;
    DECLARE uid INT;
    DECLARE is_wrong INT DEFAULT 0;

    -- find which bin this sensor belongs to
    SELECT Waste_bin_id INTO bin_id
    FROM ObjectRecognitionSensor
    WHERE sensor_id = NEW.sensor_id;

    -- find which user was near the bin at this time
    SELECT ls.User_id INTO uid
    FROM LocationSensor ls, LocationObservation lo
    WHERE ls.sensor_id = lo.sensor_id
    AND lo.timestamp = NEW.timestamp
    LIMIT 1;

    -- check if trash type does not match the bin type
    IF (SELECT COUNT(*) FROM RecycleBin
        WHERE waste_bin_id = bin_id) > 0
        AND NEW.Trash_type != 'Recycle' THEN
        SET is_wrong = 1;
    END IF;

    IF (SELECT COUNT(*) FROM LandfillBin
        WHERE waste_bin_id = bin_id) > 0
        AND NEW.Trash_type != 'LandFill' THEN
        SET is_wrong = 1;
    END IF;

    IF (SELECT COUNT(*) FROM CompostBin
        WHERE waste_bin_id = bin_id) > 0
        AND NEW.Trash_type != 'Compost' THEN
        SET is_wrong = 1;
    END IF;

    -- if wrong bin, log it in TrashViolations table
    IF is_wrong = 1 THEN
        INSERT INTO TrashViolations(user_id, timestamp, waste_bin_id, trash_type)
        VALUES (uid, NEW.timestamp, bin_id, NEW.Trash_type);
    END IF;

END //

DELIMITER ;

-- Test it:
INSERT INTO LocationObservation(sensor_id, oid, timestamp, X, Y)
VALUES (1, 100001, '2017-11-15 14:00:00', 5459, 3576);

INSERT INTO ObjectRecognitionObservation(sensor_id, oid, timestamp, trash_type)
VALUES (354, 200001, '2017-11-15 14:00:00', 'LandFill');

-- Check violations logged (bin 51 is CompostBin, LandFill thrown = violation):
SELECT * FROM TrashViolations;
