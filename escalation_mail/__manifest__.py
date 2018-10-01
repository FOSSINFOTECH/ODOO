# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Escalation Mail',
    'version': '1.0',
    'summary': '',
    'author': 'FOSS INFOTECH PVT LTD',
    'category': 'Reports',
    'website': 'http://www.fossinfotech.com',
    'description': """ 
         This Module sends notifications or Escalation Emails to the Respective Project Managers on daily basis on the status of the task when task is in TO-Do or in In-Progress state and has reached it's deadline.
        """,
    'depends': [
        'base',
        'project',
        'hr',
    ],
    'data': [

        'data/ir_cron.xml',
        'data/mail_template_data.xml',
        'views/escalation_mail_views.xml',
    ],
    
    'images': [

        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html',
        'static/description/images/3.png',
        'static/description/images/1.png',
        'static/description/images/2.png',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
