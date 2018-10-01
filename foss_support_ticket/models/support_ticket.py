## -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta
import time
from lxml import etree


SEVERITY = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'Top'),
    ('3', 'Critical'),
]

TICKET_PRIORITY = [
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

TICKET_STATE = [
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled')
]


class TicketType(models.Model):
    _name = 'ticket.type'
    _description = "Ticket Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(string="Active", track_visibility='onchange', default=True)
    name = fields.Char(string="Ticket Type", track_visibility='onchange')
    task_type_id = fields.Many2one('task.type', string="Task Type")


class TicketTag(models.Model):
    _name = 'ticket.tag'
    _description = "Ticket Tag"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(string="Active", track_visibility='onchange', default=True)
    name = fields.Char(string="Ticket Tag", track_visibility='onchange')


class TaskType(models.Model):
    _name = 'task.type'
    _description = "Task Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(string="Active", track_visibility='onchange', default=True)
    name = fields.Char(string="Task Type", track_visibility='onchange')


class SubStatus(models.Model):
    _name = 'sub.status'
    _description = "Sub Status"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(string="Active", track_visibility='onchange', default=True)
    name = fields.Char(string="Sub Status", track_visibility='onchange')
    state = fields.Selection(TICKET_STATE, string='Related State')


class ProjectPhase(models.Model):
    _name = 'project.phase'
    _description = "Project Phase"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(string="Active", track_visibility='onchange', default=True)
    name = fields.Char(string="Project Phase", track_visibility='onchange')


class ActionCode(models.Model):
    _name = 'action.code'
    _description = "Action Code"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(string="Active", track_visibility='onchange', default=True)
    name = fields.Char(string="Action Code", track_visibility='onchange')


class SupportTicket(models.Model):
    _name = 'support.ticket'
    _description = 'Ticket'
    _order = 'priority desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('ticket_line')
    @api.multi
    def _get_total_time(self):
        for self_id in self:
            for line_id in self_id.ticket_line:
                self_id.time_spent += line_id.hrs_spent

    @api.multi
    def _get_default_stage_id(self):
        stage = self.stage_find([('state', '=', 'draft')])
        return stage and stage.id or False

    @api.depends('ticket_line.from_date')
    @api.multi
    def _get_response_tat(self):
        if self.ticket_line and self.create_date:
            if self.ticket_line[0].from_date and not self.response_tat:
                fmt = "%Y-%m-%d %H:%M:%S"
                self.response_tat = datetime.strptime(self.ticket_line[0].from_date, fmt) - datetime.strptime(self.create_date, fmt)

    @api.depends('completed_date')
    @api.multi
    def _get_resolution_tat(self):
        if self.create_date and self.completed_date:
            fmt = "%Y-%m-%d %H:%M:%S"
            self.resolution_tat = datetime.strptime(self.completed_date, fmt) - datetime.strptime(self.create_date, fmt)

    name = fields.Char(string='Name', default="/")
    subject = fields.Char(string='Subject', required=True, index=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Assigned to', track_visibility='onchange')
    partner_name = fields.Char(string='Contact Person')
    partner_email = fields.Char(string='Contact Mail')
    partner_phone = fields.Char(string='Contact Number')
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='1')
    medium = fields.Many2one('utm.medium', string='Contact Mode')
    ticket_raised_date = fields.Datetime(string='Task Raised Date', default=fields.datetime.now())
    completed_date = fields.Datetime(string='Completed Date')
    solution_given = fields.Text(string='Solution Given')
    remarks = fields.Text(string='Remarks')
    ticket_type = fields.Many2one('ticket.type', string='Task Sub Type')
    project_id = fields.Many2one('project.project', string='Client')
    tag_id = fields.Many2one('ticket.tag', string='Module')
    stage_id = fields.Selection(TICKET_STATE, string='Stage', track_visibility='onchange', default='draft')
    ticket_type_id = fields.Many2one('ticket.type', string='Task Sub Type')
    time_spent = fields.Float(compute='_get_total_time', string='Time Spent', store=True)
    attachment = fields.Binary(string='Attachment')
    response_tat = fields.Char(compute='_get_response_tat', string='Reponse TAT')
    resolution_tat = fields.Char(compute='_get_resolution_tat', string='Resolution TAT')
    task_type_id = fields.Many2one('task.type', string='Task Type')
    sub_status_id = fields.Many2one('sub.status', string='Sub Status')
    phase_id = fields.Many2one('project.phase', string='Phase')
    support_user_ids = fields.Many2many('res.users', 'support_users_rel', 'support_id', 'user_id', string='Supported User')
    expected_completed_date = fields.Datetime(string='Exp. Compl. Date')
    effort_required = fields.Float(string='Effort Required')
    severity = fields.Selection(SEVERITY, string='Severity', default="0")
    reference = fields.Char(string='Reference')
    ticket_line = fields.One2many('support.ticket.line', 'ticket_id', string='Supprt Ticket Line')

    @api.model
    def create(self, vals):
        res = super(SupportTicket, self).create(vals)
        if vals.get('name', '/') == '/':
            res['name'] = self.env['ir.sequence'].next_by_code('support.ticket') or '/'
        return res

    @api.multi
    def write(self, vals):
        if vals.get('ticket_raised_date'):
            if datetime.strptime(vals.get('ticket_raised_date'), "%Y-%m-%d %H:%M:%S") > fields.datetime.now():
                raise ValidationError('Warning! \n Ticket Raise Date cannot be a future Date.')
        if vals.get('completed_date'):
            if datetime.strptime(vals.get('completed_date'), "%Y-%m-%d %H:%M:%S") > fields.datetime.now():
                raise ValidationError('Warning! \n Ticket closed Date cannot be a future Date.')
        res = super(SupportTicket, self).write(vals)
        return res

    @api.multi
    def set_todo(self):
        if not self.expected_completed_date:
            raise ValidationError('Warning! \n Kindly fill the Expected Completed Date.')

        # After Import
        if self.expected_completed_date:
            if datetime.strptime(self.expected_completed_date, "%Y-%m-%d %H:%M:%S") < fields.datetime.now():
                raise ValidationError('Warning! \n Expected Complete cannot be a previous Date.')

        if self.effort_required <= 0:
            raise ValidationError('Warning! \n Kindly fill the Effort Required.')
        if self.stage_id:
            self.write({'stage_id': 'open'})
        return True

    @api.multi
    def set_pending(self):
        if self.stage_id:
            self.write({'stage_id': 'pending'})
        return True

    @api.multi
    def set_draft(self):
        if self.stage_id:
            self.write({'stage_id': 'draft'})
        return True

    @api.multi
    def set_done(self):
        if not self.completed_date:
            raise ValidationError('Warning! \n Kindly fill The Completed Date.')
        if self.completed_date:
            if datetime.strptime(self.completed_date, "%Y-%m-%d %H:%M:%S") > fields.datetime.now():
                raise ValidationError('Warning! \n Ticket closed Date cannot be a future Date.')
        if not self.solution_given:
            raise ValidationError('Warning! \n Kindly fill The Soultion Given.')
        if self.time_spent <= 0.0:
            raise ValidationError('Warning! \n Kindly fill The Time Duration to complete the task.')
        if self.stage_id:
            self.write({'stage_id': 'done'})

        return True

    @api.multi
    def set_cancel(self):
        if self.stage_id:
            self.write({'stage_id': 'cancelled'})
        return True


class SupportTicketLine(models.Model):
    _name = 'support.ticket.line'
    _description = 'Support Ticket Line'

    @api.multi
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.ticket_id.ticket_line:
                line_rec.s_no = line_num
                line_num += 1

    @api.depends('from_date', 'to_date')
    @api.multi
    def _get_time(self):
        fmt = "%Y-%m-%d %H:%M:%S"
        for line in self:
            if line.from_date and line.to_date:
                d1 = datetime.strptime(datetime.strftime(datetime.strptime(line.from_date, fmt), "%Y-%m-%d %H:%M:00"), fmt)
                d2 = datetime.strptime(datetime.strftime(datetime.strptime(line.to_date, fmt), "%Y-%m-%d %H:%M:00"), fmt)
                date1 = d1.replace(minute=15 * (d1.minute // 15))
                date2 = d2.replace(minute=15 * (d2.minute // 15))
                days_to_seconds = 0
                days_to_seconds = (date2 - date1).days * 86400
                line.hrs_spent = (((date2 - date1).seconds) + days_to_seconds) / 3600
                line.hrs_diff = datetime.strptime(line.to_date, fmt) - datetime.strptime(line.from_date, fmt)

        return True

    name = fields.Char(string='Name', readonly=True, default='/')
    is_invisible = fields.Boolean(string='Is Line Invisible', default=False)
    ticket_id = fields.Many2one('support.ticket', string='Ticket Id')
    s_no = fields.Integer(compute='_get_line_numbers', string='No.', readonly=False)
    action_taken = fields.Char(string='Action Taken')
    user_id = fields.Many2one('res.users', string='User')
    sub_status_id = fields.Many2one('sub.status', string='Sub Status')
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    hrs_spent = fields.Float(compute='_get_time', string='Time Spent / Hrs')
    hrs_diff = fields.Char(compute='_get_time', string='Time Spent')
    entry_date = fields.Datetime(string='Entry Date', default=fields.datetime.now())
    attachment = fields. Binary(string='Attachment')
    action_code_id = fields.Many2one('action.code', string='Action Code')

    @api.model
    def create(self, vals):
        res = super(SupportTicketLine, self).create(vals)

# After Import
        if res.ticket_id.stage_id != 'open':
            raise ValidationError('Warning! \n You can create line item only the Task stage is In-Progress.')
        res.is_invisible = True
        if vals.get('sub_status_id'):
            res.ticket_id.sub_status_id = res.sub_status_id.id
        timesheet = self.env['account.analytic.line']
        employee = self.env['hr.employee'].search([('user_id', '=', res.ticket_id.user_id.id)], limit=1)
        if not employee:
            raise ValidationError('Warning! \n %s is not regisered as an Employee.' %(res.ticket_id.user_id.name))
        timesheet.create({
            'project_id': res.ticket_id.project_id.id or False,
            'date': res.from_date or False,
            'name': res.action_taken or "",
            'employee_id': employee.id or False,
            'unit_amount': res.hrs_spent or 0.00,
        })
        return res

    @api.multi
    def write(self, vals):
        res = super(SupportTicketLine, self).write(vals)
        if vals.get('sub_status_id'):
            self.ticket_id.sub_status_id = self.sub_status_id.id
        return res
