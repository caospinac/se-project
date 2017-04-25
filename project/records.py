from uuid import uuid4

from pony.orm import db_session

from models import University, SciNet
from config import database as db


def connect():
    try:
        SciNet.bind(
            db['DB_CLIENT'],
            f"{ db['DB_NAME'] }.sqlite",
            create_db=True
        )
    except Exception as e:
        return False
    else:
        SciNet.generate_mapping(create_tables=True)
    return True


@db_session
def register_university():
    universities = [
        'Universidad Nacional de Colombia',
        'Universidad de Caldas',
        'Universidad Autonoma',
        'Universidad Catolica',
        'Universidad de Manizales'
    ]
    for x in universities:
        University(uniName=x, uniId=uuid4().hex)


if __name__ == '__main__' and connect():
    print()
    register_university()
