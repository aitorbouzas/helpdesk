# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import api, fields, models, _
from openerp.addons.crm_helpdesk.crm_helpdesk import crm_helpdesk
from openerp.tools import html2plaintext

_logger = logging.getLogger(__name__)


def message_new(self, cr, uid, msg, custom_values=None, context=None):
    """ Overrides mail_thread message_new that is called by the mailgateway
        through message_process.
        This override updates the document according to the email.
    """
    if custom_values is None:
        custom_values = {}
    message = msg
    if isinstance(msg, unicode):
        message = msg.encode('utf-8')
    desc = message.get('body') or ''
    desc = "%s" % (desc)
    defaults = {
        'name': msg.get('subject') or _("No Subject"),
        'description': html2plaintext(desc),
        'email_from': msg.get('from'),
        'email_cc': msg.get('cc'),
        'user_id': False,
        'partner_id': msg.get('author_id', False),
    }
    defaults.update(custom_values)
    return super(crm_helpdesk, self).message_new(
        cr, uid, msg, custom_values=defaults, context=context)

crm_helpdesk.message_new = message_new


class CrmHelpdesk(models.Model):
    _inherit = 'crm.helpdesk'

    @api.multi
    def name_get(self):
        res = []
        for obj in self:
            case = '[' + obj.code + '] '
            res.append((obj.id, case + obj.name))
        return res

    @api.multi
    def _get_name_from(self):
        for record in self:
            record.name_from = record.partner_id.name or \
                record.email_from or ''

    email_origin = fields.Char('Email origin')
    code = fields.Char(
        'Reference', required=True,
        default="/", readonly=True, copy=False)
    user_id = fields.Many2one(
        'res.users', 'Responsible', track_visibility='onchange')
    name_from = fields.Char(
        string='Name',
        store=False, compute='_get_name_from')
    not_automatic_messages = fields.Boolean(
        'Not Automatic messages',
        default=False)

    _sql_constraints = [
        ('crm_helpdesk_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].get('crm.helpdesk')
        if vals.get('partner_id'):
            if (not vals.get('message_follower_ids', False)):
                vals['message_follower_ids'] = []
            vals['message_follower_ids'].append((4, vals['partner_id']))
        return super(CrmHelpdesk, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('partner_id'):
            if (not vals.get('message_follower_ids', False)):
                vals['message_follower_ids'] = []
            vals['message_follower_ids'].append((4, vals['partner_id']))
        return super(CrmHelpdesk, self).write(vals)

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].get('crm.helpdesk')
        return super(CrmHelpdesk, self).copy(default)


class CRMHelpdeskBlacklistLine(models.Model):
    _name = "crm.helpdesk.blacklist.line"
    _description = "Emails detected as machines"

    _sql_constraints = [
        ('crm_helpdesk_blacklist_unique_code', 'UNIQUE (email)',
         _('The email must be unique!')),
    ]

    email = fields.Char('Email', help="email to block", required=True)
    comment = fields.Text(
        'Comment',
        help="Reason wich this email is in the list", required=True)


class CRMHelpdeskWhitelistLine(models.Model):
    _name = "crm.helpdesk.whitelist.line"
    _description = "Emails excluded from blacklist"

    _sql_constraints = [
        ('crm_helpdesk_whitelist_unique_code', 'UNIQUE (email)',
         _('The email must be unique!')),
    ]

    email = fields.Char(
        'Email', help="email to exclude from blacklist",
        required=True)
    comment = fields.Text(
        'Comment',
        help="Reason wich this email is in the list", required=True)
