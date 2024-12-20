from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, CreateView
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import CustomUserCreationForm, CustomAuthenticationForm, EventForm
from .models import Profile, Event
from .utils import generate_qr_code


class EventListView(ListView):
    """
    Displays a list of all events. Supports filtering by name, location, date, food types, and allergies.
    """
    model = Event
    template_name = 'spark_bytes/all_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        """
        Filters the events based on search parameters provided in the GET request.
        """
        queryset = super().get_queryset()
        name = self.request.GET.get('name', '')
        location = self.request.GET.get('location', '')
        date = self.request.GET.get('date', '')
        food_types = self.request.GET.getlist('food_types')
        allergies = self.request.GET.getlist('allergies')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if date:
            queryset = queryset.filter(date__date=date)
        if food_types:
            queryset = queryset.filter(food_types__in=food_types)
        if allergies:
            for allergy in allergies:
                queryset = queryset.filter(allergies__icontains=allergy)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds food types, allergies, and selected filters to the context.
        """
        context = super().get_context_data(**kwargs)
        context['food_types'] = [
            "Italian", "Mediterranean", "Salad", "American", "BBQ", 
            "Chinese", "Korean", "Japanese", "Mexican", "Spanish", 
            "Indian", "Thai", "Vietnamese", "Sushi", "Breakfast", 
            "Lunch", "Vegan", "Vegetarian"
        ]
        context['allergies'] = [
            "Dairy", "Soy", "Nuts", "Fish", "Shellfish", "Eggs", 
            "Wheat", "Sesame"
        ]
        context['selected_food_types'] = self.request.GET.getlist('food_types')
        context['selected_allergies'] = self.request.GET.getlist('allergies')
        return context


class ProfileListView(ListView):
    """
    Displays a list of all user profiles.
    """
    model = Profile
    template_name = 'spark_bytes/all_profiles.html'
    context_object_name = 'profiles'


class ProfileDetailView(DetailView):
    """
    Displays details of a specific user profile, including the events created by the user.
    """
    model = Profile
    template_name = 'spark_bytes/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        """
        Adds the list of events created by the profile to the context.
        """
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(created_by=self.object)
        return context


class EventDetailView(DetailView):
    """
    Displays details of a specific event.
    """
    model = Event
    template_name = 'spark_bytes/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        """
        Adds the creator's profile to the context.
        """
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.created_by
        return context


class RegisterView(FormView):
    """
    Handles user registration using a custom user creation form.
    """
    template_name = 'spark_bytes/register.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        """
        Saves the user and creates a profile, then logs in the user.
        """
        user = form.save()
        Profile.objects.create(
            user=user,
            buid=form.cleaned_data['buid'],
            img=form.cleaned_data['img']
        )
        login(self.request, user)
        return redirect('all_events')


class CreateEventView(LoginRequiredMixin, CreateView):
    """
    Allows logged-in users to create new events.
    """
    model = Event
    form_class = EventForm
    template_name = 'spark_bytes/create_event.html'
    success_url = '/events/'

    def form_valid(self, form):
        """
        Associates the created event with the logged-in user's profile.
        """
        profile = Profile.objects.get(user=self.request.user)
        form.instance.created_by = profile
        return super().form_valid(form)


class ReserveSpotView(LoginRequiredMixin, DetailView):
    """
    Allows a user to reserve a spot for an event and generates a QR code for confirmation.
    """
    model = Event
    template_name = 'spark_bytes/event_detail.html'
    context_object_name = 'event'

    def post(self, request, *args, **kwargs):
        """
        Handles the reservation process, including checking for available spots,
        adding the user to the reservation list, and generating a QR code.
        """
        event = self.get_object()
        profile = Profile.objects.get(user=request.user)

        if event.is_full():
            return JsonResponse({'message': 'This event is full. No more spots are available.'}, status=400)

        if event.reserved_by.filter(id=profile.id).exists():
            return JsonResponse({'message': 'You have already reserved a spot for this event.'}, status=400)

        event.reserved_by.add(profile)
        unique_data = f"{profile.user.email}_{event.id}"
        qr_code_data = generate_qr_code(unique_data)
        event.save()

        return JsonResponse({
            'message': 'Reservation successful!',
            'qr_code': qr_code_data
        }, status=200)


class CustomLoginView(LoginView):
    """
    Handles user login using a custom authentication form.
    """
    template_name = 'spark_bytes/login.html'
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        """
        Redirects the user to the events list upon successful login.
        """
        return reverse_lazy('all_events')


class CustomLogoutView(LogoutView):
    """
    Logs out the user and redirects them to the login page.
    """
    next_page = 'login'


class DeleteEventView(UserPassesTestMixin, DetailView):
    """
    Allows admin users to delete an event.
    """
    model = Event
    template_name = "spark_bytes/event_detail.html"

    def test_func(self):
        """
        Restricts access to superusers only.
        """
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        """
        Deletes the event and returns a success message as JSON.
        """
        event = self.get_object()
        event.delete()
        return JsonResponse({'message': 'Event deleted successfully!'}, status=200)