from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource, reqparse
from flask_restplus import inputs
import json
import flask.json
import requests
import os

import search
from mime import fileExtensionToMimeMap

app = Flask(__name__)
api = Api(app)

print("**************************************")
print("*     FOLIO HTML SERVICE             *")
print("**************************************")

#api.add_resource(Semantics, "/<path:input>")

#app.run(debug=True)

mimeMap={
    ".htm": "text/html",
    ".html": "text/html",
    ".png": "image/png",
    ".jpg": "image/jpg"
}

def getMimeType(path):
    mimeType=''
    root,ext = os.path.splitext(path)
    if ext in fileExtensionToMimeMap:
        mimeType = fileExtensionToMimeMap[ext]
    return mimeType

#from flask import Flask
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path=='x/searchinfo':
        print('Search page')
        response = app.response_class(
            response=json.dumps(search.SearchHistory.CurrentInfo()),
            status=200,
            mimetype='application/json'
        )
        return response
    print('Received PATH REQUEST:', path)
    if path.startswith('data/'):
        path = path[len('data/'):]
    if os.path.isfile(os.path.join('./data',path)):
        #print('Sending file', path)
        return send_from_directory('./data', path)
        #with open()
        #content =
    response = app.response_class(
        response='You want path: %s' % path,
        status=200,
        mimetype='text/plain'
    )
    return response

@app.route('/x/<string:input>', methods=['POST'])
def xfunc(input):
    if input=='search':
        print('Search page')
        print(request.data.decode('utf-8'))
        response = app.response_class(
            response=search.SearchHistory.Search(request.data.decode('utf-8')),
            status=200,
            mimetype='application/json'
        )
        return response
    if input=='search-back':
        print('Search back')
        print(request.data.decode('utf-8'))
        response = app.response_class(
            response=search.SearchHistory.PrevPage(),
            status=200,
            mimetype='application/json'
        )
        return response
    if input=='search-forward':
        print('Search forward')
        print(request.data.decode('utf-8'))
        response = app.response_class(
            response=search.SearchHistory.NextPage(),
            status=200,
            mimetype='application/json'
        )
        return response


if __name__ == '__main__':
    app.run()
