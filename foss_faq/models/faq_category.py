# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class faq_category(models.Model):
    _name = "faq.category"
    _description = "Frequently Asked Questions Category"
    _order = 'sequence'

    name = fields.Char(string="Name")
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of faq category.",
                              default=10)
    faq_count = fields.Integer(compute='_compute_faq_count', string='# FAQ')

    @api.multi
    def _compute_faq_count(self):
        for fc in self:
            fc.faq_count = fc.env['faq.faq'].search_count([('category_ids', '=', fc.id)])

    @api.multi
    def open_faqs(self):
        faq_ids = self.env['faq.faq'].search([('category_ids', 'in', self.ids)])
        action_values = self.env.ref('foss_faq.action_faq_faq').read()[0]
        action_values.update({'domain': [('id', 'in', faq_ids.ids)]})
        return action_values
