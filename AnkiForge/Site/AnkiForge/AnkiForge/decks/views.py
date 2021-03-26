from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from decks.forms import CreateUserDeckForm
from decks.models import UserDecks, ForgedDecks
from django.contrib.auth.decorators import login_required
from django.urls import reverse

class DecksIndexView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    template_name = "decks/decks_preview_index.html"

class DecksPreviewStandard(LoginRequiredMixin, TemplateView):
    login_url='main_entrance:login'
    template_name="decks/decks_preview_standard.html"

class DecksPreviewStandardTBS(LoginRequiredMixin, TemplateView):
    login_url='main_entrance:login'
    template_name="decks/decks_preview_standard_TBS.html"


class UserDecksCreateView(LoginRequiredMixin, CreateView):
    login_url = 'main_entrance:login'
    
    template_name = "decks/new_deck_form.html"
    form_class = CreateUserDeckForm
    model = UserDecks

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class UserDecksList(LoginRequiredMixin, ListView):

    login_url = 'main_entrance:login'
    model = UserDecks
    template_name = 'decks/decks_list.html'
    context_object_name = 'userdecks'

    def get_queryset(self):
        current_user_decks = UserDecks.objects.filter(user=self.request.user)

        qs = {
            'current_user_decks' : current_user_decks,
        }
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # current_membership = self.get_user_membership(self.request)
        # context['current_membership'] = str(current_membership.membership)
        return context
