# -*- coding: utf-8 -*-
{
    'name': "CRM flow",

    'summary': """ CRM flow """,

    'description': """
        CRM flow
    """,

    'author': "aquíH",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['crm','mail'],

    'data': [
        'views/mail_activity_views.xml',
        'views/crm_views.xml',
    ],
    'qweb': [
    ],
}