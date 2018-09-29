# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError
import time
from datetime import datetime, timedelta
import dateutil.relativedelta as relativedelta


class crm_commission(models.Model):
    _name = 'crm.commission'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.multi
    def _commssion_manager(self):
        if self.env.user.has_group('commissioning_crm.group_crm_commissioning_manager'):
            self.is_manager = True
        else:
            self.is_manager = False

    name = fields.Char(string="Reference No.", size=256, default='/')
    partner_id = fields.Many2one('res.partner', string="Customer")
    product_id = fields.Many2one('product.product', string="Product")
    lot_id = fields.Many2one('stock.production.lot', string="Serial Number")
    user_id = fields.Many2one('res.users', string="Service Engineer")
    mobile = fields.Char(string='Mobile')
    state = fields.Selection([('unassigned', 'Un-Assigned'), ('inprogress', 'In-Progress'), ('done', 'Completed'), ('cancel', 'Cancelled'), ('failed', 'Failed')], default='unassigned')
    date = fields.Datetime(string='Commissioning Date')
    commission_id = fields.Char(string='Commissioning ID')
    sale_id = fields.Many2one('sale.order', string='Source Document')
    picking_id = fields.Many2one('stock.picking', string='Delivery Order')
    is_manager = fields.Boolean(compute='_commssion_manager', string='Commission Manager')
    is_direct = fields.Boolean(string='Direct Commission')
    failed_reason = fields.Char(string="Failed Reason")

    # when the commissioning is once confimred, a visit will be created.
    @api.multi
    def button_confirm(self):
        if not self.user_id:
            raise UserError('Warning! Kindly map the service enginner to confirm the commission')
        self.write({'state': 'inprogress'})
        project_obj = self.env['project.project']
        project_id = project_obj.search([('commission_id', '!=', False)], limit=1)
        if not project_id:
            prj_vals = {}
            prj_vals.update({
                'name': 'Commissioning',
                'alias_contact': 'everyone',
                'commission_id': self.id,
            })
            project_id = project_obj.create(prj_vals)
            stage_project_search = self.env['project.task.type'].search([])
            for stage in stage_project_search:
                stage.update({'project_ids': (4, project_id.id)})
        vals = {}
        vals.update({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'product_id': self.product_id.id,
            'user_id': self.user_id.id,
            'commission_id': self.id,
            'project_id': project_id.id,
        })
        self.env['project.task'].create(vals)
        return True

    # Buttons displays visits for the comissioning.
    @api.multi
    def get_visits(self):
        project_commissioning_id = self.env['project.project'].search([('commission_id', '!=', False)])
        action = self.env.ref('project.action_view_task').read()[0]
        action['domain'] = str("[('commission_id','='," + str(self.id) + ")]")
        action['context'] = {
            'default_name': self.name,
            'default_commission_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_product_id': self.product_id.id,
            'default_mobile': self.mobile,
            'default_project_id': project_commissioning_id.id
        }
        return action

    # sequence
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.commission') or '/'
        res = super(crm_commission, self).create(vals)
        return res

    # onchange to contact number
    @api.multi
    @api.onchange('partner_id')
    def partner_onchange(self):
        if self.partner_id:
            self.mobile = self.partner_id.phone

    # cancels commisioning
    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})

    # completes the commissioning, mail notification will be sent to service enginner.
    @api.multi
    def button_complete(self):
        context = dict(self._context or {})
        self.write({'state': 'inprogress'})
        com_list = []
        for record in self:
            com_list.append({'name': record.name, 'partner_id': record.partner_id, 'mobile': record.mobile, 'product_id': record.product_id, 'user_id': record.user_id})
        context = ({'email_to': self.user_id.email, 'name': self.user_id.name, 'today_list': com_list})
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('commissioning_crm', 'email_template_edi_com_task')[1]
        except ValueError:
            template_id = False
        if template_id:
            mail_id = self.env['mail.template'].browse(template_id).with_context(context).send_mail(self.id, True)
        task_search = self.env['project.task'].search([('commission_id', '=', self.id)])
        if task_search:  # to move related task to done state automatically when commission is completed.
            for task in task_search:
                task.stage_id = self.env['project.task.type'].search([('state', '=', 'done')], limit=1).id
        self.write({'state': 'done', 'date': datetime.now()})
        return True

    # Reset button
    @api.multi
    def button_reset(self):
        if self.state == 'failed' or self.state == 'cancel':
            self.write({'state': 'inprogress', 'date': False, 'warranty_status': False, 'failed_reason': False})

    # You cannot delete when the commissioning goes into done state.
    @api.multi
    def unlink(self):
        for stage in self:
            if stage.state == 'done':
                raise UserError('Warning! You cannot delete this commissioning if its Completed')
        return super(crm_commission, self).unlink()


class Project(models.Model):
    _inherit = 'project.project'

    commission_id = fields.Many2one('crm.commission', string='Commission ID')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    commission_ok = fields.Boolean(string='Can be Commissioned')


class Task(models.Model):
    _inherit = 'project.task'

    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    commission_id = fields.Many2one('crm.commission', string='Commissioning ID')

    @api.multi
    def write(self, vals):
        if self.commission_id:
            if self.commission_id.state == 'done' or self.commission_id.state == 'failed':
                raise UserError('Warning! This commissioning is in progress, failed or completed')
        return super(Task, self).write(vals)


class Picking(models.Model):
    _inherit = 'stock.picking'

    # This creates commission based on the done quantities.
    @api.multi
    def button_validate(self):
        com_obj = self.env['crm.commission']
        com_obj_search = com_obj.search([('picking_id', '=', self.id)])
        sale_id_search = self.env['sale.order'].search([('name', '=', self.origin)])
        for line in self.move_lines:
            for stock in line.move_line_ids:
                if stock.product_id.commission_ok:
                    if line.quantity_done:
                        qty_range = int(line.quantity_done)
                        if len(com_obj_search):
                            qty_range = qty_range - len(com_obj_search)
                        for stck in range(qty_range):
                            vals = {}
                            vals.update({
                                'partner_id': self.partner_id.id,
                                'mobile': self.partner_id.phone,
                                'lot_id': stock.lot_id.id,
                                'product_id': stock.product_id.id,
                                'sale_id': sale_id_search.id,
                                'picking_id': self.id,
                                'is_direct': True
                            })
                            vals['name'] = self.env['ir.sequence'].next_by_code('crm.commission') or '/'
                            com_obj.create(vals)
            res = super(Picking, self).button_validate()
        return res


class project_task_type(models.Model):
    _inherit = 'project.task.type'

    state = fields.Selection([('draft', 'New'), ('inprogress', 'In-Progress'), ('done', 'Completed'), ('cancelled', 'Cancelled')], string='Related Status', default='draft', required=True)
