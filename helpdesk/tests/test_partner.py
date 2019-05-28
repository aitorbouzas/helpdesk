from odoo.tests.common import TransactionCase


class TestPartner(TransactionCase):
    at_install = True
    post_install = True

    def setUp(*args, **kwargs):
        super(TestPartner, self).setUp()
        self.partner_obj = self.env['partner']
        self.ticket_obj = self.env['helpdesk.ticket']
        self.parent_id = self.env.create({'name': 'Parent 1'})
        self.child_id_1 = self.env.create({'name': 'Child 1'})
        self.child_id_2 = self.env.create({'name': 'Child 2'})
        self.child_id_3 = self.env.create({'name': 'Child 3'})
        self.parent_id.helpdesk_ticket_ids= (0, 0, {
            'name': f"Ticket of parent ",
            'priority': '2',
            'closed': True
        })
        self.child_id_1.helpdesk_ticket_ids= (0, 0, {
            'name': f"Ticket of child {self.child_1.name}",
            'priority': '2',
            'closed': True
        })
        self.child_id_2.helpdesk_ticket_ids= (0, 0, {
            'name': f"Ticket of child {self.child_2.name}",
            'priority': '2',
            'closed': True
        })
        self.child_id_3.helpdesk_ticket_ids = (0, 0, {
            'name': f"Ticket of child {self.child_3.name}",
            'priority': '2',
            'closed': True
        })
    def test_ticket_count():
        self.assertEqual(parent_id.helpdesk_ticket_count, 4)
        self.assertEqual(parent_id.helpdesk_ticket_active_count, 3)
    def test_active_ticket_count():
        parent_id._compute_helpdesk_ticket_count()
        
