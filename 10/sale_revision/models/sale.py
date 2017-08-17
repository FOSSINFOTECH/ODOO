# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import odoo.addons.decimal_precision as dp
import time
from datetime import datetime, date, timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    revision_no = fields.Char('Revision Number', size=32, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    revision_count = fields.Integer('Revision Count')
    rev_line = fields.One2many('sale.revision', 'order_id', 'Revisions')

    _sql_constraints = [
        ('name_uniq', 'unique(revision_no, company_id)', 'Revision Number must be unique!'),
    ]

    def create_revisions(self):
        rev_obj = self.env['sale.revision']
        rev_line_obj = self.env['sale.revision.line']
        sale_id = self[0]
        if sale_id.order_line:
            revision_count = sale_id.revision_count + 1
            revision_no = str(sale_id.name) + '- R' + str(revision_count)
            rev_id = rev_obj.create({
                'name': revision_no,
                'order_id': sale_id.id
                })
        else:
            raise UserError(('There is no line item to revise.'))
        for line in sale_id.order_line:
            vals = {
                'revision_id': rev_id.id,
                'name': line.name,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'product_uom_qty': line.product_uom_qty,
            }
            rev_line_obj.create(vals)
        self.write({'revision_no': revision_no, 'revision_count': revision_count})
        return True



class SaleRevision(models.Model):
    _name = 'sale.revision'

    name = fields.Char('Revision No.', size=32, readonly=True)
    order_id = fields.Many2one('sale.order', 'Order Reference')
    revision_line = fields.One2many('sale.revision.line', 'revision_id', 'Revision Lines')
    state = fields.Selection('sale.order',related='order_id.state', readonly=True)

    def apply_revisions(self):
        ''' Create order lines against revision lines '''
        revision_id = self[0]
        sale_line_obj = self.env['sale.order.line']
        for l in revision_id.order_id.order_line:
            l.unlink()
        for x in revision_id.revision_line:
            vals = {
                'name': x.name,
                'product_id': x.product_id.id,
                'price_unit': x.price_unit,
                'tax_id': [(6, 0, [a.id for a in x.tax_id])],
                'product_uom_qty': x.product_uom_qty,
                'state': 'draft',
                'order_id': x.revision_id.order_id.id
            }
            print vals, "---------------valssssssssss-----------"
            sale_line_obj.create(vals)
        self.env['sale.order'].write({'revision_no': revision_id.name})
        return True




class SaleRevisionLine(models.Model):
    _name = 'sale.revision.line'

    revision_id = fields.Many2one('sale.revision', 'Revision Ref.', required=True, ondelete='cascade', readonly=True)
    name = fields.Text('Description', required=True, readonly=True)
    # sequence = fields.integer('Sequence', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    price_unit = fields.Float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=True)
    # type = fields.selection([('make_to_stock', 'from stock'), ('make_to_order', 'on order')], 'Procurement Method', required=True, readonly=True)
    tax_id = fields.Many2many('account.tax', 'sale_revision_tax', 'revision_line_id', 'tax_id', 'Taxes', readonly=True)
    product_uom_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product UoS'), required=True, readonly=True)
    # product_uom = fields.many2one('product.uom', 'Unit of Measure ', required=True, readonly=True)
    # product_uos_qty = fields.float('Quantity (UoS)', digits_compute=dp.get_precision('Product UoS'), readonly=True)
    # product_uos = fields.many2one('product.uom', 'Product UoS', readonly=True)
    # discount = fields.float('Discount (%)', digits_compute=dp.get_precision('Discount'), readonly=True)
    # company_id = fields.many2one('res.company', 'Company', readonly=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
