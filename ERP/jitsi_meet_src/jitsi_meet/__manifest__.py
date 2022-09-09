# -*- coding: utf-8 -*-
{
    'name': 'Video Meeting',
    'version': '14.0.0.0.5',
    'category': 'Website',
    'sequence': 5,
    'summary': 'Create and share Video Meetings.',
    'description': """Adds new APP on Calendar for Video Meetings by Jitsi Meet.""",
    "depends": ['base','web','website','mail','calendar'],
    "data": [
        'calendar/data.xml',
        'views/jitsi_meet_views.xml',
        'views/template.xml',
        'data/jitsi_meet.xml',
        'data/mail_template.xml',
        
    ],
    'images': ['static/description/video_recorder.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True
}