{
    'name': 'Data Management',
    'version': '17.0',
    'summary': 'Data management Broadtech training',
    'category': 'Tools',
    'description': """Module to manage employee request to take part in company training program""",
    'author': 'juraige',
    'depends': ['base','broadtech_training','hr'],
    'data': [
        'data/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/training_request_views.xml',
    ],
    'license':'AGPL-3',
    'installable': True,
    'application': True
}