from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Extends Django's built-in User model with additional fields for user profiles.

    Attributes:
        user (User): One-to-one relationship with Django's User model.
        buid (str): Boston University ID, up to 8 characters.
        img (ImageField): Profile picture, stored in 'profile_pics/' directory, with a default image.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    buid = models.CharField(max_length=8)  # Boston University ID (BUID)
    img = models.ImageField(upload_to='profile_pics/', default='default.jpg')  # Profile picture

    def __str__(self):
        """
        Returns the username as the string representation of the Profile.
        """
        return f'{self.user.username} Profile'


class Event(models.Model):
    """
    Represents an event created by a user.

    Attributes:
        name (str): The name of the event.
        created_by (Profile): The profile of the user who created the event.
        description (str): Optional detailed description of the event.
        img (ImageField): Optional event image stored in 'event_images/' directory.
        location (str): Location where the event is held.
        date (datetime): Date and time of the event.
        food_items (str): Optional list of food items available at the event.
        food_types (str): Optional type of food available, chosen from predefined categories.
        allergies (str): Optional common allergens to be aware of, chosen from predefined categories.
        reserved_by (ManyToManyField): Profiles of users who have reserved spots for the event.
        reservation_limit (int): Maximum number of reservations allowed for the event.
        latitude (float): Optional latitude of the event location.
        longitude (float): Optional longitude of the event location.
    """
    # Choices for food types
    FOOD_TYPES = [
        ('Italian', 'Italian'),
        ('Mediterranean', 'Mediterranean'),
        ('Salad', 'Salad'),
        ('American', 'American'),
        ('BBQ', 'BBQ'),
        ('Chinese', 'Chinese'),
        ('Korean', 'Korean'),
        ('Japanese', 'Japanese'),
        ('Mexican', 'Mexican'),
        ('Spanish', 'Spanish'),
        ('Indian', 'Indian'),
        ('Thai', 'Thai'),
        ('Vietnamese', 'Vietnamese'),
        ('Sushi', 'Sushi'),
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Vegan', 'Vegan'),
        ('Vegetarian', 'Vegetarian'),
    ]

    # Choices for allergens
    ALLERGIES = [
        ('Dairy', 'Dairy'),
        ('Soy', 'Soy'),
        ('Nuts', 'Nuts'),
        ('Fish', 'Fish'),
        ('Shellfish', 'Shellfish'),
        ('Eggs', 'Eggs'),
        ('Wheat', 'Wheat'),
        ('Sesame', 'Sesame'),
    ]

    # Model fields
    name = models.CharField(max_length=255)  # Name of the event
    created_by = models.ForeignKey('Profile', on_delete=models.CASCADE)  # Creator of the event
    description = models.TextField(blank=True, null=True, help_text="Event description (optional)")
    img = models.ImageField(upload_to='event_images/', blank=True, null=True)  # Event image
    location = models.CharField(max_length=255, default="Default Location")  # Location of the event
    date = models.DateTimeField()  # Date and time of the event
    food_items = models.TextField(blank=True, null=True, help_text="List of food items available at the event")
    food_types = models.CharField(
        max_length=50, choices=FOOD_TYPES, blank=True, null=True, help_text="Select the type of food available."
    )
    allergies = models.CharField(
        max_length=50, choices=ALLERGIES, blank=True, null=True, help_text="Select common allergens to be aware of."
    )
    reserved_by = models.ManyToManyField(
        'Profile', related_name='reserved_events', blank=True  # Users who reserved a spot
    )
    reservation_limit = models.PositiveIntegerField(
        default=50, help_text="Maximum number of reservations for this event"
    )
    latitude = models.FloatField(blank=True, null=True)  # Latitude of the event location
    longitude = models.FloatField(blank=True, null=True)  # Longitude of the event location

    def is_full(self):
        """
        Check if the event has reached its reservation limit.

        Returns:
            bool: True if the reservation limit is reached, False otherwise.
        """
        return self.reserved_by.count() >= self.reservation_limit

    def __str__(self):
        """
        Returns a string representation of the event.

        Format:
            "Event: [event name] by [creator's username]"
        """
        return f"Event: {self.name} by {self.created_by.user.username}"