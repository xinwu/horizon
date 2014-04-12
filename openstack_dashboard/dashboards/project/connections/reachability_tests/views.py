# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing keypairs.
"""
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django import http
from django.template.defaultfilters import slugify  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView  # noqa
from django.views.generic import View  # noqa

from horizon import exceptions
from horizon import forms
from horizon.utils import memoized
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.connections.mockapi import ReachabilityTestAPI
from openstack_dashboard.dashboards.project.connections.reachability_tests \
    import forms as project_forms
from openstack_dashboard.dashboards.project.connections.reachability_tests \
    import tabs as project_tabs


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateReachabilityTest
    template_name = 'project/connections/reachability_tests/create.html'
    success_url = reverse_lazy("horizon:project:connections:index")


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateForm
    template_name = 'project/connections/reachability_tests/update.html'
    success_url = reverse_lazy('horizon:project:connections:index')

    @memoized.memoized_method
    def get_object(self):
        try:
	    #import pdb
	    #pdb.set_trace()
	    api = ReachabilityTestAPI()
            return api.getReachabilityTest(self.kwargs['reachability_test_id'].encode('ascii','ignore'))
        except Exception:
            msg = _('Unable to retrieve test.')
            url = reverse('horizon:project:connections:index')
            exceptions.handle(self.request, msg, redirect=url)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['reachability_test'] = self.get_object()
        return context

    def get_initial(self):
        reachability_test = self.get_object()
        properties = getattr(reachability_test, 'properties', {})
        return {'reachability_test_id': self.kwargs['reachability_test_id'],
                'name': reachability_test.name}

class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ReachabilityTestDetailTabs
    template_name = 'project/connections/reachability_tests/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["reachability_test"] = self.get_data()
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
	    api = ReachabilityTestAPI()
            return  api.getReachabilityTest(self.kwargs['reachability_test_id'].encode('ascii','ignore'))
        except Exception:
            url = reverse('horizon:project:connections:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve reachability test details.'),
                              redirect=url)

    def get_tabs(self, request, *args, **kwargs):
        reachability_test = self.get_data()
        return self.tab_group_class(request, reachability_test=reachability_test, **kwargs)
