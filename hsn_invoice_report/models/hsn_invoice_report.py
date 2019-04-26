# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    # split the product based on HSN code
    def get_hsn_code(self, hsn):
        list1 = []
        for invoice_line in self.invoice_line_ids:
            list1.append(invoice_line.product_id.l10n_in_hsn_code)
        hsn_group = list(set(list1))
        return hsn_group

    # Get Rate and Amount fot GST product
    @api.multi
    def get_gst(self, inv_id, product_id):
        invoice = self.search([('id', '=', inv_id)], limit=1)
        tax_amount = 0
        rate = 0

        for num in invoice.invoice_line_ids:
            if num.product_id.id == product_id:

                tax_rate = 0
                for i in num.invoice_line_tax_ids:

                    if i.children_tax_ids:
                        tax_rate = sum(i.children_tax_ids.mapped('amount'))

                tax_amount = ((tax_rate / 100) * num.price_subtotal) / 2
                rate = tax_rate / 2
        return [rate, tax_amount]

    # Get Rate and Amount fot IGST product
    @api.multi
    def get_igst(self, inv_id, product_id):
        invoice = self.search([('id', '=', inv_id)], limit=1)
        tax_amount = 0
        rate = 0

        for i in invoice.invoice_line_ids:
            if i.product_id.id == product_id:
                tax_rate = 0
                for t in i.invoice_line_tax_ids:
                    if not t.children_tax_ids:
                        tax_rate = t.amount
                tax_amount = (tax_rate / 100) * i.price_subtotal
                rate = tax_rate
        return [rate, tax_amount]
