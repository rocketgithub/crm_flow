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

    'depends': ['base','crm','mail','sales_team'],

    'data': [
        'views/mail_activity_views.xml',
        'views/crm_views.xml',
        'data/base_automation.xml',
        'views/crm_team_views.xml',
        'views/templates.xml',
        'security/ir.model.access.csv',
    ],

    'qweb': [
        'static/src/xml/crm_flow.xml'
    ],
}
