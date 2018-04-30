# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class product_product(models.Model):
    _inherit = 'product.product'

    seq = fields.Integer(string='Sequence')
    child_line = fields.One2many('child.product.line', 'product_tmp_id', string='Products')

    @api.multi
    def write(self, vals):
        if self.child_line:
            for line in self.child_line:
                line.product_id.seq = 10
        if self.type == 'service':
            vals.update({
                'seq': 1
            })
        return super(product_product, self).write(vals)


class child_product_line(models.Model):
    _name = "child.product.line"

    product_tmp_id = fields.Many2one('product.product', string='Product Name')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity')  
    seq = fields.Integer(string='Sequence')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def update_product(self):
        ''' Create offer products against the selling product. '''
        vals_tools = []
        ext_line = [x.product_id.id for x in self.order_line]
        for line in self.order_line:
            if line.product_id.child_line:
                for ch_line in line.product_id.child_line:
                    if ch_line.product_id.id not in ext_line:
                        if line.product_uom_qty > 0 and ch_line.product_qty > 0:
                            vals_tools.append((0, 0, {
                                'sequence': line.product_id.seq,
                                'product_id': ch_line.product_id.id,
                                'product_uom_qty': line.product_uom_qty * ch_line.product_qty,
                                'price_unit' : 0.0,
                                'is_offer_product': True
                            }))
                        else:
                            raise UserError(('Product Qty Should be greater than Zero.'))
        self.order_line = vals_tools
        return True


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    is_offer_product = fields.Boolean(string='Is Offer Product', readonly=True)

    @api.model
    def create(self, vals):
        seq = 10
        if vals.get('order_id') and not vals.get('sequence'):
            self._cr.execute("""select max(sequence) from sale_order_line where order_id = %s""", (vals.get('order_id'),))
            res = self._cr.fetchone()
            if res and res[0]:
                if res[0] % 10 != 0:
                    rem = res[0] % 10
                    vals['sequence'] = (res[0] - rem) + 10
                else:
                    vals['sequence'] = res[0] + 10
            else:
                vals['sequence'] = seq
        return super(sale_order_line, self).create(vals)

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = {}
        res = super(sale_order_line, self)._prepare_invoice_line(qty)
        if res:
            res.update({'is_offer_product': self.is_offer_product})
        return res


class stock_move(models.Model):
    _inherit = 'stock.move'

    is_offer_product = fields.Boolean(string='Is Offer Product', readonly=True)


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    is_offer_product = fields.Boolean(string='Is Offer Product', readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
