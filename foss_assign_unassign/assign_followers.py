# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
from openerp.tools.translate import _


class assign_followers_settings(osv.osv):
    _name = 'assign.followers.settings'
    _description = 'Settings for Assigning followers to a Record'
    
    _columns = {
        'name': fields.char('Name', size=128),
        'model_id': fields.many2one('ir.model', 'Model'),
        'ref_ir_act_window': fields.many2one('ir.actions.act_window', 'Sidebar action', readonly=True,
                                            help="Sidebar action to make this template available on records "
                                                 "of the related document model"),
        'ref_ir_value': fields.many2one('ir.values', 'Sidebar Button', readonly=True,
                                       help="Sidebar button to open the sidebar action"),
    }

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool.get('ir.actions.act_window')
        data_obj = self.pool.get('ir.model.data')
        for template in self.browse(cr, uid, ids, context=context):
            src_obj = template.model_id.model
            model_data_id = data_obj._get_id(cr, uid, 'assign_followers', 'view_assign_followers')
            res_id = data_obj.browse(cr, uid, model_data_id, context=context).res_id
            button_name = _('Assign/Unassign Followers')
            vals['ref_ir_act_window'] = action_obj.create(cr, uid, {
                 'name': button_name,
                 'type': 'ir.actions.act_window',
                 'res_model': 'assign.followers',
                 'src_model': src_obj,
                 'view_type': 'form',
                 'context': "{}",
                 'view_mode':'form,tree',
                 'view_id': res_id,
                 'target': 'new',
                 'auto_refresh':1
            }, context)
            vals['ref_ir_value'] = self.pool.get('ir.values').create(cr, uid, {
                 'name': button_name,
                 'model': src_obj,
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
                 'object': True,
             }, context)
        self.write(cr, uid, ids, {
                    'ref_ir_act_window': vals.get('ref_ir_act_window',False),
                    'ref_ir_value': vals.get('ref_ir_value',False),
                }, context)
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        for template in self.browse(cr, uid, ids, context=context):
            try:
                if template.ref_ir_act_window:
                    self.pool.get('ir.actions.act_window').unlink(cr, uid, template.ref_ir_act_window.id, context)
                if template.ref_ir_value:
                    ir_values_obj = self.pool.get('ir.values')
                    ir_values_obj.unlink(cr, uid, template.ref_ir_value.id, context)
            except Exception:
                raise osv.except_osv(_("Warning"), _("Deletion of the action record failed."))
        return True

assign_followers_settings()


class assign_followers(osv.osv_memory):
    _name = 'assign.followers'
    _description = 'Assign Followers to Record'

    _columns = {
        'record_followers_ids': fields.many2many('res.partner', 'record_followers_rel', 'record_id', 'partner_id', 'Followers'),
    }

    def assign_followers(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_model'):
            model_obj = self.pool.get(context['active_model'])    
            followers_ids = [j.id for j in self.browse(cr, uid, ids[0]).record_followers_ids]
            if context.get('active_ids'):    
                for value in model_obj.browse(cr, uid, context['active_ids']):
                    existing_followers_id = followers_to_assign = followers_list = []
                    existing_followers_id = [i.id for i in value.message_follower_ids]
                    followers_to_assign = list(set(followers_ids) - set(existing_followers_id))
                    for val_loop in followers_to_assign:
                        followers_list.append([4, val_loop])
                    if followers_list:        
                        model_obj.write(cr, uid, [value.id], {'message_follower_ids': followers_list})
        return True
         
    def unassign_followers(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_model'):
            model_obj = self.pool.get(context['active_model'])    
            followers_ids = [j.id for j in self.browse(cr, uid, ids[0]).record_followers_ids]
            if context.get('active_ids'):    
                for value in model_obj.browse(cr, uid, context['active_ids']):
                    existing_followers_id = followers_to_unassign = followers_list = []
                    existing_followers_id = [i.id for i in value.message_follower_ids]
                    followers_to_unassign = list(set(existing_followers_id))
                    for val_loop in followers_to_unassign:
                        if val_loop in followers_ids:
                            followers_list.append([3, val_loop])
                    if followers_list:        
                        model_obj.write(cr, uid, [value.id], {'message_follower_ids': followers_list})
        return True

assign_followers()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
