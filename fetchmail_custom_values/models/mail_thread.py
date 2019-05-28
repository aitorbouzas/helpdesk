# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Kiko Peiro <francisco.peiro@factorlibre.com>
#                      Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api
from lxml import etree
from openerp.addons.mail.mail_message import decode
from email.message import Message
import email
import time
import datetime
import dateutil
import pytz
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_xpath_text_body(self, message_parsed, xpath_expr):
        # //a[starts-with(@href, 'mailto')] expr to get mailto from body
        tree = etree.HTML(message_parsed.get('body'))
        xpath_find = tree.xpath(xpath_expr)
        if xpath_find:
            return xpath_find[0].text
        return False

    @api.model
    def _get_eval_context(self, fetchmail, message_parsed):
        """ Prepare the context used when evaluating python code, like the
        condition or code server actions.

        :param fetchmail,: the current fetchmail
        :type fetchmail: browse record
        :param message_parsed,: the current message parsed
        :type message_parsed: dict
        :returns: dict -- evaluation context given to (safe_)eval """
        return {
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            'timezone': pytz.timezone,
            'from': message_parsed.get('from'),
            'to': message_parsed.get('to'),
            'cc': message_parsed.get('cc'),
            'reply_to': message_parsed.get('reply-to'),
            'body': message_parsed.get('body'),
            'date_message': message_parsed.get('date'),
            'subject': message_parsed.get('subject'),
            'self': self,
            'context': self.env.context,
            'fetchmail_obj': fetchmail,
            'message_parsed': message_parsed,
            'get_xpath_text_body': self._get_xpath_text_body,
        }

    @api.model
    def message_parse(self, message, save_original=False):
        msg_dict = super(MailThread, self).message_parse(
            message, save_original)
        if not isinstance(message, Message):
            if isinstance(message, unicode):
                message = message.encode('utf-8')
            message = email.message_from_string(message)
        msg_dict['reply-to'] = message.get('reply-to') and \
            decode(message.get('reply-to'))
        return msg_dict

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        if not custom_values:
            custom_values = {}
        custom_vals = {}
        if self.env.context.get('fetchmail_server_id', False):
            fetchmail_obj = self.env['fetchmail.server'].browse(
                self.env.context.get('fetchmail_server_id', False))
            if fetchmail_obj.fields_lines:
                message_parsed = self.env['mail.thread'].message_parse(
                    message, save_original=save_original)
                eval_context = self._get_eval_context(
                    fetchmail_obj, message_parsed)
                vals = self.env['fetchmail.server.custom.lines'].eval_value(
                    fetchmail_obj.fields_lines, eval_context=eval_context)
            for line in fetchmail_obj.fields_lines:
                if line.id in vals:
                    if not custom_vals.get(line.col1.name, False) and\
                            vals[line.id]:
                        custom_vals[line.col1.name] = vals[line.id]
                    elif line.col1.name == 'active':
                        custom_vals[line.col1.name] = vals[line.id]
        if custom_vals:
            custom_values.update(custom_vals)
        super(MailThread, self).message_process(
            model, message, custom_values=custom_values,
            save_original=save_original, strip_attachments=strip_attachments,
            thread_id=thread_id)
        return True
