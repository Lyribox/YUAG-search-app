"""
Program Name: prepsql.py
Function: Contains modularized SQLite queries for data extraction
Usage: Import into a py module that handles the connection to the database
"""

# Function: SQLite snippet for limiting the number of results
# Usage: Concatenate at the end of non-limited query
LIMITER = "LIMIT 1000"

# Function: Query for producing table of objects with ID, label, date, agent and their parts,
#     and a comma-separated list of classifiers
# Usage: Use as base of the query and concatenate WHERE statements onto it as required
OBJECTS_SRCH = """WITH classifications AS (
        SELECT id,
        IFNULL(group_concat(lower(name), ', '), '') AS 'classified'
        FROM (
            SELECT o.id, c.name AS name
            FROM objects o
            LEFT JOIN objects_classifiers oc ON o.id = oc.obj_id
            LEFT JOIN classifiers c ON oc.cls_id = c.id
            ORDER BY lower(c.name) ASC
            )
        GROUP BY id
        ),
    agent_data AS (
        SELECT id,
        IFNULL(group_concat(name || ' (' || part || ')'), '') AS 'ag'
        FROM (
            SELECT o.id, a.name AS name, p.part AS 'part'
            FROM objects o
            LEFT JOIN productions p ON o.id = p.obj_id
            LEFT JOIN agents a ON a.id = p.agt_id
            ORDER BY a.name ASC, p.part ASC
            )
        GROUP BY id
        )
    SELECT o.id AS ID, o.label AS label, o.date AS date, a.ag AS ag, c.classified AS cls
    FROM objects o
    LEFT JOIN classifications c ON c.id = o.id
    LEFT JOIN agent_data a ON a.id = o.id """

# Function: Added to OBJECTS_SRCH to sort by label, date, and agent respectively in ascending
# Usage: Concatenate onto the OBJECTS_SRCH
OBJECTS_SRCH_SORT = """ORDER BY lower(label) ASC, lower(date) ASC, lower(ag) ASC """

# Function: Query to provide summary details of id selected. Provides table with Accession No.,
#     Date, Place, and Department of the object
# Usage: Functions as its own query with specific id string replacing the ?
DETAILS_SUMMARY = """SELECT o.accession_no AS "Accession No.",
    IFNULL(o.date, ' ') AS Date, IFNULL(pl.label, ' ') AS Place, d.name AS Department
    FROM objects o
    LEFT JOIN objects_departments od ON od.obj_id = o.id
    LEFT JOIN departments d ON d.id = od.dep_id
    LEFT JOIN objects_places op ON op.obj_id = o.id
    LEFT JOIN places pl ON pl.id = op.pl_id
    WHERE o.id = ?"""

# Function: Query to provide the label of id selected. Outputs object label only
# Usage: Functions as its own query with specific id string replacing the ?
DETAILS_LABEL = """SELECT label
    FROM objects
    WHERE id = ?"""

# Function: Query to provide producton details of id selected. Provides table with Part,
#     Name of agent, comma-separated list of agent nationalities, and the timespan of agent
# Usage: Functions as its own query with specific id string replacing the ?
DETAILS_PRODCTN = """WITH nations AS (
        SELECT agt_id,
        IFNULL(group_concat(lower(nation), ', '), 'Unknown') AS "Nationalities"
        FROM (
            SELECT an.agt_id, n.descriptor AS nation
            FROM agents_nationalities an
            LEFT JOIN agents a ON a.id = an.agt_id
            LEFT JOIN nationalities n ON n.id = an.nat_id
            ORDER BY lower(n.descriptor) ASC
            )
        GROUP BY agt_id
        ),
    times AS (
        SELECT id,
        IFNULL(group_concat(start || '-' || stop), '') AS "period"
        FROM (
            SELECT id, substr(begin_date, 1, 4) AS start, substr(end_date, 1, 4) AS stop
            FROM agents ag
            )
        GROUP BY id
        )
    SELECT p.part AS Part, a.name AS Name, nations.Nationalities AS "Nationalities",
    times.period AS Timespan
    FROM objects o
    LEFT JOIN productions p ON o.id = p.obj_id
    LEFT JOIN agents a ON a.id = p.agt_id
    LEFT JOIN nations ON nations.agt_id = p.agt_id
    LEFT JOIN times ON times.id = a.id
    WHERE o.id = ?
    ORDER BY o.id ASC, lower(a.name) ASC, lower(p.part) ASC, nations.Nationalities ASC"""

# Function: Query to provide classification details of id selected. Provides list of classes the
#     selected object belongs to
# Usage: Functions as its own query with specific id string replacing the ?
DETAILS_CLASS = """SELECT c.name AS "Classified As"
    FROM objects o
    LEFT JOIN objects_classifiers oc ON o.id = oc.obj_id
    LEFT JOIN classifiers c ON c.id = oc.cls_id
    WHERE o.id = ?
    ORDER BY lower(c.name) ASC"""

# Function: Query to provide reference details of id selected. Provides table with the Type and
#     Content of the references for the objects
# Usage: Functions as its own query with specific id string replacing the ?
DETAILS_REF = """SELECT ref.type AS "Type", ref.content AS "Content"
    FROM objects o
    LEFT JOIN 'references' ref ON ref.obj_id = o.id
    WHERE o.id = ?"""
