# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import api, fields, models, _, exceptions
from openerp.modules.registry import RegistryManager
from urlparse import urljoin
from urllib import urlencode

_logger = logging.getLogger(__name__)


class CrmHelpdesk(models.Model):
    _inherit = 'crm.helpdesk'

    section_id = fields.Many2one(
        'crm.case.section', 'Sales Team',
        select=True,
        help="""Responsible sales team. Define Responsible user and Email"""
        """account for mail gateway.""")

    @api.model
    def get_team2email(self, vals):
        members = self.env['crm.case.section'].browse(vals['section_id']).\
            member_ids
        email_to = []
        for member in members:
            if member.notify_email == 'always' and member.partner_id.email:
                email_to.append(member.partner_id.email)
        return email_to

    @api.model
    def create(self, vals):
        res = super(CrmHelpdesk, self).create(vals)
        if res and vals.get('section_id', False):
            email_to = self.get_team2email(vals)
            if email_to:
                res.send_team_mail(email_to)
        return res

    @api.multi
    def write(self, vals):
        result = super(CrmHelpdesk, self).write(vals)
        if result and vals.get('section_id', False):
            email_to = self.get_team2email(vals)
            if email_to:
                self.send_team_mail(email_to)
        return result

    @api.multi
    def send_team_mail(self, emails_to):
        template_obj = self.env['email.template']
        template_id = self.env['ir.model.data'].get_object_reference(
            'crm_helpdesk_mail_team', 'email_template_helpdesk2team')
        template = None
        if template_id:
            template = template_obj.browse(template_id[1])
            if template:
                ctx = dict(self.env.context)
                ctx['emails_to'] = ",".join(l for l in emails_to)
                base_url = self.env['ir.config_parameter'].get_param(
                    'web.base.url')
                query = {'db': self.env.cr.dbname}
                for record in self:
                    try:
                        action_id = self.env.ref('crm_helpdesk.crm_case_helpdesk_act111').id
                        fragment = {
                            'action': action_id,
                            'model': 'crm.helpdesk',
                            'view_type': 'form',
                            'id': record.id
                        }
                        base_url2 = "/web?%s#%s" % (
                            urlencode(query), urlencode(fragment))
                        url = urljoin(base_url, base_url2)
                        link = "%(portal_link)s" % {
                            'portal_link': url,
                        }
                        ctx['link_record'] = link
                        template.with_context(ctx).\
                            send_mail(record.id)
                    except:
                        pass
