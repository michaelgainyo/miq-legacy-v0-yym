
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site

from sitemgr import views

from sitemgr.forms import ContactForm
from django.contrib.sites.models import Site


class AboutView(views.FormView):
    form_class = ContactForm
    template_name = 'sitemgr/pages/about.html'
    success_url = reverse_lazy('sitemgr:about')

    def form_valid(self, form):
        cd = form.cleaned_data

        context = {
            'site': get_current_site(self.request),
            'fname': cd['first_name'],
            'lname': cd['last_name'],
            'email': cd['email'],
            'order_number': cd['order_number'],
            'message': cd['message'],
            'subject': cd['subject']}

        try:
            site = Site.objects.get(pk=get_current_site(self.request))
        except Exception:
            site = None
        finally:
            context['site'] = site or get_current_site(self.request)

        messages.success(self.request, _('Thank you! We will reply shortly'))
        return super().form_valid(form)
