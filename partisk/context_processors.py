from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'ANALYTICS_SITE_ID': settings.ANALYTICS_SITE_ID,
        'ADMIN_ENABLED': settings.ADMIN_ENABLED,
    }
