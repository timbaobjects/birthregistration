# -*- coding: utf-8 -*-
NATIONAL_REPORTING_QUERY = '''
SELECT
    state.name as loc,
    state.id as loc_id,
    COUNT(DISTINCT rc.id) AS total_centres,
    COUNT(DISTINCT br.location_id) AS reporting_centres,
    COUNT(CASE WHEN rc.created >= %s AND rc.created <= %s THEN 1 END) as new_centres,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON rc.id = br.location_id
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8 AND br.time >= %s AND br.time <= %s
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

NATIONAL_REPORTING_LITE_QUERY = '''
SELECT
    state.name as loc,
    state.id as loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON rc.id = br.location_id
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8 AND br.time >= %s AND br.time <= %s
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

STATE_REPORTING_QUERY = '''
SELECT
    lga.name as loc,
    lga.id as loc_id,
    COUNT(DISTINCT rc.id) AS total_centres,
    COUNT(DISTINCT br.location_id) AS reporting_centres,
    COUNT(CASE WHEN rc.created >= %s AND rc.created <= %s THEN 1 END) as new_centres,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON rc.id = br.location_id
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
WHERE
    rc.type_id = 8 AND br.time >= %s AND br.time <= %s AND lga.parent_id = %s
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

STATE_REPORTING_LITE_QUERY = '''
SELECT
    lga.name as loc,
    lga.id as loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON rc.id = br.location_id
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
WHERE
    rc.type_id = 8 AND br.time >= %s AND br.time <= %s AND lga.parent_id = %s
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

NATIONAL_PREV_U1_QUERY = '''
SELECT
    state.name AS loc,
    state.id AS loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS prev_u1
FROM
    locations_location AS rc
JOIN
    br_birthregistration AS br ON rc.id = br.location_id
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8 AND br.time >= %s AND br.time <= %s
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

STATE_PREV_U1_QUERY = '''
SELECT
    lga.name AS loc,
    lga.id AS loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS prev_u1
FROM
    locations_location AS rc
JOIN
    br_birthregistration AS br ON rc.id = br.location_id
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
WHERE
    rc.type_id = 8 AND br.time >= %s AND br.time <= %s AND lga.parent_id = %s
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''