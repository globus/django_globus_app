from django_globus_app.mixins import SliderFacetsMixin
from django_globus_app.generic_views import SearchView

from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

log = logging.getLogger(__name__)


def landing_page(request):

    context = {}
    return render(request, "globus-portal-framework/v2/landing-page.html", context)


class CustomSearch(SliderFacetsMixin, SearchView):
    """Search with Slider Facets enabled."""

    pass


class TransferView(TemplateView):
    template_name = "globus-portal-framework/v2/components/transfer/home.html"