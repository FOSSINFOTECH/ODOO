# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Task Score Card',
    'version': '12.0.0.0.0',
    'category': 'Generic Modules / Task Score Card',
    'description': """  This module provides Task scores according to the start date and end date.  """,
    'author': 'FOSS INFOTECH PVT LTD',
    'website': 'http://www.fossinfotech.com',
    'license': 'AGPL-3',
    'depends': [
         'project',
        ],
    'data': [
        "views/task_score_card_view.xml",
        ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html',
    ],
    'installable': True,
    'active': False,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
