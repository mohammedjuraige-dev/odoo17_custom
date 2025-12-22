from odoo import models, fields, api
from datetime import datetime, time, timedelta, date


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    late_time_hours = fields.Float(
        string="Late Time (hours)",
        help="Hours employee was late (calculated by cron every 5 minutes)"
    )

    # Remove compute dependency - cron will populate this

    # ============================================
    # Helper Method: Calculate late time for ONE record
    # ============================================
    def _calculate_late_time(self, attendance):
        """
        Calculate late time for a single attendance record
        Returns: (is_late, hours_late, message)
        """
        # Default values
        is_late = False
        hours_late = 0.0
        message = ""

        # Skip if missing data
        if not attendance.check_in or not attendance.employee_id:
            return False, 0.0, "Missing data"

        # Convert UTC to India time (IST = UTC+5:30)
        check_in_utc = fields.Datetime.to_datetime(attendance.check_in)
        check_in_india = check_in_utc + timedelta(hours=5, minutes=30)

        date_str = check_in_india.date()
        hour_str = f"{check_in_india.hour}:{check_in_india.minute:02d}"

        # Check if employee has approved half-day leave for morning
        has_morning_leave = self._check_morning_half_day_leave(
            attendance.employee_id,
            date_str
        )

        # Get employee's work calendar
        work_calendar = attendance.employee_id.resource_calendar_id
        if not work_calendar:
            return False, 0.0, "No work calendar"

        # Get weekday
        weekday = str(check_in_india.weekday())

        if has_morning_leave:
            # Employee has approved morning leave
            # They're only expected in afternoon (1:00 PM onwards)
            if check_in_india.hour < 13:
                return False, 0.0, f"Has morning leave, checked in early ({hour_str})"

            # Calculate against afternoon schedule
            shift_type = 'afternoon'
            shift_note = "afternoon (morning leave)"
        else:
            # Employee has NO approved morning leave
            if check_in_india.hour >= 12:
                # First check-in in afternoon without morning leave
                shift_type = 'morning'
                shift_note = "morning (missed entire morning)"
            else:
                # Normal: First check-in in morning
                shift_type = 'morning'
                shift_note = "morning"

        # Find the appropriate schedule
        shift_schedules = work_calendar.attendance_ids.filtered(
            lambda line: (
                    line.dayofweek == weekday and
                    shift_type in (line.name or '').lower()
            )
        )

        if not shift_schedules:
            return False, 0.0, f"No {shift_type} schedule found"

        shift_schedule = shift_schedules[0]

        try:
            scheduled_hour = float(shift_schedule.hour_from)
        except Exception:
            return False, 0.0, "Invalid schedule time"

        # Create scheduled datetime
        hour = int(scheduled_hour)
        minute = int(round((scheduled_hour - hour) * 60))
        scheduled_start = datetime.combine(
            date_str,
            time(hour, minute)
        )

        # Special case: If no morning leave but checking in afternoon
        # Calculate lateness from morning start
        if not has_morning_leave and check_in_india.hour >= 12:
            # Find morning schedule to get start time
            morning_schedules = work_calendar.attendance_ids.filtered(
                lambda line: (
                        line.dayofweek == weekday and
                        'morning' in (line.name or '').lower()
                )
            )
            if morning_schedules:
                morning_schedule = morning_schedules[0]
                try:
                    morning_start_hour = float(morning_schedule.hour_from)
                    hour = int(morning_start_hour)
                    minute = int(round((morning_start_hour - hour) * 60))
                    scheduled_start = datetime.combine(
                        date_str,
                        time(hour, minute)
                    )
                except Exception:
                    pass

        # Add timezone if needed
        if check_in_india.tzinfo:
            scheduled_start = scheduled_start.replace(tzinfo=check_in_india.tzinfo)

        # Calculate lateness
        if check_in_india > scheduled_start:
            time_difference = check_in_india - scheduled_start
            hours_late = time_difference.total_seconds() / 3600.0
            hours_late = round(hours_late, 2)
            is_late = True
            message = f"Late by {hours_late}h ({shift_note})"
        else:
            message = f"On time ({shift_note})"

        return is_late, hours_late, message

    # ============================================
    # CRON JOB: Main calculation method
    # ============================================
    @api.model
    def cron_calculate_late_time(self):
        """
        Cron Job: Calculate late time for FIRST check-ins
        Runs every 5 minutes
        """
        print("\n" + "=" * 60)
        print("⏰ CRON: Calculating Late Time (5-minute interval)")
        print("=" * 60)

        # Get today's date
        today = fields.Date.context_today(self)
        today_start = f"{today} 00:00:00"

        # 1. Find all check-ins today
        all_checkins_today = self.search([
            ('check_in', '>=', today_start),
        ])

        if not all_checkins_today:
            print("📭 No check-ins today")
            print("=" * 60 + "\n")
            return True

        print(f"📊 Total check-ins today: {len(all_checkins_today)}")

        # 2. Group by employee to find FIRST check-in for each
        employees_data = {}

        for checkin in all_checkins_today:
            if not checkin.employee_id:
                continue

            emp_id = checkin.employee_id.id

            # Store earliest check-in for each employee
            if emp_id not in employees_data or \
                    checkin.check_in < employees_data[emp_id]['checkin'].check_in:
                employees_data[emp_id] = {
                    'employee': checkin.employee_id,
                    'checkin': checkin,
                    'checkin_time': checkin.check_in,
                }

        print(f"👥 Employees with check-ins today: {len(employees_data)}")

        # 3. Process only FIRST check-ins
        processed = 0
        late_count = 0

        for emp_id, data in employees_data.items():
            first_checkin = data['checkin']
            employee = data['employee']

            # Skip if already calculated (late_time > 0)
            if first_checkin.late_time_hours and first_checkin.late_time_hours > 0:
                continue

            # Calculate late time
            is_late, hours_late, message = self._calculate_late_time(first_checkin)

            # Update the record
            first_checkin.late_time_hours = hours_late
            processed += 1

            # Log results
            check_time = fields.Datetime.to_datetime(first_checkin.check_in)
            india_time = check_time + timedelta(hours=5, minutes=30)
            time_str = india_time.strftime("%H:%M")

            if is_late:
                print(f"  ⚠️ {employee.name}: {time_str} - {message}")
                late_count += 1
            else:
                print(f"  ✅ {employee.name}: {time_str} - {message}")

        print(f"\n📈 SUMMARY")
        print(f"  First check-ins processed: {processed}")
        print(f"  Late employees found: {late_count}")
        print(f"  Total employees today: {len(employees_data)}")

        # 4. Optional: Clear late_time for non-first check-ins (safety)
        self._clear_non_first_checkin_latetime(all_checkins_today, employees_data)

        print("=" * 60 + "\n")
        return True

    def _clear_non_first_checkin_latetime(self, all_checkins, employees_data):
        """
        Safety check: Clear late_time for check-ins that are NOT first of day
        """
        cleared_count = 0

        for checkin in all_checkins:
            if not checkin.employee_id:
                continue

            emp_id = checkin.employee_id.id

            # Skip if this IS the first check-in for this employee
            if emp_id in employees_data and employees_data[emp_id]['checkin'].id == checkin.id:
                continue

            # This is NOT the first check-in, clear late_time if set
            if checkin.late_time_hours and checkin.late_time_hours > 0:
                checkin.late_time_hours = 0.0
                cleared_count += 1

        if cleared_count > 0:
            print(f"  🧹 Cleared late_time for {cleared_count} non-first check-ins")

    def _check_morning_half_day_leave(self, employee, check_date):
        """Check if employee has approved half-day leave for morning on given date"""
        # Get all approved leave requests for this employee on this date
        leave_records = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),  # Approved leaves
            ('request_date_from', '<=', check_date),
            ('request_date_to', '>=', check_date),
        ])

        for leave in leave_records:
            # Check if it's a half-day leave
            if leave.request_unit_half:
                # Check if it's morning half-day
                if leave.request_date_from_period == 'am':
                    return True
                # Some systems use 'morning' instead of 'am'
                if hasattr(leave, 'request_date_from_period') and leave.request_date_from_period == 'morning':
                    return True

        return False

