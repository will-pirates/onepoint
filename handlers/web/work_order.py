import webapp2
from handlers.web import WebRequestHandler
from auth import provider_login_required, login_required
from model.provider import Provider
from model.work_order import WorkOrder, WorkOrderHistory, work_order_display_names, workorder_listing_order
from model.appliance import Appliance
from util.util import get_work_orders_for_logged_in_user
from model.work_order import get_display_id
import json
import logging

class EstimateHandler(WebRequestHandler):
    def get(self):
        path = 'work_order_estimate.html'
        action = self['action'] if self['action'] else ''
        wo = WorkOrder.get_by_id(long(self['work_order']))
        template_values = {'work_order':self['work_order'], 'action':action, 'service_date':wo.fix_by_date}
        self.write(self.get_rendered_html(path, template_values), 200)

class CompletedHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'work_order_completed.html'
        template_values = {'work_order':self['work_order']}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProviderCheckinHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'provider_checkin.html'
        template_values = {'work_order':self['work_order']}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'workorders.html'
        wo_id = str(self['work_order']) if self['work_order'] else ''
        new_wo = str(self['new_wo']) if self['new_wo'] else ''
        workorders = get_work_orders_for_logged_in_user(self)
        workorders_by_state = {}
        for workorder in workorders:
            state = work_order_display_names[workorder.curr_state]
            if not state in workorders_by_state:
                workorders_by_state[state] = []
            workorders_by_state[state].append((workorder, workorder.get_action_url(self.session['role'])))
        workorders_list = []
        for state in workorder_listing_order:
            if state in workorders_by_state:
                workorders_list.append((state, workorders_by_state[state]))
        template_values = {'workorders_list': workorders_list, 'count': len(workorders)}
        if wo_id:
            template_values['active_wo'] = wo_id
        if new_wo:
            template_values['new_wo'] = new_wo
            template_values['display_wo'] = get_display_id(new_wo)
        template_values['role'] = self.session['role']
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/work_order/provide_estimate', EstimateHandler),
        ('/work_order/checkin_provider', ProviderCheckinHandler),
        ('/work_order/completed',CompletedHandler),
        ('/work_order/list',ListHandler)
    ]
)