# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Fetchmail Custom Values',
    'version': '8.0.1.0.0',
    'depends': [
        'fetchmail'
    ],
    'description': """
    This module allows set default values ​​in
    record creation when a incoming message is readed
    """,
    'category': 'Tools',
    'author': 'Odoo Community Association (OCA),FactorLibre',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'data': [
        'security/ir.model.access.csv',
        'views/fetchmail_view.xml',
    ],
    'installable': True,
    'application': False
}
