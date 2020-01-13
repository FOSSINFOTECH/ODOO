# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class FaqCategory(models.Model):
    _name = "faq.category"
    _description = "Frequently Asked Question's Category"

    name = fields.Char(required=True)
    question_ids = fields.One2many('faq.faq', 'category_id', string='FAQ Question')
