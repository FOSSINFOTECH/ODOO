# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Revision',
    'version': '1.0',
    'author': 'FOSS INFOTECH PVT LTD',
    'category': 'Sale',
    'website': 'http://www.fossinfotech.com',
    'description': """ 
This module adds a functionality to manage different revisions with templates. Each revision will be stored as template.
""",
    'depends': [
        'sale', 'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
