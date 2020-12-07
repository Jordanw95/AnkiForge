from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from forge.forms import AddIncomingCardForm
from decks.models import IncomingCards, UserDecks
from rest_framework import generics
from django.conf import settings
from decks.serializers import UserDecksSerializer, IncomingCardsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

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
# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     This viewset automatically provides `list` and `retrieve` actions.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class SnippetViewSet(viewsets.ModelViewSet):
#     """
#     This viewset automatically provides `list`, `create`, `retrieve`,
#     `update` and `destroy` actions.

#     Additionally we also provide an extra `highlight` action.
#     """
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,
#                           IsOwnerOrReadOnly]

#     @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
#     def highlight(self, request, *args, **kwargs):
#         snippet = self.get_object()
#         return Response(snippet.highlighted)

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

# class AddIncomingCardsView(generics.ListCreateAPIView):
#     queryset = IncomingCards.objects.all()
#     serializer_class = IncomingCardsSerializer
#     # permission_classes = [IsAuthenticated]

#     def list(self, request):
#         # Note the use of `get_queryset()` instead of `self.queryset`
#         queryset = self.get_queryset()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data)