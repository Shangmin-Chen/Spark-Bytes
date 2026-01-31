from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, CreateView
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from email.mime.image import MIMEImage
import json
import base64

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
        adding the user to the reservation list, generating a QR code, and sending confirmation email.
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

        # Send confirmation email with QR code
        try:
            self._send_reservation_email(event, profile, qr_code_data)
        except Exception as e:
            # Log error but don't fail the reservation if email fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send reservation email: {str(e)}")

        return JsonResponse({
            'message': 'Reservation successful!',
            'qr_code': qr_code_data
        }, status=200)

    def _send_reservation_email(self, event, profile, qr_code_data):
        """
        Sends a confirmation email with QR code to the user who reserved a spot.
        """
        # Render email template
        html_content = render_to_string('spark_bytes/email/qr_code_email.html', {
            'event': event,
            'profile': profile,
        })
        text_content = strip_tags(html_content)

        # Create email
        subject = f'Reservation Confirmation: {event.name}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [profile.user.email]

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")

        # Attach QR code as inline image
        qr_image_data = base64.b64decode(qr_code_data)
        qr_image = MIMEImage(qr_image_data)
        qr_image.add_header('Content-ID', '<qr_code>')
        qr_image.add_header('Content-Disposition', 'inline', filename='qr_code.png')
        email.attach(qr_image)

        # Send email
        email.send()


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


def auth0_callback(request):
    """
    Handles Auth0 OAuth callback.
    Since the frontend uses Auth0 SPA SDK which handles OAuth client-side,
    this endpoint receives user info from the frontend after Auth0 authentication
    and creates/logs in the Django user.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            name = data.get('name', '')
            sub = data.get('sub', '')  # Auth0 user ID
            
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
            
            # Get or create user
            username = email.split('@')[0]  # Use email prefix as username
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': name.split()[0] if name else '',
                    'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                }
            )
            
            # If user already exists but username is different, update it
            if not created and user.username != username:
                # Handle username conflicts
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exclude(id=user.id).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                user.username = username
                user.save()
            
            # Get or create profile
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={'buid': '00000000'}  # Default BUID, user can update later
            )
            
            # Log in the user
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully authenticated',
                'redirect': '/'
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # For GET requests, redirect to home (frontend handles OAuth flow)
    return redirect('all_events')


def registration_success(request):
    """
    Displays the registration success page.
    """
    return render(request, 'spark_bytes/registration_success.html')


class EventMapView(ListView):
    """
    Displays events on a map. Provides events as JSON for map rendering.
    """
    model = Event
    template_name = 'spark_bytes/event_map.html'
    context_object_name = 'events'

    def get_queryset(self):
        """
        Returns events that have latitude and longitude coordinates.
        """
        return Event.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).exclude(latitude=0, longitude=0)

    def get_context_data(self, **kwargs):
        """
        Adds events as JSON for map rendering.
        """
        context = super().get_context_data(**kwargs)
        events = self.get_queryset()
        
        # Serialize events for map
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'name': event.name,
                'latitude': float(event.latitude),
                'longitude': float(event.longitude),
                'location': event.location,
                'date': event.date.isoformat() if event.date else None,
                'image_url': event.img.url if event.img else '',
            })
        
        context['events_json'] = json.dumps(events_data)
        return context