from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from GeneralHandler.models import UserToExtraInfos
from GeneralHandler import extra_functions


# TEST USER: test1, testpwd12!

def register(request):

    # Stop if not on main server...
    if not extra_functions.is_main_alive():
        return render(request, 'print_in_home.html', {'to_print' : 'This action is disabled when offline!'})

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            UserToExtraInfos.objects.create(user=user) # Create entry for the user

            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_mk(request):
    logout(request=request)
    return redirect('home')


def home(request):
    return render(request, 'home.html')
