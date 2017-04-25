from passlib.hash import pbkdf2_sha256
from pony.orm import db_session

from config import SALT
from controllers import BaseController
from models import User


class SignInController(BaseController):
    async def post(self, request):
        req = request.form
        email = req.get('email')
        password = req.get('password')
        us = None
        try:
            with db_session:
                us = User.select(lambda u: u.email == email).first()
                login = pbkdf2_sha256.verify(f"{password}{SALT}", us.password)
        except Exception as e:
            login = False
        if not login or not us:
            return self.response_status(401)
        request['session']['user'] = us.id
        request['session']['auth'] = "user" if not us.admin else "admin"
        return self.response_status(200, us)
