# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Francisco Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Crm Helpdesk improvements',
    'version': '8.0.1.0.0',
    'depends': [
        'crm_helpdesk',
        'mail',
    ],
    'category': 'Sales Management',
    'author': 'Odoo Community Association (OCA),FactorLibre',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'description': """
        This module extends helpdesk ticket model functionality for example create a field to set email to origin
        ,adds unique code for each ticket, supports multicompany and add and quick button to get all tickets for each customer
    """,
    'data': [
        'security/ir_rule_data.xml',
        'security/ir.model.access.csv',
        'data/helpdesk_sequence.xml',
        'views/crm_helpdesk_view.xml',
        'views/res_partner_view.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
    'application': False
}
