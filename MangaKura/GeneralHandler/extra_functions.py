from .models import *
from django.http import HttpResponse
from django.utils.html import format_html
import os
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from MangaKura import settings as GLOBAL_SETTINGS
from django.db import connections
from django.db.utils import IntegrityError
import requests
from . import database_syncer
from django.apps import apps


TURN_OFF_SUPERUSER_CHECK = False

# This is the place where all extra functions are.
# Generally, to access them, a REST API is used.
# Simply add the path to it in urls.py and run it. The path should be api/your_new_api

# IF YOU WANT TO ADD AN API TO THE LIST UNDER /apis, PLEASE USE THE DECORATOR @api FOR THAT !

# =================================================================

# List to store API function names
api_functions = []

# Decorator definition to have the API list show to the user
def api(func):
    """Decorator to mark a function as an API and store its name."""
    api_functions.append(func.__name__)
    return func  # Returns the function unchanged

def check_is_superuser(user) -> bool:
    '''
    Takes a request.user as parameter and checks is_superuser
    '''
    if TURN_OFF_SUPERUSER_CHECK:
        return True
    
    return bool(user.is_superuser)

def is_main_alive(url=GLOBAL_SETTINGS.MAIN_WEBSITE_URL, timeout=1.5) -> bool:

    if GLOBAL_SETTINGS.OFFLINE:
        return False

    # THIS IS NECESSARY! I want to be able to do some stuff, such as registering, if and only if the main service is online.s
    try:
        requests.head(url=url, verify=False, timeout=timeout) # Head method for less overhead
        return True
    except requests.exceptions.ConnectTimeout:
        return False

def remove_file(path) -> str:
    s = 'This is a default message...'
    try:
        os.remove(path)
        s = f"File {path} deleted successfully"
        print(s)
    except FileNotFoundError:
        s = f"File {path} not found"
        print(s)
    except PermissionError:
        s = f"Permission to {path} denied"
        print(s)
    except Exception as e:
        s = f"Error: {e}"
        print(s)
    finally:
        return s

def build_html_with_content_in_pre_and_cool_api_css(content=None, title='API List', api_name='Available APIs'):
    # Full HTML response with a black background and content in gray background with green text
    html_content = format_html(
        '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>'''+title+'''</title>
            <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
            <style>
                body {{ background-color: black; color: white; font-family: Arial, sans-serif; padding: 20px; }}
                pre {{ background-color: #222; color: #0f0; padding: 10px; border-radius: 5px; }}
                a {{ color: #0f0; }}
            </style>  
        </head>
        <body>
            <h1>'''+api_name+'''</h1>
            <pre>{}</pre>
        </body>
        </html>
        ''',
        format_html(content.replace('\n', '<br>'))
    )
    return html_content

def apis(request):
    funcs = 'This an API-like interface, and not a real API.<br><br>PLEASE NOTE THAT YOU CAN USE SOME APIs IF AND ONLY IF YOU ARE A SUPERUSER!<br><br>'
    for func in api_functions:
        funcs += '🔹 <a href="/api/' + func + '">' + func + '</a>\n\n'
    
    html_content = build_html_with_content_in_pre_and_cool_api_css(content=funcs)

    return HttpResponse(html_content)



YOU_ARE_NOT_SUPERUSER_MAD_RESPONSE = build_html_with_content_in_pre_and_cool_api_css(content="YOU ARE NOT A SUPERUSER! GET OUT!",
                                                                            title='GET OUT!',
                                                                            api_name='GET OUT!')


# ================================================================================================================================
# =============================                          API Methods                      ========================================
# ================================================================================================================================



@api
def recalculate_own_manga_costs(request):
    print("\n====REQUESTED A CALL TO API recalculate_own_manga_costs====\n")
    all_mangas = UserToManga.objects.filter(user=request.user)
    changed_counter = 0
    troublesome_entries = ''
    good_entries = ''
    separator = '\n=============================\n'

    for manga in all_mangas:

        manga_cost = manga.whole_series_price
        previous_calc_cost = manga.whole_series_price_calculated

        if manga_cost > 0:
            manga_cost = manga_cost
        
        else:
            # Calc total money spent the hard way...
            single_volume_price = manga.single_volume_price
            # Find a way to translate 1-5, 7, 10-11 to being volumes from 1 to 5, 7, and 10 to 11.
            # So, in total, 8 volumes.
            def count_volumes(s):
                total = 0
                parts = s.split(", ")
                
                for part in parts:
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        total += (end - start + 1)
                    else:
                        total += 1  # Single number
                
                return total
            owned_volumes_string = manga.owned_volumes

            # Check only the correct characters (1 2 3 4 5 6 7 8 9 0 , -) are there
            test : str = owned_volumes_string.replace(" ", "").replace(",", "").replace("-", "")
            if test.isdigit():
                volumes = count_volumes(manga.owned_volumes)
                manga_cost = single_volume_price * volumes
            else:
                s = f"- Manga titled '{manga.manga_title}' has bad owned_volumes: '{owned_volumes_string}'."
                troublesome_entries += "\n" + s
                print(s)
                continue   

        if previous_calc_cost != manga_cost:
            manga.whole_series_price_calculated = manga_cost
            manga.save()
            s = f"> CHANGED {manga.manga_title}'s calculated price value."
            changed_counter += 1
        else:
            s = f"> SAME {manga.manga_title}'s calculated price value."
        print(s)
        good_entries += '\n' + s
        
    content = str(changed_counter) + ' Mangas have been changed.<br>' + troublesome_entries + separator + good_entries
    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=content, title='Manga costs', api_name='Recalculate own Manga Costs'))






@api
def cleanup_unused_images(request):
    # Considering this is a function that helps the DB delete unused images,
    # no need to check for user authentication

    # THIS IS TRUE SPAGHETTI CODE
    script_path = Path(__file__).resolve()
    mangakura_directory = script_path.parent.parent
    mangakura_directory = str(mangakura_directory)

    media_directory = os.path.join(mangakura_directory, 'media')

    files_list = []

    for root, dirs, files in os.walk(media_directory):
        for f in files:
            # Note that in DB it's in the form of /media/variant_images/WhatsApp_Image_2025-02-12_at_19.39.44.jpeg
            files_list.append(os.path.join(root, f).replace(mangakura_directory, '').replace('\\', '/'))

    all_images_objects = set(VariantImage.objects.all()) | set(WishlistImage.objects.all())
    all_images_paths = []


    for img_obj in all_images_objects:
        all_images_paths.append(img_obj.image.url)

    counter = 0
    for img in all_images_paths:
        if img in files_list:
            counter += 1
            files_list.remove(img)

    # Now i need to remove the files in files_list
    s = '<br>'
    for file_to_remove in files_list:
        # No way this works, but it does. No fancy path handling, the path has \ and / but it works i'm happy with it, cya.
        file_to_remove_path = mangakura_directory + '/' + file_to_remove
        s += '- ' + remove_file(file_to_remove_path) + '<br>'

    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(
        content=(f'I should remove {len(files_list)} files.\nImages are a total of {counter}.\n' + s),
        title='Images Cleaner',
        api_name='Cleanup Unused Images'
        )
    )







@api
def change_LAZY_setting(request):
    if not check_is_superuser(request.user):
        return HttpResponse(YOU_ARE_NOT_SUPERUSER_MAD_RESPONSE)

    GLOBAL_SETTINGS.LAZY = not GLOBAL_SETTINGS.LAZY

    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=f"Swapped LAZY from {not GLOBAL_SETTINGS.LAZY} to {GLOBAL_SETTINGS.LAZY}.",
                                                                        title="LAZY Swap",
                                                                        api_name='LAZY Setting Swap'))


    

    




@api
@csrf_exempt # It is safe, considering the superuser check.
def execute_sql_raw_query_on_db(request):

    # ESSENTIAL CHECK !
    if not check_is_superuser(request.user):
        return HttpResponse(YOU_ARE_NOT_SUPERUSER_MAD_RESPONSE)

    if request.method == 'GET':
        return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=r'''<h2>Execute Raw SQL Query</h2>
                                            <form action="/api/execute_sql_raw_query_on_db" method="POST">
                                                <label for="db">DB:</label>
                                                <textarea id="query" name="db" value="default" rows="1" cols="50"></textarea><br><br>
                                                <label for="query">QUERY:</label>
                                                <textarea id="query" name="query" rows="5" cols="50" required></textarea><br><br>
                                                <button type="submit">Execute</button>
                                            </form>''',
                            title="Execute raw SQL Query",
                            api_name="Execute raw query")
                            )
    
    elif request.method == 'POST':
        db = request.POST.get("db")
        data = request.POST.get("query")  # Get SQL query from
        with connections[db].cursor() as cursor:
            try:
                cursor.execute(data)
            except IntegrityError as e:
                return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=f'{e}',
                                                                                    title='Integrity Error',
                                                                                    api_name='Intergrity Error'), status=422) # 422 for Unprocessable Entity, because the query was bad and not processable

            results = cursor.fetchall()

            entries = ''
            for _ in results:
                entries += '<br>'+str(_)

            entries = entries.replace("{", " ||DICT_START|| ").replace("}", " ||DICT_END|| ")

            return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=f"Here is the results for query: <br>====[ {data} ]==== <br><br> {str(entries)}",
                    title="Results of raw SQL Query",
                    api_name="Results of raw SQL Query")
                    )
    '''
    USEFUL QUERIES
    
    delete from GeneralHandler_usertoextrainfos where id != 1
    select * from GeneralHandler_usertoextrainfos

    update auth_user set is_superuser = 1 where username='ZeroKuraManga'
    '''



@api
def testing(request):
    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content="Want a coffee?",
                                                                        title="Very empty land...",
                                                                        api_name="Nothing to test here..."))


def get_all_models_list():
    app_name = "GeneralHandler"
    models_list = apps.get_app_config(app_name).get_models()

    return list(models_list)


@api
def update_main_database(request):

    # ESSENTIAL CHECK !
    if not check_is_superuser(request.user):
        return HttpResponse(YOU_ARE_NOT_SUPERUSER_MAD_RESPONSE)
    
    # Times have changed...
    #if not is_main_alive():
    #    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(
    #        content="The main webserver is offline, useless to execute this request now.",
    #        title="Cannot execute operation",
    #        api_name="Cannot execute operation",
    #    ))

    as_json = False

    # models_list =  get_all_models_list()
    # Manual control is way better, don't stress me too much over this.
    content = ''
    models_list = [UserToManga, UserToVariant, UserToWishlistItem, VariantImage, WishlistImage] # UserToExtraInfos will be manually handled as it's strictly related to the Users, and that table is not merged.

    for model in models_list:
        content += f'INFORMATION FOR CLASS - {model.__name__} ================================ <br><br>'

        # Load the table data from the local db
        json_data = database_syncer.get_dict_of_a_model_in_db(model=model, as_json=as_json, using_database='local')
        
        # Interpret the table data and get next_id from the default table
        args = database_syncer.interpret_dict_of_a_model_in_db(input_dict=json_data, from_json=as_json, using_database='default')
        
        # And sync by adding in my own default db
        content += database_syncer.update_own_db_table(*args, using_database='default')
        
        content += '<br><br>'

    # Return for user feedback
    if as_json:
        return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=content, title='Update DB', api_name='Update Main Database'), content_type="application/json",)
    
    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content))














# ================================================================================================================================
# =============================                           DEPRECATED                       =======================================
# ================================================================================================================================

#@api
def create_user_extra_infos_empty_entry_if_not_exists(request):
    '''
    This function does NOT work well.
    That's why it just returns.
    '''
    return HttpResponse("Not in use.")

    try:
        entry = UserToExtraInfos.objects.get(user=request.user) # This goes in error if entry does not exist...
        print(entry)
        return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=f"The entry for the user already exists!<br><br>It is :<br><br>{entry}<br><br>Doing nothing.",
                                                                            title="Generate ExtraInfos Entry",
                                                                            api_name="Create UserToExtraInfos empty entry if it does not exist"))
    except:
        entry = UserToExtraInfos.objects.create(user=request.user) # Create entry for the user

        return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=f"The entry for the user was created!<br><br>It is :<br><br>{entry}",
                                                                        title="Generate ExtraInfos Entry",
                                                                        api_name="Create UserToExtraInfos empty entry if it does not exist"))