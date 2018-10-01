# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_hsn_code(self, hsn):
        list1 = []
        for invoice_line in self.invoice_line_ids:
            list1.append(invoice_line.product_id.l10n_in_hsn_code)
        hsn_group = list(set(list1))
        return hsn_group
