# -*- coding: utf-8 -*-
import logging

from odoo import http, tools, _

from odoo.http import request

_logger = logging.getLogger(__name__)

class JitsiMeet(http.Controller):
    @http.route('/jitsi_meet/<int:id>/', type='http', auth="public", website=True)
    def jitsi_meet(self, id, **kwargs):
        record=request.env['calendar.event'].sudo().browse(id)
        if record:
            if not record.closed:
                data = {
                    'data': record,
                }
                return request.render("jitsi_meet.meet", data)
            else:
                return request.render("jitsi_meet.meet_closed")
        else:
            return request.render("jitsi_meet.meet_closed")

    # @http.route('/mail/<int:id>/', type='http', auth="public", website=True)
    # def jitsi_meet(self, id, **kwargs):
    #     #print('route: mail.jitsi_meet.meet')

    #     _logger.info('route: mail.jitsi_meet.meet')

    #     return request.render("mail.meet")