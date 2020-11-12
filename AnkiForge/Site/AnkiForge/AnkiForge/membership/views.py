from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from membership.models import Membership, UserMembership, Subscription
from django.contrib.auth.mixins import LoginRequiredMixin

class MembershipView(LoginRequiredMixin, ListView):


    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'

    model = Membership
    template_name = 'membership/list.html'
    context_object_name = 'memberships'
    def get_user_membership(self, request):
        user_membership_qs = UserMembership.objects.filter(user=self.request.user)
        if user_membership_qs.exists():
            return user_membership_qs.first()
        return None

    def get_queryset(self):
        # Call all data from set fgrom model
        qs = {
            'all_memberships' : Membership.objects.all(),
            'paid_memberships' : Membership.objects.all().filter(membership_type__startswith='T'),
            'free_membership' : Membership.objects.all().filter(membership_type__startswith='PA').first(),
            'user_membership' : UserMembership.objects.filter(user=self.request.user).first()
        }
        return qs


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # current_membership = self.get_user_membership(self.request)
        # context['current_membership'] = str(current_membership.membership)
        return context

class UserProfileView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'
    template_name = 'membership/profileview.html'