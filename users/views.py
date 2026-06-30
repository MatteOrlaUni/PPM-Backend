import json
import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.urls import reverse, resolve
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from backend.models import Playlist
from .forms import CustomUserCreationForm

def auth_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'main'
    
    if request.user.is_authenticated:
        return redirect(next_url)
        
    login_form = AuthenticationForm(request)
    signup_form = CustomUserCreationForm()
    active_tab = 'login'
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect(next_url)
        elif action == 'signup':
            active_tab = 'signup'
            signup_form = CustomUserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect(next_url)
                
    context = {
        'login_form': login_form,
        'signup_form': signup_form,
        'active_tab': active_tab,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'login.html', context)

def custom_logout_view(request):
    referer = request.META.get('HTTP_REFERER')
    logout(request)
    if referer:
        try:
            path = urllib.parse.urlparse(referer).path
            match = resolve(path)
            public_views = ['main', 'catalog_list', 'artist_detail', 'genre_detail']
            if match.url_name in public_views:
                return redirect(referer)
        except Exception:
            pass
    return redirect('main')

class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        user = get_object_or_404(get_user_model(), username=username)
        playlists = Playlist.objects.filter(user=user)
        context['title'] = user.username
        context['subtitle'] = f"{playlists.count()} playlist pubbliche"
        context['cover_type'] = 'user'
        context['type_label'] = f"Utente - {user.role.title()}"
        context['items'] = playlists
        context['item_type'] = 'playlist'
        context['can_edit'] = self.request.user.is_curator() or self.request.user == user
        context['can_remove_item'] = False
        context['edit_url'] = reverse('user_edit_inline', args=[user.username])
        context['target_user'] = user
        context['list_title'] = "Playlist"
        return context

class UserEditInlineView(LoginRequiredMixin, View):
    def post(self, request, username):
        user = get_object_or_404(get_user_model(), username=username)
        if request.user.is_curator() or request.user == user:
            new_username = request.POST.get('new_title')
            new_password = request.POST.get('password')
            
            updated = False
            if new_username and new_username != username:
                if not get_user_model().objects.filter(username=new_username).exists():
                    user.username = new_username
                    updated = True
                else:
                    messages.error(request, "Username già in uso.")
            
            if new_password:
                user.set_password(new_password)
                updated = True
                # Keep user logged in if they changed their own password
                if request.user == user:
                    login(request, user)
                    
            new_role = request.POST.get('role')
            if new_role and request.user.is_curator() and new_role in ['listener', 'curator']:
                if user.role != new_role:
                    user.role = new_role
                    updated = True
                    
            if updated:
                user.save()
                return redirect('user_detail', username=user.username)
        else:
            messages.error(request, "Azione non consentita. Privilegi insufficienti.")

        return redirect('user_detail', username=username)

class UserDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        return redirect('main')

class AdminUserDeleteView(LoginRequiredMixin, View):
    def post(self, request, username):
        if not request.user.is_curator():
            messages.error(request, "Azione non consentita. Privilegi insufficienti.")
            return redirect('main')
            
        target_user = get_object_or_404(get_user_model(), username=username)
        # Prevent deleting yourself through this route just in case
        if target_user == request.user:
            return redirect('catalog_list')
            
        target_user.delete() # Playlists will be deleted on cascade
        
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('catalog_list')
