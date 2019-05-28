# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _crm_helpdesk_count(self):
        for record in self:
            email = record.email
            cases_ids = []
            if email:
                cases_ids = self.env['crm.helpdesk'].search([
                    '|', ('email_from', 'ilike', email),
                    ('partner_id', '=', record.id)])
            else:
                commercial_partner_id = record.commercial_partner_id.id
                if commercial_partner_id:
                    cases_ids = self.env['crm.helpdesk'].search([
                        ('partner_id.commercial_partner_id', '=',
                            record.commercial_partner_id.id)])
            record.crm_helpdesk_count = len(cases_ids)
            record.crm_helpdesk_ids = cases_ids

    crm_helpdesk_count = fields.Integer(
        compute='_crm_helpdesk_count', store=False, string='# of Cases')