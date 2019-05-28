# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Francisco Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Crm Helpdesk Mail Team',
    'version': '8.0.1.0.0',
    'depends': [
        'crm_helpdesk_improvement',
    ],
    'category': 'Helpdesk Management',
    'author': 'Odoo Community Association (OCA),FactorLibre',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'description': """
        This module extends helpdesk ticket model functionality in order to send mail for each sales team's member when field is changed
    """,
    'data': [
        'data/crm_helpdesk_template_email2team.xml'
    ],
    'installable': True,
    'application': False
}
