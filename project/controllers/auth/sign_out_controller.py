from controllers import BaseController


class SignOutController(BaseController):
    async def post(self, request):
        try:
            del request['session']['user']
            del request['session']['auth']
        except KeyError as e:
            pass
        return self.response_status(200)
