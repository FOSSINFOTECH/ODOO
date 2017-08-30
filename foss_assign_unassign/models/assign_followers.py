# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AssignFollowersSettings(models.Model):
    _name = 'assign.followers.settings'
    _description = 'Settings for Assigning followers to a Record'

    name = fields.Char('Name', size=128)
    model_id = fields.Many2one('ir.model', 'Model')
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', string='Sidebar action', readonly=True, help="Sidebar action to make this template available on records of the related document model")
    ref_ir_value = fields.Many2one('ir.values', string='Sidebar Button', readonly=True, help="Sidebar button to open the sidebar action")

    @api.multi
    def create_action(self):
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        data_obj = self.env['ir.model.data']
        for template in self:
            src_obj = template.model_id.model
            model_data_id = data_obj._get_id('foss_assign_unassign', 'view_assign_followers')
            res_id = data_obj.browse(model_data_id).res_id
            button_name = _('Assign/Unassign Followers')
            vals['ref_ir_act_window'] = action_obj.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'assign.followers',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{}",
                'view_mode': 'form,tree',
                'view_id': res_id,
                'target': 'new',
                'auto_refresh': 1
            }).id
            vals['ref_ir_value'] = self.env['ir.values'].create({
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
                'object': True,
            }).id
        self.write(dict(ref_ir_act_window=vals.get('ref_ir_act_window', False), ref_ir_value=vals.get('ref_ir_value', False)))
        return True

    def unlink_action(self):
        for template in self:
            try:
                if template.ref_ir_act_window:
                    self.env['ir.actions.act_window'].unlink(template.ref_ir_act_window.id)
                if template.ref_ir_value:
                    ir_values_obj = self.env['ir.values']
                    ir_values_obj.unlink(template.ref_ir_value.id)
            except Exception:
                raise ValidationError(_("Warning \n Deletion of the action record failed."))
        return True

AssignFollowersSettings()


class AssignFollowers(models.TransientModel):
    _name = 'assign.followers'
    _description = 'Assign Followers to Record'

    record_followers_ids = fields.Many2many('res.partner')

    @api.multi
    def followers_assign(self):
        if self._context.get('active_model'):
            model_obj = self.env[self._context.get('active_model')]
            act_model_br = model_obj.search([('id', 'in', self._context.get('active_ids'))])
            wiz_followers = [x.id for x in self.record_followers_ids]
            for line in act_model_br:
                existing_followers = [x.partner_id.id for x in line.message_follower_ids]
                assign_ids = list(set(wiz_followers).union(existing_followers) - set(existing_followers))
                for assign_id in assign_ids:
                    self.env['mail.followers'].create({
                        'res_model': self._context.get('active_model'),
                        'partner_id': assign_id,
                        'res_id': line.id
                    })
        return True

    @api.multi
    def followers_unassign(self):
        if self._context.get('active_model'):
            model_obj = self.env[self._context.get('active_model')]
            act_model_br = model_obj.search([('id', 'in', self._context.get('active_ids'))])
            wiz_followers = [x.id for x in self.record_followers_ids]
            for line in act_model_br:
                existing_followers = [x.partner_id.id for x in line.message_follower_ids]
                unassign_ids = list(set(wiz_followers).intersection(existing_followers))
                for unassign_id in unassign_ids:
                    self.env['mail.followers'].search([
                        ('res_model', '=', self._context.get('active_model')),
                        ('res_id', '=', line.id),
                        ('partner_id', '=', unassign_id)
                    ]).unlink()
        return True

AssignFollowers()
