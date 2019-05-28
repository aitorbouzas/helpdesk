from odoo import api, fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="partner_id",
        string="Assigned tickets",
    )

    helpdesk_ticket_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Tickets"
    )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        for record in self:
            helpdesk_ticket_count = len(record.helpdesk_ticket_ids)

    def action_view_helpdesk_tickets(self):
        ticket_ids = self.helpdesk_ticket_ids.ids
        for child in self.child_ids:
            for ticket in child.helpdesk_ticket_ids.ids:
                ticket_ids.append(ticket)
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "helpdesk.ticket",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", ticket_ids)],
            "context": self.env.context,
        }
