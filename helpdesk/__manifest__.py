# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Helpdesk',
    'summary': """
        Helpdesk""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), Domatix',
    'website': 'https://github.com/OCA/helpdesk',
    'depends': [
        'mail',
        'portal',
        'contacts',
    ],
    'data': [
        'data/helpdesk_data.xml',
        'views/helpdesk_team_views.xml',
        'views/partner_views.xml',
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'application': True,
    'installable': True,
}
