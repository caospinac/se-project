import sys
from uuid import uuid4

from pony.orm import db_session

from models import University, SciNet, User
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
        'Universidad Autónoma de Manizales',
        'Universidad Católica de Manizales',
        'Universidad de Manizales',
        'Other'
    ]
    for x in universities:
        University(uniName=x, uniId=uuid4().hex)


@db_session
def auth_as_admin(*emails):
    with db_session:
        for email in emails:
            user = User.get(useEmail=email)
            if user:
                user.set(useType='adm')


if __name__ == '__main__' and connect():
    register_university()
    auth_as_admin(
        "caaospinaca@unal.edu.co",
        "dsvalenciah@unal.cdu.co",
        "msochel@unal.cdu.co",
    )
