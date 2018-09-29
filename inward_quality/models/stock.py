# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime


class StockMove(models.Model):
    _inherit = "stock.move"

    pass_qty = fields.Float(string="Pass Qty", copy=False)
    fail_qty = fields.Float(string="Fail Qty", copy=False)
    fail_reason = fields.Char(string="Fail Reason", copy=False)
    check_id = fields.Many2one('stock.quality.check', string="Quality Check")

    @api.multi
    def print_quality_check_report(self):
        action = self.env.ref('inward_quality.stock_quality_check_action')
        result = action.read()[0]
        if self.check_id:
            result['domain'] = "[('id','=',%s)]" % self.check_id.id
        return result


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        res = super(Picking, self).button_validate()
        if self.picking_type_code == 'incoming':
            for line in self.move_lines:
                if line.fail_qty:
                    self.rejected_moves(line, context=None)
                total_qty = line.pass_qty + line.fail_qty
                if not total_qty == line.quantity_done:
                    raise UserError(_('Sum of Pass and Fail Qty Should be equal to Done Qty in ( ' + (line.product_id.default_code or '') + ' ' + (line.product_id.name) + ' )'))
                if line.fail_qty and not line.fail_reason:
                    raise UserError(_('There is a fail qty in (' + (line.product_id.default_code or '') + ' ' + (line.product_id.name) + ') .So Kindly give a failure reason.'))
                qc_obj = self.env['stock.quality.check']
                if not line.pass_qty and line.fail_qty:
                    qc_state = 'failed'
                elif line.pass_qty and not line.fail_qty:
                    qc_state = 'passed'
                elif line.pass_qty and line.fail_qty:
                    qc_state = 'partial'
                if line.quantity_done:
                    create_vals = {
                        'product_id': line.product_id.id,
                        'done_qty': line.quantity_done,
                        'pass_qty': line.pass_qty,
                        'fail_qty': line.fail_qty,
                        'product_uom_id': line.product_uom.id,
                        'state': qc_state,
                        'date': fields.Date.today(),
                        'move_id': line.id,
                        'reason_of_failure': line.fail_reason,
                    }
                    new_check_id = qc_obj.create(create_vals)
                    if new_check_id:
                        line.write({'check_id': new_check_id.id})
        return res

    def rejected_moves(self, line, context=None):
        vals_obj = {}
        create_vals = {}
        stock_move_obj = self.env['stock.move']
        dest_loc_id = self.env['ir.config_parameter'].sudo().get_param('inward_quality.rejection_location')
        if not dest_loc_id:
            raise UserError(_('Kindly Configure Rejected Location in Settings.'))
        vals_obj = {
            'name': self.name,
            'product_id': line.product_id.id,
            'product_uom': line.product_uom.id,
            'product_uom_qty': line.fail_qty,
            'origin': line.product_id.name or '',
            'location_id': self.location_dest_id.id,
            'location_dest_id': dest_loc_id,
            'move_line_ids': [(0, 0, {
                'reference': self.name,
                'product_id': line.product_id.id,
                'product_uom_qty': 0,
                'product_uom_id': line.product_uom.id,
                'qty_done': line.fail_qty,
                'location_id': self.location_dest_id.id,
                'location_dest_id': dest_loc_id,
            })]
        }
        new_id = stock_move_obj.create(vals_obj)
        new_id._action_done()
