"""
Custom context processors to make settings available in templates.

SECURITY NOTE: Only expose values that are safe to expose client-side.
Never expose secrets like AUTH0_CLIENT_SECRET or SECRET_KEY here.
"""
from django.conf import settings


def api_keys(request):
    """
    Makes API keys and configuration available to all templates.
    
    SECURITY: Only exposes values that MUST be client-side:
    - Google Maps API key (required for maps to work)
    - Auth0 CLIENT_ID and DOMAIN (public OAuth2 identifiers)
    
    Does NOT expose:
    - AUTH0_CLIENT_SECRET (server-side only)
    - SECRET_KEY (server-side only)
    - Email passwords (server-side only)
    """
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY or '',
        'AUTH0_DOMAIN': settings.AUTH0_DOMAIN or '',
        'AUTH0_CLIENT_ID': settings.AUTH0_CLIENT_ID or '',
        'AUTH0_CALLBACK_URL': settings.AUTH0_CALLBACK_URL or '',
    }
