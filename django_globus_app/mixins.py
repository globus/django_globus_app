from django.middleware import csrf
from django.urls import reverse
from django.views.generic import View
from urllib.parse import urlunparse, urlparse, urlencode

from globus_portal_framework.gclients import load_transfer_client
from globus_portal_framework.gsearch import get_index
from django_globus_app.generic_views import SearchView

import logging

log = logging.getLogger(__name__)


class CSRFValidationFailure(Exception):
    pass


class TransferUtils(View):
    session_transfer_var = "transfers"
    csrf_token_name = "custom_transfer_csrf_token"
    csrf_token_param_name = "csrf_token"

    def verify_session_csrf_token(self, token):
        session_csrf = self.request.session.get(self.csrf_token_param_name)
        if not session_csrf or session_csrf != token:
            log.error(f"Request CSRF {token}, stored CSRF {session_csrf}")
            # If there was a previous task, clear it out.
            self.set_task({})
            raise CSRFValidationFailure("Request Token does not " "match stored token.")
        log.debug(f"CSRF validation PASSED.")

    def set_session_csrf_token(self, token):
        log.debug(f"Set CSRF validation token: {token}")
        self.request.session[self.csrf_token_param_name] = token

    def get_task(self):
        transfers = self.request.session.get(self.session_transfer_var, {})
        return transfers.get(self.kwargs["subject"], {})

    def set_task(self, data):
        transfers = self.request.session.get(self.session_transfer_var, {})
        transfers[self.kwargs["subject"]] = data
        self.request.session[self.session_transfer_var] = transfers

    def update_task(self):
        task = self.get_task()
        if task:
            if task.get("data") and task["data"]["status"] != "ACTIVE":
                return task
            tc = load_transfer_client(self.request.user)
            task["data"] = tc.get_task(task["task_id"]).data
            self.set_task(task)
            return task
        return {}


class HelperPageMixin(TransferUtils):
    manifest_key_name = "remote_file_manifest"
    redirect_url = ""
    helper_page_params = {
        "method": "GET",
        "filelimit": 0,
        "folderlimit": 1,
        "label": "",
        "action": "",
        "cancelurl": "",
    }

    def get_context_data(self, *args, **kwargs):
        context = dict()
        context["helper_page_transfer_url"] = self.get_helper_page_url()
        return context

    def get_host(self):
        host = self.request.get_host()
        if host.startswith("localhost"):
            host = host.replace("localhost", "127.0.0.1")
        return host

    def get_redirect_url(self):
        if not self.redirect_url:
            return reverse(self.redirect_url)
        return self.request.build_absolute_uri()

    def get_helper_page_url(self):
        """Generate the helper page URL for the the Globus Webapp. Details:
        https://docs.globus.org/api/helper-pages/browse-endpoint/

        The callback url also includes a CSRF Token to prevent CSRF attacks.
        This is technically a misuse of CSRF tokens, since they weren't
        intended to leave the portal into a request sent somewhere else.
        Additionally, Django can't verify the token properly due to the helper
        pages not posting the token along with the other transfer POST data,
        so the token needs to be passed as a GET param. It's later compared
        in the SubmitTransfer view with verify_session_csrf_token
        """
        # Setup general helper page parameters and encode them into queryparams
        hp_params = self.helper_page_params.copy()
        index_data = get_index(self.kwargs.get("index"))
        cancel_url = self.request.build_absolute_uri()
        hp_params.update(
            {"label": f'{index_data["name"]} Transfer', "cancelurl": cancel_url}
        )
        hp_params_enc = urlencode(hp_params)

        token = csrf.get_token(self.request)
        # The "action" param needs to be encoded separately, since it's the
        # full redirect URL the Globus Webapp will respond with, and the
        # csrf token will be separate
        action_param_param = urlencode({self.csrf_token_param_name: token})
        self.set_session_csrf_token(token)
        # Encode the full action param url and add it to the other helper page
        # URLs
        base_url = urlunparse(
            (self.request.scheme, self.get_host(), self.get_redirect_url(), "", "", "")
        )
        redirect_url = "{}?{}".format(base_url, action_param_param)
        action_param = urlencode({"action": redirect_url})
        log.debug(f'"action" redirect helper page url: {action_param}')
        hp_params_enc = f"{hp_params_enc}&{action_param}"
        return urlunparse(
            ("https", "app.globus.org", "file-manager", "", hp_params_enc, "")
        )


class SliderFacetsMixin:
    def get_context_data(self, index):
        log.debug(f"Applying sliders to search facet context.")
        context = super().get_context_data(index)
        facets = context.get("search", {}).get("facets")
        if facets:
            context["search"]["facets"] = self.get_slider_facets(facets)
        return context

    def get_slider_facets(self, facets):
        filters = {f["field_name"]: f["values"][0] for f in self.filters}

        processed = []
        for facet in facets:
            buckets = facet.get("buckets", [])
            if not buckets:
                continue
            facet["filter_type"] = buckets[0]["filter_type"]
            facet["filter_query_key"] = buckets[0]["search_filter_query_key"]
            if facet["filter_type"] != "range":
                processed.append(facet)
                continue
            ranges = [
                (float(low), float(high))
                for low, high in [b["value"].split("--") for b in buckets]
            ]
            low, high = zip(*ranges)
            # There seems to be a problem where sliding the sliders all the way
            # to one side will result in the upper_bound or lower_bound getting
            # 'stuck' on one side, where the filter is permanently stuck to a
            # subset of results. This forces the sliders to be a little wider
            # so this hopefully won't happen.
            # incr = (max(high) - min(low)) / 5
            # Setting the incr to one below for the django_globus_app Orbit data, which seems
            # to be a little more resiliant to the problem.
            incr = 1
            facet["lower_bound"] = int(min(low) - incr)
            facet["upper_bound"] = int(max(high) + incr)
            # Set the upper and lower bounds on the filter based on the
            # values in settings
            facet_filter = filters.get(buckets[0]["field_name"], {})
            facet["filter_low"] = facet_filter.get("from")
            facet["filter_high"] = facet_filter.get("to")
            processed.append(facet)
        return processed
