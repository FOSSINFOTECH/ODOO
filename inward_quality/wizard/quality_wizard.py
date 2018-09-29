# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class QualityWizard(models.TransientModel):
    _name = 'quality.wizard'

    @api.model
    def default_get(self, fields):
        res = super(QualityWizard, self).default_get(fields)
        if self._context and self._context.get('active_id') and self._context.get('active_model'):
            if self._context.get('active_model') == 'stock.move':
                move = self.env['stock.move'].browse(self._context['active_id'])
                if move.pass_qty:
                    res['pass_qty'] = move.pass_qty
                if move.fail_qty:
                    res['fail_qty'] = move.fail_qty
                if move.fail_reason:
                    res['fail_reason'] = move.fail_reason
                if 'picking_id' in fields:
                    res['picking_id'] = move.id
                if 'product_id' in fields:
                    res['product_id'] = move.product_id.id
                if 'product_uom_id' in fields:
                    res['product_uom_id'] = move.product_uom.id
                if 'product_qty' in fields:
                    res['product_qty'] = move.quantity_done
        return res

    @api.onchange('pass_qty', 'fail_qty')
    def onchange_qc(self):
        tt_qty = self.pass_qty + self.fail_qty
        if self.pass_qty and self.fail_qty and self.product_qty < tt_qty:
            raise UserError(_('Sum of Pass and Fail Qty Should be equal to the Product Qty.'))
        if self.pass_qty and self.pass_qty > self.product_qty:
            raise UserError(_('Pass Qty Should not be greater than Product Qty.'))
        if self.fail_qty and self.fail_qty > self.product_qty:
            raise UserError(_('Fail Qty Should not be greater than Product Qty.'))

    @api.multi
    def do_quality_check(self):
        if self._context and self._context.get('active_id') and self._context.get('active_model'):
            stock_total = 0
            if self._context.get('active_model') == 'stock.move':
                move = self.env['stock.move'].browse(self._context['active_id'])
                move.pass_qty = self.pass_qty
                move.fail_qty = self.fail_qty
                move.fail_reason = self.fail_reason
                stock_total = move.pass_qty + move.fail_qty
                if stock_total != move.quantity_done:
                    raise UserError(_('Sum of Pass and Fail Qty Should be equal to the Product Qty.'))
        return True

    picking_id = fields.Many2one('stock.move', 'Stock Picking')
    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float(string='Quantity', required=True)
    product_uom_id = fields.Many2one('product.uom', 'Unit of Measure')
    pass_qty = fields.Float(string="Pass Qty")
    fail_qty = fields.Float(string="Fail Qty")
    fail_reason = fields.Char(string="Fail Reason")
