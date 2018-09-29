# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    # This creates commissioning when the apply button is clicked.
    @api.multi
    def process(self):
        res = super(StockImmediateTransfer, self).process()
        for line in self.pick_ids:
        	com_obj = self.env['crm.commission'].sudo()
	        com_obj_search = com_obj.search([('picking_id', '=', line.id)])
	        sale_id_search = self.env['sale.order'].search([('name', '=', line.origin)])
        	for mv_lines in line.move_lines:
        		for stock in mv_lines.move_line_ids:
        			if stock.product_id.commission_ok:
        				print(stock.lot_id.name)
        				if mv_lines.quantity_done:
        					qty_range = int(mv_lines.quantity_done)
        					if len(com_obj_search):
        						qty_range = qty_range - len(com_obj_search)
        					for stck in range(qty_range):
        						vals = {}
        						vals.update({
        							'partner_id': line.partner_id.id,
        							'mobile': line.partner_id.phone,
        							'lot_id': stock.lot_id.id,
        							'product_id': stock.product_id.id,
        							'sale_id': sale_id_search.id,
        							'picking_id': line.id
								})
        						vals['name'] = self.env['ir.sequence'].next_by_code('crm.commission') or '/'
        						com_obj.create(vals)
        return res
