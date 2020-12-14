from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, FormView, View
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

# class TestMediaCollectView(FormView):
#     template_name = "forge/testmediacollect.html"
#     form_class = TestMediaCollectForm
#     success_url = "main_entrance:index"

#     def form_valid(self, form):
#         form.send_task()
#         # return super().form_valid(form)


# from django.shortcuts import render
# from django.http import HttpResponse

# def test_media_collect(request):
#     test_taa.delay()
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




