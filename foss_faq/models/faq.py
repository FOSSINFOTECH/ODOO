# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class faq_faq(models.Model):
    _name = "faq.faq"
    _description = "Frequently Asked Questions"

    active = fields.Boolean(string="Active", default=True)
    name = fields.Text(string="Questions")
    solution = fields.Html(string="Solution", track_visibility="always")
    attachment = fields.Binary(string="Attachment")
    filename = fields.Char(string="Filename")


faq_faq()
