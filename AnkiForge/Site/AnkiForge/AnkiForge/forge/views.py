from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, FormView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from forge.forms import AddIncomingCardForm
from decks.models import IncomingCards, UserDecks
from rest_framework import generics
from django.conf import settings
from decks.serializers import UserDecksSerializer, IncomingCardsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from forge.tasks import translate_and_archive
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

class ForgeIndexView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
    
    template_name = "forge/forge_index.html"

class IncomingCardCreateView(LoginRequiredMixin, CreateView):
    login_url = 'main_entrance:login'

    template_name = "forge/add_incoming_card.html"
    form_class = AddIncomingCardForm
    model = IncomingCards

    # Passing the user to forms to adjust options
    def get_form_kwargs(self):
        kwargs = super(IncomingCardCreateView,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# class ForgeDecks(LoginRequiredMixin, ListView):

#     login_url = 'main_entrance:login'
#     # redirect_field_name= 'main_entrance/index.html'

#     model = UserDecks
#     template_name = 'forge/forge_decks.html'
#     context_object_name = 'userdecks'


#     def get_queryset(self):
#         # Call all data from set fgrom model
#         qs = {
#             'current_user_decks' : UserDecks.objects.filter(user=self.request.user),
#         }
#         return qs


#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # current_membership = self.get_user_membership(self.request)
#         # context['current_membership'] = str(current_membership.membership)
#         return context


"""Building view up from base"""

class ForgeDecksIndex(LoginRequiredMixin, ListView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'

    model = UserDecks
    template_name = 'forge/forge_decks_index.html'
    context_object_name = 'userdecks' 

    def get_queryset(self):
        return UserDecks.objects.filter(user= self.request.user)
         
 
class ForgeDecksList(LoginRequiredMixin, ListView):
    login_url = 'main_entrance:login'
    template_name = 'forge/forge_decks.html'
    context_object_name = 'userdecks'

    def get_queryset(self):
        self.current_deck = get_object_or_404(UserDecks, id=self.kwargs['pk'], user=self.request.user)
        self.deck_name = self.current_deck.ankiforge_deck_name
        self.current_decks_cards = IncomingCards.objects.filter(deck=self.current_deck)
        return UserDecks.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['deck_name'] = self.deck_name
        context['current_decks_cards'] = self.current_decks_cards
        context['current_deck'] = self.current_deck
        return context

@login_required
def forge_action(request, pk):
    current_deck = get_object_or_404(UserDecks, id=pk, user=request.user)
    current_decks_cards = IncomingCards.objects.filter(deck=current_deck)
    for card in current_decks_cards:
        print(card.incoming_quote)
    return redirect('main_entrance:index')


# class ForgeDecksList(ListView):

#     template_name = 'forge/forge_decks.html'
#     context_object_name = 'userdecks'

#     def get_queryset(self):
#         self.deck_name = get_object_or_404(UserDecks, ankiforge_deck_name=self.kwargs['deck_name'])
#         self.current_decks_cards = IncomingCards.objects.filter(deck=self.deck_name)
#         return UserDecks.objects.filter(user=self.request.user)

#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the publisher
#         context['deck_name'] = self.deck_name
#         context['current_decks_cards'] = self.current_decks_cards
#         return context

# class PublisherDetail(DetailView):

#     model = Publisher

#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in a QuerySet of all the books
#         context['book_list'] = Book.objects.all()
#         return context


""" View for testing media collect task"""
# from django.shortcuts import render
# from django.http import HttpResponse

# def test_media_collect(request):
#     translate_and_archive.delay()
#     return HttpResponse("The task should be sent!")

"""API VIEWS"""

"""Retrieve decks for current user """
class UserDecksAPIList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDecksSerializer

    def get_queryset(self):
        user = self.request.user
        return UserDecks.objects.filter(user=user)

""" Add cards API """
class UserIncomingCardsAPIList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IncomingCardsSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

        # This may be useful if problems with perform create
    # def create(self, request, *args, **kwargs):
    #     creating_user = IncomingCards(user=self.request.user)
    #     serializer = self.serializer_class(creating_user, data = request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else : 
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_queryset(self):
        user = self.request.user
        return IncomingCards.objects.filter(user=user)


"""All incoming cards view AdminCardsView (TBC if go through this route) """




