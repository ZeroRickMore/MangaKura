# DO NOT IMPORT ALL MODELS OR issubclass() WILL FAIL DUE TO IMPORT STUFF
from django.db import models
from django.http import HttpResponse
from pprint import pprint

SEPARATOR = '__/__'

def get_column_names_of_a_model(model=None) -> list[str]:

    if not issubclass(model, models.Model):
        raise Exception("Please pass a model.")
    
    return [field.column for field in model._meta.fields]



def get_dict_of_a_model_in_db(model : models.Model = None, 
                              primary_key : list[str] = None
    ) -> tuple[str , dict[tuple[list[str] , list[str]]]]:
    '''
    Given a model, returns the name of the model, 
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

    # Gather all the objects in db
    all_objects = model.objects.all()

    # Gather all the column values in order
    all_column_values = all_objects.values() # All column values

    # Gather the keys
    for entry in all_column_values: # Iterate over the db entries ordered by value
        entry : dict
        key = []

        for k_name in primary_key:
            value = entry[k_name]
            key.append(k_name+SEPARATOR+str(value))

        key = tuple(key) # To become a key must be immutable

        all_items_dict[key] = entry

    return model.__name__ , all_items_dict


def read_dict_of_a_model_in_db(input_dict : dict):

    # Type check
    if not isinstance(input_dict, dict):
        raise Exception("Please give a dict.")
    
    