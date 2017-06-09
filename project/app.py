from datetime import datetime
import json as pyjson
import pandas as pd
from time import time
from uuid import uuid4
from pprint import pprint

from jinja2 import Environment, PackageLoader
from passlib.hash import pbkdf2_sha256
from pony.orm import *
from sanic import Sanic
from sanic.exceptions import NotFound, FileNotFound
from sanic.response import html, json, redirect
from sanic_session import InMemorySessionInterface

from config import database, SALT, server, PRODUCTION
from models import *
from scripts.isi_processor import TreeOfScience as ToS


app = Sanic(__name__)
app.static("/", "./project/static/")
app.config.update(server)
app.config.update(database)

env = Environment(
    loader=PackageLoader("app", "templates"),
)

session_interface = InMemorySessionInterface()


def not_null_data(**kw):
    return dict(
        (k, v)
        for k, v in kw.items()
        if v
    )


def crypt(value):
    return pbkdf2_sha256.hash(f'{value}{SALT}')


@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session_interface.save(request, response)


@app.exception(NotFound, FileNotFound)
def ignore_404s(request, exception):
    view = env.get_template("404.html")
    html_content = view.render()
    return html(html_content)


@app.route("/", methods=['GET', 'POST'])
async def index(request):
    if request['session'].get('user'):
        url = app.url_for("home")
        return redirect(url)
    view = env.get_template("base.html")
    html_content = view.render()
    return html(html_content)


@app.route("/home", methods=['GET', 'POST'])
async def home(request):
    view = env.get_template("home.html")
    name = request['session'].get('name')
    html_content = view.render(
        name=name, role=request['session'].get('auth')
    ) if name else view.render()
    return html(html_content)


@app.route("/sign-in", methods=['POST', 'GET'])
async def sign_in(request):
    req = request.form
    email = req.get('email')
    password = req.get('password')
    us = None
    try:
        with db_session:
            us = User.select(lambda u: u.useEmail == email).first()
            login = pbkdf2_sha256.verify(f"{password}{SALT}", us.usePassword)
    except Exception as e:
        login = False
    if not login or not us:
        view = env.get_template("base.html")
        html_content = view.render(msg="Incorrect email or password")
        return html(html_content)
    else:
        request['session']['user'] = us.useId
        request['session']['name'] = us.useName
        request['session']['auth'] = us.useType
        url = app.url_for('home')
    return redirect(url)


@app.route("/sign-up", methods=['GET', 'POST'])
async def sign_up(request):
    if request.method == 'POST':
        req = request.form
        try:
            with db_session:
                uid = uuid4().hex
                us = User(
                    **not_null_data(
                        useId=uid,
                        useName=req.get('name'),
                        useLastName=req.get('lastname'),
                        useArea=req.get('area'),
                        useEmail=req.get('email'),
                        usePassword=crypt(req.get('password')),
                        university=University[req.get('university')]
                    )
                )
                request['session']['user'] = us.useId
                request['session']['name'] = us.useName
                request['session']['auth'] = us.useType
            url = app.url_for('home')
            return redirect(url)
        except Exception as e:
            raise e
    view = env.get_template("sign-up.html")
    with db_session:
        html_content = view.render(universities=select(x for x in University))
        return html(html_content)
    return json("Failed")


@app.route("/sign-out", methods=['GET', 'POST'])
async def sign_out(request):
    try:
        del request['session']['user']
        del request['session']['name']
        del request['session']['auth']
    except KeyError as e:
        pass
    url = app.url_for('index')
    return redirect(url)


def get_html_with_graph(nodes, edges, time, name):
    view = env.get_template("graph.html")
    nodes = pyjson.loads(nodes)
    edges = pyjson.loads(edges)
    html_content = view.render(
        nodes=pyjson.dumps(nodes),
        edges=pyjson.dumps(edges),
        time=time,
        name=name
    )
    return html(html_content)


@app.route('/graph/<graph_id>')
async def graph(request, graph_id):
    view = env.get_template("home.html")
    time_start = time()
    graph = None
    try:
        with db_session:
            graph = Result.select(lambda r: r.resId == graph_id).first()
    except Exception:
        view_default = view.render(msg="An error was occurred in data load")
        pass
    if graph:
        graph_data = {
            "nodes": pyjson.loads(graph.resGraph)["nodes"],
            "edges": pyjson.loads(graph.resGraph)["edges"]
        }
        # print("nolas", graph_data)
        return get_html_with_graph(
            nodes=graph_data["nodes"],
            edges=graph_data["edges"],
            time=time() - time_start,
            name=request["session"].get("name")
        )
    else:
        view_default = view.render(msg="Graph not found")
    return html(view_default)


def save_query(req, graph_data, total_time, user):
    validate_value = lambda value: value.strip() if value else None
    try:
        with db_session:
            query = Query(
                **not_null_data(
                    queId=uuid4().hex,
                    queTopic=validate_value(
                        req.get('topic').strip()
                    ),
                    queDescription=validate_value(
                        req.get('description').strip()
                    ),
                    user=User[user],
                )
            )
            result = Result(
                resId=uuid4().hex,
                resGraph=pyjson.dumps(
                    {
                        "nodes": graph_data["nodes"],
                        "edges": graph_data["edges"]
                    }
                ),
                resTime=total_time,
                articles=list(),
                query=query,
            )
            return result.resId
    except Exception as e:
        return None


@app.route("/query", methods=['POST', 'GET'])
async def query(request):
    view = env.get_template("home.html")
    req_file = request.files.get('file')
    if not req_file:
        view_default = view.render(msg="An error in file upload")
        return html(view_default)
    time_start = time()
    body = req_file.body.decode("unicode_escape")
    tos = ToS(body)
    graph_data = tos.get_graph()
    if graph_data["status"] == "OK":
        user = request['session'].get('user')
        if not user:
            return get_html_with_graph(
                nodes=graph_data["nodes"],
                edges=graph_data["edges"],
                time=time() - time_start,
                name=request["session"].get("name")
            )
        graph = save_query(request.form, graph_data, time() - time_start, user)
        if graph:
            return redirect(
                app.url_for('graph', graph_id=graph)
            )
        else:
            view_default = view.render(msg="An error in query save")
    else:
        view_default = view.render(msg=graph_data["status"])
    return html(view_default)


@app.route("/report", methods=['POST', 'GET'])
async def report(request):
    user = request["session"].get("user")
    name = request["session"].get("name")
    auth = request["session"].get("auth")
    if not user or auth != "adm":
        return redirect(
            app.url_for("index")
        )
    req = request.args
    # print("req:", req)
    email = req['email'][0] if 'email' in req else None

    try:
        date0 = datetime.strptime(req['min_date'][0], "%Y-%m-%d") \
            if 'min_date' in req else None
        date1 = datetime.strptime(req['max_date'][0], "%Y-%m-%d") \
            if 'max_date' in req else None
        list_report = list()
        with db_session:
            if email and date0 and date1:
                queries = select(
                    (
                        x.queId, x.queDate,
                        x.user.useName, x.user.useLastName, x.user.useEmail,
                        x.queTopic, x.queDescription
                    )
                    for x in Query
                    if (
                        email in x.user.useEmail and
                        date0 <= x.queDate and x.queDate <= date1
                    )
                )
            elif email:
                queries = select(
                    (
                        x.queId, x.queDate,
                        x.user.useName, x.user.useLastName, x.user.useEmail,
                        x.queTopic, x.queDescription
                    )
                    for x in Query
                    if email in x.user.useEmail
                )

            elif date0 and date1:
                # print("dates:", date0, date1)
                queries = select(
                    (
                        x.queId, x.queDate,
                        x.user.useName, x.user.useLastName, x.user.useEmail,
                        x.queTopic, x.queDescription
                    )
                    for x in Query
                    if date0 <= x.queDate and x.queDate <= date1
                )
            else:
                queries = select(
                    (
                        x.queId, x.queDate,
                        x.user.useName, x.user.useLastName, x.user.useEmail,
                        x.queTopic, x.queDescription
                    )
                    for x in Query
                )
            for x in queries:
                list_report.append(x[1:])
            df = pd.DataFrame(
                list_report,
                columns=[
                    "Date",
                    "Name",
                    "Lastname",
                    "Email",
                    "Topic",
                    "Description"]
            )
            df.to_csv("project/static/report.csv", sep='\t', encoding='utf-8')
            template = env.get_template("report.html")
            html_content = template.render(
                queries=queries, name=request["session"].get("name")
            )
            return html(html_content)
    except Exception as e:
        return redirect(app.url_for("report"))


async def report_user(request):
    return json(request.args)


if __name__ == '__main__':
    sql_debug(app.config.SQL_DEBUG)
    try:
        if not PRODUCTION:
            SciNet.bind(
                app.config.DB_CLIENT,
                f"{app.config.DB_NAME}.sqlite", create_db=True
            )
        else:
            SciNet.bind(
                'postgres',
                user=app.config.DB_USER,
                password=app.config.DB_PASSWORD,
                host=app.config.DB_HOST,
                database=app.config.DB_NAME
            )
    except Exception as e:
        raise e
    else:
        SciNet.generate_mapping(create_tables=True)

    app.run(
        debug=app.config.DEBUG,
        host=app.config.HOST,
        port=app.config.PORT
    )
