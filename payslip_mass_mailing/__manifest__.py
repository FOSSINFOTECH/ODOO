# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payslip Mass Mailing',
    'version': '12.0.0.0.0',
    'category': 'Human Resources',
    'website': 'http://www.fossinfotech.com',
    'license': 'AGPL-3',
    'author': 'FOSS INFOTECH PVT LTD',
    'summary': 'Select multiple Payslip in tree view, send to respective employee by email',
    'depends': [
        'hr',
        'l10n_in_hr_payroll',
        'mail',
    ],
    'data': [
        "data/payslip_mail_template.xml",
        "wizard/payslip_mass_mailing.xml",
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
