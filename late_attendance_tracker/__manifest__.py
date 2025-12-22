{
    "name": "late_attendance_tracker",
    "version": "1.0",
    "summary": "Add computed late time to hr.attendance (hours and display)",
    "description": "Compute how late an employee is based on check-in vs scheduled start",
    "category": "Human Resources",
    "author": "Juraige",
    "license": "LGPL-3",
    "depends": ["hr_attendance"],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_attendance_late_cron.xml",
        "views/hr_attendance_late_view.xml",
    ],
    "installable": True,
    "application": False,
}