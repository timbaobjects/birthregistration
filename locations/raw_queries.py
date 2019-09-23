# -*- coding: utf-8 -*-
FACILITY_QUERY = '''
SELECT
    loc.name, loc.active, loc.latitude, loc.longitude, typ.name AS type
FROM
    locations_facility AS fac
JOIN
    locations_location AS loc ON fac.location_id = loc.id
JOIN
    locations_locationtype AS typ ON loc.type_id = typ.id
JOIN
    locations_location AS ans ON (loc.lft >= ans.lft AND loc.rgt <= ans.rgt)
WHERE
    ans.id = %s;
'''
