{
    'name': 'Training Session',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Juraige',
    'summary': 'Training Session',
    'description': """
    Training Session
    """,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/training_session_views.xml',
        'views/training_session_line_views.xml',
        'views/training_partner_views.xml',



    ],
    'installable': True,
    'application': True,
}