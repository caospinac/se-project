from uuid import uuid4

from pony.orm import db_session, select
from passlib.hash import pbkdf2_sha256

from config import SALT
from .base_controller import BaseController
from models import User


class UserController(BaseController):
    @staticmethod
    def crypt(value):
        return pbkdf2_sha256.hash(f'{value}{SALT}')

    async def post(self, request):
        req = request.form
        try:
            with db_session:
                if User.exists(email=req.get('email')):
                    return self.response_status(409)
                User(
                    **self.not_null_data(
                        useId=uuid4().hex,
                        useNickName=req.get('useNickName'),
                        useArea=req.get('useArea'),
                        usePassword=self.crypt(req.get('password')),
                    )
                )
        except Exception as e:
            raise e
        return self.response_status(201)

    async def get(self, request, id):
        with db_session:
            if id == 'all':
                return self.response_status(
                    200, select(
                        (u.useId, u.useType,
                            u.useNickName, u.useState, u.useArea)
                        for u in User if u.useState == 'active'
                    )
                )
            if not User.exists(id=id):
                return self.response_status(404)
            return self.response_status(
                200, select(
                    (u.useId, u.useType, u.useNickName, u.useState, u.useArea)
                    for u in User if u.id == id u.useState == 'active'
                )
            )
