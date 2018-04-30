# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo.addons.decimal_precision as dp
from odoo import api, fields, models
from datetime import datetime
import time
from odoo.exceptions import UserError

class Task(models.Model):
    _inherit = "project.task"
    _description = "Task"

    @api.model
    def get_delay_days(self):
        res = {}
        for record in self:
            delay_days = False
            if record.date_deadline:
                if (datetime.strptime(record.date_deadline, "%Y-%m-%d") > datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")):
                    delay_days = 0
                elif (datetime.strptime(record.date_deadline, "%Y-%m-%d") < datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")):    
                    delay_days = (datetime.strptime(record.date_deadline, "%Y-%m-%d") - datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")).days
            record.delay_days = abs(delay_days)

    @api.model
    def get_points(self):
        res = {}
        for val in self:
            points = 0
            if val.delay_days < 10:
                points = 100 - (val.delay_days * 10)
            elif val.delay_days >= 10 and val.delay_days <= 14:
                points = 0
            elif val.delay_days >= 15 and val.delay_days <= 19:
                points = -50
            elif val.delay_days >= 20:
                points = -100
            val.points = points

    delay_days = fields.Integer(compute='get_delay_days', string='Days Delayed')
    points = fields.Integer(compute='get_points', string='Points')
    date_assign = fields.Date(string='Assigning Date', index=True, copy=False, readonly=True)

    @api.multi
    def write(self, vals):
        res = super(Task, self).write(vals)
        for dt in self:
            if dt.date_assign > dt.date_deadline:
                raise UserError(("Date Deadline should not be less than the Assigned Date."))
        return res
