# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        res = super(MrpProductProduce, self).do_produce()
        msg = _('Quantity Produced: ') + str(self.product_qty)
        self.production_id.message_post(body=msg)
        for ml in self.production_id.move_raw_ids:
            total_qty = 0
            sq = self.env['stock.quant'].search([('product_id', '=', ml.product_id.id), ('location_id', '=', self.production_id.location_src_id.id)])
            if sq.id == False:
                raise UserError(_('There is no stock available for the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) in the stock location. Kindly add the required stock.'))
            else:
                for bom_line in self.production_id.bom_id.bom_line_ids:
                    if ml.product_id == bom_line.product_id:
                        total_qty = bom_line.product_qty * self.product_qty
                        for i in sq:
                            if total_qty > i.quantity:
                                raise UserError(_('You cannot validate this stock operation because the stock level of the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) would become negative on the stock location and negative stock is not allowed for this product.'))
        return res
