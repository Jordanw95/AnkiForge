from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from decks.forms import CreateUserDeckForm
from decks.models import UserDecks
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

class DecksIndexView(LoginRequiredMixin, TemplateView):
    login_url = 'main_entrance:login'
 
    template_name = "decks/decks_index.html"

class UserDeckCreateView(LoginRequiredMixin, CreateView):
    login_url = 'main_entrance:login'
    
    template_name = "decks/new_deck_form.html"
    form_class = CreateUserDeckForm
    model = UserDecks

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('decks:decks_index')
        
# @loginrequired
# def create_deck_view(request):
    
#     if request.method == 'POST':
#         form = CreateUserDeck(request.POST)

#         if form.is_valid():
#             deck = form.save(commit = False)
#             comment.post = post
#             comment.save()
#             return redirect('post_detail', pk=post.pk )
#     else : 
#         form = CommentForm()
#     return render(request, 'blog/comment_form.html', {'form':form })
# Create your views here.
