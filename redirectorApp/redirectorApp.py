import os
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory, jsonify, _request_ctx_stack
import requests
from werkzeug.local import LocalProxy
from flask.ext.cors import CORS, cross_origin
import pymongo
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, errors


app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')
CORS(app)


def connect():
# Substitute the 5 pieces of information you got when creating
# the Mongo DB Database (underlined in red in the screenshots)
# Obviously, do not store your password as plaintext in practice
    print os.environ['OPENSHIFT_MONGODB_DB_URL']
    print int(os.environ['OPENSHIFT_MONGODB_DB_PORT'])
    print os.environ['OPENSHIFT_MONGODB_DB_USERNAME']
    print os.environ['OPENSHIFT_MONGODB_DB_PASSWORD']
    connection = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'],int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))
    handle = connection["dnsreroute"]
    handle.authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'],os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'])
    return handle

handle = connect()

# Controllers API
@app.route("/")
def home():
    host = request.headers['Host']
    host = host.split(':')[0]
    if host != 'home.dnsreroute.xyz':
        route = handle.routes.find_one({'incomingRoute': host})
        if route:
            outgoingRoute = route['outgoingRoute']
            if route['type'] == "301":
                return redirect(outgoingRoute, 301)
            elif route['type'] == "302":
                return redirect(outgoingRoute)
            else:
                return '{"message": "Error - not able to determine redirect type"}'
        else:
            return '{"message": "Could not find a matching route"}', 404

    else:
      return "The Host header is {hostHeader}.This is the unsecured home page".format(hostHeader=request.headers['Host'])

# Controllers API
@app.route("/health")
def healthCheck():
    return '{"message": "System OK!"}'


if __name__ == '__main__':
    app.run(app.config['IP'], app.config['PORT'])
