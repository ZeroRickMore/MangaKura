from .models import UserToManga
from django.http import HttpResponse
from django.utils.html import format_html

# This is the place where all extra functions are.
# Generally, to access them, a REST API is used.
# Simply add the path to it in urls.py and run it. The path should be api/your_new_api

# IF YOU WANT TO ADD AN API TO THE LIST UNDER /apis, PLEASE USE THE DECORATOR @api FOR THAT !

# =================================================================



# List to store API function names
api_functions = []

# Decorator definition
def api(func):
    """Decorator to mark a function as an API and store its name."""
    api_functions.append(func.__name__)
    return func  # Returns the function unchanged


def build_html_with_content_in_pre_and_cool_api_css(content):
    # Full HTML response with a black background and content in gray background with green text
    html_content = format_html(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API List</title>
            <style>
                body {{ background-color: black; color: white; font-family: Arial, sans-serif; padding: 20px; }}
                pre {{ background-color: #222; color: #0f0; padding: 10px; border-radius: 5px; }}
                a {{ color: #0f0; }}
            </style>
        </head>
        <body>
            <h1>Available APIs</h1>
            <pre>{}</pre>
        </body>
        </html>
        """,
        format_html(content)
    )

    return html_content


def apis(request):
    funcs = ''
    for func in api_functions:
        funcs += '🔹 <a href="/api/' + func + '">' + func + '</a>\n\n'
    
    html_content = build_html_with_content_in_pre_and_cool_api_css(content=funcs)

    return HttpResponse(html_content)

@api
def recalculate_own_manga_costs(request):
    print("\n====REQUESTED A CALL TO API recalculate_own_manga_costs====\n")
    all_mangas = UserToManga.objects.filter(user=request.user)
    s_tot = ''
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
        else:
            s = f"> SAME {manga.manga_title}'s calculated price value."
        print(s)
        good_entries += '\n' + s
        
    content = troublesome_entries + separator + good_entries
    return HttpResponse(build_html_with_content_in_pre_and_cool_api_css(content=content))
