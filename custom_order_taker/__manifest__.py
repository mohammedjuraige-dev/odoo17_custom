{
    "name": "custom_order_taker",
    "version": "17.0.1.0.0",
    "author": "juraige",
    "license": "AGPL-3",
    "depends": ['base','product_validator','mail'],
    "data": [
        'views/custom_order_taker_views.xml',
        'views/wizard_views.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
    "application": True
}
