# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api

class hr_company_holidays(models.Model):
    _name = 'hr.company.holidays'
    _description = 'Company Holidays Management'
    _order = 'date'
    _rec_name = 'description'

    # Get month and year value for the given date
    @api.depends('date')
    def get_month_year(self):
        res = {}
        for record in self:
            if record.date:
                res[record.id] = {'month': 0, 'year': 0}
                month = record.date.strftime("%B")
                year = record.date.strftime("%Y")
                record.update({
                    'month': str(month),
                    'year': str(year),
                })

    date = fields.Date(string='Date')
    description = fields.Char(string='Description', size=128)
    category_id = fields.Selection([('weekend', 'Weekend'),
            ('national_holiday', 'National Holiday'),
            ('declared_holiday', 'Declared Holiday')], 'Category')
    active = fields.Boolean(string='Active', help="Check this box to indicate that this holiday is active.", default=True)
    month = fields.Char(string="Month", method=True, store=True, multi="get_value", compute='get_month_year')
    year = fields.Char(compute='get_month_year' , string="Year", method=True, store=True, multi="get_value")
    calendar_id = fields.Many2one('calendar.event', string='Calendar Event')

    @api.model
    def create(self, values):
        user_obj = self.env['res.users']
        calendar_obj = self.env['calendar.event']
        res = super(hr_company_holidays, self).create(values)
        user_partner_id = user_obj.browse(self._uid).partner_id.id
        partners = []
        for part in user_obj.search([]):
            partners.append(part.partner_id.id)
        calendar_vals = {
            'name': 'HL: ' + values.get('description', ''),
            'start_date': values.get('date', False),
            'stop_date': values.get('date', False),
            'start': values.get('date', False),
            'stop': values.get('date', False),
            'partner_ids': [[6, 0, partners]] or [(4, user_partner_id)],
            'allday': True,
            'active': True
        }
        calendar_id = calendar_obj.create(calendar_vals)
        values['calendar_id'] = calendar_id
        calendar_obj.write({'res_id': res})
        res.write({'calendar_id': calendar_id.id})
        return res

    @api.multi
    def write(self, values):
        res = super(hr_company_holidays, self).write(values)
        user_obj = self.env['res.users']
        user_partner_id = user_obj.browse(self._uid).partner_id.id
        partners = []
        for part in user_obj.search([]):
            partners.append(part.partner_id.id)
        if values.get('description', False) or values.get('date', False) or values.get('active') == True or values.get('active') == False:
            for val in self:
                calendar_vals = {
                    'name': 'HL: ' + val.description,
                    'start_date': val.date,
                    'stop_date': val.date,
                    'start': val.date,
                    'stop': val.date,
                    'partner_ids': [[6, 0, partners]] or [(4, user_partner_id)],
                    'active': val.active
                }
                if val.calendar_id.id:
                    val.calendar_id.write(calendar_vals)
        return res

    @api.multi
    def unlink(self):
        for val in self:
            if val.calendar_id.id:
                val.calendar_id.unlink()
        return super(hr_company_holidays, self).unlink()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
