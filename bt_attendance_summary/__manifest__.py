{
    'name': 'BT Attendance Summary',
    'version': '17.0.0.1',
    'category': 'Attendance',
    'summary': 'BT Attendance Summary',
    'description': """Attendance summary for employee""",
    'author': 'juraige',
    'depends': ['base','broadtech_training','hr_attendance','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_summary_views.xml',


    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True
}
