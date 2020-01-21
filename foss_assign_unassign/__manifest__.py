# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Assign/Unassign Followers',

    'version': '13.0.0.0.0',

    'summary': 'Assign and Unassign Followers',

    'author': 'FOSS INFOTECH PVT LTD',

    'license': 'AGPL-3',

    'sequence': 10,

    'live_test_url': 'https://www.youtube.com/watch?v=USdanmoOeaI',

    'website': 'http://www.fossinfotech.com',

    'description': """
        Assign and Unassign Followers
        ====================
        Odoo assign followers module. Using this module, we can assign a bulk number of followers
        to a particular record or N number of records. We can assign multiple followers to multiple of records using the wizard.

        Assign followers to a Record of any Model
        ++++++++++++++++++++++++++++++++++++++++
        Step 1:  After installing the module go to Settings > Technical > Action > Assign followers

        Step 2: Create a Model for assigning Followers to records by giving the Name and choosing Model. Save it and click “Add Action” button.

        Step 3: It will be shown in the Lead/Opportunity tree view more button. Now we can assign a bulk number of followers to a particular record or N number of records.

        Step 4: Now we can assign multiple followers to multiple records using the wizard.
    """,

    'category': 'Tools',

    'website': 'https://www.fossinfotech.com/',

    'data': [
        'views/assign_followers_view.xml',
        'security/ir.model.access.csv'
    ],

     'images': [ 
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
