# DO NOT IMPORT ALL MODELS OR issubclass() WILL FAIL DUE TO IMPORT STUFF
from django.db import models
import json
from django.apps import apps
from MangaKura import settings as GLOBAL_SETTINGS
import requests
from django.db import connections
from django.db.utils import IntegrityError

#KEYVALUE_SEPARATOR = '/__KEYVAL__/'
#KEYKEY_SEPARATOR = '/__KEYKEY__/'

def get_column_names_of_a_model(model=None) -> list[str]:

    if not issubclass(model, models.Model):
        raise Exception("Please pass a model.")
    
    return [field.column for field in model._meta.fields]



def get_dict_of_a_model_in_db(model : models.Model = None, 
                              #primary_key : list[str] = None,
                              as_json : bool = False,
                              using_database : str = None,
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
    
    if not using_database:
        raise Exception("Give a db to use.")

    # Initial arg checks
    if not issubclass(model, models.Model):
        raise Exception("Please pass a model.")
    
    #if not isinstance(primary_key, list):
    #    raise Exception("Please pass a list.")

    if not isinstance(as_json, bool) or not isinstance(using_database, str):
        raise Exception("Something went wrong.")

    # Create the dict
    all_items_dict = {}
    all_items_dict['Model_Name'] = model._meta.db_table

    # Gather all the objects in db
    all_objects = model.objects.using(using_database).all() # This will raise an exception is the db does not exist

    # Gather all the column values in order
    all_column_values = all_objects.values() # All column values

    # Gather the keys
    i = 0
    for entry in all_column_values: # Iterate over the db entries ordered by value
        entry : dict

        try: 
            entry['release_date'] = entry['release_date'].isoformat()
        except:
            pass
        
        key = f"OBJ{i}"
        i += 1

        # All useless... 
        #for k_name in primary_key:
        #    value = entry[k_name]
        #    key += k_name+KEYVALUE_SEPARATOR+str(value)+KEYKEY_SEPARATOR
        #key = key[:-len(KEYKEY_SEPARATOR)] # Remove the last separator

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
                               app_label : str ='GeneralHandler',
                               using_database : str = None) -> tuple[str, models.Model, int, dict]:
    '''
    First call get_dict_of_a_model_in_db() and then give the output here.


    The dict must be in format:

    { "any string"  :   {
                            "id": 6, 
                            "user_id": 1, 
                            "title": "My Hero Academia 41 + 42, roba varia", 
                            "price": null, 
                            "release_date": "2025-05-06T00:00:00+00:00", 
                            "description": "Nella foto c'\u00e8 un botto di roba", 
                            "copies_to_buy": null, 
                            "useful_links": []
                        } ,
        ...
    }
    '''

    if not using_database:
        raise Exception("Give a db to use.")

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
    with connections[using_database].cursor() as cursor:
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = %s", [table_name])
        result = cursor.fetchone()
        next_id = result[0] + 1  # The next value is the current value + 1. Note that even if it's zero, the result "0" is returned so no need to check for a result to exist.

    input_dict.pop('Model_Name') # Useless from here onwards

    return table_name, model, next_id, input_dict



def update_own_db_table(table_name : str, model : models.Model, next_id : int, input_dict : dict, using_database : str = None):
    '''
    First call interpret_dict_of_a_model_in_db() and then this
    '''

    if not using_database:
        raise Exception("Give a db to use.")

    # Type check
    if not isinstance(table_name, str) or not issubclass(model, models.Model) or not isinstance(next_id, int) or not isinstance(input_dict, dict) or not isinstance(using_database, str):
        raise Exception("Something went wrong.")
    
    stats = ''
    added = 0
    updated = 0

    # NOTE: No need to check for the pre-existance of the primary key, as SQLite will fail due to the containt fail.
    # Considering that, I can simply execute INSERT queries without checking the existence first.
    # I just need to adjust the autoincrement id properly.
    # Also, the sqlite_sequence table is updated automatically.

    input_dict.pop('Model_Name', None) # Just in case it's still here, as it's useless now

    for k in input_dict:
        entry = input_dict[k] # Database entry as a dict column_name : value

        entry['id'] = next_id
        column_names_in_order = ""
        column_values_in_order = []

        for column_name in entry:
            value = entry[column_name]

            if isinstance(value, list):
                value = "[]"
            
            column_names_in_order += f"{column_name},"
            column_values_in_order.append(value)

        column_names_in_order = column_names_in_order[:-1] # Remove last ","

        query = f"INSERT INTO {table_name} ({column_names_in_order}) VALUES ({f"{'%s,'*len(column_values_in_order)}"[:-1]})"
        
        print(column_values_in_order)

        with connections[using_database].cursor() as cursor:
            try:
                cursor.execute(query, column_values_in_order)
                s = f'Added {entry['title']} to DB.' 
                stats += s+'<br>'
                added += 1
                next_id += 1
            except IntegrityError as e:
                s = f"Item {entry['title']} -> {e}"

                # This is the error type
                # UNIQUE constraint failed: GeneralHandler_usertowishlistitem.user_id, GeneralHandler_usertowishlistitem.title
                e = str(e)
                e = e.replace("UNIQUE constraint failed: ", "")
                e = e.replace(str(model._meta.db_table)+".", "")
                e = e.replace(" ", "")
                e = e.split(",")

                #print(column_names_in_order)
                query_update = f"UPDATE {table_name} SET {str([ str(column)+'=%s' for column in column_names_in_order.replace(" ", "").split(",") if column != 'id' ])[1:-1].replace("'", "")} where id=(select id from {table_name} where {str([str(pkey_name)+'=%s' for pkey_name in e])[1:-1].replace("'", "").replace(",", " and")})"

                # Prepare for %s query
                column_values_in_order.pop(0) # Remove id
                for k in e: # Append primary key column names
                   column_values_in_order.append(entry[k]) 

                #print(query_update.count("%s"), "  -  ", len(column_values_in_order))
                cursor.execute(query_update, column_values_in_order)

                #s += '<br>'+query_update+'<br>'+str(column_values_in_order)+'<br><br>'
                stats += s+'<br>'
                
                updated += 1

            
            #print(s)

    return '<br>'.join([stats, "Added - "+str(added), "updated - "+str(updated)])




'''
Put into extra_functions if necessary

@api
def testing(request):
    def test_get_dict():
        return database_syncer.get_dict_of_a_model_in_db(model=UserToWishlistItem, as_json=as_json)

    
    def test_read_dict():
        json_data = database_syncer.get_dict_of_a_model_in_db(model=UserToWishlistItem, as_json=as_json)

        return database_syncer.interpret_dict_of_a_model_in_db(input_dict=json_data, from_json=as_json)

    def test_update():
        json_data = database_syncer.get_dict_of_a_model_in_db(model=UserToWishlistItem, as_json=as_json, using_database=using_database)
        args = database_syncer.interpret_dict_of_a_model_in_db(input_dict=json_data, from_json=as_json, using_database=using_database)
        return database_syncer.update_own_db_table(*args, using_database=using_database)
        

    def test_update_single():
        input_dict =   {'OBJ18': {  'copies_to_buy': None,
                                    'description': 'Ho qualche volume, vorrei averceli tutti!\r\n'
                                                    'Sarebbe figo...',
                                    'id': 26,
                                    'price': 6.0,
                                    'release_date': None,
                                    'title': 'The Walking Dead Color Edition 500 Copie Tedesco (serie '
                                                'completa)',
                                    'useful_links': ['https://saldapress.com/ricerca/s/model_AllTypeOfProducts/lingua_It/allpsearch_the%20walking%20dead/ptype_0/autore_388/categoria_20/promo_0/bundles_0/cartagiovani_0/anteprima_0/autografo_0/prezzo_0%7C%7C464/numresult_30/page_0/'],
                                    'user_id': 1},
        }
        
        return database_syncer.update_own_db_table(table_name='GeneralHandler_usertowishlistitem', model=UserToWishlistItem, next_id=30, input_dict=input_dict)

    as_json = True
    using_database = 'default'

    if not as_json:
        return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(test_update()), content_type="application/json")
    
    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(test_update()))
'''




'''
TESTS

1) Metti nel db local
local
insert into GeneralHandler_usertowishlistitem (id, user_id, title, description, useful_links) values (1, 1, 'test', 'testDesc', '[]')


2) Guarda che sta li e non pure in default
local
select * from GeneralHandler_usertowishlistitem where id=1
(fa vedere la entry con id 1)

default
select * from GeneralHandler_usertowishlistitem where id=1
(vuoto)

3) Updata con API
Output -> Added test to DB.

4) Controlla di nuovo
default
select * from GeneralHandler_usertowishlistitem where title='test'
(fa vedere la entry con id 34 perché è il next!)

5) Testa con update
local
update GeneralHandler_usertowishlistitem set title='testMODIFIED' where title='test'

6) Updata con API 
Output -> Added testMODIFIED to DB.
(ha funzionato modificando una entry ma lasciandogli lo stesso id!)

6.5) Controlla le entry sul default
====[ select * from GeneralHandler_usertowishlistitem where title like('test%') ]==== 
(34, 'test', None, None, 'testDesc', None, '[]', 1)
(35, 'testMODIFIED', None, None, 'testDesc', None, '[]', 1)

7) Modifica un parametro non chiave (descrizione)
local
update GeneralHandler_usertowishlistitem set description='descMODIFIED' where title='testMODIFIED'

7.5) Controlla la modifica sul locale
====[ select * from GeneralHandler_usertowishlistitem where title='testMODIFIED' ]==== 
(1, 'testMODIFIED', None, None, 'descMODIFIED', None, '[]', 1)

8) Attiva API
(Added - 0) Perfetto! Non ha aggiunto niente perché nnon ho modificato una key

9) Controlla la modifica sul default
====[ select * from GeneralHandler_usertowishlistitem where title='testMODIFIED' ]==== 
(35, 'testMODIFIED', None, None, 'descMODIFIED', None, '[]', 1)
'''