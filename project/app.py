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
from models import (
    SciNet,
    Graph, Query, University, User, File, Result, Article
)
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


@app.route("/sign-in", methods=['POST'])
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
        raise e
        login = False
    if not login or not us:
        url = app.url_for('index')
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


@app.route("/query", methods=['POST', 'GET'])
async def query(request):
    req_file = request.files.get('file')
    if not req_file:
        return redirect(app.url_for("query"))
    time_start = time()
    body = req_file.body.decode("unicode_escape")
    tos = ToS(body)
    nodes, edges = tos.get_graph()
    data = {"nodes": nodes, "edges": edges}
    user = request['session'].get('user')
    if not user:
        return get_html_with_graph(
            nodes=data['nodes'],
            edges=data['edges'],
            time=time() - time_start,
            name=request["session"].get("name")
        )
    try:
        # articles = []
        req = request.form
        with db_session:
            file = File(
                filId=uuid4().hex,
                filName=req_file.name,
                filContent=body,
            )
            query = Query(
                queId=uuid4().hex,
                queTopic=req.get('topic'),
                queDescription=req.get('description'),
                user=User[user],
                file=file,
            )
            graph = Graph(
                graId=uuid4().hex,
                graContent=pyjson.dumps(data),
                query=Query[query.queId]
            )
            result = Result(
                resId=uuid4().hex,
                resTime=time() - time_start,
                graph=graph,
            )
        return get_html_with_graph(
            nodes=data['nodes'],
            edges=data['edges'],
            time=time() - time_start,
            name=request["session"].get("name")
        )
    except Exception as e:
        raise e



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
    print("req:", req)
    email = req['email'][0] if 'email' in req else None
    date0 = datetime.strptime(req['min_date'][0], "%Y-%m-%d") \
        if 'min_date' in req else None
    date1 = datetime.strptime(req['max_date'][0], "%Y-%m-%d") \
        if 'max_date' in req else None
    list_report = list()
    try:
        with db_session:
            if email and date0 and date1:
                queries = select(
                    (
                        x.queId, x.queDate,
                        x.user.useName, x.user.useLastName, x.user.useEmail,
                        x.queTopic, x.queDescription
                    )
                    for x in Query
                    if x.user.useEmail == email and date0 <= x.queDate <= date1
                )
            elif email:
                queries = select(
                    (
                        x.queId, x.queDate,
                        x.user.useName, x.user.useLastName, x.user.useEmail,
                        x.queTopic, x.queDescription
                    )
                    for x in Query
                    if x.user.useEmail == email
                )

            elif date0 and date1:
                print("dates:", date0, date1)
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
        raise e


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
