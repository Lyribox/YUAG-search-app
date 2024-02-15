"""
Program: flaskapp.py
Usage: Runs the YUAG search application.
"""
from flask import Flask, request, make_response, redirect, render_template
import werkzeug
import querylib

# create an instance of a Flask app
# set template folder location to current directory
app = Flask(__name__, template_folder='.')
app.jinja_options["autoescape"] = lambda _: True

# keeps track of when the first search is made
# used to decide whether to display no search results message or not
MADE_FIRST_SEARCH = False

@app.route("/")
def index():
    """Creates a response to the '/' route."""
    # retrieve cookies if they exist
    props = {}

    label = request.cookies.get("label")
    if label:
        props["label"] = label
    else:
        props["label"] = ""

    date = request.cookies.get("date")
    if date:
        props["date"] = date
    else:
        props["date"] = ""

    agent = request.cookies.get("agent")
    if agent:
        props["agent"] = agent
    else:
        props["agent"] = ""

    classifier = request.cookies.get("classifier")
    if classifier:
        props["classifier"] = classifier
    else:
        props["classifier"] = ""

    # as long as the search fields aren't empty, make a search
    if(not (props["label"] == "" and
            props["date"] == "" and
            props["agent"] == "" and
            props["classifier"] == "")):
        results = querylib.query_objects(props)
        res_props = {
            "results": results
        }
        html = render_template("objlist.html", props=res_props)
        props["table"] = html
    else:
        # if cookies have been initialized
        if MADE_FIRST_SEARCH:
            props["table"] = "No search terms provided. Please enter some search terms."
        else:
            props["table"] = ""
    return render_template("index.html", props=props)

@app.route("/search")
def search():
    """Creates a response to the '/search' route."""
    try:
        global MADE_FIRST_SEARCH
        args = {}

        if request.args.get("l"):
            args["label"] = request.args.get("l")
        else:
            args["label"] = ""
        if request.args.get("d"):
            args["date"] = request.args.get("d")
        else:
            args["date"] = ""
        if request.args.get("c"):
            args["classifier"] = request.args.get("c")
        else:
            args["classifier"] = ""
        if request.args.get("a"):
            args["agent"] = request.args.get("a")
        else:
            args["agent"] = ""

        results = ""
        if(not (args["label"] == "" and
                args["date"] == "" and
                args["agent"] == "" and
                args["classifier"] == "")):
            results = querylib.query_objects(args)
        else:
            response = make_response("No search terms provided. Please enter some search terms.")
            if MADE_FIRST_SEARCH == False:
                MADE_FIRST_SEARCH = True
                response = make_response("")
            for key in args:
                response.set_cookie(key, args[key])
            return response

        res_props = {
            "results": results
        }
        html = render_template("objlist.html", props=res_props)

        response = make_response(html)
        # set cookies
        for key in args:
            response.set_cookie(key, args[key])

        return response
    except Exception as err:
        return make_response("Something went wrong. " + str(err))

@app.route("/obj/<int:obj_id>")
def obj(obj_id):
    """Creates a response to the '/obj/<int:obj_id>' route."""
    results = querylib.query_details(str(obj_id))
    print(results)
    if sum([len(res) for res in results.values()]) == 0:
        return make_response(f"Error: no object with id {obj_id} exists"), 404
    props = {
        "results": results,
        "imgUrl": "https://media.collections.yale.edu/thumbnail/yuag/obj/" + str(obj_id)
    }
    return render_template("objdata.html", props=props)

# Error Handling:
@app.errorhandler(werkzeug.exceptions.NotFound)
def handle404(err):
    """Handles not found errors from flask."""
    req_params = request.path.split("/")
    # handles when obj given bad param var
    if(req_params[1] == "obj" and len(req_params) >= 3):
        return make_response(f"Error: no object with id '{req_params[2]}' exists."), 404
    # handles when obj is lonely
    if(req_params[1] == "obj" and len(req_params) == 2):
        return make_response(f"Error: missing object id."), 404
    return make_response(f"ERROR {err.code} {err.name}: {request.path}"), 404
