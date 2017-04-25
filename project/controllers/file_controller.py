from hashlib import sha1

from pony.orm import db_session, select

from .base_controller import BaseController
from models import File


class UniversityController(BaseController):
    async def post(self, request):
        user = request['session'].get('user')
        if not user:
            return self.response_status(401)
        req = request.form
        try:
            with db_session:
                File(
                    **self.not_null_data(
                        filName=req.get('uniName'),
                        filId=sha1(name.encode('utf-8')).hexdigest()
                        filContent=req.get('filContent')

                    )
                )
        except Exception as e:
            raise e
        return self.response_status(201)

    async def get(self, request, id):
        user = request['session'].get('user')
        if not user:
            return self.response_status(401)
        with db_session:
            if id == 'all':
                return self.response_status(
                    200, select(
                        (x.filId, x.filName, x.filContent)
                        for x in File
                    )[:10]
                )
            if not File.exists(id=id):
                return self.response_status(404)
            return self.response_status(
                200, select(
                    (x.filName, x.filContent)
                    for x in File if x.id == id
                )
            )
