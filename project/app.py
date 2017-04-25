from uuid import uuid4

from jinja2 import Environment, PackageLoader
from passlib.hash import pbkdf2_sha256
from pony.orm import *
from sanic import Sanic
from sanic.exceptions import NotFound, FileNotFound
from sanic.response import html, json, redirect
from sanic_session import InMemorySessionInterface

from config import database, SALT, server
from models import (
    SciNet,
    User,
    University
)


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
    name = request['session'].get('nickname')
    html_content = view.render(name=name) if name else view.render()
    return html(html_content)


@app.route("/do", methods=['GET', 'POST'])
async def do(request):
    view = env.get_template("network.html")
    html_content = view.render()
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
        login = False
    if not login or not us:
        url = app.url_for('index')
    else:
        request['session']['user'] = us.useId
        request['session']['nickname'] = us.useNickName
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
                        useNickName=req.get('nickname'),
                        useArea=req.get('area'),
                        useEmail=req.get('email'),
                        usePassword=crypt(req.get('password')),
                        university=University[req.get('university')]
                    )
                )
                request['session']['user'] = us.useId
                request['session']['nickname'] = us.useNickName
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
        del request['session']['nickname']
        del request['session']['auth']
    except KeyError as e:
        pass
    url = app.url_for('index')
    return redirect(url)


@app.route("/graph/<graId:\w{32}>", methods=['GET', 'POST'])
async def graph(request):
    user = request['session'].get('user')
    if not user:
        return self.response_status(401)
    with db_session:
        if id == 'all':
            return self.response_status(
                200, select(
                    (l.id, l.name, l.state, l.city, l.address)
                    for l in Land
                    if l.user == User[user] and l.active
                )
            )
        if not Land.exists(id=id):
            return self.response_status(404)
        return self.response_status(
            200, select(
                (l.name, l.state, l.city, l.address)
                for l in Land if l.id == id and l.active
            )
        )
    script = graph_script(request.file.body)
    view = env.get_template("graph.html")
    html_content = view.render(script=script)
    return html(html_content)


@app.route("/upload", methods=['POST', 'GET'])
async def upload(request):
    file = request.files.get('selectedFile')
    try:
        script = util.build_graph(file.body)
        content = [(row[0], row[1:]) for row in content0]
    except Exception as e:
        raise e
        content = []

    template = env.get_template("input.html")
    html_content = template.render(
        uploaded=content, measure_labels=ms.labels)
    return html(html_content)


@app.route("/reports", methods=['POST', 'GET'])
async def reports(request):
    template = env.get_template("reports.html")
    html_content = template.render()
    return html(html_content)

if __name__ == '__main__':
    sql_debug(app.config.SQL_DEBUG)
    try:
        SciNet.bind(
            app.config.DB_CLIENT,
            f"{app.config.DB_NAME}.sqlite", create_db=True
        )
        '''
        SciNet.bind(
            'postgres',
            user=app.config.DB_USER,
            password=app.config.DB_PASSWORD,
            host=app.config.DB_HOST,
            database=app.config.DB_NAME
        )
        '''
    except Exception as e:
        raise e
    else:
        SciNet.generate_mapping(create_tables=True)

    app.run(
        debug=app.config.DEBUG,
        host=app.config.HOST,
        port=app.config.PORT
    )
