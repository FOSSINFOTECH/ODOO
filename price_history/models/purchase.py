# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    po_revision_ids = fields.One2many('purchase.revision.line', 'po_id', string="Revision Line")

    @api.multi
    def button_purchase_revision(self):
        create_vals = {}
        revision_list = []
        po_line_list = []
        po_rev_obj = self.env['purchase.revision.line']
        po_line_obj = self.env['purchase.order.line']
        for rev_line in self.po_revision_ids:
            revision_list.append(rev_line.product_id.id)
        for po_line in self.order_line:
            po_line_list.append(po_line.product_id.id)
        for po_product in set(po_line_list):
            if po_line_list.count(po_product) > 1:
                product_br = self.env['product.product'].browse(po_product)
                raise UserError(_('[' + (product_br.default_code or '') + ']' + product_br.name + ' Product already exists in Order Line.'))
        for rev_line in revision_list:
            # Remove PO Lines from Revision which is not present in POL
            if rev_line not in po_line_list:
                rev_sr = po_rev_obj.search([('product_id', '=', rev_line), ('po_id', '=', self.id)])
                if rev_sr:
                    rev_sr.unlink()
            # Update Qty and Unit Price to Revision Lines from POL
            else:
                rev_sr = po_rev_obj.search([('product_id', '=', rev_line), ('po_id', '=', self.id)])
                line_sr = po_line_obj.search([('product_id', '=', rev_line), ('order_id', '=', self.id)])
                if rev_sr or line_sr.price_unit or line_sr.product_qty:
                    rev_sr.update({'unit_price': line_sr.price_unit, 'product_qty': line_sr.product_qty})
        # Add all the new PO lines to Revision Lines
        for po_line in po_line_list:
            if po_line not in revision_list:
                line_sr = po_line_obj.search([('product_id', '=', po_line), ('order_id', '=', self.id)])
                if line_sr:
                    for line in line_sr:
                        create_vals = {
                            'product_id': line.product_id.id,
                            'product_qty': line.product_qty,
                            'unit_price': line.price_unit,
                            'product_uom': line.product_uom.id,
                            'po_id': self.id,
                            'po_requisition_id': self.requisition_id.id,
                        }
                        new_id = po_rev_obj.create(create_vals)
        return True

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if not self.po_revision_ids:
            self.button_purchase_revision()
        return True


class PurchaseRevisionLine(models.Model):
    _name = 'purchase.revision.line'

    product_id = fields.Many2one('product.product', string="Product")
    po_requisition_id = fields.Many2one('purchase.requisition', string='Requisition')
    product_qty = fields.Float(string="Quantity")
    product_uom = fields.Many2one('product.uom', string="Product UoM")
    unit_price = fields.Float(string="Unit Price")
    po_id = fields.Many2one('purchase.order', string="Revision")
