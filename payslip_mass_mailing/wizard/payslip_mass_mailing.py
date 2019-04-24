# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError


class payslip_mass_mailing(models.TransientModel):
    _name = "payslip.mass.mailing"

    @api.multi
    def payslip_mass_mailing(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        payslip_obj = self.env['hr.payslip']
        ids = self.env.context.get('active_ids', [])
        ctx = dict()
        employee_name = ''
        for id_vals in ids:
            payslip_browse = payslip_obj.browse(id_vals)
            if not payslip_browse.employee_id.work_email:
                employee_name += payslip_browse.employee_id.name + ' ,'
            if payslip_browse.state == 'done':
                if payslip_browse.employee_id.work_email:
                    try:
                        template_id = ir_model_data.get_object_reference('payslip_mass_mailing', 'email_template_hr_payslip')[1]
                    except ValueError:
                        template_id = False

                    ctx.update({
                        'default_model': 'hr.payslip',
                        'default_res_id': payslip_browse.id,
                        'default_use_template': bool(template_id),
                        'default_template_id': template_id,
                        'default_composition_mode': 'comment',
                        'email_to': payslip_browse.employee_id.work_email,
                    })
                    mail_id = self.env['mail.template'].browse(template_id).with_context(ctx).send_mail(payslip_browse.id, True)
            else:
                raise UserError(_('Payslips should be in Done state'))
        if employee_name:
            raise UserError(_('Payslip not sent to ' + str(employee_name) + ' map work email in employee form'))
        return True
