# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class css_order(models.Model):
    _name = 'css.order'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='CSS', default='/')
    search_no = fields.Char(string='Search Mobile No')
    partner_id = fields.Many2one('res.partner', string="Customer Name", track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('done', 'Done')], default='draft', track_visibility='always')
    css_line = fields.One2many('css.order.line', 'css_id', string="CSS Line")

    @api.model
    def create(self, vals):
        res = super(css_order, self).create(vals)
        if vals.get('name', '/') == '/':
            res['name'] = self.env['ir.sequence'].next_by_code('css.order') or '/'
        if vals.get('search_no') == '/':
            if vals.get('partner_id'):
                res_partner_search = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
                if not vals.get('mobile'):
                    vals['mobile'] = res_partner_search.mobile
                if res_partner_search.phone or res_partner_search.mobile:
                    vals['search_no'] = res_partner_search.phone or res_partner_search.mobile
        return res

    # This function fetches the customer name when the contact number of the customer is entered.
    @api.multi
    @api.onchange('search_no')
    def onchange_search_phone(self):
        res = {}
        res_domain = {}
        if self.search_no == '-':
            res['partner_id'] = False
        elif self.search_no != '+91':
            partner_obj = self.env['res.partner']
            part_ids = partner_obj.search([
                '|', '|', '|',
                ('phone', 'ilike', self.search_no),
                ('mobile', 'ilike', self.search_no),
                ('parent_id.phone', 'ilike', self.search_no),
                ('parent_id.mobile', 'ilike', self.search_no),
            ])
            if part_ids:
                company_ids = []
                for p_id in part_ids:
                    if (not p_id.is_company) and p_id.parent_id:
                        company_ids.append(p_id.parent_id.id)
                    else:
                        company_ids.append(p_id.id)
                res_domain['partner_id'] = [('id', 'in', list(set(company_ids)))]
                if len(list(set(company_ids))) == 1:
                    res['partner_id'] = list(set(company_ids))[0]
                else:
                    res['partner_id'] = False
        return {'value': res, 'domain': res_domain}

    # when the call is done you can not delete it.
    @api.multi
    def unlink(self):
        for order in self:
            if order.state == 'done':
                raise UserError('Warning! You cannot delete this call when it is done')
        return super(css_order, self).unlink()

    # This function fetches all the products(which are stockable)from the delivery order bought by the customer.
    @api.multi
    @api.onchange('partner_id')
    def partner_id_onchange(self):
        stock_obj = self.env['stock.move']
        search_partner = stock_obj.search([('partner_id', '=', self.partner_id.id), ('state', '=', 'done')])
        pro_list = []
        if self.partner_id and search_partner:
            for line in search_partner:
                for stock in line.move_line_ids:
                    if stock.product_id.type == 'service' or stock.product_id.type == 'product':
                        for range_type in range(0, int(line.product_uom_qty)):
                            vals = {}
                            vals.update({
                                'product_id': stock.move_id.product_id,
                                'lot_id': stock.lot_id.id
                            })
                            pro_list.append((0, 0, vals))
                self.update({'css_line': pro_list})
        else:
            self.update({'css_line': pro_list})
        self.check_service_ticket()

    @api.multi
    def check_service_ticket(self):
        claim_obj = self.env['crm.claim']
        claim_search = []
        for line in self.css_line:
            claim_search = claim_obj.search(
                [
                    ('partner_id', '=', self.partner_id.id),
                    ('product_id', '=', line.product_id.id),
                    ('state', 'in', ('draft', 'inprogress'))
                ])
        if claim_search:
            for claim in claim_search:
                for line in self.css_line:
                    if line.product_id.id == claim.product_id.id:
                        line.claim_id = claim.name

        return claim_search


class css_order_line(models.Model):
    _name = 'css.order.line'
    _description = 'task'

    css_id = fields.Many2one('css.order')
    name = fields.Char(string='Reference', default='/')
    product_id = fields.Many2one('product.product', string="Product")
    partner_id = fields.Many2one(related='css_id.partner_id', string='Customer')
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('done', 'Done')], default='draft')
    lot_id = fields.Many2one('stock.production.lot', string='Serial Number')
    claim_id = fields.Char(string='Service Ticket')

    # The function creates service ticket
    @api.multi
    def create_ticket(self, context):
        # res_address = self.partner_id.street + self.partner_id.city or '' + self.partner_id.zip or '' + self.partner_id.state_id

        if self.css_id.state == 'done':
            raise UserError(_('Call is Already Done, Kindly create new call.'))
        context.update({
            'default_partner_id': self.partner_id and self.partner_id.id or False,
            'default_product_id': self.product_id and self.product_id.id or False,
            'default_history_line_id': self.id or False,
            'partner_css_order_line_id': self.id,  # This id for update current in history line
            'default_css_order_line_id': self.id,  # This id for update current in history line
            'default_css_order_id': self.css_id.id or False,
            'default_lot_id': self.lot_id.id or False,
        })
        view_ref = self.env.ref('css_support.crm_case_claims_form_view')
        view_id = view_ref and view_ref.id or False,
        return {
            'type': 'ir.actions.act_window',
            'name': ('Service Ticket'),
            'res_model': 'crm.claim',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'context': context,
        }

    # This function is to view the service ticket which is already created.
    @api.multi
    def view_ticket(self):
        action = self.env.ref('css_support.action_service').read()[0]
        if self.claim_id:
            claim = self.env['crm.claim'].search([('name', '=', self.claim_id)])
            action['domain'] = str("[('id', '=', " + str(claim.id) + ")]")
        else:
            action['domain'] = str("[('history_line_id', '=', " + str(self.id) + ")]")
            action['context'] = {
                'default_history_line_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_product_id': self.product_id.id,
                'default_css_order_id': self.css_id.id
            }
        return action

    # sequence
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('css.order.line') or '/'
        return super(css_order_line, self).create(vals)


class crm_claim(models.Model):
    _name = 'crm.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='Service ticket', default='/')
    history_line_id = fields.Many2one('css.order.line', string="Product Reference")
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Date(string="Ticket Date")
    user_id = fields.Many2one('res.users', string="Service Engineer")
    lot_id = fields.Many2one('stock.production.lot', string='Serial Number')
    state = fields.Selection([('draft', 'New'), ('inprogress', 'In Progress'), ('done', 'Closed'), ('cancel', 'Cancelled')], default='draft')
    css_order_id = fields.Many2one('css.order', string='CSS Reference')

    # cancels the ticket
    @api.multi
    def cancel_ticket(self, vals):
        task_stage_inprogress_id = self.env['project.task.type'].search([('state', '=', 'draft')], limit=1)
        pro_task = self.env['project.task'].search([('service_id', '=', self.id), ('stage_id', '=', task_stage_inprogress_id.id)])
        task_stage_id = self.env['project.task.type'].search([('state', '=', 'cancelled')], limit=1)
        for task in pro_task:
            if task_stage_id:
                task.write({'stage_id': task_stage_id.id})
                task._cr.commit()
        self.write({'state': 'cancel'})
        return True

    # resets to draft
    @api.multi
    def reset(self, vals):
        self.write({'state': 'draft', 'date': datetime.now()})
        return True

    # Functions closes the service ticket and sends a mail to the service engineer regarding the completion of the visit.
    @api.multi
    def close_ticket(self, vals):
        task_stage_inprogress_id = self.env['project.task.type'].search([('state', '=', 'draft')], limit=1)
        pro_task = self.env['project.task'].search([('service_id', '=', self.id), ('stage_id', '=', task_stage_inprogress_id.id)])
        task_stage_id = self.env['project.task.type'].search([('state', '=', 'done')], limit=1)
        for task in pro_task:
            if task_stage_id:
                task.write({'stage_id': task_stage_id.id})
                task._cr.commit()
        self.write({'state': 'done'})
        service_tick_list = []
        service_tick_list.append({
            'name': self.name,
            'partner_id': self.partner_id,
            'product_id': self.product_id,
            'user_id': self.user_id
        })
        context = ({
            'email_to': self.user_id.email,
            'name': self.user_id.name,
            'today_list': service_tick_list
        })
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('css_support', 'email_template_edi_support_service_ticket')[1]
        except ValueError:
            template_id = False
        if template_id:
            self.env['mail.template'].browse(template_id).with_context(context).send_mail(self.id, True)
        return True

    # get_visits to view the visits(Task) for the service ticket.
    @api.multi
    def get_visits(self):
        action = self.env.ref('project.action_view_task').read()[0]
        action['domain'] = str("[('service_id','='," + str(self.id) + ")]")
        action['context'] = {
            'default_name': self.name,
            'default_service_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_product_id': self.product_id.id,
            'default_pro_refer': self.history_line_id.name
        }
        return action

    # creates a service ticket and also a visit.
    @api.model
    def create(self, vals):
        if vals.get('name', '/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.claim') or '/'
        res = super(crm_claim, self).create(vals)
        if res.history_line_id:
            res.history_line_id.write({'claim_id': res.name})
        res.write({'date': datetime.now()})
        return res

    @api.multi
    def action_confirm(self):
        if not self.user_id:
            raise UserError('Warning! Kindly map the service enginner to confirm the serivce ticket')
        self.write({'state': 'inprogress'})
        if self.state == 'inprogress':
            self.css_order_id.write({'state': 'open'})

        project_obj = self.env['project.project']
        project_id = project_obj.search([('service_id', '!=', False)], limit=1)
        if not project_id:
            prj_vals = {}
            prj_vals.update({
                'name': 'Service Visit',
                'alias_contact': 'everyone',
                'service_id': self.id,
            })
            project_id = project_obj.create(prj_vals)
            stage_project_search = self.env['project.task.type'].search([])
            for stage in stage_project_search:
                stage.update({'project_ids': (4, project_id.id)})
        vals = {}
        task_obj = self.env['project.task']
        if project_id:
            if self.name:
                vals.update({
                    'name': self.name,
                    'partner_id': self.partner_id.id,
                    'product_id': self.product_id.id,
                    'user_id': self.user_id.id,
                    'service_id': self.id,
                    'pro_refer': self.history_line_id.name,
                    'project_id': project_id.id,
                })
        if vals:
            task_obj.create(vals)
        return True

    # The call will be done if the all tickets are closed.
    @api.multi
    def write(self, vals):
        draft_state = []
        res = super(crm_claim, self).write(vals)
        claim_search = self.search([('history_line_id', "in", self.sudo().css_order_id.css_line.ids)])
        for claim in claim_search:
            if claim.state == 'draft' or claim.state == 'inprogress':
                draft_state.append('True')
            else:
                draft_state.append('False')
        if 'True' in draft_state:
            pass
        else:
            self.css_order_id.sudo().write({'state': 'done'})
        return res

    # shows a warning when you delete a service ticket which is in progress or completed.
    @api.multi
    def unlink(self):
        for stage in self:
            if stage.state == 'inprogress' or stage.state == 'done':
                raise UserError('Warning! You cannot delete a service ticket, Try cancelling it.')
        return super(crm_claim, self).unlink()


class Picking(models.Model):
    _inherit = 'stock.picking'

    partner_id = fields.Many2one('res.partner', string='Partner')


class Task(models.Model):
    _inherit = 'project.task'

    service_id = fields.Many2one('crm.claim', string='Service Ticket')
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Char(string='Serial Number')
    pro_refer = fields.Char(string='Product Reference')

    # shows a warning when you delete created visits or tasks.
    @api.multi
    def unlink(self):
        for task in self:
            if task.service_id:
                raise UserError('Warning! You cannot delete created tasks')
        return super(Task, self).unlink()


class Project(models.Model):
    _inherit = 'project.project'

    service_id = fields.Many2one('crm.claim', string='service ticket ID')


class project_task_type(models.Model):
    _inherit = 'project.task.type'

    state = fields.Selection([('draft', 'New'), ('inprogress', 'In-Progress'), ('done', 'Completed'), ('cancelled', 'Cancelled')], string='Related Status', default='draft', required=True)
