# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TargetSaleEngineer(models.Model):
    _name = 'target.sale.engineer'
    _description = 'Assign Monthly Target For Sale Engineer'

    name = fields.Char(string='Reference')
    active = fields.Boolean(string="Active", default=True, track_visibility='onchange')
    from_date = fields.Date(string="From Date")
    end_date = fields.Date(string="To Date")
    user_line = fields.One2many('user.line', 'line_id', string="Users List")

    @api.multi
    def fetch_value(self):
        sale_search = []
        for line in self.user_line:
            if line:
                line.actual = 0
                line.pending = 0
        sale_obj = self.env['sale.order']
        for line in self.user_line:
            sale_search = sale_obj.search([
                ('user_id', '=', line.user_id.id),
                ('state', '=', 'sale'),
                ('confirmation_date', '>=', self.from_date),
                ('confirmation_date', '<=', self.end_date)
            ])
            if sale_search:
                for sale in sale_search:
                    for line in self.user_line:
                        if line.user_id == sale.user_id:
                            line.actual += sale.amount_total
                            line.pending = line.target - sale.amount_total
        return True


class UserLine(models.Model):
    _name = 'user.line'
    _description = 'Sales Person Target'

    user_id = fields.Many2one('res.users', string="Sales Person")
    target = fields.Float(string="Target")
    actual = fields.Float(string="Actual")
    pending = fields.Float(string="Pending")
    line_id = fields.Many2one('target.sale.engineer', string="Target Id")
