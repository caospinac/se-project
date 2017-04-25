from jinja2 import Environment, PackageLoader
from pony import orm
from sanic import Sanic
from sanic.exceptions import NotFound, FileNotFound
from sanic.response import html

from config import database, server


app = Sanic(__name__)
app.static("/", "./project/static/")
app.config.update(server)
app.config.update(database)

env = Environment(
    loader=PackageLoader("app", "templates"),
)


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


if __name__ == '__main__':
    orm.sql_debug(app.config.SQL_DEBUG)
    try:
        engine.bind(
            app.config.DB_CLIENT,
            f"{app.config.DB_NAME}.sqlite", create_db=True
        )

        engine.bind(
            'postgres',
            user=app.config.DB_USER,
            password=app.config.DB_PASSWORD,
            host=app.config.DB_HOST,
            database=app.config.DB_NAME
        )
    except Exception as e:
        pass
    else:
        engine.generate_mapping(create_tables=True)

    app.run(
        debug=app.config.DEBUG,
        host=app.config.HOST,
        port=app.config.PORT
    )
