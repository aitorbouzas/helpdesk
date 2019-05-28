from odoo import api, fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="partner_id",
        string="Related tickets",
    )

    helpdesk_ticket_count = fields.Char(
        compute="_compute_helpdesk_ticket_count", 
        string="Ticket count",
        default="0/0 related ticket(s)"
    )

    helpdesk_ticket_active_count = fields.Integer(
        string="Active ticket count"
    )

    def get_active_ticket_ids(self):
        return self.helpdesk_ticket_ids.filtered(
            lambda ticket: ticket.stage_id.closed == False
        )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        for record in self:
            active_ticket_ids = record.get_active_ticket_ids()
            ticket_ids = self.helpdesk_ticket_ids
            for child in self.child_ids:
                for ticket in child.helpdesk_ticket_ids.ids:
                    ticket_ids.append(ticket)
                    active_ticket_ids.append(child.get_active_ticket_ids())
            record = record.with_context(
                ticket_ids=ticket_ids.ids, active_ticket_ids=active_ticket_ids.ids
            )
            record.helpdesk_ticket_active_count = len(active_ticket_ids)
            record.helpdesk_ticket_count = f"{active_ticket_ids}/{ticket_ids} related ticket(s)"

    def action_view_helpdesk_tickets(self):
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "helpdesk.ticket",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            "context": self.env.context,
        }
