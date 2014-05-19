from flask import Flask, request, abort, render_template, redirect, url_for


from .utils import get_reqs


app = Flask(__name__)


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

    pkg_name, reqs = get_reqs(pkg_name)
    if reqs is None:
        abort(404)

    return render_template('show.html', pkg_name=pkg_name, reqs=reqs)
