# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models

class TentativePrice(models.Model):
    _name = "tentative.price"
    _inherit = ['mail.thread']
    _descirption = "Tentative Price List"
    _order = "number desc"

    number = fields.Char(string='Sequence', default='New')
    name =  fields.Char(string='Name', required=True)
    reference = fields.Char(string='Reference')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft')
    tentative_price_ids =  fields.One2many('tentative.price.lines', 'tentative_price_id', string='Tentative Price Reference')

    @api.model
    def create(self, vals):
        if vals.get('number', 'New') == 'New':
            vals['number'] = self.env['ir.sequence'].next_by_code('tentative.price') or '/'
        return super(TentativePrice, self).create(vals)

    @api.multi
    def confirm(self):
        self.write({'state': "confirmed"})
        return True


class TentativePriceLines(models.Model):
    _name = "tentative.price.lines"
    _descirption = "Tentative Price List Lines"

    @api.model
    def get_purchased_amt(self):
        res = {}
        po_obj = self.env['purchase.order']
        for tprice in self:
            if tprice.tentative_price_id.state not in 'draft':
                po_price = 0
                po_sr = po_obj.search([('tpl_pricelist_id', '=', tprice.tentative_price_id.id)])
                if po_sr:
                    for po in po_sr:
                        for line in po.order_line:
                            if tprice.product_id == line.product_id.parent_id:
                                if po.state not in 'cancel':
                                    po_price += line.price_subtotal
                    tprice.purchased_amt = po_price

    @api.model
    def get_remaining_tpl_amt(self):
        res = {}
        for tremain in self:
            if tremain.tentative_price_id.state not in 'draft':
                remain_tpl_amt = tremain.tpl_amt - tremain.purchased_amt
                tremain.remaining_tpl_amt = remain_tpl_amt
        return res

    tentative_price_id = fields.Many2one('tentative.price', string='Tentative Price')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    product_uom = fields.Many2one('product.uom', string='UoM', required=True)
    rate_unit = fields.Integer(string='Rate/Unit', required=True)
    tpl_amt = fields.Integer(string='TPL Amount', digits=dp.get_precision('Product Price'), required=True)
    purchased_amt = fields.Float(compute='get_purchased_amt', string='Purchased Amount', digits=dp.get_precision('Product Price'))
    remaining_tpl_amt = fields.Float(compute='get_remaining_tpl_amt', string='Remaining TPL Amount', digits=dp.get_precision('Product Price'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        return res

    @api.onchange('quantity', 'rate_unit')
    def onchange_tpl_amt(self):
        res = {}
        self.tpl_amt = self.quantity * self.rate_unit
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    parent_id = fields.Many2one('product.template', string='Parent Product')
    is_parent = fields.Boolean(string='Is Parent')


class ProductProduct(models.Model):
    _inherit = "product.product"

    parent_id = fields.Many2one('product.product', string='Parent Product')
    is_parent = fields.Boolean(string='Is Parent')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    tpl_pricelist_id = fields.Many2one('tentative.price', string='Tentative List Name')


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    remain_tpl_amt = fields.Float(compute='get_remain_tpl_amt',string='Remaining TPL Amount', digits=dp.get_precision('Product Price'))

    def get_remain_tpl_amt(self):
        res = {}
        tpl_obj = self.env['tentative.price']
        tpl_line_obj = self.env['tentative.price.lines']
        for po in self:
            res[po.id] = {
                'remain_tpl_amt': 0.0,
            }
            tpl_line_sr = tpl_line_obj.search([('tentative_price_id', '=', po.order_id.tpl_pricelist_id.id)])
            if tpl_line_sr:
                for tr in tpl_line_sr:
                    if tr.product_id == po.product_id.parent_id:
                        if po.state not in 'cancel' and tr.tentative_price_id: 
                            if tr.tentative_price_id.state not in 'draft':
                                remain_tpl_amt = tr.remaining_tpl_amt
                                po.remain_tpl_amt = remain_tpl_amt or 0.0
                        else:
                            po.remain_tpl_amt = 0.0
                            
    
