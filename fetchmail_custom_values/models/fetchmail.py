# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models, api


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    fields_lines = fields.One2many(
        comodel_name='fetchmail.server.custom.lines',
        inverse_name='server_id',
        string='Value Mapping')

    @api.model
    def _update_cron(self):
        if self.env.context and self.env.context.get('fetchmail_cron_running'):
            return
        try:
            self.env['ir.model.data'].get_object(
                'fetchmail', 'ir_cron_mail_gateway_action')
        except ValueError:
            # Nevermind if default cron cannot be found
            return
        # Enabled/Disable cron based on the number of 'done' server of type pop or imap
            # cron.toggle(model=self._name, domain=[
            #     ('state', '=', 'done'),
            #     ('type', 'in', ['pop', 'imap'])])


class FetchmailServerCustomLines(models.Model):
    _name = "fetchmail.server.custom.lines"
    _description = "Custom values when record created"
    _order = "sequence"

    sequence = fields.Integer('Sequence', help="Determine the display order", default=1)

    server_id = fields.Many2one(
        comodel_name='fetchmail.server',
        string='Related Fetchmail Server',
        required=True,
        ondelete='cascade')
    col1 = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        required=True)
    value = fields.Text(
        string='Value',
        required=True,
        help="Expression containing a value specification. \n"
             "When Formula type is selected, this field may be a Python expression "
             " that can use the same values as for the condition field on the fetchmail_server.\n"
             "If Value type is selected, the value will be used directly without evaluation.")
    type = fields.Selection(
        string='Evaluation Type',
        change_default=True,
        required=True,
        selection=[('value', 'Value'), ('equation', 'expression')],
        default='value')

    @api.model
    def eval_value(self, lines, eval_context=None):
        res = dict.fromkeys(lines.ids, False)
        for line in lines:
            expr = line.value
            if line.type == 'equation':
                try:
                    expr = eval(line.value, eval_context)
                except Exception:
                    expr = False
                    pass
            elif line.col1.ttype in ['many2one', 'integer']:
                try:
                    expr = int(line.value)
                except Exception:
                    expr = False
                    pass
            res[line.id] = expr
        return res
