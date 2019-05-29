from odoo.tests.common import SavepointCase


class TestPartner(SavepointCase):
    def setUp(self):
        super(TestPartner, self).setUp()
        self.partner_obj = self.env["res.partner"]
        self.ticket_obj = self.env["helpdesk.ticket"]
        self.tickets = []
        self.parent_id = self.partner_obj.create({"name": "Parent 1"})
        self.child_id_1 = self.partner_obj.create({"name": "Child 1"})
        self.child_id_2 = self.partner_obj.create({"name": "Child 2"})
        self.child_id_3 = self.partner_obj.create({"name": "Child 3"})
        self.parent_id.child_ids = [
            (4, self.child_id_1.id),
            (4, self.child_id_2.id),
            (4, self.child_id_3.id),
        ]
        for i in [69, 155, 314, 420]:
            closed = False
            if i == 420:
                closed = True
            self.tickets.append(
                self.ticket_obj.create(
                    {
                        "name": f"Nice ticket {i}",
                        "description": f"Nice ticket {i} description",
                        "closed": closed,
                    }
                )
            )
        self.parent_id.helpdesk_ticket_ids = [4, self.tickets[0].id]
        self.child_id_1.helpdesk_ticket_ids = [4, self.tickets[1].id]
        self.child_id_2.helpdesk_ticket_ids = [4, self.tickets[2].id]
        self.child_id_3.helpdesk_ticket_ids = [4, self.tickets[3].id]

    def test_ticket_count(self):
        self.parent_id._compute_helpdesk_ticket_count()
        # self.assertEqual(self.parent_id.helpdesk_ticket_count, 4)
        self.assertEqual(self.parent_id.helpdesk_ticket_active_count, 3)

    def test_ticket_string(self):
        self.parent_id._compute_helpdesk_ticket_count()
        self.assertEqual(
            self.parent_id.helpdesk_ticket_count_string, "3/4 related ticket(s)"
        )
