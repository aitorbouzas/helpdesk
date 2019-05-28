# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from email.utils import getaddresses
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        if not custom_values:
            custom_values = {}
        custom_vals = {}
        if self.env.context.get('fetchmail_server_id', False):
            fetchmail_obj = self.env['fetchmail.server'].browse(
                self.env.context.get('fetchmail_server_id', False))
            if fetchmail_obj.object_id and \
                    fetchmail_obj.object_id.model == 'crm.helpdesk':
                try:
                    message_parsed = self.env['mail.thread'].message_parse(
                        message, save_original=save_original)
                    mail_from = message_parsed.get('from')
                    mail_from = getaddresses([mail_from])[0][1].lower()
                    if mail_from:
                        cr = self.env.cr
                        sql = """select id from crm_helpdesk_blacklist_line
                                where position(lower(email)
                                in \'%s\')>0""" % (mail_from)
                        cr.execute(sql)
                        lines = cr.dictfetchall()
                        if lines:
                            custom_vals = {'not_automatic_messages': True}
                        else:
                            sql = """select id from crm_helpdesk_whitelist_line
                                    where position(lower(email)
                                    in \'%s\')>0""" % (mail_from)
                            cr.execute(sql)
                            lines = cr.dictfetchall()
                            pool_config = self.env["ir.config_parameter"]
                            if not lines:
                                num_tickets = int(pool_config.get_param(
                                    "crm_helpdesk_improvement.number_of_tickets"))
                                num_minutes = int(pool_config.get_param(
                                    "crm_helpdesk_improvement.number_of_minutes"))
                                if num_tickets > 0 and num_minutes > 0:
                                    sql = """select id from crm_helpdesk
                                            where position('%s'
                                            in lower(email_from))>0 and
                                            create_date > now()
                                            at time
                                            zone 'utc' - (%s ||' minutes')::
                                            interval
                                            """ % (mail_from, num_minutes)
                                    cr.execute(sql)
                                    lines = cr.dictfetchall()
                                    if lines and len(lines) >= num_tickets:
                                        custom_vals = {
                                            'not_automatic_messages': True}
                                        self.env['crm.helpdesk.blacklist.line'].create({
                                            'email': mail_from,
                                            'comment': 'Odoo automatic creation'
                                        })
                except Exception:
                    pass
        if custom_vals:
            custom_values.update(custom_vals)
        super(MailThread, self).message_process(
            model, message, custom_values=custom_values,
            save_original=save_original, strip_attachments=strip_attachments,
            thread_id=thread_id)
        return True
