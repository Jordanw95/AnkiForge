from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, FormView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from forge.forms import AddCardForm
from decks.models import IncomingCards, UserDecks, ForgedDecks
from membership.models import UserMembership, Subscription
from rest_framework import generics
from django.conf import settings
from decks.serializers import UserDecksSerializer, IncomingCardsSerializer,ReadyForForgeCardsSerializer, UserPointsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from forge.tasks import translate_and_archive
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import celery
import requests
import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from AnkiForge.mixins import LoggedInRedirectMixin, UserSubscribedMixin, UserSubscribedWithPointsMixin
from django.urls import reverse_lazy
from AnkiForge.decorators import user_is_subscribed, user_has_points



"""****CLASS BASED VIEWS****"""


class ForgeIndexView(UserSubscribedMixin, TemplateView):
    template_name = "forge/forge_index.html"
    redirect_url = reverse_lazy('main_entrance:index')
    

class AddCardIndex(UserSubscribedWithPointsMixin, ListView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'

    model = UserDecks
    template_name = 'forge/add_card_index.html'
    context_object_name = 'userdecks' 
    
    def get_queryset(self):
        return UserDecks.objects.filter(user= self.request.user)

    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class ForgeDecksIndex(UserSubscribedMixin, ListView):
    login_url = 'main_entrance:login'
    # redirect_field_name= 'main_entrance/index.html'

    model = UserDecks
    template_name = 'forge/forge_decks_index.html'
    context_object_name = 'userdecks' 

    def get_queryset(self):
        return UserDecks.objects.filter(user= self.request.user)
         
 
class ForgeDecksList(UserSubscribedMixin, ListView):
    login_url = 'main_entrance:login'
    template_name = 'forge/forge_decks.html'
    context_object_name = 'userdecks'

    def get_queryset(self):
        self.current_deck = get_object_or_404(UserDecks, id=self.kwargs['pk'], user=self.request.user)
        self.deck_name = self.current_deck.ankiforge_deck_name
        self.current_decks_cards = IncomingCards.readyforforge.filter(deck=self.current_deck)
        return UserDecks.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['deck_name'] = self.deck_name
        context['current_decks_cards'] = self.current_decks_cards
        context['current_deck'] = self.current_deck
        return context

class AlreadyForgedDecksIndex(UserSubscribedMixin, ListView):
    login_url = 'main_entrance:login'
    template_name = 'forge/already_forged_decks_index.html'
    context_object_name = 'userdecks'

    def get_queryset(self):
        return UserDecks.objects.filter(user= self.request.user)

class AlreadyForgedDecksList(UserSubscribedMixin, ListView):
    login_url = 'main_entrance:login'
    template_name = 'forge/already_forged_decks_list.html'
    context_object_name = 'userdecks'

    def get_queryset(self):
        self.current_deck = get_object_or_404(UserDecks, id=self.kwargs['pk'], user=self.request.user)
        self.deck_name = self.current_deck.ankiforge_deck_name
        self.current_deck_forged_decks = ForgedDecks.objects.filter(deck=self.current_deck)
        return UserDecks.objects.filter(user= self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['deck_name'] = self.deck_name
        context['forged_decks'] = self.current_deck_forged_decks
        context['current_deck'] = self.deck_name
        return context

class AnkiForgeDesktopDowload(UserSubscribedMixin, TemplateView):
    template_name = "forge/ankiforge_desktop.html"
    redirect_url = reverse_lazy('main_entrance:index')


"""****FUNCTION BASED VIEWS*****"""



@login_required
@user_is_subscribed
def forge_action(request, pk):
    # current_deck = get_object_or_404(UserDecks, id=pk, user=request.user)
    current_decks_cards = IncomingCards.readyforforge.filter(deck=pk, user =request.user)
    user = request.user
    # Check if there are actually any cards to make
    if current_decks_cards.exists():
        result = celery.current_app.send_task('forge_deck', (pk, user.id))
        print("THERE ARE SOME CARDS TO BE MADE IN THIS DECK, TASK SENT")
        return render(request, 'forge/display_progress.html', context={'task_id':result.task_id})
    else: 
        print("THERE ARE NO CARDS TO BE MADE IN THIS DECK")
        return render(request, 'forge/no_items_to_forge.html', context={'deck': UserDecks.objects.filter(id=pk).first()})

@login_required
@user_is_subscribed
def get_download(request, pk):
    forged_deck_requested = get_object_or_404(ForgedDecks, id=pk)
    download_link = forged_deck_requested.aws_download_link
    r = requests.get(download_link)
    if r.status_code == 200:
        print("*DOWNLOAD LINK NOT EXPIRED*")
        return redirect(download_link)
    else: 
        print("*DOWNLOAD LINK EXPIRED CREATING A NEW ONE*")
        s3 = boto3.client('s3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        config=Config(
            signature_version='s3v4',
            region_name = 'us-east-2'
            ))
        try :
            response = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket':os.environ['AWS_STORAGE_BUCKET_NAME'],
                    'Key' : forged_deck_requested.aws_file_path
                },
                ExpiresIn=600
            )
            forged_deck_requested.aws_download_link = response
            forged_deck_requested.save()
            return redirect(response)
        except ClientError as e:
            logging.error(e)
            return render(request, 'main_entrance/index.html')

@login_required
@user_is_subscribed
@user_has_points
def add_card_form(request, pk):
    current_deck = get_object_or_404(UserDecks, id=pk, user=request.user)
    userdecks = UserDecks.objects.filter(user=request.user)
    if request.method == 'POST':
        form = AddCardForm(request.POST, deck=current_deck)
        if form.is_valid():
            incoming_card = form.save(commit = False)
            incoming_card.deck = current_deck
            incoming_card.user = request.user
            incoming_card.save()
            return redirect('forge:forge_add_card_form', pk = pk)
    else:
        form = AddCardForm()

    context = {
        'current_deck' : current_deck,
        'userdecks' : userdecks,
        'form' : form
    }
    return render(request, 'forge/add_card.html', context)




"""API VIEWS"""




"""Retrieve decks for current user """
class UserDecksAPIList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDecksSerializer

    def get_queryset(self):
        user = self.request.user
        return UserDecks.objects.filter(user=user)

""" Add cards API """
class UserIncomingCardsAPIList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IncomingCardsSerializer

    def post(self, request, *args, **kwargs):
        user= self.request.user
        # Every user will have UserMembership
        user_membership = UserMembership.objects.get(user=user)
        user_subscription = Subscription.objects.get(user_membership = user_membership)
        if user_subscription.active and user_membership.user_points > 30 :
            return self.create(request, *args, **kwargs)
        return Response(status=403, data={
            "error": "not authorized to add"
        })


    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


    def get_queryset(self):
        user = self.request.user
        return IncomingCards.objects.filter(user=user)




""" USER CARDS READY FOR FORGING """



class UserReadyForForgeAPIList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReadyForForgeCardsSerializer

    def get_queryset(self):
        user = self.request.user
        # deckid = self.request.query_params.get('deck')
        # print(deckid)
        deck = self.request.data['deck']
        return IncomingCards.readyforforge.filter(user=user, deck=deck)


"""GET USER CURRENT POINTS"""
class UserPointsAPIList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPointsSerializer

    def get_queryset(self):
        user = self.request.user
        return UserMembership.objects.filter(user = user)



