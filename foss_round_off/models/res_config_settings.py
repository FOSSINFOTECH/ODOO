# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    round_off = fields.Boolean(string='Allow rounding of invoice amount', help="Allow rounding of invoice amount")
    round_off_account = fields.Many2one('account.account', string='Round Off Account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            round_off_account=int(ICPSudo.get_param('foss_roundoff.round_off_account')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("foss_roundoff.round_off_account", self.round_off_account.id)
