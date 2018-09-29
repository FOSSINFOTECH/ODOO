# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class stock_quality_check(models.Model):
    _name = "stock.quality.check"
    _description = "Quality Check"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'
    _order = 'number desc'

    number = fields.Char(string="Sequence", default="/")
    product_id = fields.Many2one('product.product', string="Product")
    product_uom_id = fields.Many2one('product.uom', string="Product UoM")
    done_qty = fields.Float(string="Done Qty")
    pass_qty = fields.Float(string="Pass Qty")
    fail_qty = fields.Float('Fail Qty')
    date = fields.Date(string="Date")
    state = fields.Selection([
        ('partial', 'Partial'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], 'Status', copy=False, default='draft', track_visibility='onchange')
    reason_of_failure = fields.Text(string="Reason of Failure")
    move_id = fields.Many2one('stock.move', string="Stock Move")

    def create(self, vals):
        if vals.get('number', '/') == '/':
            if vals.get('move_id'):
                vals['number'] = self.env['ir.sequence'].next_by_code(
                    'stock.quality.check.receipts') or '/'
        res = super(stock_quality_check, self).create(vals)
        return res
