# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FaqFaq(models.Model):
    _name = "faq.faq"
    _description = "Frequently Asked Questions"

    active = fields.Boolean(string="Active", default=True)
    name = fields.Text(string="Questions")
    solution = fields.Html(string="Solution", track_visibility="always")
    attachment = fields.Binary(string="Attachment")
    filename = fields.Char(string="Filename")

    # Additional Fields 11/09/19
    tag_ids = fields.Many2many('faq.tag', string='Tags')
    category_id = fields.Many2one('faq.category', string='Category')
    video = fields.Char()
