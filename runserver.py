"""
Program Name: runserver.py
Usage: Runs the flaskapp server on the specified port.
"""
import argparse
import sys
from sqlite3 import OperationalError
import querylib
from flaskapp import app

def main():
    """Runs the application on the designated server."""
    # argument parser
    parser = argparse.ArgumentParser(
        prog="The YUAG seach application"
    )
    parser.add_argument("port",
                        help="the port at which the server should listen")
    args = parser.parse_args()

    # validate port argument
    port = None
    try:
        port = int(args.port)
    except ValueError:
        print(f"Port must be a number, not '{args.port}'", file=sys.stderr)
        sys.exit(1)
    except ConnectionRefusedError:
        print(f"The port '{args.port}' is unavailable.", file=sys.stderr)
        sys.exit(1)
    # validate lux.sqlite exists
    try:
        querylib.check_connect()
    except OperationalError as err:
        print("There was a problem with the database file: " + str(err),
              file=sys.stderr)
        sys.exit(1)
    # attempt to run the application
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    main()
