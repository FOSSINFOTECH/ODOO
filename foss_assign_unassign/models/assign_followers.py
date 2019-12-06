# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class AssignFollowersSettings(models.Model):
	_name = 'assign.followers.settings'
	_description = 'Settings for Assigning followers to a Record'

	name = fields.Char(string='Name', size=128)
	model_id = fields.Many2one('ir.model', string='Model')
	ref_ir_act_window = fields.Many2one('ir.actions.act_window', string='Sidebar action', readonly=True, help="Sidebar action to make this template available on records of the related document model")
	ref_ir_value = fields.Many2one('ir.actions.server', string='Sidebar Button', readonly=True, help="Sidebar button to open the sidebar action")
	
	def create_action(self):
		vals = {}
		action_obj = self.env['ir.actions.act_window']
		data_obj = self.env['ir.model.data']
		obj_binding_id = self.env['ir.actions.server']
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
				'auto_refresh': 1,
				'binding_model_id':template.model_id.id
			}).id
			vals['ref_ir_value'] = obj_binding_id.create({
				'name': button_name,
				'model_id': template.model_id.id,
				'binding_type': 'action',
				'state': 'code',
				'usage':'ir_actions_server',
				'type': 'ir.actions.server'
				}).id
			self.write(dict(ref_ir_act_window=vals.get('ref_ir_act_window', False), ref_ir_value=vals.get('ref_ir_value', False)))
			return True

	def unlink_action(self):
		for template in self:
			model = template.model_id.model
			for i in self.env[ model ].search([]):
				i.message_follower_ids.unlink()
			if template.ref_ir_act_window:
				self.env['ir.actions.act_window'].browse(template.ref_ir_act_window.id).unlink()
			if template.ref_ir_value:
				self.env['ir.actions.server'].browse(template.ref_ir_value.id).unlink()
		return True

	def unlink(self):
		for val in self:
			model = val.model_id.model
			for i in self.env[ model ].search([]):
				i.message_follower_ids.unlink()
			if val.ref_ir_act_window:
				self.env['ir.actions.act_window'].browse(val.ref_ir_act_window.id).unlink()
			if val.ref_ir_value:
				self.env['ir.actions.server'].browse(val.ref_ir_value.id).unlink()
		return super(AssignFollowersSettings, self).unlink()


class AssignFollowers(models.TransientModel):
	_name = 'assign.followers'
	_description = 'Assign Followers to Record'

	record_followers_ids = fields.Many2many('res.partner')

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


