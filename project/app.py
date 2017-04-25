from uuid import uuid4

from jinja2 import Environment, PackageLoader
from passlib.hash import pbkdf2_sha256
from pony.orm import *
from sanic import Sanic
from sanic.exceptions import NotFound, FileNotFound
from sanic.response import html, json
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
    view = env.get_template("base.html")
    html_content = view.render()
    return html(html_content)


@app.route("/home", methods=['GET', 'POST'])
async def home(request):
    view = env.get_template("home.html")
    html_content = view.render()
    return html(html_content)


@app.route("/do", methods=['GET', 'POST'])
async def do(request):
    view = env.get_template("network.html")
    html_content = view.render()
    return html(html_content)


@app.route("/sign-up", methods=['GET', 'POST'])
async def do(request):
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
                request['session']['auth'] = us.useType
                view = env.get_template("home.html")
                html_content = view.render(
                    name=User[request['session'].get('user')]
                )
        except Exception as e:
            raise e
    view = env.get_template("sign-up.html")
    with db_session:
        html_content = view.render(universities=select(x for x in University))
        return html(html_content)
    return json("Failed")


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
