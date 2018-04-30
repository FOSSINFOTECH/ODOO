# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Tentative Price List',
    'version': '1.2',
    'category': 'Generic Modules / Tentative Price List',
    'description': """  This modules helps you set a target amount for a set of products in purchase order.  """,
    'author': 'FOSS INFOTECH',
    'website': 'http://www.fossinfotech.com',
    'depends': [
        'purchase',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/tentative_price_view.xml',
        'views/tentative_price_sequence.xml',
        ],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
