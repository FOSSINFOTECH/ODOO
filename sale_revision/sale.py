# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'revision_no': fields.char('Revision Number', size=32, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'revision_count': fields.integer('Revision Count'),
        'rev_line': fields.one2many('sale.revision', 'order_id', 'Revisions'),
        'covering_letter': fields.text('Covering Letter')
    }

    _sql_constraints = [
        ('name_uniq', 'unique(revision_no, company_id)', 'Revision Number must be unique!'),
    ]

    def create_revisions(self, cr, uid, ids, context=None):
        rev_obj = self.pool.get('sale.revision')
        rev_line_obj = self.pool.get('sale.revision.line')
        sale_id = self.browse(cr, uid, ids)[0]
        revision_count = sale_id.revision_count + 1
        revision_no = str(sale_id.name) + '- R' + str(revision_count)
        rev_id = rev_obj.create(cr, uid, {
            'name': revision_no,
            'order_id': sale_id.id
            })
        for line in sale_id.order_line:
            vals = {
                'revision_id': rev_id,
                'name': line.name,
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'type': line.type,
                'tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'product_uos_qty': line.product_uos_qty,
                'product_uos': line.product_uos.id,
                'discount': line.discount,
                'company_id': line.company_id.id,
            }
            rev_line_obj.create(cr, uid, vals)
        self.write(cr, uid, ids, {'revision_no': revision_no, 'revision_count': revision_count})
        return True

sale_order()


class sale_revision(osv.osv):
    _name = 'sale.revision'

    _columns = {
        'name': fields.char('Revision No.', size=32, readonly=True),
        'order_id': fields.many2one('sale.order', 'Order Reference'),
        'revision_line': fields.one2many('sale.revision.line', 'revision_id', 'Revision Lines'),
        'state': fields.related('order_id', 'state', type='char',string='State', readonly=True)
    }

    def apply_revisions(self, cr, uid, ids, context=None):
        ''' Create order lines against revision lines '''
        revision_id = self.browse(cr, uid, ids)[0]
        sale_line_obj = self.pool.get('sale.order.line')
        for l in revision_id.order_id.order_line:
            sale_line_obj.unlink(cr, uid, [l.id], context=context)
        for x in revision_id.revision_line:
            vals = {
                'name': x.name,
                'sequence': x.sequence,
                'product_id': x.product_id.id,
                'price_unit': x.price_unit,
                'type': x.type,
                'tax_id': [(6, 0, [a.id for a in x.tax_id])],
                'product_uom_qty': x.product_uom_qty,
                'product_uom': x.product_uom.id,
                'product_uos_qty': x.product_uos_qty,
                'product_uos': x.product_uos.id,
                'discount': x.discount,
                'company_id': x.company_id.id,
                'state': 'draft',
                'order_id': x.revision_id.order_id.id
            }
            sale_line_obj.create(cr, uid, vals)
        self.pool.get('sale.order').write(cr, uid, [revision_id.order_id.id], {'revision_no': revision_id.name})
        return True


sale_revision()


class sale_revision_line(osv.osv):
    _name = 'sale.revision.line'

    _columns = {
        'revision_id': fields.many2one('sale.revision', 'Revision Ref.', required=True, ondelete='cascade', readonly=True),
        'name': fields.text('Description', required=True, readonly=True),
        'sequence': fields.integer('Sequence', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=True),
        'type': fields.selection([('make_to_stock', 'from stock'), ('make_to_order', 'on order')], 'Procurement Method', required=True, readonly=True),
        'tax_id': fields.many2many('account.tax', 'sale_revision_tax', 'revision_line_id', 'tax_id', 'Taxes', readonly=True),
        'product_uom_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS'), required=True, readonly=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True, readonly=True),
        'product_uos_qty': fields.float('Quantity (UoS)', digits_compute=dp.get_precision('Product UoS'), readonly=True),
        'product_uos': fields.many2one('product.uom', 'Product UoS', readonly=True),
        'discount': fields.float('Discount (%)', digits_compute=dp.get_precision('Discount'), readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
    }

sale_revision_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
