{
    'name': 'Training management',
    'author': 'juraige',
    'license': 'AGPL-3',
    'version': '17.0',
    'depends': ['base'],
    'data': [
    'security/ir.model.access.csv',
    'views/training_management_views.xml'
    ],
    'installable': True,
    'application': True,

'assets': {
    'web.assets_backend': [
        'training_management/static/src/scss/trainee_popup.scss',
    ],
},

}
