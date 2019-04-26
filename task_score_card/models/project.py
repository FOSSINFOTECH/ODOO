# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models
from datetime import datetime, date
import time
from odoo.exceptions import UserError


class Task(models.Model):
    _inherit = "project.task"
    _description = "Task"

    @api.model
    @api.depends('date_assigned', 'date_deadline')
    # caclulate a delay days
    def get_delay_days(self):
        if self.date_deadline:
            if self.date_deadline > date.today():
                self.delay_days = 0
            elif self.date_deadline < date.today():
                self.delay_days = (date.today() - self.date_deadline).days

    @api.model
    # calculate points based on delay days
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
    date_assigned = fields.Date(string='Assigning Date', index=True, copy=False, readonly=True)

    @api.model
    def create(self, vals):
        res = super(Task, self).create(vals)
        if not vals.get('date_assigned'):
            raise UserError(("Kindly fill out all the fields."))
        if not vals.get('date_deadline'):
            raise UserError(("kindly fill out all the fields."))
        return res

    @api.multi
    def write(self, vals):
        res = super(Task, self).write(vals)
        for date in self:
            if not date.date_assigned:
                raise UserError(("Kindly give the Assigning date for the task."))
            if not date.date_deadline:
                raise UserError(("Kindly give the deadline for the task"))
            if date.date_assigned > date.date_deadline:
                raise UserError(("Date Deadline should not be less than the Assigned Date."))
        return res
