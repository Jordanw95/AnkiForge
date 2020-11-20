from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from forge.forms import AddIncomingCardForm
from decks.models import IncomingCards, UserDecks

class ForgeIndexView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    
    template_name = "forge/forge_index.html"

class IncomingCardCreateView(LoginRequiredMixin, CreateView):
    login_url = 'main_entrance:login'

    template_name = "forge/add_incoming_card.html"
    form_class = AddIncomingCardForm
    model = IncomingCards

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)