import os

from flask import Flask, request, abort, render_template, redirect, url_for, send_file
from graphviz import Graph

from .utils import get_reqs, reqs_graph


app = Flask(__name__)


cache_dir = os.path.join(os.path.dirname(__file__), '..', 'img-cache')
if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)


@app.route("/")
def main():
    pkg_name = request.args.get('pkg_name')
    if pkg_name:
        return redirect(url_for('show', pkg_name=pkg_name))
    return render_template('main.html')


@app.route("/show/<pkg_name>")
def show(pkg_name):
    if not pkg_name:
        abort(404)

    result = get_reqs(pkg_name)
    if result is None:
        abort(404)
    pkg_label, reqs = result

    return render_template('show.html', pkg_name=pkg_label, reqs=reqs)


@app.route("/graph/<pkg_name>")
def graph(pkg_name):
    return render_template('graph.html', pkg_name=pkg_name)


@app.route("/graph/<pkg_name>/img")
def graph_data(pkg_name):
    if not pkg_name:
        abort(404)

    filepath = os.path.join(cache_dir, pkg_name.lower())
    if not os.path.exists(filepath + '.png'):
        nodes, edges = reqs_graph(pkg_name)

        if not nodes:
            return redirect(url_for('static', filename='img/blank.png'))

        dot = Graph()
        dot.format = 'png'
        dot.node('0', nodes[0], fillcolor='#fbb4ae', style='filled', shape='box')
        for i, pkg_name in enumerate(nodes[1:]):
            dot.node(str(i+1), pkg_name, fillcolor='#ccebc5', style='filled')

        dot.edges([
            [str(i[0]), str(i[1])]
            for i in edges
        ])

        dot.render(filepath)

    return send_file(filepath + '.png')

