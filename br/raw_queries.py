# -*- coding: utf-8 -*-
NATIONAL_REPORTING_QUERY = '''
SELECT state_table.name AS state,
state_table.id AS state_id,
COUNT(DISTINCT br_birthregistration.location_id) AS loc_count,
SUM(br_birthregistration.girls_below1) AS girls_below1,
SUM(br_birthregistration.girls_1to4) AS girls_1to4,
SUM(br_birthregistration.girls_5to9) AS girls_5to9,
SUM(br_birthregistration.girls_10to18) AS girls_10to18,
SUM(br_birthregistration.boys_below1) AS boys_below1,
SUM(br_birthregistration.boys_1to4) AS boys_1to4,
SUM(br_birthregistration.boys_5to9) AS boys_5to9,
SUM(br_birthregistration.boys_10to18) AS boys_10to18
FROM
locations_location AS rc_table
JOIN locations_location AS lga_table ON rc_table.parent_id = lga_table.id
JOIN locations_location AS state_table ON lga_table.parent_id = state_table.id
JOIN br_birthregistration ON rc_table.id = br_birthregistration.location_id
WHERE br_birthregistration.time BETWEEN %s AND %s AND br_birthregistration.disabled = FALSE
GROUP BY state, state_id ORDER BY state;
'''

NATIONAL_CUMULATIVE_QUERY = '''
SELECT state_table.name AS state,
state_table.id AS state_id,
COUNT(DISTINCT br_birthregistration.location_id) AS loc_count,
SUM(br_birthregistration.girls_below1) AS girls_below1,
SUM(br_birthregistration.girls_1to4) AS girls_1to4,
SUM(br_birthregistration.girls_5to9) AS girls_5to9,
SUM(br_birthregistration.girls_10to18) AS girls_10to18,
SUM(br_birthregistration.boys_below1) AS boys_below1,
SUM(br_birthregistration.boys_1to4) AS boys_1to4,
SUM(br_birthregistration.boys_5to9) AS boys_5to9,
SUM(br_birthregistration.boys_10to18) AS boys_10to18
FROM
locations_location AS rc_table
JOIN locations_location AS lga_table ON rc_table.parent_id = lga_table.id
JOIN locations_location AS state_table ON lga_table.parent_id = state_table.id
JOIN br_birthregistration ON rc_table.id = br_birthregistration.location_id
WHERE br_birthregistration.time <= %s AND br_birthregistration.disabled = FALSE
GROUP BY state, state_id ORDER BY state;
'''

STATE_REPORTING_QUERY = '''
SELECT lga_table.name AS lga, lga_table.id AS lga_id, rc_table.name AS rc,
COUNT(DISTINCT br_birthregistration.location_id) AS loc_count,
SUM(br_birthregistration.girls_below1) AS girls_below1,
SUM(br_birthregistration.girls_1to4) AS girls_1to4,
SUM(br_birthregistration.girls_5to9) AS girls_5to9,
SUM(br_birthregistration.girls_10to18) AS girls_10to18,
SUM(br_birthregistration.boys_below1) AS boys_below1,
SUM(br_birthregistration.boys_1to4) AS boys_1to4,
SUM(br_birthregistration.boys_5to9) AS boys_5to9,
SUM(br_birthregistration.boys_10to18) AS boys_10to18
FROM
locations_location AS rc_table
JOIN locations_location AS lga_table ON rc_table.parent_id = lga_table.id
JOIN br_birthregistration ON rc_table.id = br_birthregistration.location_id
WHERE br_birthregistration.time BETWEEN %s AND %s AND br_birthregistration.disabled = FALSE
AND lga_table.parent_id = %s
GROUP BY lga, lga_id, rc ORDER BY lga, rc;
'''

STATE_CUMULATIVE_QUERY = '''
SELECT lga_table.name AS lga, lga_table.id AS lga_id, rc_table.name AS rc,
COUNT(DISTINCT br_birthregistration.location_id) AS loc_count,
SUM(br_birthregistration.girls_below1) AS girls_below1,
SUM(br_birthregistration.girls_1to4) AS girls_1to4,
SUM(br_birthregistration.girls_5to9) AS girls_5to9,
SUM(br_birthregistration.girls_10to18) AS girls_10to18,
SUM(br_birthregistration.boys_below1) AS boys_below1,
SUM(br_birthregistration.boys_1to4) AS boys_1to4,
SUM(br_birthregistration.boys_5to9) AS boys_5to9,
SUM(br_birthregistration.boys_10to18) AS boys_10to18
FROM
locations_location AS rc_table
JOIN locations_location AS lga_table ON rc_table.parent_id = lga_table.id
JOIN br_birthregistration ON rc_table.id = br_birthregistration.location_id
WHERE lga_table.parent_id = %s AND br_birthregistration.time <= %s
AND br_birthregistration.disabled = FALSE
GROUP BY lga, lga_id, rc ORDER BY lga, rc;
'''

NATIONAL_PRIOR_U1_REPORTING_QUERY = '''
SELECT state_table.id AS state_id,
SUM(br_birthregistration.girls_below1) + SUM(br_birthregistration.boys_below1)
AS u1
FROM
locations_location AS rc_table
JOIN locations_location AS lga_table ON rc_table.parent_id = lga_table.id
JOIN locations_location AS state_table ON lga_table.parent_id = state_table.id
JOIN br_birthregistration ON rc_table.id = br_birthregistration.location_id
WHERE br_birthregistration.time BETWEEN %s AND %s AND br_birthregistration.disabled = FALSE
GROUP BY state_id ORDER BY state_table.name;
'''


STATE_PRIOR_U1_REPORTING_QUERY = '''
SELECT lga_table.id AS lga_id,
SUM(br_birthregistration.girls_below1) + SUM(br_birthregistration.boys_below1)
AS u1
FROM
locations_location AS rc_table
JOIN locations_location AS lga_table ON rc_table.parent_id = lga_table.id
JOIN br_birthregistration ON rc_table.id = br_birthregistration.location_id
WHERE br_birthregistration.time BETWEEN %s AND %s AND br_birthregistration.disabled = FALSE
AND lga_table.parent_id = %s
GROUP BY lga_id ORDER BY lga_table.name;
'''

CENSUS_QUERY = '''
'''

REPORTING_RANGE_QUERY = '''
SELECT
    MIN(br_birthregistration.time),
    MAX(br_birthregistration.time)
FROM
    br_birthregistration;
'''

STATE_NODES_QUERY = '''
SELECT st.id, st.name FROM locations_location AS st
JOIN locations_locationtype AS lt ON st.type_id = lt.id
WHERE lt.name = 'State' ORDER BY st.name;
'''

LGA_NODES_QUERY = '''
SELECT loc.id, loc.name, lt.name FROM
locations_location AS loc JOIN locations_locationtype AS lt
ON loc.type_id = lt.id WHERE loc.lft > %s AND loc.rgt < %s
AND lt.name in ('LGA', 'RC') ORDER BY loc.lft;
'''

DATA_QUERY = '''
SELECT
    lga.name as lga,
    lga.id as lga_id,
    state.name AS state,
    state.id AS state_id,
    COUNT(DISTINCT rc.id) AS centre_count,
    COUNT(DISTINCT br.location_id) AS reporting_centre_count,
    COUNT(CASE WHEN br.id IS NULL THEN 1 END) AS missing,
    SUM(br.girls_below1) AS girls_below1,
    SUM(br.girls_1to4) AS girls_1to4,
    SUM(br.girls_5to9) AS girls_5to9,
    SUM(br.girls_10to18) AS girls_10to18,
    SUM(br.boys_below1) AS boys_below1,
    SUM(br.boys_1to4) AS boys_1to4,
    SUM(br.boys_5to9) AS boys_5to9,
    SUM(br.boys_10to18) AS boys_10to18,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br
ON
    br.location_id = rc.id AND br.time BETWEEN %s AND %s
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
JOIN
    locations_location AS state ON lga.parent_id = state.id
JOIN
    locations_location AS loc ON (rc.lft >= loc.lft AND rc.rgt <= loc.rgt)
WHERE
    loc.id = %s AND rc.type_id = 8 AND br_birthregistration.disabled = FALSE
GROUP BY
    lga, lga_id, state, state_id
ORDER BY
    state, lga;
'''

PRIOR_DATA_QUERY = '''
SELECT
    lga.name as lga,
    lga.id as lga_id,
    state.name AS state,
    state.id AS state_id,
    SUM(br.girls_below1 + br.boys_below1) AS u1
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br
ON
    br.location_id = rc.id AND br.time BETWEEN %s AND %s
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
JOIN
    locations_location AS state ON lga.parent_id = state.id
JOIN
    locations_location AS loc ON (rc.lft >= loc.lft AND rc.rgt <= loc.rgt)
WHERE
    loc.id = %s AND rc.type_id = 8 AND br_birthregistration.disabled = FALSE
GROUP BY
    lga_id, state_id
ORDER BY
    state, lga;
'''

CENTRE_REPORTING_QUERY = '''
SELECT
    lga.name AS lga,
    lga.id AS lga_id,
    state.name AS state,
    state.id AS state_id,
    COUNT(DISTINCT rc.id) AS total,
    COUNT(CASE WHEN br.id IS NULL THEN 1 END) AS missing
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON br.location_id = rc.id AND br.time BETWEEN %s AND %s
JOIN
    locations_location AS loc ON (rc.lft >= loc.lft AND rc.rgt <= loc.rgt)
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
JOIN
    locations_location AS state ON lga.parent_id = state.id
WHERE
    loc.id = %s AND rc.type_id = 8
GROUP BY
    lga_id, state_id
ORDER BY
    state, lga
'''
