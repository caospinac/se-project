from controllers import (
    BaseController as Base,
    UserController as User
)
from controllers.auth import (
    SignInController as SignIn,
    SignOutController as SignOut
)


api_routes = [

    # Base routes
    (Base.as_view(), '/api/base'),

    # Base routes
    (Base.as_view(), '/api/base/<arg>'),

    # User routes
    (User.as_view(), '/api/user'),
    (User.as_view(), '/api/user/<id:\w{32}>'),
    (User.as_view(), '/api/user/<id:all>'),

    # SignIn routes
    (SignIn.as_view(), '/api/sign-in'),

    # SignOut routes
    (SignOut.as_view(), '/api/sign-out'),
]
