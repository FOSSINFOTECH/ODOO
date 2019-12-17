# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime, timedelta
from datetime import *
from dateutil.relativedelta import *
import time
from odoo.exceptions import UserError


_TASK_STATE = [('draft', 'New'),
               ('open', 'In Progress'),
               ('pending', 'Pending'),
               ('done', 'Done'),
               ('cancelled', 'Cancelled')
               ]


class Project(models.Model):
    _inherit = 'project.project'

    project_status = fields.Selection(compute='_project_task_status', method=True,
                                      selection=[
                                          ('on_track', 'On Track'),
                                          ('off_track', 'Delayed'),
                                          ('at_risk', 'At Risk'),
                                          ('onhold', 'On Hold'),
                                          ('done', 'Completed'),
                                          ('not_active', 'Not Active'),
                                          ('cancelled', 'Cancelled')
                                      ], string='Project Status', track_visibility='onchange',store=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('close', 'Completed'),
        ('cancelled', 'Cancelled')],
        'Status', copy=False, default='draft', track_visibility='onchange')
    status_color = fields.Integer(compute='_check_color', method=True, string='Colour',store=True)
    projected_date_end = fields.Date(compute='_get_projected_date_end', method=True, string="Projected End Date", store=True, default=time.strftime('%Y-%m-%d'))
    actual_date_start = fields.Date('Actual Starting Date', copy=False)
    actual_date_end = fields.Date('Actual Ending Date', copy=False)
    planned_hours = fields.Float(compute='_hours_get', multi="progress", string='Planned Time', store=True)
    effective_hours = fields.Float(compute='_hours_get', multi="progress", string='Time Spent', store=True)
    total_hours = fields.Float(compute='_hours_get', multi="progress", string='Total Time', store=True)
    progress_rate = fields.Float(compute='_hours_get', multi="progress", string='Progress', group_operator="avg", store=True)
    date_start = fields.Date(string='Start Date', default=fields.Datetime.now().date(), track_visibility='onchange')
    date = fields.Date(string='End Date', index=True, track_visibility='onchange', default=fields.Datetime.now().date())

    @api.depends('state', 'date_start', 'date', 'projected_date_end')
    def _project_task_status(self):
        for val in self:
            project_status = False
            if val.date_start and val.date:
                date_start = val.date_start
                date_end = val.date
                pr_end_date = val.projected_date_end
                today = datetime.now().date()
                if val.state == 'draft':
                    project_status = 'not_active'
                if val.state == 'open':
                    project_status = 'on_track'
                if val.state == 'pending':
                    project_status = 'onhold'
                if val.state == 'open' and today >= (date_end + relativedelta(days=-2)):
                    project_status = 'at_risk'
                if not val.state == 'pending' and datetime.now().date() > date_end:
                    project_status = 'off_track'
                if val.state == 'close':
                    project_status = 'done'
                else:
                    if val.actual_date_start and val.actual_date_end:
                        project_status = 'done'
                    elif val.state == 'cancelled':
                        project_status = 'cancelled'
                    elif (not val.actual_date_start and (date_start > datetime.now().date())):
                        project_status = 'onhold'
                val.project_status = project_status

    @api.depends('project_status')
    def _check_color(self):
        for val in self:
            # project_status = False
            color = 0
            if val.project_status == u'on_track':
                color = 1
            elif val.project_status == u'off_track':
                color = 2
            elif val.project_status == u'at_risk':
                color = 3
            elif val.project_status == u'onhold':
                color = 4
            elif val.project_status == u'done':
                color = 5
            elif val.project_status == u'cancelled':
                color = 6
            elif val.project_status == u'not_active':
                color = 7
            val.status_color = color

    @api.depends('date_start','date')
    def _get_projected_date_end(self):
        for val in self:
            projected_date_end = False
            today = datetime.now().date()
            if val.date and val.date_start:
                diff_days = (val.date - val.date_start).days or 0
                if not val.actual_date_start:
                    if today <= val.date_start:
                        projected_date_end = val.date
                    elif today > val.date_start:
                        projected_date_end = today + timedelta(days=int(diff_days))
                    else:
                        projected_date_end = val.date
                else:
                    if val.state not in ('draft', 'cancelled'):
                        progress = 1 - (val.progress_rate / 100)
                        progress_days = str(int(round(abs(progress * diff_days))))
                        projected_date_end = today + timedelta(days=int(progress_days))
                    else:
                        projected_date_end = val.date
            val.projected_date_end = projected_date_end

    def _check_tasks(self):
        task_br = self.env['project.task']
        task_search = task_br.search([('project_id', '=', self.id)])
        if task_search:
            for task in task_search:
                if task.state not in ('done', 'cancelled', 'pending'):
                    raise UserError('Warning! \n Task - ' + task.name + ' is in ' + task.state + ' state You cannot complete ,cancel or put this on hold this project unless the tasks \n related to this project are completed or cancelled.')
        return True

    @api.onchange('date_start','date')
    def onchange_check_date(self):
        if self.date_start and self.date:
            if self.date_start > self.date:
                raise UserError('Start Date cannot be lesser than End Date')

    def set_cancel(self):
        self._check_tasks()
        self._project_task_status()
        if self.state in 'open':
            self.write({'state': 'cancelled'})

    def start_project(self):
        self._project_task_status()
        self.write({'state': 'open', 'actual_date_start': datetime.now()})

    def set_done(self):
        self._check_tasks()
        self._project_task_status()
        self.write({'state': 'close', 'actual_date_end': datetime.now(), 'project_status': 'done'})

    def set_pending(self):
        self._project_task_status()
        self.write({'state': 'pending'})

    def set_open(self):
        self._project_task_status()
        self.write({'state': 'open'})

    def reset_project(self):
        self._project_task_status()
        self.write({'state': 'open'})

    # set active value for a project, its sub projects and its tasks
    def setActive(self, value=True):
        self._project_task_status()
        task_obj = self.env['project.task']
        for proj in self:
            self.write({'state': value and 'open'})
            self._cr.execute('select id from project_task where project_id=%s', (proj.id,))
            tasks_id = [x[0] for x in self._cr.fetchall()]
            if tasks_id:
                task_obj.write({'active': value})
        return True

    @api.depends('task_ids.planned_hours', 'task_ids.effective_hours')
    def _hours_get(self):
        for project in self:

            for task in project.task_ids:
                project.planned_hours += task.planned_hours
                project.total_hours = project.planned_hours
                for work_time in task.timesheet_ids:
                    project.effective_hours += work_time.unit_amount

                if task.stage_id and task.stage_id.fold:
                    project.progress_rate = 100.0
                elif (project.planned_hours > 0.0):
                    project.progress_rate = round(100.0 * (project.effective_hours) / project.planned_hours, 2)
                else:
                    project.progress_rate = 0.0

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        stage_project_task = self.env['project.task.type']
        stage_project_search = stage_project_task.search([])
        for i in stage_project_search:
            if i.state:
                i.update({
                    'project_ids': [(4, res.id)]
                })
        return res


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    state = fields.Selection(_TASK_STATE, 'Related Status')


class Task(models.Model):
    _inherit = 'project.task'

    def _check_project(self):
        for i in self:
            if i.project_id:
                if i.project_id.state != 'open':
                    raise UserError('Warning! \n Project - ' + i.project_id.name + ' is in ' + i.project_id.state + ' state \n You cannot start this task.')
        return True

    def days_between(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days) + 1

    @api.depends('project_id.state', 'state', 'date_start', 'date_end', 'date_deadline', 'projected_date_end')
    def _get_task_status(self):
        for val in self:
            status = ''
            if val.date_start and val.date_deadline:
                date_start = val.date_start
                date_end = val.date_deadline
                pr_end_date = val.projected_date_end
                today = datetime.now().date()
                if val.state not in ('open', 'pending', 'done'):
                    status = 'not_active'
                if val.state == 'open':
                    status = 'on_track'
                if val.state == 'pending':
                    status = 'onhold'
                if val.state == 'open' and today >= (date_end + relativedelta(days=-2)):
                    status = 'at_risk'
                if not val.state == 'pending' and datetime.now().date() > date_end:
                    status = 'off_track'
                if val.project_id and val.state in ('done'):
                    status = 'done'
                else:
                    if val.actual_date_start and val.actual_date_end:
                        status = 'done'
                    elif val.state == 'cancelled':
                        status = 'cancelled'
                    elif (not val.actual_date_start and (date_start > datetime.now().date())):
                        status = 'onhold'
                val.task_status = status

    @api.depends('task_status')
    def _check_color(self):
        for record in self:
            color = 0
            if record.task_status == u'on_track':
                color = 1
            elif record.task_status == u'off_track':
                color = 2
            elif record.task_status == u'at_risk':
                color = 3
            elif record.task_status == u'onhold':
                color = 4
            elif record.task_status == u'done':
                color = 5
            elif record.task_status == u'cancelled':
                color = 6
            elif record.task_status == u'not_active':
                color = 7
            record.status_color = color

    def write(self, vals):
        if vals.get('stage_id'):
            if self.state in ('done', 'cancelled'):
                raise UserError(('You cannot modify the task which is ' + self.state + ' '))
            vals.update({'state': self.env['project.task.type'].browse(vals.get('stage_id')).state})
        if vals.get('sequence'):
            vals.update({'state': self.stage_id.state})
        if vals.get('state') == 'open':
            vals.update({'actual_date_start': datetime.now()})
        if vals.get('state') == 'done':
            vals.update({'actual_date_end': datetime.now()})
        if vals.get('state') != 'done':
            vals.update({'actual_date_end': False})
        if vals.get('state') == 'draft':
            vals.update({'actual_date_start': False})
        if vals.get('state') == 'done' and not vals.get('actual_date_start'):
            vals.update({'actual_date_start': datetime.now()})
        if vals.get('date_start'):
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if self.project_id.date_start:
                if date_start < self.project_id.date_start:
                    raise UserError(('Task start date cannot be greater than the project starting date (' + str(self.project_id.date_start) + ' )'))
        if vals.get('date_deadline') and self.date_start:
            deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            if deadline < self.date_start:
                raise UserError(('Deadline cannot be lesser than the starting date'))
        if self.date_deadline and vals.get('date_start'):
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if self.date_deadline < date_start:
                raise UserError(('Deadline cannot be lesser than the starting date'))
        if vals.get('date_deadline'):
            if self.project_id.date:
                date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
                prj_end_date = self.project_id.date
                if prj_end_date < date_deadline:
                    raise UserError(('Deadline cannot be greater than the project end date (' + str(self.project_id.date) + ' )'))
        res = super(Task, self).write(vals)
        return res

    @api.depends('date_start','date_deadline')
    def _get_projected_date_end(self):
        for val in self:
            if val.date_deadline and val.date_start:
                projected_date_end = False
                diff_days = 0
                today = datetime.now().date()
                start_date = datetime.strftime(val.date_start, "%Y-%m-%d")
                end_date = datetime.strftime(val.date_deadline, "%Y-%m-%d")
                if val.date_start and val.date_deadline:
                    diff_days = abs(datetime.strptime(start_date, "%Y-%m-%d") - datetime.strptime(end_date, "%Y-%m-%d")).days
                if not val.actual_date_start:
                    if today <= val.date_start:
                        projected_date_end = val.date_deadline
                    elif today > val.date_start and diff_days:
                        projected_date_end = str(today + timedelta(days=int(diff_days)))
                    else:
                        projected_date_end = val.date_deadline
                else:
                    if val.state not in ('draft', 'cancelled'):
                        progress = 1 - (val.progress / 100)
                        progress_days = str(int(round(abs(progress * diff_days))))
                        projected_date_end = today + timedelta(days=int(progress_days))
                    else:
                        projected_date_end = val.date_deadline
                val.projected_date_end = projected_date_end

    def _get_default_stage_id(self):
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', False)]):
            if stage_search:
                raise UserError(('Kindly configure your stages with the related status field'))
        return True

    @api.model
    def create(self, vals):
        if vals.get('date_deadline'):
            date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if date_deadline < date_start:
                qq
                raise UserError(('Deadline cannot be lesser than the starting date'))
        if vals.get('project_id'):
            project_end_date = self.env['project.project'].browse(vals.get('project_id')).date
            if not project_end_date:
                raise UserError('Kindly Fill the Project End Date')
            date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            starting_dt = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if vals.get('date_start'):
                project_starting_date = self.env['project.project'].browse(vals.get('project_id')).date_start
                if project_starting_date > starting_dt:
                    raise UserError(('Task start date cannot be greater than the project starting date (' + str(self.env['project.project'].browse(vals.get('project_id')).date_start) + ')'))
            if project_end_date < date_deadline:
                raise UserError(('Deadline cannot be greater than the project end date (' + str(self.env['project.project'].browse(vals.get('project_id')).date) + ')'))
        return super(Task, self).create(vals)

    def unlink(self):
        for i in self:
            if i.state != 'draft':
                raise UserError('Warning! You cannot delete a created task')
        return super(Task, self).unlink()

    task_status = fields.Selection(compute='_get_task_status', method=True,
                                   selection=[
                                       ('on_track', 'On Track'),
                                       ('off_track', 'Delayed'),
                                       ('onhold', 'On Hold'),
                                       ('at_risk', 'At Risk'),
                                       ('future', 'Future'),
                                       ('done', 'Completed'),
                                       ('cancelled', 'Cancelled'),
                                       ('new', 'New'),
                                       ('not_active', 'Not Active')
                                   ], string='Task Status', track_visibility='onchange',store=True)
    status_color = fields.Integer(compute='_check_color', string='Colour', method=True,store=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled')], string="Status", readonly=False, store=True,
        help='The status is set to \'Draft\', when a case is created.\
                      If the case is in progress the status is set to \'Open\'.\
                      When the case is over, the status is set to \'Done\'.\
                      If the case needs to be reviewed then the status is \
                      set to \'Pending\'.', default='draft')
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
                               default=_get_default_stage_id,
                               group_expand='_read_group_stage_ids',
                               domain="[('project_ids', '=', project_id)]", copy=False)
    date_start = fields.Date('Starting Date', copy=False, track_visibility='onchange', default=fields.Datetime.now().date())
    projected_date_end = fields.Date(compute='_get_projected_date_end', method=True, string="Projected End Date", store=True)
    actual_date_start = fields.Date('Actual Starting Date', copy=False)
    actual_date_end = fields.Date('Actual Ending Date', copy=False)
    progress_status = fields.Boolean('Progress Status', copy=False)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, track_visibility='onchange', default=time.strftime('%Y-%m-%d'))

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_start = fields.Datetime.now().date()

    @api.onchange('date_start','date_deadline')
    def onchange_check_date(self):
        if self.date_start and self.date_deadline:
            if self.date_start > self.date_deadline:
                raise UserError('Start Date cannot be lesser than deadline')

    def start_task(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', 'open')]):
            self.write({'stage_id': stage_search.id, 'state': 'open', 'actual_date_start': datetime.now()})

    def set_open(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', 'open')]):
            self.write({'stage_id': stage_search.id, 'state': 'open'})

    def set_done(self):
        self._check_project()
        if self.state == 'draft':
            raise UserError(('You cannot completed the task if the task has not been started'))
        stage_obj = self.env['project.task.type'].search([('state', '=', 'done')])
        for stage_search in stage_obj.search([('state', '=', 'done')]):
            self.write({'stage_id': stage_search.id, 'state': 'done', 'actual_date_end': datetime.now()})

    def set_cancel(self):
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', 'cancelled')]):
            self.write({'stage_id': stage_search.id, 'state': 'cancelled'})

    def set_pending(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', 'pending')]):
            self.write({'stage_id': stage_search.id, 'state': 'pending'})
