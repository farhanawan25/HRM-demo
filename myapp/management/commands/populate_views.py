from django.core.management.base import BaseCommand
from myapp.models import ViewsAccess  # Replace 'myapp' with your actual app name

class Command(BaseCommand):
    help = 'Populate ViewsAccess with common views'

    def handle(self, *args, **options):
        # Based on your actual URL names from urls.py
        views_to_create = [
            # Core Views
            ('dashboard', 'Main Dashboard'),
            
            # Employee Management
            ('employee_pay', 'Employee Pay Management'),
            ('employee_search', 'Employee Search'),
            ('search_employees', 'Search Employees'),
            ('employee_pay_search', 'Employee Pay Search'),
            ('employee_pay_table', 'Employee Pay Details'),
            
            # Payroll Management
            ('sal_period_list', 'Payroll Period Management'),
            ('payroll_initialize', 'Payroll Initialize'),
            ('payroll_history', 'Payroll History'),
            ('payroll_tracking', 'Payroll Tracking'),
            
            # Attendance Management
            ('update_attendance', 'Update Attendance'),
            ('attendance_marking', 'Attendance Marking'),
            ('attendance_detail', 'Attendance Detail View'),
            ('attendance_acceptance', 'Attendance Acceptance'),
            ('attendance_summary_detail', 'Attendance Summary Detail'),
            ('attendance_approval_summary', 'Attendance Approval Summary'),
            ('approve_attendance', 'Approve Attendance'),
            
            # Loan Management
            ('loan_allotment', 'Loan Entry/Allotment'),
            ('get_installments', 'Get Loan Installments'),
            ('update_installment_status', 'Update Installment Status'),
            
            # Allowances
            ('pay_allowances', 'Pay Allowances'),
            ('add_allowance', 'Add Allowance'),
            
            # Reports
            ('generate_pdf', 'Generate PDF Reports'),
            
            # Access Control (Admin only)
            ('system_access_control', 'System Access Control'),
            ('manage_views', 'Manage Views'),
        ]
        
        created_count = 0
        updated_count = 0
        
        for view_name, view_desc in views_to_create:
            view, created = ViewsAccess.objects.get_or_create(
                view_name=view_name,
                defaults={'view_desc': view_desc}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created view: {view_name}")
            else:
                # Update description if it's different
                if view.view_desc != view_desc:
                    view.view_desc = view_desc
                    view.save()
                    updated_count += 1
                    self.stdout.write(f"Updated view: {view_name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed views: {created_count} created, {updated_count} updated'
            )
        )