# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Company Holiday Management',
    'version': '12.0.0.0.0',
    'author': 'FOSS INFOTECH PVT LTD',
    'sequence': 10,
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'website': 'http://www.fossinfotech.com',
    'description': """This module is used to manage the Company Holidays.""",
    'depends': [
        'hr','calendar'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_company_holidays_view.xml'
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html'
    ],

    'installable': True,
    'application': True,
}
