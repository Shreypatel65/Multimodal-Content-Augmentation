from django.shortcuts import redirect


def is_logged_in(function):
    """Decorator to check if the user is logged in.\n
    LOGIN->CURRENT PAGE | NO LOGIN->INDEX PAGE"""
    def wrapper(request, *args, **kwargs):
        if 'username' in request.session:
            print('User is logged in')
            return function(request, *args, **kwargs)
        else:
            print('User is not logged in')
            return redirect('index')
    return wrapper


def is_not_logged_in(function):
    """Decorator to check if the user is not logged in.\n
    NO LOGIN->CURRENT PAGE | LOGIN->HOME PAGE"""
    def wrapper(request, *args, **kwargs):
        if 'username' in request.session:
            return redirect('home')
        else:
            return function(request, *args, **kwargs)
    return wrapper
