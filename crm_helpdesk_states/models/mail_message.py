# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import api, models
from email.utils import parseaddr

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        email_from = vals.get('email_from', False)
        author_id = vals.get('author_id', False)
        crm_helpdesk_pool = self.env['crm.helpdesk']
        if vals.get('model', False) and vals.get('model') == 'crm.helpdesk' \
                and vals.get('res_id') and vals.get('type') == 'email':
            helpdesk_id = crm_helpdesk_pool.browse(vals.get('res_id'))
            if helpdesk_id.state in ['pending', 'waiting', 'closed', 'done', 'cancel']:
                if (email_from == helpdesk_id.email_from or author_id == helpdesk_id.partner_id.id):
                    helpdesk_id.write({'state': 'open'})
                elif email_from and helpdesk_id.email_from:
                    try:
                        email_from = parseaddr(email_from)[1]
                        email_from_ticket = parseaddr(helpdesk_id.email_from)[1]
                        if email_from:
                            if email_from == email_from_ticket:
                                helpdesk_id.write({'state': 'open'})
                            else:
                                is_user = self.env['res.users'].search([
                                    ('login', '=', email_from.lower())])
                                if not is_user:
                                    partner = self.env['res.partner'].search([
                                        ('email', '=', email_from.lower()),
                                        ('user_ids', '!=', False)])
                                    if not partner:
                                        helpdesk_id.write({'state': 'open'})
                    except Exception:
                        pass
        return super(MailMessage, self).create(vals)
