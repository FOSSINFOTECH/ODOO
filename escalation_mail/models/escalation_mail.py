# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError


class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    def cron_do_task(self):
        context = dict(self._context or {})
        project_task = self.env['project.task']
        stage_ids = self.env['project.task.type'].search(['|',('state','=', 'draft'),('state','=', 'open')])
        for user in self.env['res.users'].search([]):
            list1 = []
            prj_manager = self.env['project.project'].search([('user_id', '=', user.id)])
            for project_id in prj_manager:
                prj_search = project_task.search([('project_id', '=', project_id.id),('stage_id.state', 'in', ('draft', 'open') )])
                for project in prj_search:
                    if project.date_deadline:
                        date_deadline = datetime.strptime(project.date_deadline, '%Y-%m-%d').date()
                        if datetime.now().date() > date_deadline:
                            list1.append({'Manager':user.name,'usr_name': project.user_id.name,'task_name': project.name,'pro_name': project.project_id.name, 'date_dead': date_deadline, 'date_ass': project.date_assign})
            if list1:
                # -------------Sending Mails to Respective Project Managers
                ir_model_data = self.env['ir.model.data']
                context.update({'closed_list': list1,'manager':user.name,'email_to_user': user.partner_id.email, 'email_subject': 'Delayed Tasks'})
                template_id = ir_model_data.get_object_reference('escalation_mail', 'email_template_escalation_project_task_mail')[1]
                try:
                    mail_send = self.env['mail.template'].browse(template_id).with_context(context).send_mail(self.id, True)
                except Exception as e:
                    print(e,"============ Failed")
        return True


    @api.model
    def create(self,vals):
        if vals.get('date_deadline'):
            date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            if date_deadline < datetime.now().date():
                raise UserError(('Deadline cannot be lesser than the current date'))
        return super(Task, self).create(vals)

    @api.multi
    def write(self,vals):
        if vals.get('date_deadline'):
            date_deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            if date_deadline < datetime.now().date():
                raise UserError(('Deadline cannot be lesser than the current date'))
        return super(Task, self).write(vals)




class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('close', 'Completed'),
        ('cancelled', 'Cancelled')],
        'Related Status', copy=False, default='draft', track_visibility='onchange')


