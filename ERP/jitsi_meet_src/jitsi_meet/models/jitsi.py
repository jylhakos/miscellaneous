from email.policy import default
from odoo import models, fields, api
import datetime

from odoo.tools.misc import detect_ip_addr, DEFAULT_SERVER_DATETIME_FORMAT

from random import choice

import logging

import pytz

def create_hash():
    size = 32
    values = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    p = ''
    p = p.join([choice(values) for i in range(size)])
    return p

class JitsiMeet(models.Model):
    _inherit = "calendar.event"

    def _get_default_participant(self):
        result = []
        result.append(self.env.user.id)
        return [(6, 0, result)]

    hash = fields.Char('Hash')

    date_formated = fields.Char(string='Date Formated', required=False)

    jitsi_meet_enabled = fields.Boolean(string='Video Meeting', required=False, default=False)

    jitsi_host_ip = fields.Boolean('localhost', default='get_host_ip_addr')

    url = fields.Char(string='The URL link to Jitsi Meet', compute='_compute_url')

    url_to_link = fields.Char(string='URL to link', compute='_compute_url')

    current_user = fields.Many2one('res.users', compute='_get_current_user')

    domain = fields.Char(string='Domain',  required=False, compute='_compute_domain')

    password_required = fields.Boolean(string='Set username and password', required=False, default=False)

    password = fields.Char(string='Password', required=False)

    user = fields.Char(string='Username', required=False)

    start_time_str = fields.Char(string='Start Time', compute_sudo=False, compute='_compute_start_time_str')

    #start_time = fields.Datetime(string='Start Time Datetime', required=True)

    start_time = fields.Char(string='Start Time Long', required=True)

    date_delay = fields.Float('Duration', required=True, default=1.0)

    end_time = fields.Float('End Time', store=True, required=True, default=1.0, compute='_compute_start_time_str')

    closed = fields.Boolean('Closed', compute_sudo=False, default=False, compute='_compute_start_time_str')

    #end_time = fields.Float('End Time', store=True, required=True, default=1.0, compute='_compute_endtime')

    #closed = fields.Boolean('Closed', compute_sudo=False, default=False, compute='_compute_close')

    start_meet = fields.Datetime('Start Meet', required=True, tracking=True, default=fields.Date.today, help="Start of an event")

    start_meet_str = fields.Char(string='Start Meet Str', required=True)

    def _compute_start_time_str(self):
        for item in self:

            logging.info('item.start: %s', item.start)

            item.start_time = datetime.datetime.strftime(item.start, '%Y-%m-%d %H:%M:%S')

            logging.info('start_time: %s', item.start_time)

            user_tz = self.env.user.tz or pytz.utc

            local = pytz.timezone(user_tz)

            logging.info(local)

            #item.start_meet = datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.strptime(item.start_time, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),'%Y-%m-%d %H:%M:%S')

            item.start_meet = datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.strptime(item.start_time, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),'%Y-%m-%d %H:%M:%S')

            logging.info(item.start_meet)

            item.start_meet_str = datetime.datetime.strftime(item.start_meet, '%Y-%m-%d %H:%M:%S')

            logging.info(item.start_meet_str)

            #item.start_time_str = datetime.datetime.strftime(item.start, '%m-%d %H:%M')

            item.start_time_str = datetime.datetime.strftime(item.start_meet, '%m-%d %H:%M')

            logging.info('start_time_str: %s', item.start_time_str)

            #item.start_time_str = datetime.datetime.strftime(item.start_meet, '%m-%d %H:%M')

            #logging.info('start_time_str: %s', item.start_time_str)

            #item.start_time = fields.Datetime.from_string(item.start)

            #timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'

            #logging.info(timezone)

            #self_tz = self.with_context(tz=timezone)

            #logging.info(self_tz)

            #item.start_meet = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(item.start)) 

            #user_tz = self.env.user.tz or pytz.utc

            #local = pytz.timezone(user_tz)

            #logging.info(local)

            #item.start_meet = datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.strptime(item.start_time, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),'%Y-%m-%d %H:%M:%S')

            #item.start_meet = datetime.strftime(fields.Datetime.context_timestamp(self, item.start), "%Y-%m-%d %H:%M:%S")

            #logging.info(item.start_meet)

            logging.info(item)

            if item.start_time:
                #start = fields.Datetime.from_string(item.start_time)
                duration = datetime.timedelta(hours=(item.date_delay))
                logging.info(duration)
                #end = datetime.datetime.strptime(item.start_time, '%Y-%m-%d %H:%M:%S') + duration
                end = datetime.datetime.strptime(item.start_meet_str, '%Y-%m-%d %H:%M:%S') + duration
                logging.info('end: %s', end)
                item.end_time = float(end.strftime('%Y%m%d%H%M%S.%f'))
            if item.end_time:
                #now = fields.Datetime.now()
                now_datetime = datetime.datetime.now()
                logging.info('now: %s', now_datetime)
                now_float = float(now_datetime.strftime('%Y%m%d%H%M%S.%f'))
                logging.info('now_float: %f', now_float)
                item.closed = item.end_time < now_float
                logging.info('closed: %r', item.closed)

    #@api.depends('start_time')
    #def _compute_endtime(self):
    #    for item in self:
    #        if item.start_time:
    #            #start = fields.Datetime.from_string(item.start_time)
    #            duration = datetime.timedelta(hours=(item.date_delay))
    #            logging.info('duration %d', duration)
    #            end = datetime.datetime.strptime(item.start_time, '%Y-%m-%d %H:%M:%S') + duration
    #            logging.info('end %s', end)
    #            item.end_time = float(end.strftime('%Y%m%d%H%M%S.%f'))

                #item.end_time = fields.Datetime.to_string(start + duration)

    #@api.depends('start_time_str', 'start_time')
    #def _compute_endtime(self):
    #    for item in self:
    #        logging.info(item)
    #        if item.start_time:
                #start = fields.Datetime.from_string(item.start_time)
    #            duration = datetime.timedelta(hours=(item.date_delay))
    #            logging.info(duration)
    #            end = datetime.datetime.strptime(item.start_time, '%Y-%m-%d %H:%M:%S') + duration
    #            logging.info('End %s', end)
    #            item.end_time = float(end.strftime('%Y%m%d%H%M%S.%f'))

                #item.end_time = fields.Datetime.to_string(start + duration)

    #@api.depends('start_time_str', 'start_time', 'end_time')
    #def _compute_close(self):
    #    for item in self:
    #        if item.end_time:
    #            #now = fields.Datetime.now()
    #            now_datetime = datetime.datetime.now()
    #            logging.info('now %s', now_datetime)
    #            now_float = float(now_datetime.strftime('%Y%m%d%H%M%S.%f'))
    #            logging.info('now_float %f', now_float)
    #            item.closed = item.end_time < now_float
    #            logging.info('closed %r', item.closed)

    def get_host_ip_addr():
        return detect_ip_addr()

    def _compute_domain(self):
        for r in self:
            r.domain = self.env['ir.config_parameter'].sudo().get_param('jitsi_calendar.meet_url', default='jitsi_host_ip')
            #default='meet.jit.si')

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user

    @api.model
    def create(self, vals):
        vals['hash'] = create_hash()
        res = super(JitsiMeet, self).create(vals)
        return res

    def open(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://' + 'jitsi_host_ip' + ':8069')
        return {'name': 'JITSI MEET', 'res_model': 'ir.actions.act_url', 'type': 'ir.actions.act_url', 'target': 'new', 'url': url + "/jitsi_meet/" + str(self.id)}

    def action_reopen_meeting(self):
        self.write({'closed': False})

    def action_close_meeting(self):
        self.write({'closed': True})

    def _compute_url(self):
        #config_url = self.env['ir.config_parameter'].sudo().get_param('jitsi_calendar.meet_url', default='localhost')
        config_url = self.env['ir.config_parameter'].sudo().get_param('jitsi_calendar.meet_url', default='jitsi_host_ip')

        url_site = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://' + 'jitsi_host_ip' + ':8069')

        if not self.hash:
            self.hash = create_hash()

        for r in self:
            if r.hash and r.name:
                r.url = config_url + r.hash
                r.url_to_link=url_site + "/jitsi_meet/" + str(r.id)

    def send_mail(self):
        for record in self.partner_ids:
            template = self.env.ref('jitsi_meet.email_template_edi_jitsi_meet')

            _MAIL_TEMPLATE_FIELDS = ['subject', 'body_html', 'email_from', 'email_to', 'email_cc', 'reply_to', 'scheduled_date', 'attachment_ids']
            if template:
                values = template.generate_email(self.id, _MAIL_TEMPLATE_FIELDS)

                mail_mail_obj = self.env['mail.mail']

                msg_id = mail_mail_obj.sudo().create(values)

                if msg_id:
                    mail_mail_obj.sudo().send(msg_id)
                    mail_mail_obj.sudo().process_email_queue()

    def _format_date(self):
        for part in self:
            part.date_formated = fields.Datetime.from_string(part.start_datetime).strftime('%m/%d/%Y, %H:%M:%S')
