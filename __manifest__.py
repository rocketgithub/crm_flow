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

    'depends': ['base','crm','mail'],

    'data': [
        'views/mail_activity_views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/crm_flow.xml'
    ],
}
