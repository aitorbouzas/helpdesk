from odoo import api, fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="partner_id",
        string="Related tickets",
    )
    helpdesk_ticket_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Ticket count"
    )
    helpdesk_ticket_active_count = fields.Integer(string="Active ticket count")
    helpdesk_ticket_count_string = fields.Char(string="Ticket count")

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        for record in self:
            ticket_ids = self.env["helpdesk.ticket"].search(
                [("partner_id", "child_of", record.id)]
            )
            record.helpdesk_ticket_count = len(ticket_ids)
            record.helpdesk_active_ticket_count = len(
                ticket_ids.filtered(lambda ticket: ticket.stage_id.closed == False)
            )
            record.helpdesk_ticket_count_string = f"{record.helpdesk_active_ticket_count}/{record.helpdesk_ticket_count} related ticket(s)"

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
