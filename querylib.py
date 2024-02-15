"""
Program Name: querylib.py
Function: Contains functions for building the correct SQL queries required by client
"""
from contextlib import closing
from sqlite3 import connect
import prepsql

DATABASE_URL = "file:lux.sqlite?mode=ro"

def check_connect():
    """Used to check if the db can be connected to. Returns
    an error otherwise."""
    with connect(DATABASE_URL, isolation_level=None,
                 uri=True) as connection:
        # Building the Table of details for the object
        with closing(connection.cursor()) as cursor:
            return 0

def query_details(obj_id: str) -> str:
    """
    Function: Creates the SQL queries for the details of the id input and puts them into table
    Usage: Called with id being a string of the id selected by user
    Output: A list of tables and lists containing details of the object
    """
    with connect(DATABASE_URL, isolation_level=None,
                 uri=True) as connection:
        # Building the Table of details for the object
        with closing(connection.cursor()) as cursor:
            all_results = {}

            # Summary details
            query = prepsql.DETAILS_SUMMARY
            cursor.execute(query, [obj_id])
            results = cursor.fetchall()
            all_results["summary"] = results

            # Label
            query = prepsql.DETAILS_LABEL
            cursor.execute(query, [obj_id])
            results = cursor.fetchall()
            all_results["label"] = results

            # Production details
            query = prepsql.DETAILS_PRODCTN
            cursor.execute(query, [obj_id])
            results = cursor.fetchall()
            all_results["production"] = results

            # Classifier details
            query = prepsql.DETAILS_CLASS
            cursor.execute(query, [obj_id])
            results = cursor.fetchall()
            all_results["classifier"] = results

            # Reference details
            query = prepsql.DETAILS_REF
            cursor.execute(query, [obj_id])
            results = cursor.fetchall()
            all_results["reference"] = results
            # after appending all tables
            return all_results

def query_objects(args: dict) -> str:
    """
    Function: Creates the SQL query for the objects search based on user parameters
    Usage: Called with a single argument being a dictionary of the args
    Output: A list of tuples containing the objects that meet the search criteria
    """
    with connect(DATABASE_URL, isolation_level=None,
                 uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            filters = []
            prepared_statements = {"classifier": None,
                                   "agent": None,
                                   "date": None,
                                   "label": None}
            # classifier
            # checks that there is some input there
            if len(args["classifier"]) > 0:
                filters.append("cls LIKE :cls")
                prepared_statements["cls"] = "%" + args["classifier"] + "%"
            # agent
            if len(args["agent"]) > 0:
                filters.append("ag LIKE :agent")
                prepared_statements["agent"] = "%" + args["agent"] + "%"
            # date
            if len(args["date"]) > 0:
                filters.append("date LIKE :date")
                prepared_statements["date"] = "%" + args["date"] + "%"
            # label
            if len(args["label"]) > 0:
                filters.append("label LIKE :label")
                prepared_statements["label"] = "%" + args["label"] + "%"

            query = prepsql.OBJECTS_SRCH
            query += " WHERE label LIKE :label " if prepared_statements["label"] is not None else " "
            query += "GROUP BY o.id, o.label, o.date "
            query += "HAVING "
            query += " AND ".join(filters) if len(filters) > 0 else " "

            query += " " + prepsql.OBJECTS_SRCH_SORT + prepsql.LIMITER

            print(query)
            print(prepared_statements)

            cursor.execute(query, prepared_statements)
            results = cursor.fetchall()

            print("Search Produced: " + str(len(results))  + " items")

            return results
