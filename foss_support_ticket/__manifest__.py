# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Support Ticket',
    'version': '1.0',
    'summary': 'Support Ticketing System',
    'author': 'FOSS INFOTECH PVT LTD',
    'category': 'Extra Tools',
    'website': 'http://www.fossinfotech.com',
    'description': """Support Ticket System""",
    'depends': ['base', 'project','hr_timesheet','link_tracker'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'views/support_ticket_views.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
