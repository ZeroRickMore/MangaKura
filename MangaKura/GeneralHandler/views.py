from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MangaForm, VariantImageFormSet
from django.utils.html import format_html
from .forms import UserToVariantForm, CopiesSoldForm
from .models import UserToVariant, VariantImage
from collections import defaultdict



@login_required
# Link a new manga to the logged in User
def insert_manga(request):
    if request.method == "POST":
        form = MangaForm(request.POST)
        if form.is_valid():
            manga = form.save(commit=False)
            manga.user = request.user  # Link the manga to the logged-in user
            manga.manga_title = manga.manga_title[0].upper() +  manga.manga_title[1:] # Capitalize first letter
            manga.save()
            return redirect('manga_detail', manga_id=manga.id)
    else:
        form = MangaForm()

    return render(request, 'insert_manga.html', {'form': form})



# Link a new Variant to the logged in User

@login_required
def insert_variant(request):
    if request.method == 'POST':
        form = UserToVariantForm(request.POST, request.FILES)


        # Generate the correct number of CopiesSoldForm instances
        copies_sold_forms = CopiesSoldForm(request.POST, prefix=f'copy_0')

        form.copies_sold_forms = copies_sold_forms  # Attach to main form

        # 🚨 Debugging: Print received POST data
        print("\n🔍 DEBUG: request.POST\n", dict(request.POST))

        # 🚨 Debugging: Print form errors
        if not form.is_valid():
            print("\n🚨 Form Errors:", form.errors)

        if not copies_sold_forms.is_valid():
            print(f"\n🚨 CopiesSoldForm Errors:", copies_sold_forms.errors)

        # ✅ Proceed only if all forms are valid
        if form.is_valid() and copies_sold_forms.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

            # Process Copies Sold Data
            copies_sold_data = []

            price_list = copies_sold_forms.cleaned_data.get('price')
            amount_list = copies_sold_forms.cleaned_data.get('amount')

            for i in range(len(price_list)):
                price = price_list[i]
                amount = amount_list[i]
                if price is not None and amount is not None:
                    copies_sold_data.append({"price": price, "amount": amount})

            instance.copies_sold = copies_sold_data  # Save copies_sold data
            instance.variant_title = instance.variant_title[0].upper() +  instance.variant_title[1:] # Capitalize first letter


            instance.save()

            # Save Images (handle multiple images)
            if 'images' in request.FILES:  # Check if images are included in the request
                images = request.FILES.getlist('images')  # Get the list of images
                for image in images:
                    VariantImage.objects.create(variant=instance, image=image)  # Save each image

            return redirect('variant_detail', variant_id=instance.id)

        else:
            print("\n❌ Validation failed. Fix the above errors.")

    else:
        form = UserToVariantForm()
        copies_sold_forms = [CopiesSoldForm(prefix=f'copy_0')]

    return render(request, 'insert_variant.html', {'form': form, 'copies_sold_forms': copies_sold_forms})





@login_required
def variant_detail(request, variant_id):
    # Fetch the saved UserToVariant instance by ID
    variant = get_object_or_404(UserToVariant, id=variant_id, user=request.user)
    variant.description = format_html('<br><br>' + variant.description.replace('\n', '<br>'))
    variant.vinted_description = format_html('<br><br>' + variant.vinted_description.replace('\n', '<br>'))
    # Get associated images for this variant
    images = VariantImage.objects.filter(variant=variant)

    # Render the data in the template
    return render(request, 'variant_detail.html', {
        'variant': variant,
        'images': images,
        'copies_sold': variant.copies_sold,  # Assuming it's stored as JSON
        'useful_links': variant.useful_links,  # Display useful links (if any)
    })



@login_required
def manga_detail(request, manga_id):
    manga = get_object_or_404(UserToManga, id=manga_id, user=request.user)
    manga.description = format_html('<br><br>' + manga.description.replace('\n', '<br>'))
    return render(request, 'manga_detail.html', {'manga': manga})



# =================== VISUALIZE METHODS ============================

from .models import UserToManga, UserToVariant

@login_required
def view_manga(request):
    user_manga = UserToManga.objects.filter(user=request.user).order_by('manga_title')
    return render(request, 'user_manga_list.html', {'user_manga': user_manga})

@login_required
def view_variant(request):
    # Prefetch related images using the 'images' related name
    user_variants = UserToVariant.objects.filter(user=request.user).order_by('variant_title').prefetch_related('images')
    
    return render(request, 'user_variant_list.html', {'user_variants': user_variants})


#Location


@login_required
def view_variants(request):
    sort_order = [
        "Quadro sopra il PC",
        "Mensola sopra PC 1",
        "Mensola sopra PC 2",
        "Libreria nera mensola 1",
        "Libreria nera mensola 2",
        "Libreria nera mensola 3",
        "Libreria nera mensola 4",
        "Libreria nera mensola 5",
        "Mensola sopra termosifone 1",
        "Mensola sopra termosifone 2",
        "Mensola sopra termosifone 3",
        "Scaffale pianoforte sx 1",
        "Scaffale pianoforte sx 2",
        "Scaffale pianoforte dx 1",
        "Scaffale pianoforte dx 2",
        "Mobile della scrivania 1",
        "Mobile della scrivania 2",
        "Mobile della scrivania 3",
        "Mensola sopra il letto",
        "Armadio del letto",
        "Baule",
        "All",
    ]

    variants = UserToVariant.objects.all().order_by('variant_title')

    variants_in_multiple_locations = []
    
    # Group variants by location
    grouped_variants = defaultdict(list)
    for variant in variants:
        physical_positions = variant.physical_position.split(" | ")

        if len(physical_positions) > 1:
            variants_in_multiple_locations.append(variant.variant_title)

        for physical_pos in physical_positions:
            physical_pos = physical_pos.strip()
            grouped_variants[physical_pos].append(variant)

    # Sort locations based on the predefined order
    sorted_groups = [(loc, grouped_variants[loc]) for loc in sort_order if loc in grouped_variants.keys()]



    # DEBUG AND CHECKS =================================================================

    error_msg = ""

    sorted_variant_sum = 0
    sorted_variants_names = []
    for _ in sorted_groups:
        variant_list = _[1] # It's a tuple (location, list_of_variant_in_location)
        sorted_variant_sum += len(variant_list)
        for var in variant_list:
            sorted_variants_names.append(var.variant_title)

    duplicates = []

    variants_names = [_.variant_title for _ in variants]
    
    for var_name in variants_names:
        if var_name in duplicates:
            s = f"{var_name} DUPPED IN VARIANTS_NAMES"
            print(s)
            error_msg += s + '\n'
        else:
            duplicates.append(var_name)

        if var_name not in sorted_variants_names:
            s = f"{var_name} not in sorted"
            print(s)
            error_msg += s + '\n'
    
    duplicates = []
    duplicated_but_correct_because_multiple_locations = 0

    for var_name in sorted_variants_names:
        if var_name in duplicates:
            # It is an error, this should not be duplicated
            s = f"{var_name} DUPPED IN sorted_variants_names"
            print(s)
            error_msg += s + '\n'
        else:
            duplicates.append(var_name)

        if var_name not in variants_names:
            s= f"{var_name} not in unsorted"
            print(s)
            error_msg += s + '\n'

    print("- Expected Variants ->", len(variants_names))
    print("- Sorted Variants ->", len(sorted_variants_names))
    print("- Duplicated Correctly because of multiple locations ->", duplicated_but_correct_because_multiple_locations)
    print("- Is all good? ->", len(variants_names) == (len(sorted_variants_names) - duplicated_but_correct_because_multiple_locations))
    print("- ERRORS ->", error_msg)

    if error_msg != '':
        error_msg = 'ERRORS:\n' + error_msg
    # DEBUG AND CHECKS =================================================================

    
    return render(request, "user_variant_list_location_sorted.html", {"sorted_groups": sorted_groups, "error_msg": error_msg})



@login_required
def view_mangas(request):
    sort_order = [
        "Quadro sopra il PC",
        "Mensola sopra PC 1",
        "Mensola sopra PC 2",
        "Libreria nera mensola 1",
        "Libreria nera mensola 2",
        "Libreria nera mensola 3",
        "Libreria nera mensola 4",
        "Libreria nera mensola 5",
        "Mensola sopra termosifone 1",
        "Mensola sopra termosifone 2",
        "Mensola sopra termosifone 3",
        "Scaffale pianoforte sx 1",
        "Scaffale pianoforte sx 2",
        "Scaffale pianoforte dx 1",
        "Scaffale pianoforte dx 2",
        "Mobile della scrivania 1",
        "Mobile della scrivania 2",
        "Mobile della scrivania 3",
        "Mensola sopra il letto",
        "Armadio del letto",
        "Baule",
        "All",
    ]

    mangas = UserToManga.objects.all().order_by('manga_title')
    
    mangas_in_multiple_locations = []

    # Group variants by location
    grouped_mangas = defaultdict(list)
    for manga in mangas:
        physical_positions = manga.physical_position.split(" | ")

        if len(physical_positions) > 1:
            mangas_in_multiple_locations.append(manga.manga_title)

        for physical_pos in physical_positions:
            physical_pos = physical_pos.strip()
            grouped_mangas[physical_pos].append(manga)

    # Sort locations based on the predefined order
    sorted_groups = [(loc, grouped_mangas[loc]) for loc in sort_order if loc in grouped_mangas.keys()]



    # DEBUG AND CHECKS =================================================================

    error_msg = ""

    sorted_mangas_sum = 0
    sorted_mangas_names = []
    for _ in sorted_groups:
        manga_list = _[1] # It's a tuple (location, list_of_variant_in_location)
        sorted_mangas_sum += len(manga_list)
        for manga in manga_list:
            sorted_mangas_names.append(manga.manga_title)

    duplicates = []

    mangas_names = [_.manga_title for _ in mangas]
    
    for manga_name in mangas_names:
        if manga in duplicates:
            s = f"{manga} DUPPED IN MANGAS_NAMES"
            print(s)
            error_msg += s + '\n'
        else:
            duplicates.append(manga_name)

        if manga_name not in sorted_mangas_names:
            s = f"{manga_name} not in sorted"
            print(s)
            error_msg += s + '\n'
    
    duplicates = []
    duplicated_but_correct_because_multiple_locations = 0

    for manga_name in sorted_mangas_names:
        if manga_name in duplicates:
            if manga_name not in mangas_in_multiple_locations:
                # It is an error, this should not be duplicated
                s = f"{manga_name} DUPPED IN sorted_variants_names"
                print(s)
                error_msg += s + '\n'
            else:
                print(f"{manga_name} is duplicated but it's fine as it is in multiple locations!")
                duplicated_but_correct_because_multiple_locations += 1
        else:
            duplicates.append(manga_name)

        if manga_name not in mangas_names:
            s= f"{manga_name} not in unsorted"
            print(s)
            error_msg += s + '\n'

    print("- Expected Mangas ->", len(mangas_names))
    print("- Sorted Mangas ->", len(sorted_mangas_names))
    print("- Duplicated Correctly because of multiple locations ->", duplicated_but_correct_because_multiple_locations)
    print("- Is all good? ->", len(mangas_names) == (len(sorted_mangas_names) - duplicated_but_correct_because_multiple_locations))
    print("- ERRORS ->", error_msg)


    if error_msg != '':
        error_msg = 'ERRORS:\n' + error_msg
    # DEBUG AND CHECKS =================================================================

    
    return render(request, "user_manga_list_location_sorted.html", {"sorted_groups": sorted_groups, "error_msg": error_msg})




# ==================== DELETE AND EDIT METHODS =========================


login_required
def edit_manga(request, manga_id):
    manga = get_object_or_404(UserToManga, id=manga_id, user=request.user)
    if request.method == "POST":
        form = MangaForm(request.POST, instance=manga)
        if form.is_valid():
            form.save()
            return redirect('manga_detail', manga_id=manga.id)
    else:
        form = MangaForm(instance=manga)
    return render(request, 'edit_manga.html', {'form': form})

@login_required
def delete_manga(request, manga_id):
    manga = get_object_or_404(UserToManga, id=manga_id, user=request.user)
    if request.method == "POST":
        manga.delete()
        return redirect('view_manga')
    return render(request, 'delete_manga.html', {'manga': manga})

@login_required
def edit_variant(request, variant_id):
    variant = get_object_or_404(UserToVariant, id=variant_id, user=request.user)
    if request.method == "POST":
        form = UserToVariantForm(request.POST, instance=variant)
        formset = VariantImageFormSet(request.POST, request.FILES, instance=variant)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('variant_detail', variant_id=variant.id)
    else:
        form = UserToVariantForm(instance=variant)
        formset = VariantImageFormSet(instance=variant)
    
    return render(request, 'edit_variant.html', {'form': form, 'formset': formset})

@login_required
def delete_variant(request, variant_id):
    variant = get_object_or_404(UserToVariant, id=variant_id, user=request.user)
    if request.method == "POST":
        variant.delete()
        return redirect('view_variant')  # Redirect to user's dashboard after deletion
    return render(request, 'delete_variant.html', {'variant': variant})






# ====================== SEARCH METHODS ============================

def search_view(request, category):
    query = request.GET.get('q', '')

    if category == "Manga":
        results = UserToManga.objects.filter(manga_title__icontains=query, user=request.user).order_by('manga_title')
    elif category == "Variant":
        results = UserToVariant.objects.filter(variant_title__icontains=query, user=request.user).order_by('variant_title')
    else:  # Default: Any
        results = list(UserToManga.objects.filter(manga_title__icontains=query, user=request.user).order_by('manga_title')) + list(UserToVariant.objects.filter(variant_title__icontains=query, user=request.user).order_by('variant_title'))

    return render(request, 'search_results.html', {'results': results, 'query': query, 'category': category})
