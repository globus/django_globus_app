from django.shortcuts import render

import logging

from django_globus_app.mixins import HelperPageMixin, SliderFacetsMixin
from django_globus_app.generic_views import SearchView

log = logging.getLogger(__name__)


def landing_page(request):

    context = {}
    return render(request, "globus-portal-framework/v2/landing-page.html", context)


class CustomSearch(SliderFacetsMixin, SearchView):
    """Search with Slider Facets enabled."""

    pass