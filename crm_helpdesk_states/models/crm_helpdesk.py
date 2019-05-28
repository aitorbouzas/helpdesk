# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import api, fields, models
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class CrmHelpdesk(models.Model):
    _inherit = 'crm.helpdesk'

    state = fields.Selection(
        selection=[
            ('draft', 'New'),  # Nuevo
            ('pending', 'Pending'),  # Pendiente
            ('open', 'In Progress'),  # Abierto
            ('waiting', 'Waiting'),  # En Espera
            ('done', 'Resolved'),  # Resuelto
            ('closed', 'Closed'),  # Cerrado
            ('cancel', 'Cancelled')  # Cancelado
        ], string='Status', readonly=True,
        track_visibility='onchange',
        help='', default='draft')
    color = fields.Char('color', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('user_id') and (not vals.get('state', False)):
            vals['state'] = 'open'
        return super(CrmHelpdesk, self).create(vals)

    @api.multi
    def write(self, vals):
        result = True

        enable_state_transition = self.env.ref(
            'crm_helpdesk_states.group_crm_helpdesk_states_transitions') in \
            self.env.user.groups_id

        for record in self:
            if (vals.get('state', False) in ['draft', 'closed']) and \
                    not enable_state_transition:
                return True
            if (record.state in ['cancel', 'closed']) and \
                    not enable_state_transition:
                return True
            values = vals
            if values.get('user_id', False) and record.state == 'draft':
                values['state'] = 'open'
            if 'user_id' in values and not values['user_id'] and \
                    record.user_id and \
                    record.state not in ['cancel', 'done', 'closed']:
                values['state'] = 'draft'
            if values.get('state', False) and\
                    values.get('state') == 'closed' and not \
                    record.date_closed and not values.get('date_closed'):
                values['date_closed'] = fields.datetime.now()
            if values.get('state', False) and\
                    values.get('state') == 'done' and\
                    record.date_closed:
                values['date_closed'] = record.date_closed
            if values.get('state', False) and\
                    values.get('state') not in ['done', 'closed'] and \
                    record.state in ['done', 'closed']:
                values['date_closed'] = False
            result = super(CrmHelpdesk, self).write(values)
        return result

    @api.model
    def _check_days_done(self, days=10):
        closed_date_limit = datetime.now() - timedelta(days=days)
        closed_date_limit = datetime.strftime(
            closed_date_limit,
            DEFAULT_SERVER_DATETIME_FORMAT)

        crm_helpdesk_ids = self.search([
            ('state', '=', 'done'),
            ('date_closed', '<=', closed_date_limit)
        ])
        crm_helpdesk_ids.write({'state': 'closed'})
        return True
