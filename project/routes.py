from controllers import (
    BaseController as Base,
    CardController as Card,
    CropController as Crop,
    FertilizerController as Fertilizer,
    LabController as Lab,
    LandController as Land,
    NutrientSetController as NutrientSet,
    IdealController as Ideal,
    RecomendationController as Recomendation,
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

    # Card routes
    (Card.as_view(), '/api/card'),

    # Crop routes
    (Crop.as_view(), '/api/crop'),
    (Crop.as_view(), '/api/crop/<id:\w{32}>'),
    (Crop.as_view(), '/api/crop/<id:all>'),

    # Fertilizer routes
    (Fertilizer.as_view(), '/api/fertilizer'),
    (Fertilizer.as_view(), '/api/fertilizer/<id:\w{32}>'),
    (Fertilizer.as_view(), '/api/fertilizer/<id:all>'),

    # Lab routes
    (Lab.as_view(), '/api/lab'),
    (Lab.as_view(), '/api/lab/<id:\w{32}>'),
    (Lab.as_view(), '/api/lab/<id:all>'),

    # Land routes
    (Land.as_view(), '/api/land'),
    (Land.as_view(), '/api/land/<id:\w{32}>'),
    (Land.as_view(), '/api/land/<id:all>'),

    # NutrientSet routes
    (NutrientSet.as_view(), '/api/nutrientset'),

    # Ideal routes
    (Ideal.as_view(), '/api/ideal'),

    # Recomendation routes
    (Recomendation.as_view(), '/api/recomendation'),

    # User routes
    (User.as_view(), '/api/user'),
    (User.as_view(), '/api/user/<id:\w{32}>'),
    (User.as_view(), '/api/user/<id:all>'),

    # SignIn routes
    (SignIn.as_view(), '/api/sign-in'),

    # SignOut routes
    (SignOut.as_view(), '/api/sign-out'),
]
