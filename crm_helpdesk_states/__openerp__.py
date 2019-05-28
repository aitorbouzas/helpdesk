# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Crm Helpdesk states',
    'version': '8.0.1.0.0',
    'depends': [
        'web_tree_dynamic_colored_field',
        'crm_helpdesk_improvement',
        'mail',
    ],
    'category': 'Sales Management',
    'author': 'Odoo Community Association (OCA),FactorLibre',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'description': """
        This module extends helpdesk ticket model functionality making automatic transiction through states
    """,
    'data': [
        'security/crm_helpdesk_states_group.xml',
        'views/crm_helpdesk_view.xml',
        'data/ir_cron_data.xml'
    ],
    'installable': True,
    'application': False
}
