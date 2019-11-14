# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


# Additional Model 11/09/19
class FaqTag(models.Model):
    _name = "faq.tag"
    _description = "Frequently Asked Question's Tag"

    name = fields.Char(required=True)
    color = fields.Integer("Color Index")
