from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from membership.models import Subscription, UserMembership
from django.urls import reverse_lazy
# def user_is_entry_author(function):
#     def wrap(request, *args, **kwargs):
#         entry = Entry.objects.get(pk=kwargs['entry_id'])
#         if entry.created_by == request.user:
#             return function(request, *args, **kwargs)
#         else:
#             raise PermissionDenied
#     wrap.__doc__ = function.__doc__
#     wrap.__name__ = function.__name__
#     return wrap

def user_is_subscribed(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        user_membership = UserMembership.objects.get(user=user)
        user_subscription = Subscription.objects.get(user_membership = user_membership)
        if user_subscription.active:
            return function(request, *args, **kwargs)
        else: 
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# Need to write decorator for user has no points
# Do I really need to redirect for this? User shouldn't have access to initial view to to access this because of mixin
# However potentially a link from desktop app would input in the direct url, so yes i need redirect

def user_has_points(function):
    def wrap(request, *args, **kwargs):
        user= request.user
        user_membership = UserMembership.objects.get(user=user)
        if user_membership.user_points >0:
            return function(request, *args, **kwargs)
        else:
            redirect_url = reverse_lazy('main_entrance:index')
            return redirect(redirect_url)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap