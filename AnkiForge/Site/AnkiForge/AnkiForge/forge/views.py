from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, FormView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from forge.forms import AddIncomingCardForm
from decks.models import IncomingCards, UserDecks, ForgedDecks
from rest_framework import generics
from django.conf import settings
from decks.serializers import UserDecksSerializer, IncomingCardsSerializer
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

class AlreadyForgedDecksIndex(LoginRequiredMixin, ListView):
    login_url = 'main_entrance:login'
    template_name = 'forge/already_forged_decks_index.html'
    context_object_name = 'userdecks'

    def get_queryset(self):
        return UserDecks.objects.filter(user= self.request.user)

class AlreadyForgedDecksList(LoginRequiredMixin, ListView):
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

@login_required
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

@login_required
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


class TestingAllIncomingCards(generics.ListCreateAPIView):
    serializer_class = IncomingCardsSerializer

    def get_queryset(self):
        return IncomingCards.objects.all()




