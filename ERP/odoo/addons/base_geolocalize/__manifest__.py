# -*- coding: utf-8 -*-
{
    'name': 'Contacts Location Page',
    'summary': '''Configure the location on Contacts page.''',
    'version': '2.3',
    'category': 'Website',
    'description': """Contacts Geolocation
    """,
    'depends': ['base_setup', 'base_openstreet'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'data/data.xml',
    ],
    'installable': True,
}
