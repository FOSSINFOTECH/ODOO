# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
class schedule_calendar(models.Model):
    _name = "schedule.calendar"
    _description = "Schedule Calendar"

    name = fields.Char(string='Name', required=True)
    res_model = fields.Char(string='Model', readonly=True)
    res_id = fields.Integer(string='Record ID', readonly=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    color_partner_id = fields.Integer(related='user_id.partner_id.id', string="colorize", store=False, group_operator='+')  # Color of creator
    active = fields.Boolean(string='Active', default=1, help="If the active field is set to false, it will allow you to hide the event alarm information without removing it.")
    attendee_ids = fields.Many2many('res.partner', 'schedule_partner_rel', 'schedule_id', 'partner_id', string='Attendees')

    @api.multi
    def call_action(self):
        imd = self.env['ir.model.data']
        ctx = {}
        form_view_id = False
        for val in self:
            if val.res_model == 'project.task':
                form_view_id = imd.xmlid_to_res_id('project.view_task_form2')
            elif val.res_model == 'calendar.event':
                form_view_id = imd.xmlid_to_res_id('calendar.view_calendar_event_form')
            elif val.res_model == 'hr.company.holidays':
                form_view_id = imd.xmlid_to_res_id('hr_company_holidays.hr_company_holidays_form')

            if form_view_id:
                result = {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': str(val.res_model),
                    'views': [(form_view_id, 'form')],
                    'view_id': form_view_id,
                    'res_id': val.res_id,
                    'target': 'current',
                    'context': ctx,
                }
                return result


class calendar_event(models.Model):
    _inherit = 'calendar.event'

    schedule_calendar_id = fields.Many2one('schedule.calendar', string='Schedule Calendar')

    @api.model
    def create(self, values):
        create_vals = {}
        schedule_calendar_obj = self.env['schedule.calendar']
        res = super(calendar_event, self).create(values)
        create_vals = {
            'name': 'Meeting: ' + values.get('name', ''),
            'res_model': self._name,
            'start_date': values.get('start_date',  False) or values.get('start_datetime',  False),
            'end_date': values.get('stop_date', False) or values.get('stop_datetime',  False),
            'user_id': values.get('user_id', False),
            'attendee_ids': values.get('partner_ids', False),
            'res_id': res,
            'active': True
        }
        if values.get('name')[:3] != 'HL:':
            schedule_calendar_id = schedule_calendar_obj.create(create_vals)
            values['schedule_calendar_id'] = schedule_calendar_id
            schedule_calendar_obj.write({'res_id': res})
            res.write({'schedule_calendar_id': schedule_calendar_id.id})
        return res

    @api.multi
    def write(self, values):
        res = super(calendar_event, self).write(values)
        if values.get('name', False) or values.get('duration', False) or values.get('start_date', False) or values.get('stop_date', False) or values.get('start_datetime',  False) or values.get('stop_datetime',  False) or values.get('user_id', False) or values.get('partner_ids', False):
            for val in self:
                write_vals = {
                    'name': 'Meeting: ' + val.name,
                    'start_date': val.start_date or val.start_datetime,
                    'end_date': val.stop_date or val.stop_datetime,
                    'user_id': val.user_id.id,
                    'attendee_ids': [[5, val.schedule_calendar_id.id], [6, 0, [i.id for i in val.partner_ids]]],
                    'active': True
                    }
                if val.schedule_calendar_id.id:
                    val.schedule_calendar_id.write(write_vals)
        return res

    @api.multi
    def unlink(self):
        for val in self:
            if val.schedule_calendar_id.id:
                val.schedule_calendar_id.unlink()
        return super(calendar_event, self).unlink()


class Task(models.Model):
    _inherit = 'project.task'

    schedule_calendar_id = fields.Many2one('schedule.calendar', string='Schedule Calendar')
    date_start = fields.Date('Start Date', required="1")
    date_end = fields.Date('End Date', required="1")

    @api.model
    def create(self, values):
        create_vals = {}
        schedule_calendar_obj = self.env['schedule.calendar']
        test=values.get('date_end')     
        res = super(Task, self).create(values)
        res.date_end = test
        user_partner_id = self.env['res.users'].browse(values.get('user_id')).partner_id.id
        if values.get('user_id', False):
            create_vals = {
                'name': 'Task: ' + values.get('name', ''),
                'res_model': self._name,
                'start_date':  values.get('date_start', False),
                'end_date':  res.date_end or False,
                'user_id': values.get('user_id', False),
                'res_id': res,
                'attendee_ids': [(4, user_partner_id)],
                'active': True,
            }
            schedule_calendar_id = schedule_calendar_obj.create(create_vals)
            values['schedule_calendar_id'] = schedule_calendar_id
            schedule_calendar_obj.write({'res_id': res})
            res.write({'schedule_calendar_id': schedule_calendar_id.id})
        return res

    @api.multi
    def write(self, values):
        res = super(Task, self).write(values)
        if values.get('name', False) or values.get('stage_id', False) or values.get('date_start', False) or values.get('date_end', False) or values.get('user_id', False):
            for val in self:
                if val.user_id:
                    write_vals = {
                        'name': 'Task: ' + val.name,
                        'start_date': val.date_start,
                        'end_date': val.date_end,
                        'user_id': val.user_id.id,
                        'attendee_ids': [[5, val.schedule_calendar_id.id], [6, 0, [val.user_id.partner_id.id]]],
                        'active': True,
                        }
                if val.schedule_calendar_id.id:
                    val.schedule_calendar_id.write(write_vals)
        return res

    @api.multi
    def unlink(self):
        for val in self:
            if val.schedule_calendar_id.id:
                val.schedule_calendar_id.unlink()
        return super(Task, self).unlink()

