#!/usr/bin/python3

from flask import Flask, render_template, request

import search

application = app = Flask(__name__)
app.debug = True

@app.route('/search', methods=["GET"])
def dosearch():
    query = request.args['query']
    qtype = request.args.get('query_type','and')
    offset = int(request.args.get('offset', 1))

    search_results, result_len = search.search(query, qtype, offset)
    return render_template('results.html',
            query=query,
            qtype=qtype,
            offset=offset,
            results=result_len,
            search_results=search_results)

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        pass
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
