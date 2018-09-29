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


class project_project(models.Model):
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
                                      ], string='Project Status', track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('close', 'Completed'),
        ('cancelled', 'Cancelled')],
        'Status', copy=False, default='draft', track_visibility='onchange')
    status_color = fields.Integer(compute='_check_color', method=True, string='Colour')
    projected_date_end = fields.Date(compute='_get_projected_date_end', method=True, string="Projected End Date", store=False, default=time.strftime('%Y-%m-%d'))
    actual_date_start = fields.Date('Actual Starting Date', copy=False)
    actual_date_end = fields.Date('Actual Ending Date', copy=False)
    planned_hours = fields.Float(compute='_hours_get', multi="progress", string='Planned Time', store=False)
    effective_hours = fields.Float(compute='_hours_get', multi="progress", string='Time Spent', store=False)
    total_hours = fields.Float(compute='_hours_get', multi="progress", string='Total Time', store=False)
    progress_rate = fields.Float(compute='_hours_get', multi="progress", string='Progress', group_operator="avg", store=False)
    date_start = fields.Date(string='Start Date', default=time.strftime('%Y-%m-%d'), track_visibility='onchange')
    date = fields.Date(string='End Date', index=True, track_visibility='onchange', default=time.strftime('%Y-%m-%d'))

    @api.multi
    @api.depends('state', 'date_start', 'date', 'projected_date_end')
    def _project_task_status(self):
        for val in self:
            project_status = ''
            if val.date_start and val.date:
                date_start = val.date_start[:10]
                date_end = val.date[:10]
                pr_end_date = val.projected_date_end[:10]
                today = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
                if val.state == 'draft':
                    project_status = 'not_active'
                if val.state == 'open':
                    project_status = 'on_track'
                if val.state == 'pending':
                    project_status = 'onhold'
                if val.state == 'open' and today >= ((datetime.strptime(date_end, "%Y-%m-%d")) + relativedelta(days=-2)):
                    project_status = 'at_risk'
                if not val.state == 'pending' and datetime.now().strftime("%Y-%m-%d") > date_end:
                    project_status = 'off_track'
                if val.state == 'close':
                    project_status = 'done'
                else:
                    if val.actual_date_start and val.actual_date_end:
                        project_status = 'done'
                    elif val.state == 'cancelled':
                        project_status = 'cancelled'
                    elif (not val.actual_date_start and (date_start > datetime.now().strftime('%Y-%m-%d'))):
                        project_status = 'onhold'
                val.project_status = project_status
    @api.multi
    @api.depends('project_status')
    def _check_color(self):
        for val in self:
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

    @api.multi
    def _get_projected_date_end(self):
        for val in self:
            projected_date_end = False
            today = time.strftime("%Y-%m-%d")
            if val.date and val.date_start:
                diff_days = abs(datetime.strptime(val.date, "%Y-%m-%d") - datetime.strptime(val.date_start, "%Y-%m-%d")).days or 0
                if not val.actual_date_start:
                    if today <= val.date_start:
                        projected_date_end = val.date
                    elif today > val.date_start:
                        projected_date_end = str(datetime.strptime(today, "%Y-%m-%d") + timedelta(days=int(diff_days)))[:10]
                    else:
                        projected_date_end = val.date
                else:
                    if val.state not in ('draft', 'cancelled'):
                        progress = 1 - (val.progress_rate / 100)
                        progress_days = str(int(round(abs(progress * diff_days))))
                        projected_date_end = str(datetime.strptime(today, "%Y-%m-%d") + timedelta(days=int(progress_days)))[:10]
                    else:
                        projected_date_end = val.date
            val.projected_date_end = projected_date_end

    def _check_tasks(self):
        task_br = self.env['project.task']
        task_search = task_br.search([('project_id', '=', self.id)])
        if task_search:
            for task in task_search:
                if task.state not in ('done', 'cancelled','pending'):
                    raise UserError('Warning! \n Task - ' + task.name + ' is in ' + task.state + ' state You cannot complete ,cancel or put this on hold this project unless the tasks \n related to this project are completed or cancelled.')
        return True

    @api.multi
    def set_cancel(self):
        self._check_tasks()
        self._project_task_status()
        if self.state in 'open':
            self.write({'state': 'cancelled'})

    @api.multi
    def start_project(self):
        self._project_task_status()
        self.write({'state': 'open', 'actual_date_start': datetime.now()})

    @api.multi
    def set_done(self):
        self._check_tasks()
        self._project_task_status()
        self.write({'state': 'close', 'actual_date_end': datetime.now(), 'project_status':'done'})

    @api.multi
    def set_pending(self):
        self._project_task_status()
        self.write({'state': 'pending'})

    @api.multi
    def set_open(self):
        self._project_task_status()
        self.write({'state': 'open'})

    @api.multi
    def reset_project(self):
        self._project_task_status()
        self.write({'state':'open'})

    # set active value for a project, its sub projects and its tasks
    @api.multi
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
        stage_project_task = self.env['project.task.type']
        stage_project_search = stage_project_task.search([])
        res = super(project_project, self).create(vals)
        for i in stage_project_search:
            if i.state:
                i.update({'project_ids': (4, res.id)})
        return res


class project_task_type(models.Model):
    _inherit = 'project.task.type'

    state = fields.Selection(_TASK_STATE, 'Related Status', required=True)


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
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

    @api.multi
    @api.depends('project_id.state', 'state', 'date_start', 'date_end', 'date_deadline', 'projected_date_end')
    def _get_task_status(self):
        for val in self:
            status = ''
            if val.date_start and val.date_deadline:
                date_start = val.date_start[:10]
                date_end = val.date_deadline[:10]
                pr_end_date = val.projected_date_end[:10]
                today = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
                if val.state not in ('open', 'pending', 'done'):
                    status = 'not_active'
                if val.state == 'open':
                    status = 'on_track'
                if val.state == 'pending':
                    status = 'onhold'
                if val.state == 'open' and today >= ((datetime.strptime(date_end, "%Y-%m-%d")) + relativedelta(days=-2)):
                    status = 'at_risk'
                if not val.state == 'pending' and datetime.now().strftime("%Y-%m-%d") > date_end:
                    status = 'off_track'
                if val.project_id and val.state in ('done'):
                    status = 'done'
                else:
                    if val.actual_date_start and val.actual_date_end:
                        status = 'done'
                    elif val.state == 'cancelled':
                        status = 'cancelled'
                    elif (not val.actual_date_start and (date_start > datetime.now().strftime('%Y-%m-%d'))):
                        status = 'onhold'
                val.task_status = status

    @api.multi
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

    @api.multi
    def write(self, vals):
        if vals.get('stage_id'):
            if self.state in ('done','cancelled'):
                raise UserError(('You cannot modify the task which is '+ self.state +' '))
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
        if self.date_deadline and self.date_start:
            date_deadline = datetime.strptime(self.date_deadline, '%Y-%m-%d').date()
            date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()
            if date_deadline < date_start:
                raise UserError(('Deadline cannot be lesser than the starting date'))
        if self.date_deadline and vals.get('date_start'):
            date_deadline = datetime.strptime(self.date_deadline, '%Y-%m-%d').date()
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if date_deadline < date_start:
                raise UserError(('Deadline cannot be lesser than the starting date'))
        if vals.get('date_deadline'):
            date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            prj_end_date = datetime.strptime(self.project_id.date, '%Y-%m-%d').date()
            if prj_end_date < date_deadline:
                raise UserError(('Deadline cannot be greater than the project end date'))

        res = super(Task, self).write(vals)
        return res

    @api.multi
    def _get_projected_date_end(self):
        for val in self:
            if val.date_deadline and val.date_start:
                projected_date_end = False
                diff_days = 0
                today = time.strftime("%Y-%m-%d")
                start_date = datetime.strftime(datetime.strptime(val.date_start, "%Y-%m-%d"), "%Y-%m-%d")
                end_date = datetime.strftime(datetime.strptime(val.date_deadline, "%Y-%m-%d"), "%Y-%m-%d")
                if val.date_start and val.date_deadline:
                    diff_days = abs(datetime.strptime(start_date, "%Y-%m-%d") - datetime.strptime(end_date, "%Y-%m-%d")).days
                if not val.actual_date_start:
                    if today <= val.date_start:
                        projected_date_end = val.date_deadline
                    elif today > val.date_start and diff_days:
                        projected_date_end = str(datetime.strptime(today, "%Y-%m-%d") + timedelta(days=int(diff_days)))[:10]
                    else:
                        projected_date_end = val.date_deadline
                else:
                    if val.state not in ('draft', 'cancelled'):
                        progress = 1 - (val.progress / 100)
                        progress_days = str(int(round(abs(progress * diff_days))))
                        projected_date_end = str(datetime.strptime(today, "%Y-%m-%d") + timedelta(days=int(progress_days)))[:10]
                    else:
                        projected_date_end = val.date_deadline
                val.projected_date_end = projected_date_end

    @api.multi
    def _get_default_stage_id(self):
        stage_obj = self.env['project.task.type']
        stage_search = stage_obj.search([('state','=','draft')])
        if len(stage_search) > 1:
            raise UserError(('Kindly map the stages to create your task'))
        return stage_search.id

    @api.model
    def create(self,vals):
        if vals.get('date_deadline'):
            date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if date_deadline < date_start:
                raise UserError(('Deadline cannot be lesser than the starting date'))
        if vals.get('project_id'):
            prj_end_date = datetime.strptime(self.env['project.project'].browse(vals.get('project_id')).date, '%Y-%m-%d').date()
            if prj_end_date < date_deadline:
                raise UserError(('Deadline cannot be greater than the project end date'))

        return super(Task, self).create(vals)


    @api.multi
    def unlink(self):
        for i in self:
            if i.state:
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
                                   ], string='Task Status', track_visibility='onchange')
    status_color = fields.Integer(compute='_check_color', string='Colour', method=True)
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
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               domain="[('project_ids', '=', project_id)]", copy=False)
    date_start = fields.Date('Starting Date', copy=False, track_visibility='onchange', default=time.strftime('%Y-%m-%d'))
    projected_date_end = fields.Date(compute='_get_projected_date_end', method=True, string="Projected End Date", store=False)
    actual_date_start = fields.Date('Actual Starting Date', copy=False)
    actual_date_end = fields.Date('Actual Ending Date', copy=False)
    progress_status = fields.Boolean('Progress Status', copy=False)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, track_visibility='onchange', default=time.strftime('%Y-%m-%d'))

    @api.multi
    def start_task(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        stage_search = stage_obj.search([('state', '=', 'open')])
        self.write({'stage_id': stage_search.id, 'state': 'open', 'actual_date_start': datetime.now()})

    @api.multi
    def set_open(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        stage_search = stage_obj.search([('state', '=', 'open')])
        if stage_search:
            self.write({'stage_id': stage_search.id, 'state': 'open'})

    @api.multi
    def set_done(self):
        self._check_project()
        if self.state == 'draft':
            raise UserError(('You cannot completed the task if the task has not been started'))
        stage_obj = self.env['project.task.type']
        stage_search = stage_obj.search([('state', '=', 'done')])
        if stage_search:
            self.write({'stage_id': stage_search.id, 'state': 'done', 'actual_date_end': datetime.now()})


    @api.multi
    def set_cancel(self):
        stage_obj = self.env['project.task.type']
        stage_search = stage_obj.search([('state', '=', 'cancelled')])
        if stage_search:
            self.write({'stage_id': stage_search.id, 'state': 'cancelled'})

    @api.multi
    def set_pending(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        stage_search = stage_obj.search([('state', '=', 'pending')])
        if stage_search:
            self.write({'stage_id': stage_search.id, 'state': 'pending'})
