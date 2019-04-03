# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, tools, models, _


class PriceHistoryReport(models.Model):
    _name = "price.history.report"
    _description = "Price History Report"
    _auto = False

    requisition_id = fields.Many2one('purchase.requisition', 'Purchase Agreement', readonly=True)
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order', readonly=True)
    unit_price = fields.Float('Unit Price', readonly=True)
    date_order = fields.Datetime('Order Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], 'Order Status', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Reference Unit of Measure', required=True)
    product_qty = fields.Float('Product Quantity', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'price_history_report')
        self._cr.execute("""
            create view price_history_report as (
               select
                    s.id as id,
                    s.id as purchase_id,
                    s.requisition_id as requisition_id,
                    s.partner_id as partner_id,
                    s.date_order,
                    prl.product_id,
                    prl.product_uom,
                    prl.product_qty,
                    prl.unit_price,
                    s.state
                from purchase_revision_line prl,purchase_order s
                where prl.po_id=s.id
                group by
                    s.id,
                    s.requisition_id,
                    s.partner_id,
                    s.date_order,
                    prl.product_id,
                    prl.product_uom,
                    prl.product_qty,
                    prl.unit_price,
                    s.state
            )
        """)
