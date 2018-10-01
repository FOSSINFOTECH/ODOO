# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class CommissioningFailure(models.TransientModel):
    _name = 'commissioning.failure'
    _description = 'Commssioning Failure'

    name = fields.Char(string="Failure Reason")

    @api.multi
    def apply_action(self):
        context = dict(self._context or {})
        commission_obj = self.env['crm.commission']
        if context.get('active_ids'):
            try:
                for val in commission_obj.browse(context['active_ids']):
                    if self.name:
                        val.write({
                            'failed_reason' : self.name,
                            'state' : 'failed',
                        })
            except Exception:
                raise UserError(_("Warning \n Kindly check all details properly."))
        return True


