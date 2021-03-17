from rest_framework import permissions
from membership.models import Subscription, UserMembership

# Think its not working because i am trying to apply it to a list view, see 
# /If you require object-level filtering of list views, you'll need to filter the queryset separately.

# class UserSubscribedAndHasPoints(permissions.BasePermission):
#     """
#     Object-level permission to only allow owners of an object to edit it.
#     Assumes the model instance has an `owner` attribute.
#     """

#     def has_object_permission(self, request, view, obj):
#         if view.action == 'create':
#             print("CUNT****")
#             user = request.user
#             user_membership = UserMembership.objects.get(user=user)
#             user_subscription = Subscription.objects.get(user_membership = user_membership)
#             if (user_subscription.active and user_membership.user_points > 0):
#                 return True
#             else:
#                 return False
#         else: 
#             return True
