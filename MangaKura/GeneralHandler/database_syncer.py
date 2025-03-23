# DO NOT IMPORT ALL MODELS OR issubclass() WILL FAIL DUE TO IMPORT STUFF
from django.db import models
import json
from django.apps import apps
from MangaKura import settings as GLOBAL_SETTINGS
import requests
from django.db import connection


KEYVALUE_SEPARATOR = '/__KEYVAL__/'
KEYKEY_SEPARATOR = '/__KEYKEY__/'

def get_column_names_of_a_model(model=None) -> list[str]:

    if not issubclass(model, models.Model):
        raise Exception("Please pass a model.")
    
    return [field.column for field in model._meta.fields]



def get_dict_of_a_model_in_db(model : models.Model = None, 
                              primary_key : list[str] = None,
                              as_json = False,
    ) -> tuple[str , dict[tuple[list[str] , list[str]]]]:
    '''
    Given a model, returns the name of the DB table of the given model, 
    and a dict built like this:

    {
        ('key_name1__/__key_value1', ...) : {'column_name_1' : 'value' , ...} ,
    }


    For example:


    ('user_id__/__1'  , 'title__/__Yu-Gi-Oh Complete Edition dal 3 al 13') : {  'copies_to_buy': None,
                                                                                'description': '',
                                                                                'id': 17,
                                                                                'price': None,
                                                                                'release_date': None,
                                                                                'title': 'Yu-Gi-Oh '
                                                                                        'Complete '
                                                                                        'Edition '
                                                                                        'dal '
                                                                                        '3 '
                                                                                        'al '
                                                                                        '13 '
                                                                                        '(ho '
                                                                                        'i '
                                                                                        'primi '
                                                                                        'due)',
                                                                                'useful_links': [],
                                                                                'user_id': 1}}
    
    '''

    # Initial arg checks
    if not issubclass(model, models.Model):
        raise Exception("Please pass a model.")
    
    if not isinstance(primary_key, list):
        raise Exception("Please pass a list.")


    # Create the dict
    all_items_dict = {}
    all_items_dict['Model_Name'] = model._meta.db_table

    # Gather all the objects in db
    all_objects = model.objects.all()

    # Gather all the column values in order
    all_column_values = all_objects.values() # All column values

    # Gather the keys
    for entry in all_column_values: # Iterate over the db entries ordered by value
        entry : dict

        if as_json:
            # If a datetime is used, must be converted for json
            try: 
                entry['release_date'] = entry['release_date'].isoformat()
            except:
                pass
        
        key = ''

        for k_name in primary_key:
            value = entry[k_name]
            key += k_name+KEYVALUE_SEPARATOR+str(value)+KEYKEY_SEPARATOR

        key = key[:-len(KEYKEY_SEPARATOR)] # Remove the last separator

        all_items_dict[key] = entry

    if not as_json:
        return all_items_dict

    json_data = json.dumps(all_items_dict)
    return json_data


def get_model_from_table(table_name, app_label):
    try:
        # Iterate through all models in the app
        for model in apps.get_app_config(app_label).get_models():
            if model._meta.db_table == table_name:
                return model
    except LookupError:
        return None  # Model not found



def interpret_dict_of_a_model_in_db(input_dict : dict, 
                               from_json : bool = True,
                               app_label='GeneralHandler') -> tuple[str, models.Model, int, dict]:
    '''
    First call get_dict_of_a_model_in_db() and then give the output here.


    The dict must be in format:

    { "user_id/__KEYVAL__/1/__KEYKEY__/title/__KEYVAL__/My Hero Academia 41 + 42, roba varia" : {
                                                                                                    "id": 6, 
                                                                                                    "user_id": 1, 
                                                                                                    "title": "My Hero Academia 41 + 42, roba varia", 
                                                                                                    "price": null, 
                                                                                                    "release_date": "2025-05-06T00:00:00+00:00", 
                                                                                                    "description": "Nella foto c'\u00e8 un botto di roba", 
                                                                                                    "copies_to_buy": null, 
                                                                                                    "useful_links": []
                                                                                                },
    '''

    if from_json:
        input_dict = json.loads(input_dict)

    # Type check
    if not isinstance(input_dict, dict):
        raise Exception('Please give a dict.')

    # Get model from the dict
    table_name=input_dict['Model_Name']
    model : models.Model = get_model_from_table(table_name, app_label=app_label)

    if not model or not issubclass(model, models.Model):
        raise Exception(f"Model {input_dict['Model_Name']} not found")

    # Find next autoincrement id. No need to check for table_name's correctness as it's already checked if no models.Model is found
    with connection.cursor() as cursor:
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = %s", [table_name])
        result = cursor.fetchone()
        print(result)
        next_id = result[0] + 1  # The next value is the current value + 1. Note that even if it's zero, the result "0" is returned so no need to check for a result to exist.

    return table_name, model, next_id, input_dict
    


def update_own_db_table(table_name : str, model : models.Model, next_id : int, input_dict : dict):
    # Type check
    if not isinstance(table_name, str) or not issubclass(model, models.Model) or not isinstance(next_id, int) or not isinstance(input_dict, dict):
        raise Exception("Something went wrong.")
    
    
