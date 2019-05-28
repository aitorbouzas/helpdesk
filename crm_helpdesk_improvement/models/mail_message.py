# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import api, models, fields
from email.utils import parseaddr, formataddr
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import tools, SUPERUSER_ID


_logger = logging.getLogger(__name__)


class MailNotification(models.Model):
    _inherit = 'mail.notification'

    def get_signature_footer(self, cr, uid, user_id, res_model=None, res_id=None, context=None, user_signature=True):
        """ Format a standard footer for notification emails (such as pushed messages
            notification or invite emails).
            Format:
                <p>--<br />
                    Administrator
                </p>
                <div>
                    <small>Sent from <a ...>Your Company</a> using <a ...>OpenERP</a>.</small>
                </div>
        """
        footer = ""
        if not user_id:
            return footer

        # add user signature
        user = self.pool.get("res.users").browse(cr, SUPERUSER_ID, [user_id], context=context)[0]
        if user_signature:
            if user.signature:
                signature = user.signature
            else:
                signature = "--<br />%s" % user.name
            footer = tools.append_content_to_html(footer, signature, plaintext=False)
        return footer


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _get_default_from(self):
        context = self._context
        email_from = False
        if context and \
                context.get('default_model', False) == 'crm.helpdesk' and \
                context.get('default_res_id', False):
            helpdesk_ids = self.env['crm.helpdesk'].search(
                [('id', '=', context.get('default_res_id', False))])
            try:
                email_from = helpdesk_ids and helpdesk_ids[0].email_origin \
                    and parseaddr(helpdesk_ids[0].email_origin)[1] or False
                this = self.env['res.users'].browse(self._uid)
                if this and this.name and email_from:
                    email_from = formataddr(
                        ("[%s] %s" % (
                            helpdesk_ids[0].code, this.name), email_from))
                else:
                    email_from = False
            except:
                email_from = False
                pass
        if not email_from:
            email_from = super(MailMessage, self)._get_default_from()
        return email_from

    @api.model
    def _create_partner(self, helpdesk_obj, vals):
        res_partner_pool = self.env['res.partner']
        partner_id = helpdesk_obj.partner_id
        if not partner_id and helpdesk_obj.email_from:
            try:
                email = parseaddr(helpdesk_obj.email_from)[1]
                partner_id = res_partner_pool.search([('email', '=', email)])
            except:
                pass
        if not partner_id:
            partner_id = res_partner_pool.create({
                'name': email,
                'email': email
            })
        if not helpdesk_obj.partner_id and partner_id:
            helpdesk_obj.partner_id = partner_id
            followers = helpdesk_obj.message_follower_ids.ids or []
            followers.append(partner_id.id)
            helpdesk_obj.message_follower_ids = [(6, 0, followers)]

    @api.model
    def create(self, vals):
        crm_helpdesk_pool = self.env['crm.helpdesk']
        if vals.get('model', False) and vals.get('model') == 'crm.helpdesk' \
                and vals.get('res_id'):
            helpdesk_id = crm_helpdesk_pool.browse(vals.get('res_id'))
            helpdesk_id.name = helpdesk_id.name
            if 'email_from' in vals:
                try:
                    email_from = parseaddr(vals.get('email_from'))[1]
                    partner = self.env['res.partner'].search(
                        [('email', '=', email_from)])
                    if partner:
                        user = self.env['res.users'].search(
                            [('partner_id', 'in', partner.ids)])
                        if helpdesk_id:
                            email_from = helpdesk_id.email_origin \
                                and (
                                    parseaddr(helpdesk_id.email_origin)[1] or
                                    False)
                            if email_from:
                                if user:
                                    self._create_partner(helpdesk_id, vals)
                                    email_from = formataddr(
                                        ("[%s] %s" % (
                                            helpdesk_id.code, user[0].name),
                                            email_from))
                                    vals['email_from'] = email_from
                                    vals['reply_to'] = email_from
                                else:
                                    vals['reply_to'] = email_from
                    else:
                        vals['reply_to'] = helpdesk_id.email_origin
                except:
                    pass
            else:
                vals['reply_to'] = helpdesk_id.email_origin
        return super(MailMessage, self).create(vals)


class MailThread(models.Model):
    _inherit = 'mail.thread'

    def _find_partner_from_emails(self, cr, uid, id, emails, model=None, context=None, check_followers=True):
        """ Utility method to find partners from email addresses. The rules are :
            1 - check in document (model | self, id) followers
            2 - try to find a matching partner that is also an user
            3 - try to find a matching partner

            :param list emails: list of email addresses
            :param string model: model to fetch related record; by default self
                is used.
            :param boolean check_followers: check in document followers
        """
        partner_obj = self.pool['res.partner']
        users_obj = self.pool['res.users']
        partner_ids = []
        obj = None
        uid_or_superuser = SUPERUSER_ID if model != 'crm.helpdesk' else uid
        if id and (model or self._name != 'mail.thread') and check_followers:
            if model:
                obj = self.pool[model].browse(cr, uid_or_superuser, id, context=context)
            else:
                obj = self.browse(cr, uid_or_superuser, id, context=context)
        for contact in emails:
            partner_id = False
            email_address = tools.email_split(contact)
            if not email_address:
                partner_ids.append(partner_id)
                continue
            email_address = email_address[0]
            # first try: check in document's followers
            if obj:
                for follower in obj.message_follower_ids:
                    if follower.email == email_address:
                        partner_id = follower.id
            # second try: check in partners that are also users
            # Escape special SQL characters in email_address to avoid invalid matches
            email_address = (email_address.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_'))
            email_brackets = "<%s>" % email_address
            if not partner_id:
                # exact, case-insensitive match
                user_ids = users_obj.search(cr, uid_or_superuser,
                                         [('email', '=ilike', email_address)],
                                         limit=1, context=context)
                ids = [users_obj.browse(cr, uid_or_superuser, user_ids, context=context).partner_id.id]
                if not ids:
                    # if no match with addr-spec, attempt substring match within name-addr pair
                    user_ids = users_obj.search(cr, uid_or_superuser,
                                             [('email', 'ilike', email_brackets)], limit=1, context=context)
                    ids = [users_obj.browse(cr, uid_or_superuser, user_ids, context=context).partner_id.id]
                if ids:
                    partner_id = ids[0]
            # third try: check in partners
            if not partner_id:
                # exact, case-insensitive match
                ids = partner_obj.search(cr, uid_or_superuser,
                                         [('email', '=ilike', email_address)],
                                         limit=1, context=context)
                if not ids:
                    # if no match with addr-spec, attempt substring match within name-addr pair
                    ids = partner_obj.search(cr, uid_or_superuser,
                                             [('email', 'ilike', email_brackets)],
                                             limit=1, context=context)
                if ids:
                    partner_id = ids[0]
            partner_ids.append(partner_id)
        return partner_ids
