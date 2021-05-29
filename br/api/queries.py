# -*- coding: utf-8 -*-
COUNTRY_REPORTING_QUERY = '''
SELECT
    COUNT(DISTINCT rc.id) AS total_centres,
    COUNT(DISTINCT br.location_id) AS reporting_centres,
    COUNT(CASE WHEN rc.created >= %s AND rc.created <= %s THEN 1 END) as new_centres,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.boys_5to9 + br.boys_10to18 + br.girls_5to9 + br.girls_10to18) AS five_plus,
    SUM(br.boys_below1) AS u1_boys,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys,
    SUM(br.boys_5to9 + br.boys_10to18) AS five_plus_boys,
    SUM(br.girls_below1) AS u1_girls,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.girls_5to9 + br.girls_10to18) AS five_plus_girls,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT OUTER JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
WHERE
    rc.type_id = 8
'''

COUNTRY_REPORTING_LITE_QUERY = '''
SELECT
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.boys_5to9 + br.boys_10to18 + br.girls_5to9 + br.girls_10to18) AS five_plus,
    SUM(br.boys_below1) AS u1_boys,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys,
    SUM(br.boys_5to9 + br.boys_10to18) AS five_plus_boys,
    SUM(br.girls_below1) AS u1_girls,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.girls_5to9 + br.girls_10to18) AS five_plus_girls,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT OUTER JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
WHERE
    rc.type_id = 8
'''

COUNTRY_PREV_U1_QUERY = '''
SELECT
    SUM(br.girls_below1 + br.boys_below1) AS prev_u1
FROM
    locations_location AS rc
JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8
'''


STATE_REPORTING_QUERY = '''
SELECT
    state.name as loc,
    state.id as loc_id,
    COUNT(DISTINCT rc.id) AS total_centres,
    COUNT(DISTINCT br.location_id) AS reporting_centres,
    COUNT(CASE WHEN rc.created >= %s AND rc.created <= %s THEN 1 END) as new_centres,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.boys_5to9 + br.boys_10to18 + br.girls_5to9 + br.girls_10to18) AS five_plus,
    SUM(br.boys_below1) AS u1_boys,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys,
    SUM(br.boys_5to9 + br.boys_10to18) AS five_plus_boys,
    SUM(br.girls_below1) AS u1_girls,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.girls_5to9 + br.girls_10to18) AS five_plus_girls,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT OUTER JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

STATE_REPORTING_LITE_QUERY = '''
SELECT
    state.name as loc,
    state.id as loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.boys_5to9 + br.boys_10to18 + br.girls_5to9 + br.girls_10to18) AS five_plus,
    SUM(br.boys_below1) AS u1_boys,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys,
    SUM(br.boys_5to9 + br.boys_10to18) AS five_plus_boys,
    SUM(br.girls_below1) AS u1_girls,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.girls_5to9 + br.girls_10to18) AS five_plus_girls,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT OUTER JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

LGA_REPORTING_QUERY = '''
SELECT
    lga.name as loc,
    lga.id as loc_id,
    COUNT(DISTINCT rc.id) AS total_centres,
    COUNT(DISTINCT br.location_id) AS reporting_centres,
    COUNT(CASE WHEN rc.created >= %s AND rc.created <= %s THEN 1 END) as new_centres,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.boys_5to9 + br.boys_10to18 + br.girls_5to9 + br.girls_10to18) AS five_plus,
    SUM(br.boys_below1) AS u1_boys,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys,
    SUM(br.boys_5to9 + br.boys_10to18) AS five_plus_boys,
    SUM(br.girls_below1) AS u1_girls,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.girls_5to9 + br.girls_10to18) AS five_plus_girls,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
WHERE
    rc.type_id = 8
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

LGA_REPORTING_LITE_QUERY = '''
SELECT
    lga.name as loc,
    lga.id as loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS u1,
    SUM(br.girls_below1 + br.boys_below1 + br.girls_1to4 + br.boys_1to4) AS u5,
    SUM(br.boys_5to9 + br.boys_10to18 + br.girls_5to9 + br.girls_10to18) AS five_plus,
    SUM(br.boys_below1) AS u1_boys,
    SUM(br.boys_below1 + br.boys_1to4) AS u5_boys,
    SUM(br.boys_5to9 + br.boys_10to18) AS five_plus_boys,
    SUM(br.girls_below1) AS u1_girls,
    SUM(br.girls_below1 + br.girls_1to4) AS u5_girls,
    SUM(br.girls_5to9 + br.girls_10to18) AS five_plus_girls,
    SUM(br.girls_below1 + br.girls_1to4 + br.girls_5to9 + br.girls_10to18) AS girls,
    SUM(br.boys_below1 + br.boys_1to4 + br.boys_5to9 + br.boys_10to18) AS boys
FROM
    locations_location AS rc
LEFT JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
WHERE
    rc.type_id = 8
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

STATE_PREV_U1_QUERY = '''
SELECT
    state.name AS loc,
    state.id AS loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS prev_u1
FROM
    locations_location AS rc
JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS state ON rc.lft >= state.lft AND rc.rgt <= state.rgt AND state.type_id = 2
WHERE
    rc.type_id = 8
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''

LGA_PREV_U1_QUERY = '''
SELECT
    lga.name AS loc,
    lga.id AS loc_id,
    SUM(br.girls_below1 + br.boys_below1) AS prev_u1
FROM
    locations_location AS rc
JOIN
    br_birthregistration AS br ON rc.id = br.location_id AND br.time >= %s AND br.time <= %s
JOIN
    locations_location AS lga ON rc.parent_id = lga.id
WHERE
    rc.type_id = 8
GROUP BY
    loc, loc_id
ORDER BY
    loc
'''
