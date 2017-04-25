import re
from uuid import uuid4

import pandas as pd
from pony.orm import db_session

from config import database as db
from models import engine, Lab, Fertilizer, NutrientSet, Ideal


def normalize_dict(data):
    normalized_values = []
    for v in data.values():
        normalized_values.append(
            re.sub('\s+', ' ', v.strip())
            if type(v) is str else v
        )
    return dict(zip(data.keys(), normalized_values))


def parse(labs_record, products_record):
    labs = []
    products = []
    for lab in labs_record:
        new_lab = lab.copy()
        del new_lab['code']
        labs.append(normalize_dict(new_lab))
        for product in (
            product
            for product in products_record
            if product['lab_code'] == lab['code']
        ):
            nutrient_set = product.copy()
            del nutrient_set['code']
            del nutrient_set['lab_code']
            fertilizer = {
                'name': nutrient_set.pop('name', ''),
                'presentation': nutrient_set.pop('presentation', '')
            }
            products.append(
                (normalize_dict(fertilizer), normalize_dict(nutrient_set))
            )
    return labs, products


def connect():
    try:
        engine.bind(
            'postgres',
            user=db['DB_USER'],
            password=db['DB_PASSWORD'],
            host=db['DB_HOST'],
            database=db['DB_NAME']
        )
    except Exception as e:
        return False
    else:
        engine.generate_mapping(create_tables=True)
    return True


def not_null_data(**kw):
        return dict(
            (k, v)
            for k, v in kw.items()
            if v
        )


def do_insert(entity_class, **data):
    return entity_class(id=uuid4().hex, **not_null_data(**data))


if __name__ == '__main__' and connect():
    file = 'data/labs_and_products.xlsx'

    labs = pd.read_excel(
        file, sheetname='labs', na_values='str', keep_default_na=False
    )
    products = pd.read_excel(
        file, sheetname='products', na_values='str', keep_default_na=False
    )
    ideals = pd.read_excel(
        file, sheetname='ideals', na_values='str', keep_default_na=False
    )

    labs_record = labs.to_dict(orient='record')
    products_record = products.to_dict(orient='record')
    ideals_record = ideals.to_dict(orient='record')

    final_labs, final_products = parse(labs_record, products_record)
    with db_session:
        print("Labs and products...")
        for rl in final_labs:
            lab = do_insert(Lab, **rl)
            for rp in final_products:
                nutrient_set = do_insert(NutrientSet, **rp[1])
                fertilizer = do_insert(
                    Fertilizer, nutrient_set=nutrient_set, **rp[0]
                )
                fertilizer.labs.add(lab)
    with db_session:
        print("Ideals...")
        for ro in ideals_record:
            do_insert(Ideal, **ro)
