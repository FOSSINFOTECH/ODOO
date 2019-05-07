# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class faq_faq(models.Model):
    _name = "faq.faq"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Frequently Asked Questions"

    active = fields.Boolean(string="Active", default=True)
    name = fields.Text(string="Questions")
    solution = fields.Html(string="Solution", track_visibility="always")
    attachment = fields.Binary(string="Attachment")
    filename = fields.Char(string="Filename")
    category_ids = fields.Many2many('faq.category', string='Category', required=True)


faq_faq()
