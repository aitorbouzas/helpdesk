# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    # Getter / Setter Section
    @api.model
    def get_default_crm_helpdesk_improvement_number_of_minutes(self, fields):
        return {
            'crm_helpdesk_improvement_number_of_minutes':
            int(self.env["ir.config_parameter"].get_param(
                "crm_helpdesk_improvement.number_of_minutes") or '0')
        }

    @api.multi
    def set_crm_helpdesk_improvement_number_of_minutes(self):
        for config in self:
            self.env['ir.config_parameter'].set_param(
                "crm_helpdesk_improvement.number_of_minutes",
                config.crm_helpdesk_improvement_number_of_minutes or '')

    @api.model
    def get_default_crm_helpdesk_improvement_number_of_tickets(self, fields):
        return {
            'crm_helpdesk_improvement_number_of_tickets':
            int(self.env["ir.config_parameter"].get_param(
                "crm_helpdesk_improvement.number_of_tickets") or '0')
        }

    @api.multi
    def set_crm_helpdesk_improvement_number_of_tickets(self):
        for config in self:
            self.env['ir.config_parameter'].set_param(
                "crm_helpdesk_improvement.number_of_tickets",
                config.crm_helpdesk_improvement_number_of_tickets or '')

    crm_helpdesk_improvement_number_of_tickets = fields.Integer(
        string='Number of tickets.')

    crm_helpdesk_improvement_number_of_minutes = fields.Integer(
        string='Number of minutes.')
