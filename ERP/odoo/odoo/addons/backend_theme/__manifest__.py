# -*- coding: utf-8 -*-
{
    "name": "backend_theme",
    "version": "14.0.0.1",
    "category": "Themes",
	"description": """
		Backend Theme for Odoo Community Edition.
    """,
	'images':[
        'images/screen.png'
	],
    "installable": True,
    "auto_install": False,
    "application": False,
    "depends": [
        'web',
        'web_responsive',

    ],
    "data": [
        'views/assets.xml',
		'views/res_company_view.xml',
		'views/users.xml',
        'views/sidebar.xml',
    ],

}
