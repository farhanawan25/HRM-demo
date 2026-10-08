############ necessary imports #############

import json
import traceback
from io import BytesIO
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import connection, transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.timezone import datetime as timezone_datetime

from django.views.decorators.csrf import csrf_exempt

from dateutil.relativedelta import relativedelta

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image as ReportImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from PIL import Image

from myapp.models import (
    Emp, LoanAllotment, LoanInstallment,
    Users, SalPeriod, Att, EmpLeav, AuditEmp
)


################# View Functions ########################


def get_zone_wise_data(payroll_period):
    """
    Fetch zone-wise salary data for current and previous periods
    Returns zone data, totals, comparison data, chart data, and trend data
    """
    zone_data = []
    zone_totals = {
        'total_gross': Decimal('0.00'),
        'total_deductions': Decimal('0.00'),
        'total_net': Decimal('0.00')
    }
    zone_comparison_data = {}
    zone_chart_data = []
    zone_trend_data = {}
    
    try:
        with connection.cursor() as cursor:
            # Get zone-wise data for current period
            zone_query = """
            SELECT   zone_id,ord,WSSP_STAFF, SUM (gross_salary)gross_salary, SUM (deductions)deductions, SUM (gross_salary)+SUM (deductions)Net_Salary
            FROM (SELECT   e.zone_id,'1' ord,'WSSP-STAFF' AS WSSP_STAFF,
                   SUM (p.payroll_allwamt + p.payroll_arrears) gross_salary,
                   0 deductions
              FROM payroll p, allw a, emp e
             WHERE p.payroll_allw = a.allw_id
               AND a.allw_typ <> 'E'
               AND e.emp_no = p.payroll_emp
               AND payroll_period = %s
               AND a.allw_earn_deduc = 1
               AND E.EMP_PAY_SUBGRP != 110105 
            GROUP BY e.zone_id
            UNION ALL
            SELECT   e.zone_id,'1'ord,'WSSP-STAFF' AS WSSP_STAFF,
            0 gross_salary,
                   SUM (p.payroll_allwamt + p.payroll_arrears) deductions
              FROM payroll p, allw a, emp e
             WHERE p.payroll_allw = a.allw_id
               AND a.allw_typ <> 'E'
               AND e.emp_no = p.payroll_emp
               AND payroll_period = %s
               AND a.allw_earn_deduc = -1
               AND E.EMP_PAY_SUBGRP != 110105
            GROUP BY e.zone_id
            UNION ALL
            SELECT   e.zone_id,'2'ord,'WSSP-PROJECT-STAFF UNICEF' AS WSSP_STAFF,
            SUM (p.payroll_allwamt + p.payroll_arrears) gross_salary,
                   0 deductions
              FROM payroll p, allw a, emp e
             WHERE p.payroll_allw = a.allw_id
               AND a.allw_typ <> 'E'
               AND e.emp_no = p.payroll_emp
               AND payroll_period = %s
               AND a.allw_earn_deduc = 1
               AND E.EMP_PAY_SUBGRP = 110105
            GROUP BY e.zone_id
            UNION ALL
            SELECT   e.zone_id,'2'ord,'WSSP-PROJECT-STAFF UNICEF' AS WSSP_STAFF,
            0 gross_salary,
                   SUM (p.payroll_allwamt + p.payroll_arrears) deductions
              FROM payroll p, allw a, emp e
             WHERE p.payroll_allw = a.allw_id
               AND a.allw_typ <> 'E'
               AND e.emp_no = p.payroll_emp
               AND payroll_period = %s
               AND a.allw_earn_deduc = -1
               AND E.EMP_PAY_SUBGRP = 110105
          GROUP BY e.zone_id )
            GROUP BY zone_id,ord,WSSP_STAFF
            order by 2,1

            """
            
            cursor.execute(zone_query, [payroll_period, payroll_period, payroll_period, payroll_period])
            current_period_rows = cursor.fetchall()
            
            print(f"Current period zone data rows: {len(current_period_rows)}")
            
            # Process current period data
            current_zone_data = {}
            for row in current_period_rows:
                zone_id = row[0]
                ord = row[1]
                staff_type = row[2]
                gross_salary = Decimal(row[3] or 0)
                deductions = Decimal(row[4] or 0)
                net_salary = Decimal(row[5] or 0)
                
                # Create unique key for zone + staff type
                zone_key = f"{zone_id}_{staff_type}"
                
                if zone_key not in current_zone_data:
                    current_zone_data[zone_key] = {
                        'zone_id': zone_id,
                        'staff_type': staff_type,
                        'staff_type_short': 'WSSP' if staff_type == 'WSSP-STAFF' else 'PROJECT',
                        'ord': ord,
                        'gross_salary': Decimal('0.00'),
                        'deductions': Decimal('0.00'),
                        'net_salary': Decimal('0.00')
                    }
                
                current_zone_data[zone_key]['gross_salary'] += gross_salary
                current_zone_data[zone_key]['deductions'] += deductions
                current_zone_data[zone_key]['net_salary'] = (
                    current_zone_data[zone_key]['gross_salary'] +
                    current_zone_data[zone_key]['deductions']
                )
                
                # Update totals
                zone_totals['total_gross'] += gross_salary
                zone_totals['total_deductions'] += deductions
            
            # Recalculate total net
            zone_totals['total_net'] = zone_totals['total_gross'] + zone_totals['total_deductions']
            
            # Get previous period data for comparison
            previous_period = payroll_period - 1
            cursor.execute(zone_query, [previous_period, previous_period, previous_period, previous_period])
            previous_period_rows = cursor.fetchall()
            
            print(f"Previous period zone data rows: {len(previous_period_rows)}")
            
            # Process previous period data
            previous_zone_data = {}
            previous_totals = {
                'total_gross': Decimal('0.00'),
                'total_deductions': Decimal('0.00'),
                'total_net': Decimal('0.00')
            }
            
            for row in previous_period_rows:
                zone_id = row[0]
                ord = row[1]
                staff_type = row[2]
                gross_salary = Decimal(row[3] or 0)
                deductions = Decimal(row[4] or 0)
                net_salary = Decimal(row[5] or 0)
                
                zone_key = f"{zone_id}_{staff_type}"
                
                if zone_key not in previous_zone_data:
                    previous_zone_data[zone_key] = {
                        'gross_salary': Decimal('0.00'),
                        'deductions': Decimal('0.00'),
                        'net_salary': Decimal('0.00')
                    }
                
                previous_zone_data[zone_key]['gross_salary'] += gross_salary
                previous_zone_data[zone_key]['deductions'] += deductions
                previous_zone_data[zone_key]['net_salary'] = (
                    previous_zone_data[zone_key]['gross_salary'] - 
                    previous_zone_data[zone_key]['deductions']
                )
                
                # Update previous totals
                previous_totals['total_gross'] += gross_salary
                previous_totals['total_deductions'] += deductions
            
            previous_totals['total_net'] = previous_totals['total_gross'] - previous_totals['total_deductions']
            
            # Calculate comparisons and build final data
            for zone_key, current_data in current_zone_data.items():
                zone_info = current_data.copy()
                
                # Add comparison data if previous period exists
                if zone_key in previous_zone_data:
                    prev_data = previous_zone_data[zone_key]
                    
                    # Calculate changes
                    gross_change = current_data['gross_salary'] - prev_data['gross_salary']
                    deductions_change = current_data['deductions'] - prev_data['deductions']
                    net_change = current_data['net_salary'] - prev_data['net_salary']
                    
                    # Calculate percentages
                    gross_percent = (gross_change / prev_data['gross_salary'] * 100) if prev_data['gross_salary'] > 0 else 0
                    deductions_percent = (deductions_change / prev_data['deductions'] * 100) if prev_data['deductions'] > 0 else 0
                    net_percent = (net_change / prev_data['net_salary'] * 100) if prev_data['net_salary'] > 0 else 0
                    
                    zone_info.update({
                        'prev_gross': prev_data['gross_salary'],
                        'prev_deductions': prev_data['deductions'],
                        'prev_net': prev_data['net_salary'],
                        'gross_change': gross_change,
                        'deductions_change': deductions_change,
                        'net_change': net_change,
                        'gross_percent': float(gross_percent),
                        'deductions_percent': float(deductions_percent),
                        'net_percent': float(net_percent)
                    })
                else:
                    # No previous data
                    zone_info.update({
                        'prev_gross': Decimal('0.00'),
                        'prev_deductions': Decimal('0.00'),
                        'prev_net': Decimal('0.00'),
                        'gross_change': current_data['gross_salary'],
                        'deductions_change': current_data['deductions'],
                        'net_change': current_data['net_salary'],
                        'gross_percent': 100.0 if current_data['gross_salary'] > 0 else 0.0,
                        'deductions_percent': 100.0 if current_data['deductions'] > 0 else 0.0,
                        'net_percent': 100.0 if current_data['net_salary'] > 0 else 0.0
                    })
                
                zone_data.append(zone_info)
            
            # Sort zone data
            zone_data.sort(key=lambda x: (x['ord'], x['zone_id']))
            
            # Calculate overall comparison data
            total_gross_change = zone_totals['total_gross'] - previous_totals['total_gross']
            total_deductions_change = zone_totals['total_deductions'] - previous_totals['total_deductions']
            total_net_change = zone_totals['total_net'] - previous_totals['total_net']
            
            zone_comparison_data = {
                'current_period': payroll_period,
                'previous_period': previous_period,
                'total_gross_change': float(total_gross_change),
                'total_deductions_change': float(total_deductions_change),
                'total_net_change': float(total_net_change),
                'total_gross_percent': float(total_gross_change / previous_totals['total_gross'] * 100) if previous_totals['total_gross'] > 0 else 0,
                'total_deductions_percent': float(total_deductions_change / previous_totals['total_deductions'] * 100) if previous_totals['total_deductions'] > 0 else 0,
                'total_net_percent': float(total_net_change / previous_totals['total_net'] * 100) if previous_totals['total_net'] > 0 else 0
            }
            
            # Prepare chart data - group by zone for visualization
            zone_chart_groups = {}
            for zone_info in zone_data:
                zone_id = zone_info['zone_id']
                staff_type = zone_info['staff_type']
                
                chart_item = {
                    'zone_id': zone_id,
                    'staff_type': staff_type,
                    'staff_type_short': zone_info['staff_type_short'],
                    'gross_salary': float(zone_info['gross_salary']),
                    'deductions': float(zone_info['deductions']),
                    'net_salary': float(zone_info['net_salary']),
                    'gross_change': float(zone_info.get('gross_change', 0)),
                    'deductions_change': float(zone_info.get('deductions_change', 0)),
                    'net_change': float(zone_info.get('net_change', 0))
                }
                
                zone_chart_data.append(chart_item)
            
            # Get trend data for last 3 periods for each zone
            trend_periods = [payroll_period - 2, payroll_period - 1, payroll_period]
            
            for period in trend_periods:
                if period <= 0:
                    continue
                    
                cursor.execute(zone_query, [period, period, period, period])
                trend_rows = cursor.fetchall()
                
                period_zone_data = {}
                for row in trend_rows:
                    zone_id = row[0]
                    staff_type = row[2]
                    gross_salary = Decimal(row[3] or 0)
                    deductions = Decimal(row[4] or 0)
                    net_salary = Decimal(row[5] or 0)
                    
                    zone_key = f"{zone_id}_{staff_type}"
                    
                    if zone_key not in period_zone_data:
                        period_zone_data[zone_key] = {
                            'gross_salary': Decimal('0.00'),
                            'deductions': Decimal('0.00'),
                            'net_salary': Decimal('0.00')
                        }
                    
                    period_zone_data[zone_key]['gross_salary'] += gross_salary
                    period_zone_data[zone_key]['deductions'] += deductions
                    period_zone_data[zone_key]['net_salary'] = (
                        period_zone_data[zone_key]['gross_salary'] - 
                        period_zone_data[zone_key]['deductions']
                    )
                
                # Add to trend data
                for zone_key, trend_info in period_zone_data.items():
                    zone_id = zone_key.split('_')[0]
                    
                    if zone_id not in zone_trend_data:
                        zone_trend_data[zone_id] = []
                    
                    zone_trend_data[zone_id].append({
                        'period': period,
                        'gross_salary': float(trend_info['gross_salary']),
                        'deductions': float(trend_info['deductions']),
                        'net_salary': float(trend_info['net_salary'])
                    })
            
            # Sort trend data by period
            for zone_id in zone_trend_data:
                zone_trend_data[zone_id].sort(key=lambda x: x['period'])
            
            print(f"Zone data processed: {len(zone_data)} entries")
            print(f"Zone totals: {zone_totals}")
            print(f"Zone comparison: {zone_comparison_data}")
            
    except Exception as e:
        print(f"Error in get_zone_wise_data: {e}")
        import traceback
        traceback.print_exc()
    
    return zone_data, zone_totals, zone_comparison_data, zone_chart_data, zone_trend_data

# Updated dashboard view to include zone data
@login_required
def dashboard_view(request):
    context = {
        'active_employees': 0,
        'total_salary': Decimal('0.00'),
        'active_loans': 0,
        'payroll_periods': 0,
        'latest_payroll_period': None,
        'total_earning': Decimal('0.00'),
        'total_deduction': Decimal('0.00'),
        'employer_pension': Decimal('0.00'),
        'net_salary': Decimal('0.00'),
        'gross_salary': Decimal('0.00'),
        'payroll_entries': [],
        'chart_data': '[]',
        'period_comparison': {},
        'payroll_summary': []
    }
    
    try:
        with connection.cursor() as cursor:
            # 1. Get Active Employees Count (emp_flg = 'O')
            cursor.execute("SELECT COUNT(*) FROM emp WHERE emp_flg = 'O'")
            result = cursor.fetchone()
            context['active_employees'] = result[0] if result else 0
            
            # 2. Get Latest Payroll Period
            cursor.execute("SELECT MAX(payroll_period) FROM payroll")
            latest_period = cursor.fetchone()
            context['latest_payroll_period'] = latest_period[0] if latest_period and latest_period[0] else 1062
            
            # 3. Get Payroll Data for Latest Period
            payroll_query = """
                SELECT 
                    p.payroll_emp, p.payroll_allw, p.payroll_allwamt, p.payroll_allwrate, 
                    p.payroll_flg, a.allw_earn_deduc, a.allw_desc, p.payroll_duty_days,
                    e.emp_name
                FROM payroll p
                JOIN allw a ON a.allw_id = p.payroll_allw
                JOIN emp e ON e.emp_no = p.payroll_emp
                WHERE p.payroll_period = %s
                ORDER BY p.payroll_emp, p.payroll_allw
            """
            
            cursor.execute(payroll_query, [context['latest_payroll_period']])
            rows = cursor.fetchall()
            
            # Process payroll data for current period
            for row in rows:
                emp_no = row[0]
                pay_id = row[1]
                amount = Decimal(row[2] or 0)
                rate = Decimal(row[3] or 0)
                flag = row[4]
                
                try:
                    earn_deduc = int(row[5])
                except (ValueError, TypeError):
                    earn_deduc = 0
                    
                pay_desc = row[6]
                duty_days = row[7]
                emp_name = row[8]
                
                total = amount

                entry = {
                    'emp_no': emp_no,
                    'emp_name': emp_name,
                    'pay_id': pay_id,
                    'pay_desc': pay_desc,
                    'rate': rate,
                    'amount': amount,
                    'flag': flag,
                    'earn_deduc': earn_deduc,
                    'duty_days': duty_days,
                    'calc_mode': 'Monthly',
                    'total': total
                }
                
                context['payroll_entries'].append(entry)

                if earn_deduc == 0:
                    context['employer_pension'] += total
                elif earn_deduc == 1:
                    context['total_earning'] += total
                elif earn_deduc == -1:
                    context['total_deduction'] += abs(total)

            # Calculate totals for current period
            context['gross_salary'] = context['total_earning'] + context['employer_pension']
            context['net_salary'] = context['total_earning'] - context['total_deduction']
            context['total_salary'] = context['net_salary']
            
            # 4. Get Active Loans Count
            try:
                cursor.execute("SELECT COUNT(*) FROM loan_allotment WHERE loan_status = 'N'")
                result = cursor.fetchone()
                context['active_loans'] = result[0] if result else 0
            except:
                context['active_loans'] = 0
            
            # 5. Get Total Payroll Periods Count
            cursor.execute("SELECT COUNT(DISTINCT payroll_period) FROM payroll")
            result = cursor.fetchone()
            context['payroll_periods'] = result[0] if result else 0
            
            # 6. Get Chart Data for Last 3 Periods
            cursor.execute("SELECT * FROM ( SELECT DISTINCT payroll_period FROM payroll ORDER BY payroll_period DESC) WHERE ROWNUM <= 3")
            periods = cursor.fetchall()
            
            chart_data = []
            payroll_summary = []
            
            print(f"Found {len(periods)} periods for chart")
            
            for period_row in periods:
                period = period_row[0]
                print(f"Processing period: {period}")
                
                # Get data for this period
                cursor.execute(payroll_query, [period])
                period_rows = cursor.fetchall()
                
                period_earning = Decimal('0.00')
                period_deduction = Decimal('0.00')
                period_pension = Decimal('0.00')
                employee_count = 0
                employees_processed = set()
                
                for row in period_rows:
                    amount = Decimal(row[2] or 0)
                    emp_no = row[0]
                    
                    # Count unique employees for this period
                    employees_processed.add(emp_no)
                    
                    try:
                        earn_deduc = int(row[5])
                    except (ValueError, TypeError):
                        earn_deduc = 0
                    
                    if earn_deduc == 0:
                        period_pension += amount
                    elif earn_deduc == 1:
                        period_earning += amount
                    elif earn_deduc == -1:
                        period_deduction += abs(amount)
                
                employee_count = len(employees_processed)
                period_gross = period_earning + period_pension
                period_net = period_earning - period_deduction
                
                # Average per employee calculations
                avg_gross = period_gross / employee_count if employee_count > 0 else 0
                avg_net = period_net / employee_count if employee_count > 0 else 0
                avg_deduction = period_deduction / employee_count if employee_count > 0 else 0
                
                period_data = {
                    'period': period,
                    'earnings': float(period_earning),
                    'deductions': float(period_deduction),
                    'gross_salary': float(period_gross),
                    'net_salary': float(period_net),
                    'pension': float(period_pension),
                    'employee_count': employee_count,
                    'avg_gross': float(avg_gross),
                    'avg_net': float(avg_net),
                    'avg_deduction': float(avg_deduction)
                }
                
                chart_data.append(period_data)
                payroll_summary.append({
                    'period': period,
                    'total_employees': employee_count,
                    'gross_salary': period_gross,
                    'total_deductions': period_deduction,
                    'net_salary': period_net,
                    'avg_salary_per_employee': avg_net
                })
                
                print(f"Period {period}: Employees={employee_count}, Gross={period_gross}, Deductions={period_deduction}, Net={period_net}")
            
            # Sort by period ascending for chart
            chart_data.sort(key=lambda x: x['period'])
            payroll_summary.sort(key=lambda x: x['period'], reverse=True)
            
            # Convert to JSON string
            context['chart_data'] = json.dumps(chart_data)
            context['payroll_summary'] = payroll_summary[:6]  # Keep last 6 periods for summary table
            
            print(f"Final chart data: {context['chart_data']}")
            
            # 7. Calculate Period-over-Period Comparison (Current vs Previous)
            if len(chart_data) >= 2:
                current_period = chart_data[-1]  # Latest period
                previous_period = chart_data[-2]  # Previous period
                
                def calculate_change_percent(current, previous):
                    if previous == 0:
                        return 100 if current > 0 else 0
                    return ((current - previous) / previous * 100)
                
                context['period_comparison'] = {
                    'current_period': current_period['period'],
                    'previous_period': previous_period['period'],
                    
                    # Gross Salary Comparison
                    'gross_current': current_period['gross_salary'],
                    'gross_previous': previous_period['gross_salary'],
                    'gross_change': current_period['gross_salary'] - previous_period['gross_salary'],
                    'gross_percent': calculate_change_percent(current_period['gross_salary'], previous_period['gross_salary']),
                    
                    # Net Salary Comparison
                    'net_current': current_period['net_salary'],
                    'net_previous': previous_period['net_salary'],
                    'net_change': current_period['net_salary'] - previous_period['net_salary'],
                    'net_percent': calculate_change_percent(current_period['net_salary'], previous_period['net_salary']),
                    
                    # Deductions Comparison
                    'deduction_current': current_period['deductions'],
                    'deduction_previous': previous_period['deductions'],
                    'deduction_change': current_period['deductions'] - previous_period['deductions'],
                    'deduction_percent': calculate_change_percent(current_period['deductions'], previous_period['deductions']),
                    
                    # Employee Count Comparison
                    'employee_current': current_period['employee_count'],
                    'employee_previous': previous_period['employee_count'],
                    'employee_change': current_period['employee_count'] - previous_period['employee_count'],
                    'employee_percent': calculate_change_percent(current_period['employee_count'], previous_period['employee_count']),
                    
                    # Average Salary per Employee
                    'avg_net_current': current_period['avg_net'],
                    'avg_net_previous': previous_period['avg_net'],
                    'avg_net_change': current_period['avg_net'] - previous_period['avg_net'],
                    'avg_net_percent': calculate_change_percent(current_period['avg_net'], previous_period['avg_net']),
                }
            
            # 8. Calculate Quarter-over-Quarter and Year-over-Year if enough data
            if len(chart_data) >= 4:
                # Quarter comparison (3 periods back)
                quarter_previous = chart_data[-4]
                context['period_comparison']['quarter_comparison'] = {
                    'gross_change': current_period['gross_salary'] - quarter_previous['gross_salary'],
                    'net_change': current_period['net_salary'] - quarter_previous['net_salary'],
                    'deduction_change': current_period['deductions'] - quarter_previous['deductions'],
                }
            
    except Exception as e:
        print(f"Database error in dashboard: {e}")
        import traceback
        traceback.print_exc()
        # Keep default values in case of error
        pass
    
    # Get Zone-wise Data
    zone_data, zone_totals, zone_comparison_data, zone_chart_data, zone_trend_data = get_zone_wise_data(context['latest_payroll_period'])
    
    context.update({
        'zone_data': zone_data,
        'zone_totals': zone_totals,
        'zone_comparison_data': zone_comparison_data,
        'zone_chart_data': json.dumps(zone_chart_data),
        'zone_trend_data': json.dumps(zone_trend_data),
        'total_zones': len(set([z['zone_id'] for z in zone_data])) if zone_data else 0
    })

    return render(request, 'myapp/dashboard.html', context)

from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            try:
                custom_user = Users.objects.get(USER_ID=user.username)
                user_desc = custom_user.USER_DESC
                request.session['user_desc'] = user_desc
            except Users.DoesNotExist:
                request.session['user_desc'] = ''
            
            request.session['user_id'] = str(user.username)

            messages.success(request, f"Welcome, {user_desc}!")
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'myapp/login.html')

def logout_view(request):
    request.session.flush() 
    logout(request)  # Logs out the user
    return redirect('login')  # Redirects to the login page

@login_required
def employee_pay_view(request):
    return render(request, 'myapp/emp_pay.html')

def search_employees(request):
    term = request.GET.get('term', '')
    employees = []
    
    if term:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EMP_NO, EMP_NAME 
                FROM EMP 
                WHERE EMP_NO LIKE %s
                ORDER BY EMP_NO
                FETCH FIRST 10 ROWS ONLY
            """, [f"{term}%"])
            rows = cursor.fetchall()
            employees = [{'id': row[0], 'name': row[1]} for row in rows]
    
    return JsonResponse(employees, safe=False)

##########################   Salary Period Definition Views  ######################################

@login_required
def payroll_period_view(request):
    sal_period_id = None

    if request.method == 'POST':
        try:
            # Step 0: Prevent new period if latest one is already open ('N') or not processed ('P')
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT SAL_PERIOD_ID, SAL_PERIOD_FLG FROM SAL_PERIOD 
                    ORDER BY SAL_PERIOD_ID DESC
                    FETCH FIRST 1 ROWS ONLY
                """)
                latest_period = cursor.fetchone()
                if latest_period:
                    period_id, period_flg = latest_period
                    if period_flg == 'N':
                        messages.error(request, f"Payroll Period {period_id} is still open. Complete it before creating a new one.")
                        return redirect('sal_period_list')
                    elif period_flg != 'P':
                        messages.error(request, f"Payroll Period {period_id} is not processed yet (status: {period_flg}). Process it before creating a new one.")
                        return redirect('sal_period_list')
                
            # Step 1: Audit check
            with connection.cursor() as cursor:
                cursor.execute(""" 
                    SELECT COUNT(*) FROM AUDIT_EMP
                    WHERE AUDIT_EMP_AUDITFLG = 'N' AND AUDIT_EMP_NO IS NOT NULL
                """)
                audit_pending = cursor.fetchone()[0]
                if audit_pending != 0:
                    print("Employee records are pending to be authorized/rejected.")

            # Step 2: Get form data
            sal_period_from = request.POST.get('sal_period_from')
            sal_period_to = request.POST.get('sal_period_to')

            if not sal_period_from or not sal_period_to:
                messages.error(request, "Start date and end date are required.")
                return redirect('sal_period_list')

            try:
                start_date = datetime.strptime(sal_period_from, '%Y-%m-%d')
                end_date = datetime.strptime(sal_period_to, '%Y-%m-%d')
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('sal_period_list')

            if start_date.year < 1 or end_date.year < 1:
                messages.error(request, "Year must be greater than 0.")
                return redirect('sal_period_list')

            if start_date > end_date:
                messages.error(request, "Start date cannot be later than end date.")
                return redirect('sal_period_list')

            days_count = (end_date - start_date).days + 1

            if days_count > 31:
                messages.error(request, "Payroll period cannot exceed 31 days.")
                return redirect('sal_period_list')

            # This is the key change - calculate the month based on period end date instead of start date
            # For payroll periods, it's common to name the period based on when the salary is paid
            # rather than when it starts
            # This will help avoid duplicate month entries in the database
            
            # sal_period_month = end_date.replace(day=1).strftime('%Y-%m-%d')
            # sal_period_yr = end_date.year
            # sal_period_dt = start_date

            sal_period_month = end_date.replace(day=1).strftime('%Y-%m-%d')

            # Financial year calculation
            if end_date.month >= 7:  # July to December
                financial_year = f"{end_date.year}{str(end_date.year + 1)[2:]}"
            else:  # January to June
                financial_year = f"{end_date.year - 1}{str(end_date.year)[2:]}"
    
            sal_period_yr = int(financial_year)  # Convert to int if database expects integer
            sal_period_dt = start_date

            # Check for existing period with same month and year to avoid constraint violation
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM SAL_PERIOD
                    WHERE EXTRACT(YEAR FROM SAL_PERIOD_MONTH) = %s
                    AND EXTRACT(MONTH FROM SAL_PERIOD_MONTH) = %s
                """, [sal_period_yr, end_date.month])
                existing_period_count = cursor.fetchone()[0]
                
                if existing_period_count > 0:
                    messages.error(request, f"A payroll period already exists for {end_date.strftime('%B %Y')}. Please adjust your dates.")
                    return redirect('sal_period_list')

            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            sal_period_dt_str = sal_period_dt.strftime('%Y-%m-%d')

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(MAX(SAL_PERIOD_ID), 1000) + 1 FROM SAL_PERIOD
                """)
                sal_period_id = cursor.fetchone()[0]

            with connection.cursor() as cursor:
                cursor.execute(""" 
                    INSERT INTO SAL_PERIOD (
                        SAL_PERIOD_ID, SAL_PERIOD_FROM, SAL_PERIOD_TO,
                        SAL_PERIOD_MONTH, SAL_PERIOD_YR,
                        SAL_PERIOD_DAYsCOUNT, SAL_PERIOD_FLG, SAL_PERIOD_DT
                    )
                    VALUES (%s, TO_DATE(%s, 'YYYY-MM-DD'), TO_DATE(%s, 'YYYY-MM-DD'),
                            TO_DATE(%s,'YYYY-MM-DD'), %s, %s, 'N', TO_DATE(%s, 'YYYY-MM-DD'))
                """, [
                    sal_period_id, start_date_str, end_date_str,
                    sal_period_month, sal_period_yr, days_count, sal_period_dt_str
                ])

            with connection.cursor() as cursor:
                cursor.execute("SELECT EMP_NO, EMP_MGR FROM EMP WHERE EMP_FLG = 'O'")
                employees = cursor.fetchall()

                for emp_no, emp_mgr in employees:
                    for i in range(days_count):
                        att_date = start_date + timedelta(days=i)
                        att_status = 'H' if att_date.weekday() == 6 else 'P'
                        cursor.execute("""
                            INSERT INTO ATT (
                                ATT_PERIOD, ATT_DT, ATT_EMP, ATT_STATUS, ATT_HOLIDAY_TYP,
                                ATT_LEAVE_TYP, ATT_OVERTIME_TYP, ATT_POSTED_BY, ATT_APPROVED_BY,
                                ATT_ACCEPTED_BY, ATT_FLG
                            ) VALUES (%s, %s, %s, %s, 'N', 0, 'N', %s, 1500001, 1500007, 'V')
                        """, [sal_period_id, att_date, emp_no, att_status, emp_mgr])

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ATT
                    SET ATT_STATUS = 'L',
                        ATT_LEAVE_TYP = (
                            SELECT EMP_LEAV_TYP FROM EMP_LEAV
                            WHERE EMP_LEAV_EMP = ATT.ATT_EMP
                            AND ATT.ATT_DT BETWEEN EMP_LEAV_FROM AND EMP_LEAV_TO
                            FETCH FIRST 1 ROWS ONLY
                        )
                    WHERE EXISTS (
                        SELECT 1 FROM EMP_LEAV
                        WHERE EMP_LEAV_EMP = ATT.ATT_EMP
                        AND ATT.ATT_DT BETWEEN EMP_LEAV_FROM AND EMP_LEAV_TO
                    ) AND ATT_PERIOD = %s
                """, [sal_period_id])

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ATT
                    SET ATT_STATUS = 
                        CASE 
                            WHEN EXISTS (
                                SELECT 1 FROM EMP 
                                WHERE EMP.EMP_NO = ATT.ATT_EMP
                                AND (EMP.EMP_LEAVING_DT IS NULL OR EMP.EMP_LEAVING_DT >= ATT.ATT_DT)
                            ) THEN 
                                CASE WHEN TO_CHAR(ATT.ATT_DT, 'DAY') LIKE 'SUNDAY%%' THEN 'H' ELSE 'P' END
                            ELSE 'A' 
                        END
                    WHERE ATT_PERIOD = %s
                """, [sal_period_id])

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE EMP_PAY 
                    SET EMP_PAY_ALLWRATE = 0, EMP_PAY_ALLWAMT = 0 
                    WHERE EMP_PAY_EMP IN (
                        SELECT EMP_PAY_EMP FROM EMP_PAY p, ALLW a
                        WHERE p.EMP_PAY_ALLW = a.ALLW_ID AND a.ALLW_EARN_DEDUC = -1
                        AND a.ALLW_TYP = 'R' AND p.EMP_PAY_ALLWAMT <> 0
                    )
                    AND EMP_PAY_ALLW IN (
                        SELECT EMP_PAY_ALLW FROM EMP_PAY p, ALLW a
                        WHERE p.EMP_PAY_ALLW = a.ALLW_ID AND a.ALLW_EARN_DEDUC = -1
                        AND a.ALLW_TYP = 'R' AND p.EMP_PAY_ALLWAMT <> 0
                    )
                    AND EMP_PAY_ALLWAMT <> 0
                """)
                cursor.execute("""
                    UPDATE EMP_PAY 
                    SET EMP_PAY_ALLWRATE = 0, EMP_PAY_ALLWAMT = 0 
                    WHERE EMP_PAY_ALLW = 1014 AND EMP_PAY_ALLWAMT <> 0
                """)

            messages.success(request, f"Payroll Period {sal_period_id} created successfully.")
            return redirect('sal_period_list')

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            messages.error(request, f"Error occurred: {str(e)}")
            return redirect('sal_period_list')

    # Display existing periods (optional: limit to top 5)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SAL_PERIOD_ID, SAL_PERIOD_YR, SAL_PERIOD_MONTH, 
                   SAL_PERIOD_FROM, SAL_PERIOD_TO, SAL_PERIOD_DAYsCOUNT, 
                   SAL_PERIOD_FLG, SAL_PERIOD_DT
            FROM SAL_PERIOD
            ORDER BY SAL_PERIOD_ID DESC
            FETCH FIRST 5 ROWS ONLY
        """)
        periods = cursor.fetchall()
    
    context = {
        'sal_periods': [
            {
                'sal_period_id': row[0],
                'sal_period_yr': row[1],
                'sal_period_month': row[2],
                'sal_period_from': row[3],
                'sal_period_to': row[4],
                'sal_period_dayscount': row[5],
                'sal_period_flg': row[6],
                'sal_period_dt': row[7]
            } for row in periods
        ]
    }

    return render(request, 'myapp/payroll_period.html', context)

@login_required
def update_attendance(request, sal_period_id):
    try:
        with connection.cursor() as cursor:
            # Get the period's FROM and TO dates
            cursor.execute("""
                SELECT SAL_PERIOD_FROM, SAL_PERIOD_TO
                FROM SAL_PERIOD
                WHERE SAL_PERIOD_ID = :1
            """, [sal_period_id])
            row = cursor.fetchone()
            if not row:
                messages.error(request, "Payroll period not found.")
                return redirect('sal_period_list')

            start_date, end_date = row
            days_count = (end_date - start_date).days + 1

            # Step 1: Clear previous attendance for the period (optional, Oracle Forms logic may not allow duplicates)
            cursor.execute("DELETE FROM ATT WHERE ATT_PERIOD = :1", [sal_period_id])

            # Step 2: Re-insert attendance
            cursor.execute("SELECT EMP_NO, EMP_MGR FROM EMP WHERE EMP_FLG = 'O'")
            employees = cursor.fetchall()

            for emp_no, emp_mgr in employees:
                for i in range(days_count):
                    att_date = start_date + timedelta(days=i)
                    att_status = 'H' if att_date.weekday() == 6 else 'P'
                    cursor.execute("""
                        INSERT INTO ATT (
                            ATT_PERIOD, ATT_DT, ATT_EMP, ATT_STATUS, ATT_HOLIDAY_TYP,
                            ATT_LEAVE_TYP, ATT_OVERTIME_TYP, ATT_POSTED_BY, ATT_APPROVED_BY,
                            ATT_ACCEPTED_BY, ATT_FLG, ATT_REMARKS
                        ) VALUES (:1, :2, :3, :4, 'N', 0, 'N', :5, 1500001, NULL, 'V', NULL)
                    """, [sal_period_id, att_date, emp_no, att_status, emp_mgr])

            # Step 3: Update leave-based status
            cursor.execute("""
                UPDATE ATT
                SET ATT_STATUS = 'L',
                    ATT_LEAVE_TYP = (
                        SELECT EMP_LEAV_TYP FROM EMP_LEAV
                        WHERE EMP_LEAV_EMP = ATT.ATT_EMP
                        AND ATT.ATT_DT BETWEEN EMP_LEAV_FROM AND EMP_LEAV_TO
                        FETCH FIRST 1 ROWS ONLY
                    )
                WHERE EXISTS (
                    SELECT 1 FROM EMP_LEAV
                    WHERE EMP_LEAV_EMP = ATT.ATT_EMP
                    AND ATT.ATT_DT BETWEEN EMP_LEAV_FROM AND EMP_LEAV_TO
                ) AND ATT_PERIOD = :1
            """, [sal_period_id])

            # Step 4: Mark terminated employees as 'A'
            cursor.execute("""
                UPDATE ATT
                SET ATT_STATUS = 
                    CASE 
                        WHEN EXISTS (
                            SELECT 1 FROM EMP 
                            WHERE EMP.EMP_NO = ATT.ATT_EMP
                            AND (EMP.EMP_LEAVING_DT IS NULL OR EMP.EMP_LEAVING_DT >= ATT.ATT_DT)
                        ) THEN 
                            CASE WHEN TO_CHAR(ATT.ATT_DT, 'DAY') LIKE 'SUNDAY%' THEN 'H' ELSE 'P' END
                        ELSE 'A' 
                    END
                WHERE ATT_PERIOD = :1
            """, [sal_period_id])

        messages.success(request, f"Attendance successfully updated for period {sal_period_id}.")
    except Exception as e:
        messages.error(request, f"Error updating attendance: {e}")
    return redirect('sal_period_list')

###############################  Attendence Marking & Details View, and Approval View ####################################

@login_required
def attendance_marking_view(request):
    selected_month = request.GET.get('month')
    selected_uc = request.GET.get('uc')
    selected_section = request.GET.get('section')
    selected_employee = request.GET.get('employee')  # ✅ New employee filter

    records = []
    months, ucs, sections, employees = [], [], [], []  # ✅ Added employees list

    # ✅ Get manager ID from custom auth user
    manager_id = request.user.USER_ID

    # Month dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TO_CHAR(sal_period_month, 'YYYY-MM') AS value,
                   TO_CHAR(sal_period_month, 'Month YYYY') AS label
            FROM sal_period
            GROUP BY TO_CHAR(sal_period_month, 'YYYY-MM'), TO_CHAR(sal_period_month, 'Month YYYY')
            ORDER BY TO_CHAR(sal_period_month, 'YYYY-MM') DESC
        """)
        months = [{'value': row[0], 'label': row[1].strip()} for row in cursor.fetchall()]

    # UC dropdown (areas managed by this manager)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT a.area_id, a.area_desc 
            FROM area a
            WHERE a.area_id IN (
                SELECT e.emp_duty_loc 
                FROM emp e 
                WHERE e.emp_mgr = %s
            )
            ORDER BY a.area_desc
        """, [manager_id])
        ucs = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    # Section dropdown (departments managed by this manager)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT d.deptt_id, d.deptt_desc
            FROM deptt d
            WHERE d.deptt_id IN (
                SELECT e.emp_deptt
                FROM emp e
                WHERE e.emp_mgr = %s
            )
            ORDER BY d.deptt_desc
        """, [manager_id])
        sections = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    # ✅ Employee dropdown (employees managed by this manager)
    employee_sql = """
        SELECT e.emp_no, e.emp_name, a.area_desc, d.deptt_desc
        FROM emp e
        LEFT JOIN area a ON e.emp_duty_loc = a.area_id
        LEFT JOIN deptt d ON e.emp_deptt = d.deptt_id
        WHERE e.emp_mgr = %s
    """
    employee_params = [manager_id]

    # ✅ Filter employees based on selected UC and Section
    if selected_uc:
        employee_sql += " AND e.emp_duty_loc = %s"
        employee_params.append(selected_uc)

    if selected_section:
        employee_sql += " AND e.emp_deptt = %s"
        employee_params.append(selected_section)

    employee_sql += " ORDER BY e.emp_name"

    with connection.cursor() as cursor:
        cursor.execute(employee_sql, employee_params)
        employees = [
            {
                'emp_no': row[0], 
                'name': f"{row[1]} ({row[0]})",  # Display name with emp_no
                'uc': row[2] or 'N/A',
                'section': row[3] or 'N/A'
            } 
            for row in cursor.fetchall()
        ]

    # Fetch employee records if month is selected
    if selected_month:
        sql = """
            SELECT e.emp_no, 
                   e.emp_name, 
                   e.emp_fname, 
                   e.emp_cnic,
                   j.job_desc AS designation, 
                   e.emp_grade, 
                   a.area_desc AS uc
            FROM emp e
            LEFT JOIN job j ON e.emp_job = j.job_id
            LEFT JOIN area a ON e.emp_duty_loc = a.area_id
            WHERE e.emp_mgr = %s
        """
        params = [manager_id]

        if selected_uc:
            sql += " AND e.emp_duty_loc = %s"
            params.append(selected_uc)

        if selected_section:
            sql += " AND e.emp_deptt = %s"
            params.append(selected_section)

        # ✅ Add employee filter
        if selected_employee:
            sql += " AND e.emp_no = %s"
            params.append(selected_employee)

        sql += " ORDER BY e.emp_no"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            records = [
                {
                    'emp_no': row[0],
                    'emp_name': row[1],
                    'father_name': row[2],
                    'cnic': row[3],
                    'designation': row[4],
                    'grade': row[5],
                    'uc': row[6]
                }
                for row in rows
            ]

    return render(request, 'myapp/attendence_marking.html', {
        'months': months,
        'ucs': ucs,
        'sections': sections,
        'employees': employees,  # ✅ Pass employees to template
        'records': records,
        'selected_month': selected_month,
        'selected_uc': selected_uc,
        'selected_section': selected_section,
        'selected_employee': selected_employee  # ✅ Pass selected employee
    })

@login_required
def attendance_detail_view(request, emp_no, month):
    with connection.cursor() as cursor:
        # Fetch employee data
        cursor.execute("""
            SELECT e.emp_no, e.emp_name, e.emp_fname, j.job_desc
            FROM emp e
            LEFT JOIN job j ON e.emp_job = j.job_id
            WHERE e.emp_no = %s
        """, [emp_no])
        emp_row = cursor.fetchone()
        if not emp_row:
            return render(request, 'myapp/attendence_details.html', {'error': 'Employee not found.'})

        emp_data = {
            'emp_no': emp_row[0],
            'emp_name': emp_row[1],
            'emp_fname': emp_row[2],
            'designation': emp_row[3],
        }

        # Get payroll period details
        cursor.execute("""
            SELECT sal_period_id, sal_period_from, sal_period_to
            FROM sal_period
            WHERE TO_CHAR(sal_period_month, 'YYYY-MM') = %s
        """, [month])
        period_row = cursor.fetchone()
        if not period_row:
            return render(request, 'myapp/attendence_details.html', {'error': 'Payroll period not found.'})

        period_data = {
            'period_id': period_row[0],
            'period_from': period_row[1],
            'period_to': period_row[2],
        }

        # Fetch leave types
        cursor.execute("SELECT leav_typid, leav_typdesc FROM leav_typ")
        leave_types_list = cursor.fetchall()
        leave_desc_to_id = {desc.upper(): id for id, desc in leave_types_list}
        leave_id_to_desc = {id: desc for id, desc in leave_types_list}

        if request.method == 'POST':
            cursor.execute("""
                SELECT att_dt
                FROM att
                WHERE att_emp = %s AND att_dt BETWEEN %s AND %s
                ORDER BY att_dt
            """, [emp_no, period_data['period_from'], period_data['period_to']])
            att_dates = [row[0] for row in cursor.fetchall()]

            for index, att_date in enumerate(att_dates, start=1):
                status = request.POST.get(f'status_{index}', '').strip()
                leave_id = request.POST.get(f'leave_{index}', '').strip()
                overtime = request.POST.get(f'overtime_{index}', '').strip()

                update_fields = []
                update_values = []

                if status in ['A', 'P', 'L', 'H']:
                    update_fields.append("att_status = %s")
                    update_values.append(status)

                if leave_id.isdigit():
                    update_fields.append("att_leave_typ = %s")
                    update_values.append(int(leave_id))
                else:
                    update_fields.append("att_leave_typ = %s")
                    update_values.append(0)

                if overtime in ['OVT', 'DOVT']:
                    update_fields.append("att_overtime_typ = %s")
                    update_values.append('O')
                    
                elif overtime == 'NOOVT' or not overtime:
                    update_fields.append("att_overtime_typ = %s")
                    update_values.append('N')

                if update_fields:
                    update_values.extend([emp_no, att_date])
                    query = f"""
                        UPDATE att
                        SET {', '.join(update_fields)}
                        WHERE att_emp = %s AND att_dt = %s
                    """
                    cursor.execute(query, update_values)

            # ✅ Success message
            messages.success(request, 'Attendance updated and submitted for Acceptance.')
            return redirect('attendance_detail', emp_no=emp_no, month=month)

        # GET request
        cursor.execute("""
            SELECT att_dt, att_status, att_leave_typ, att_overtime_typ
            FROM att
            WHERE att_emp = %s AND att_dt BETWEEN %s AND %s
            ORDER BY att_dt
        """, [emp_no, period_data['period_from'], period_data['period_to']])
        attendance_rows = cursor.fetchall()

        date_entries = []
        for row in attendance_rows:
            att_date, att_status, att_leave_typ, att_overtime_typ = row
            leave_desc = leave_id_to_desc.get(att_leave_typ, '')
            date_entries.append({
                'date': att_date,
                'status': att_status,
                'leave_id': att_leave_typ,
                'leave_desc': leave_desc,
                'overtime': att_overtime_typ or ''
            })

    return render(request, 'myapp/attendence_details.html', {
        'emp': emp_data,
        'period': period_data,
        'selected_month': month,
        'date_entries': date_entries,
        'leave_types': leave_types_list,
    }) 

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
import json

@login_required
def attendance_approval_summary(request):
    selected_period = request.GET.get('period')
    selected_zm = request.GET.get('zm_id')

    periods = []
    zm_list = []
    summary_data = []
    previous_summary_data = []
    comparison_data = []
    period_details = None
    previous_period_details = None
    chart_data = {}
    rejected_records_count = 0  # New variable for rejected records
    has_pending_approvals = False  # New variable to check pending approvals

    ZM_AM_MAPPING = {
        '1200021': {'name': 'Zone A', 'am_id': '1500002'},
        '1200026': {'name': 'Zone B', 'am_id': '1500003'},
        '1200030': {'name': 'Zone C', 'am_id': '1500004'},
        '1200015': {'name': 'Zone D', 'am_id': '1500005'},
        '1200011': {'name': 'Zone E', 'am_id': '1204190'},
        '1500008': {'name': 'HO',      'am_id': '1500008'},
    }

    # Get Top 5 Salary Periods
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sal_period_id, TO_CHAR(sal_period_month, 'Month YYYY')
            FROM sal_period
            ORDER BY sal_period_month DESC
            FETCH FIRST 5 ROWS ONLY
        """)
        periods = [{'id': row[0], 'label': row[1].strip()} for row in cursor.fetchall()]

    # Get ZM list
    zm_ids = tuple(ZM_AM_MAPPING.keys())
    placeholders = ','.join(['%s'] * len(zm_ids))

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT e.emp_no, e.emp_name, j.job_desc
            FROM emp e
            LEFT JOIN job j ON j.job_id = e.emp_job
            WHERE e.emp_no IN ({placeholders})
        """, zm_ids)
        zm_details = {str(row[0]): {'name': row[1], 'desc': row[2]} for row in cursor.fetchall()}

    for zm_id, mapping in ZM_AM_MAPPING.items():
        detail = zm_details.get(zm_id, {'name': '', 'desc': ''})
        zm_list.append({
            'id': zm_id,
            'name': detail['name'],
            'desc': detail['desc'],
            'zone': mapping['name']
        })

    # Fetch period metadata (start date, end date, days count)
    if selected_period:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    TO_CHAR(sal_period_from, 'DD-Mon-YYYY') as date_from,
                    TO_CHAR(sal_period_to, 'DD-Mon-YYYY') as date_to,
                    sal_period_dayscount,
                    TO_CHAR(sal_period_month, 'Month YYYY') as month_label,
                    sal_period_flg
                FROM sal_period
                WHERE sal_period_id = %s
            """, [selected_period])
            row = cursor.fetchone()
            if row:
                period_details = {
                    'from': row[0],
                    'to': row[1],
                    'days': row[2],
                    'month': row[3].strip(),
                    'status': row[4]
                }

        # Get previous period details for comparison
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    sal_period_id,
                    TO_CHAR(sal_period_from, 'DD-Mon-YYYY') as date_from,
                    TO_CHAR(sal_period_to, 'DD-Mon-YYYY') as date_to,
                    sal_period_dayscount,
                    TO_CHAR(sal_period_month, 'Month YYYY') as month_label,
                    sal_period_flg
                FROM sal_period
                WHERE sal_period_month < (SELECT sal_period_month FROM sal_period WHERE sal_period_id = %s)
                ORDER BY sal_period_month DESC
                FETCH FIRST 1 ROWS ONLY
            """, [selected_period])
            row = cursor.fetchone()
            if row:
                previous_period_id = row[0]
                previous_period_details = {
                    'id': previous_period_id,
                    'from': row[1],
                    'to': row[2],
                    'days': row[3],
                    'month': row[4].strip(),
                    'status': row[5]
                }

    # Fetch summary only if both filters are selected
    if selected_period and selected_zm:
        am_id = ZM_AM_MAPPING.get(selected_zm, {}).get('am_id')
        if am_id:
            # Check for rejected records (status 'J') for this ZM's employees
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM att a
                    JOIN emp e ON a.att_emp = e.emp_no
                    WHERE a.att_period = %s 
                    AND a.att_flg = 'J'
                    AND e.emp_mgr = %s
                """, [selected_period, am_id])
                rejected_records_count = cursor.fetchone()[0]

            # Check for pending approvals (status 'V')
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM att a
                    JOIN emp e ON a.att_emp = e.emp_no
                    WHERE a.att_period = %s 
                    AND a.att_flg = 'V'
                    AND e.emp_mgr = %s
                """, [selected_period, am_id])
                pending_count = cursor.fetchone()[0]
                has_pending_approvals = pending_count > 0

            # Current period summary
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        d.deptt_desc AS section,
                        COUNT(DISTINCT e.emp_no) AS total_employees,
                        COUNT(a.att_status) AS total_attendance_marked,
                        SUM(CASE WHEN a.att_status = 'A' THEN 1 ELSE 0 END) AS absent_count,
                        SUM(CASE WHEN a.att_status = 'L' THEN 1 ELSE 0 END) AS leave_count
                    FROM emp e
                    JOIN deptt d ON e.emp_deptt = d.deptt_id
                    LEFT JOIN att a ON a.att_emp = e.emp_no AND a.att_period = %s
                    WHERE e.emp_mgr = %s
                    GROUP BY d.deptt_desc
                    ORDER BY d.deptt_desc
                """, [selected_period, am_id])

                summary_data = [
                    {
                        'section': row[0],
                        'total_employees': row[1],
                        'total_attendance': row[2],
                        'absent': row[3],
                        'leave': row[4]
                    }
                    for row in cursor.fetchall()
                ]

            # Previous period summary (if previous period exists)
            if previous_period_details:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            d.deptt_desc AS section,
                            COUNT(DISTINCT e.emp_no) AS total_employees,
                            COUNT(a.att_status) AS total_attendance_marked,
                            SUM(CASE WHEN a.att_status = 'A' THEN 1 ELSE 0 END) AS absent_count,
                            SUM(CASE WHEN a.att_status = 'L' THEN 1 ELSE 0 END) AS leave_count
                        FROM emp e
                        JOIN deptt d ON e.emp_deptt = d.deptt_id
                        LEFT JOIN att a ON a.att_emp = e.emp_no AND a.att_period = %s
                        WHERE e.emp_mgr = %s
                        GROUP BY d.deptt_desc
                        ORDER BY d.deptt_desc
                    """, [previous_period_details['id'], am_id])

                    previous_summary_data = [
                        {
                            'section': row[0],
                            'total_employees': row[1],
                            'total_attendance': row[2],
                            'absent': row[3],
                            'leave': row[4]
                        }
                        for row in cursor.fetchall()
                    ]

                # Create comparison data
                prev_dict = {item['section']: item for item in previous_summary_data}
                
                for current in summary_data:
                    section = current['section']
                    prev = prev_dict.get(section, {
                        'total_employees': 0,
                        'total_attendance': 0,
                        'absent': 0,
                        'leave': 0
                    })
                    
                    comparison_data.append({
                        'section': section,
                        'current': current,
                        'previous': prev,
                        'diff_employees': current['total_employees'] - prev['total_employees'],
                        'diff_attendance': current['total_attendance'] - prev['total_attendance'],
                        'diff_absent': current['absent'] - prev['absent'],
                        'diff_leave': current['leave'] - prev['leave']
                    })

            # Prepare chart data for JSON serialization
            if summary_data:
                # Aggregate totals for pie chart
                total_attendance = sum(item['total_attendance'] for item in summary_data)
                total_absent = sum(item['absent'] for item in summary_data)
                total_leave = sum(item['leave'] for item in summary_data)
                
                chart_data = {
                    'sections': [item['section'] for item in summary_data],
                    'attendance': [item['total_attendance'] for item in summary_data],
                    'absent': [item['absent'] for item in summary_data],
                    'leave': [item['leave'] for item in summary_data],
                    'employees': [item['total_employees'] for item in summary_data],
                    'pie_data': {
                        'attendance': total_attendance,
                        'absent': total_absent,
                        'leave': total_leave
                    }
                }
                
                # Add comparison data for trend chart if available
                if comparison_data:
                    chart_data['comparison'] = {
                        'sections': [item['section'] for item in comparison_data],
                        'current_attendance': [item['current']['total_attendance'] for item in comparison_data],
                        'previous_attendance': [item['previous']['total_attendance'] for item in comparison_data],
                        'current_absent': [item['current']['absent'] for item in comparison_data],
                        'previous_absent': [item['previous']['absent'] for item in comparison_data]
                    }

    return render(request, 'myapp/attendence_approval.html', {
        'periods': periods,
        'zm_list': zm_list,
        'selected_period': selected_period,
        'selected_zm': selected_zm,
        'summary_data': summary_data,
        'previous_summary_data': previous_summary_data,
        'comparison_data': comparison_data,
        'period_details': period_details,
        'previous_period_details': previous_period_details,
        'chart_data': chart_data,
        'rejected_records_count': rejected_records_count,  # Pass to template
        'has_pending_approvals': has_pending_approvals,  # Pass to template
    })

@login_required
@require_POST
@csrf_exempt
def approve_attendance(request):
    """
    Approve attendance by updating att_flg from 'V' to 'A' for employees under selected ZM
    """
    try:
        # Debug logging
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request body: {request.body}")
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid JSON data: {str(e)}'
                }, status=400)
        else:
            # Handle form data
            data = {
                'period': request.POST.get('period'),
                'zm_id': request.POST.get('zm_id')
            }
        
        selected_period = data.get('period')
        selected_zm = data.get('zm_id')
        
        print(f"Selected period: {selected_period}")
        print(f"Selected ZM: {selected_zm}")
        
        if not selected_period or not selected_zm:
            return JsonResponse({
                'success': False,
                'message': 'Period and Zone Manager are required'
            }, status=400)

        ZM_AM_MAPPING = {
            '1200021': {'name': 'Zone A', 'am_id': '1500002'},
            '1200026': {'name': 'Zone B', 'am_id': '1500003'},
            '1200030': {'name': 'Zone C', 'am_id': '1500004'},
            '1200015': {'name': 'Zone D', 'am_id': '1500005'},
            '1200011': {'name': 'Zone E', 'am_id': '1204190'},
            '1500008': {'name': 'HO',      'am_id': '1500008'},
        }

        am_id = ZM_AM_MAPPING.get(selected_zm, {}).get('am_id')
        if not am_id:
            return JsonResponse({
                'success': False,
                'message': 'Invalid Zone Manager selected'
            }, status=400)

        # First, check if there are any records to update
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM att a
                JOIN emp e ON a.att_emp = e.emp_no
                WHERE a.att_period = %s 
                AND a.att_flg = 'V'
                AND e.emp_mgr = %s
            """, [selected_period, am_id])
            
            pending_count = cursor.fetchone()[0]
            print(f"Pending records found: {pending_count}")

        if pending_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'No pending attendance records found to approve'
            })

        # Update attendance flag from 'V' to 'A' for employees under the selected AM
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE att 
                SET att_flg = 'A'
                WHERE att_period = %s 
                AND att_flg = 'V'
                AND att_emp IN (
                    SELECT emp_no 
                    FROM emp 
                    WHERE emp_mgr = %s
                )
            """, [selected_period, am_id])
            
            updated_count = cursor.rowcount
            print(f"Updated records: {updated_count}")

        # Commit the transaction explicitly
        connection.commit()

        if updated_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully approved attendance for {updated_count} records',
                'updated_count': updated_count
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No records were updated. They may have already been approved.'
            })

    except Exception as e:
        print(f"Error in approve_attendance: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
@require_POST
@csrf_exempt
def return_for_correction(request):
    """
    Return rejected attendance records back to Assistant Manager for correction
    Changes att_flg from 'J' to 'V' for rejected records
    """
    try:
        # Debug logging
        print(f"Return for correction - Request method: {request.method}")
        print(f"Request body: {request.body}")
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid JSON data: {str(e)}'
                }, status=400)
        else:
            # Handle form data
            data = {
                'period': request.POST.get('period'),
                'zm_id': request.POST.get('zm_id')
            }
        
        selected_period = data.get('period')
        selected_zm = data.get('zm_id')
        
        print(f"Selected period: {selected_period}")
        print(f"Selected ZM: {selected_zm}")
        
        if not selected_period or not selected_zm:
            return JsonResponse({
                'success': False,
                'message': 'Period and Zone Manager are required'
            }, status=400)

        ZM_AM_MAPPING = {
            '1200021': {'name': 'Zone A', 'am_id': '1500002'},
            '1200026': {'name': 'Zone B', 'am_id': '1500003'},
            '1200030': {'name': 'Zone C', 'am_id': '1500004'},
            '1200015': {'name': 'Zone D', 'am_id': '1500005'},
            '1200011': {'name': 'Zone E', 'am_id': '1204190'},
            '1500008': {'name': 'HO',      'am_id': '1500008'},
        }

        am_id = ZM_AM_MAPPING.get(selected_zm, {}).get('am_id')
        if not am_id:
            return JsonResponse({
                'success': False,
                'message': 'Invalid Zone Manager selected'
            }, status=400)

        # Check if there are any rejected records to return
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM att a
                JOIN emp e ON a.att_emp = e.emp_no
                WHERE a.att_period = %s 
                AND a.att_flg = 'J'
                AND e.emp_mgr = %s
            """, [selected_period, am_id])
            
            rejected_count = cursor.fetchone()[0]
            print(f"Rejected records found: {rejected_count}")

        if rejected_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'No rejected attendance records found to return for correction'
            })

        # Update attendance flag from 'J' to 'V' for rejected records
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE att 
                SET att_flg = 'V'
                WHERE att_period = %s 
                AND att_flg = 'J'
                AND att_emp IN (
                    SELECT emp_no 
                    FROM emp 
                    WHERE emp_mgr = %s
                )
            """, [selected_period, am_id])
            
            updated_count = cursor.rowcount
            print(f"Returned records: {updated_count}")

        # Commit the transaction explicitly
        connection.commit()

        if updated_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully returned {updated_count} rejected records for correction',
                'updated_count': updated_count
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No records were returned. Please try again.'
            })

    except Exception as e:
        print(f"Error in return_for_correction: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)
    
############################### Attendence Acceptance View #############################################

@login_required
def attendance_acceptance_view(request):
    selected_period_id = request.GET.get('sal_period_id')

    # Fetch all salary periods in ascending order
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sal_period_id, sal_period_month, sal_period_yr
            FROM sal_period
            ORDER BY sal_period_id DESC FETCH FIRST 5 ROWS ONLY
        """)
        periods = [
            {'sal_period_id': row[0], 'sal_period_month': row[1].date(), 'sal_period_yr': row[2]}
            for row in cursor.fetchall()
        ]

    selected_period = None
    total_employees = 0
    managers = []
    approver = {}

    if selected_period_id:
        # Ensure selected_period_id is an integer (since it's from GET, it could be a string)
        selected_period_id = int(selected_period_id)

        with connection.cursor() as cursor:
            # Fetch specific period data
            cursor.execute("""
                SELECT sal_period_month, sal_period_dayscount, sal_period_from, sal_period_to, sal_period_flg
                FROM sal_period WHERE sal_period_id = %s
            """, [selected_period_id])
            row = cursor.fetchone()
            if row:
                # Stripping the time from the date fields
                sal_period_from = row[2].date() if row[2] else None
                sal_period_to = row[3].date() if row[3] else None

                selected_period = {
                    'sal_period_id': selected_period_id,
                    'sal_period_month': row[0].date(),
                    'sal_period_dayscount': row[1],
                    'sal_period_from': sal_period_from,
                    'sal_period_to': sal_period_to,
                    'sal_period_flg': row[4]
                }

            # Get the total number of employees for the selected period
            cursor.execute("""
                SELECT COUNT(DISTINCT att_emp)
                FROM att WHERE att_period = %s
            """, [selected_period_id])
            total_employees = cursor.fetchone()[0]

            # Get the managers for the selected period
            cursor.execute("""
                SELECT DISTINCT e.emp_no, e.emp_name
                FROM emp e
                WHERE e.emp_no IN (
                    SELECT DISTINCT emp_mgr FROM emp WHERE emp_no IN (
                        SELECT DISTINCT att_emp FROM att WHERE att_period = %s
                    )
                )
            """, [selected_period_id])
            managers = [{'emp_no': row[0], 'emp_name': row[1]} for row in cursor.fetchall()]

            # Fetch the approver (static ID: 1500001)
            cursor.execute("""
                SELECT user_id, user_desc
                FROM users WHERE user_id = '1500001'
            """)
            row = cursor.fetchone()
            if row:
                approver = {
                    'approver_id': row[0],
                    'approver_name': row[1]
                }

    context = {
        'sal_periods': periods,
        'selected_period_id': selected_period_id,
        'selected_period': selected_period,
        'total_employees': total_employees,
        'managers': managers,
        'approver': approver,
    }

    return render(request, 'myapp/attendence_acceptance.html', context)

# Attendance Acceptance Details 
@login_required
def attendance_summary_detail(request, manager_id, period_id):
    user_id = str(request.session.get('user_id'))  # Assuming user_id is in session

    with connection.cursor() as cursor:
        # Fetch period info
        cursor.execute("""
            SELECT sal_period_from, sal_period_to, sal_period_dayscount
            FROM sal_period
            WHERE sal_period_id = %s
        """, [period_id])
        period_data = cursor.fetchone()

        if not period_data:
            messages.error(request, "Invalid period selected.")
            return redirect('attendance_acceptance')

        period_from, period_to, period_dayscount = period_data
        days_count = (period_to - period_from).days + 1

        # Count employees and attendance
        cursor.execute("""
            SELECT 
                NVL((SELECT COUNT(DISTINCT att_emp) FROM att 
                     WHERE att_posted_by = %s AND att_period = %s), 0),
                NVL((SELECT COUNT(DISTINCT emp_no) FROM emp 
                     WHERE emp_mgr = %s AND emp_flg LIKE '%%O%%'), 0)
            FROM dual
        """, [manager_id, period_id, manager_id])
        att_emp_count, tagged_count = cursor.fetchone()
        diff = tagged_count - att_emp_count

        # Get current attendance flag and approver
        cursor.execute("""
            SELECT att_approved_by, att_flg
            FROM (
                SELECT att_approved_by, att_flg
                FROM att
                WHERE att_period = %s AND att_posted_by = %s
                AND ROWNUM = 1
            )
        """, [period_id, manager_id])
        row = cursor.fetchone()
        att_approved_by = row[0] if row else None
        att_flg = row[1] if row else 'V'

        # Handle form submission
        if request.method == 'POST':
            selected_action = request.POST.get('status')

            if att_flg == 'C':
                messages.info(request, "✅ Attendance already accepted. No further changes allowed.")
                return redirect('attendance_summary_detail', manager_id=manager_id, period_id=period_id)

            # Handle different status changes based on selected radio button
            if selected_action == 'V':  # In Process - only allow if current status allows it
                if att_flg in ['A', 'J']:
                    cursor.execute("""
                        UPDATE att
                        SET att_flg = 'V', att_approved_by = %s
                        WHERE att_period = %s AND att_posted_by = %s
                    """, [user_id, period_id, manager_id])
                    
                    if cursor.rowcount > 0:
                        messages.success(request, "📝 Status updated to In Process.")
                        att_flg = 'V'
                    else:
                        messages.warning(request, "⚠️ No records found to update.")
                else:
                    messages.warning(request, "⚠️ Cannot change to In Process from current status.")
                    
            elif selected_action == 'C':  # Accept
                if att_flg == 'A':  # Only allow acceptance if approved by zonal manager
                    cursor.execute("""
                        UPDATE att
                        SET att_flg = 'C', att_approved_by = %s
                        WHERE att_period = %s AND att_posted_by = %s
                    """, [user_id, period_id, manager_id])
                    
                    if cursor.rowcount > 0:
                        messages.success(request, "✅ Attendance has been accepted successfully.")
                        att_flg = 'C'
                    else:
                        messages.warning(request, "⚠️ No records found to update.")
                else:
                    messages.warning(request, "⚠️ Attendance must be approved by Zonal Manager first (Status: A) to accept.")

            elif selected_action == 'J':  # Reject
                if att_flg == 'A':  # Only allow rejection if approved by zonal manager
                    cursor.execute("""
                        UPDATE att
                        SET att_flg = 'J', att_approved_by = %s
                        WHERE att_period = %s AND att_posted_by = %s
                    """, [user_id, period_id, manager_id])
                    
                    if cursor.rowcount > 0:
                        messages.success(request, "🔁 Attendance has been rejected.")
                        att_flg = 'J'
                    else:
                        messages.warning(request, "⚠️ No records found to update.")
                else:
                    messages.warning(request, "⚠️ Attendance must be approved by Zonal Manager first (Status: A) to reject.")

            return redirect('attendance_summary_detail', manager_id=manager_id, period_id=period_id)

    return render(request, 'myapp/attendence_acceptance_details.html', {
        'manager_id': manager_id,
        'selected_period_id': period_id,
        'days_count': days_count,
        'att_emp_count': att_emp_count,
        'tagged_count': tagged_count,
        'diff': diff,
        'att_flg': att_flg,
        'period_dayscount': period_dayscount,
        'current_user': user_id
    })

################## Payroll Initialization with attendence deduction and income tax as well #################

@csrf_exempt
@login_required
def payroll_initialize_view(request):
    context = {
        'periods': [],
        'employee_details': [],
        'period': {},
        'payroll_entries': [],
        'total_earning': Decimal('0.00'),
        'total_deduction': Decimal('0.00'),
        'net_salary': Decimal('0.00'),
        'employer_pension': Decimal('0.00')
    }

    # Fetch top 5 latest periods
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sal_period_id, TO_CHAR(sal_period_month, 'Mon-YYYY')
            FROM sal_period 
            ORDER BY sal_period_id DESC 
            FETCH FIRST 5 ROWS ONLY
        """)
        context['periods'] = cursor.fetchall()

    period_id = request.GET.get('period_id') or request.POST.get('period_id')
    initialize_requested = 'initialize' in request.POST

    if period_id:
        # Load selected period details
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_month, sal_period_dayscount, sal_period_from, sal_period_to, sal_period_flg
                FROM sal_period 
                WHERE sal_period_id = %s
            """, [period_id])
            row = cursor.fetchone()

        if row:
            context['period'] = {
                'period_id': period_id,
                'period_month': row[0].strftime('%Y-%m-%d'),
                'period_days': row[1],
                'period_from': row[2].strftime('%Y-%m-%d'),
                'period_to': row[3].strftime('%Y-%m-%d'),
                'period_flg': row[4]
            }

        # Check if payroll already exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM payroll WHERE payroll_period = %s", [period_id])
            record_count = cursor.fetchone()[0]
            context['records_exist'] = record_count > 0

        # Check if all attendance records for this period have been accepted (att_flg = 'C')
        if request.method == 'POST' and initialize_requested and record_count == 0:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM att 
                    WHERE att_period = %s 
                    AND att_flg != 'C'
                """, [period_id])
                pending_attendance_count = cursor.fetchone()[0]
                
                if pending_attendance_count > 0:
                    messages.error(request, f'Cannot initialize payroll. {pending_attendance_count} attendance records are not yet accepted. All attendance must be accepted before payroll initialization.')
                    return render(request, 'myapp/payroll_initiallization.html', context)

        # Insert only if it's a POST request with initialize button clicked and no payroll exists yet
        if request.method == 'POST' and initialize_requested and record_count == 0:
            try:
                with connection.cursor() as cursor:
                    # Set allowance IDs
                    off_day_allw_id = 1012
                    income_tax_allw_id = 1058

                    # Get all active employees
                    cursor.execute("""
                        SELECT 
                            e.emp_no, e.emp_name, e.emp_job, e.emp_deptt, e.emp_duty_loc, e.emp_grade,
                            e.emp_pay_subgrp, e.emp_typ, e.emp_saltyp, e.emp_bank,
                            e.emp_bank_acc, e.emp_pay_mode, e.emp_flg, e.emp_mgr
                        FROM emp e
                        WHERE e.emp_flg = 'O'
                          AND e.emp_no <> 1009999
                        ORDER BY e.emp_no
                    """)
                    all_active_employees = {row[0]: row for row in cursor.fetchall()}
                    
                    # Fetch employee allowances
                    cursor.execute("""
                        SELECT  
                            p.emp_pay_emp, e.emp_name, p.emp_pay_allw, a.allw_typ, a.allw_desc, 
                            e.emp_saltyp, ROUND(p.emp_pay_allwrate), ROUND(NVL(p.emp_pay_allwamt, 0)), 
                            t.emp_saltyp_freq, a.allw_earn_deduc, 
                            e.emp_deptt, e.emp_job, e.emp_grade, e.emp_typ, e.emp_duty_loc,
                            e.emp_bank, e.emp_bank_acc, e.emp_pay_mode, e.emp_pay_subgrp, 
                            e.emp_mgr, e.emp_flg
                        FROM emp_pay p
                        JOIN allw a ON p.emp_pay_allw = a.allw_id
                        JOIN emp e ON p.emp_pay_emp = e.emp_no
                        JOIN emp_saltyp t ON e.emp_saltyp = t.emp_saltyp_id
                        WHERE e.emp_flg = 'O'
                          AND p.emp_pay_allwrule = 1
                          AND e.emp_no <> 1009999
                        ORDER BY e.emp_no, p.emp_pay_allw
                    """)
                    emp_allws = cursor.fetchall()
                    
                    # Track earnings and inserted allowances
                    employee_earnings = {}
                    employees_with_entries = set()
                    employee_allowances = {}
                    
                    # First pass: Create regular payroll entries (excluding off days)
                    for emp in emp_allws:
                        (
                            emp_no, emp_name, allw_id, allw_typ, allw_desc, saltyp,
                            rate, amt, freq, earn_deduc,
                            deptt, job, grade, emptyp, duty_loc,
                            bank, bank_acc, pay_mode, pay_subgrp,
                            emp_mgr, emp_flg
                        ) = emp

                        employees_with_entries.add(emp_no)
                        
                        if emp_no not in employee_allowances:
                            employee_allowances[emp_no] = set()
                        
                        if allw_id in employee_allowances[emp_no]:
                            continue
                        
                        employee_allowances[emp_no].add(allw_id)
                        
                        rate = Decimal(rate or 0)
                        amt = Decimal(amt or 0)
                        days = int(context['period']['period_days'])
                        
                        if allw_id == off_day_allw_id:
                            continue
                        
                        try:
                            earn_deduc_val = int(earn_deduc)
                        except (ValueError, TypeError):
                            earn_deduc_val = 0

                        if saltyp == 2 and allw_typ == 'F':
                            amount = rate * Decimal(days)
                        elif allw_typ == 'D':
                            amount = amt
                        elif allw_typ in ('P', 'E', 'I', 'R'):
                            amount = amt
                        else:
                            amount = amt
                        
                        if earn_deduc_val == 1:
                            if emp_no not in employee_earnings:
                                employee_earnings[emp_no] = Decimal('0.00')
                            employee_earnings[emp_no] += amount
                        
                        cursor.execute("""
                            INSERT INTO payroll (
                                payroll_period, payroll_emp, payroll_allw, payroll_duty_days,
                                payroll_allwrate, payroll_flg, payroll_arrears, payroll_allwamt,
                                payroll_emp_job, payroll_emp_deptt, payroll_emp_pop, payroll_emp_grd,
                                payroll_pay_subgrp, payroll_emptyp, payroll_emp_saltyp, payroll_emp_bank,
                                payroll_emp_bankacc, payroll_emp_paymode, payroll_emp_flg, payroll_emp_mgr
                            ) VALUES (
                                %s, %s, %s, %s,
                                %s, 'N', 0, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s
                            )
                        """, [
                            period_id, emp_no, allw_id, days,
                            rate, amount,
                            job, deptt, duty_loc, grade,
                            pay_subgrp, emptyp, saltyp, bank,
                            bank_acc, pay_mode, emp_flg, emp_mgr
                        ])
                    
                    # Second pass: Initialize Off Days entries for all active employees (always insert with amount 0)
                    for emp_no, emp in all_active_employees.items():
                        (emp_no, emp_name, job, deptt, duty_loc, grade,
                         pay_subgrp, emptyp, saltyp, bank,
                         bank_acc, pay_mode, emp_flg, emp_mgr) = emp
                        
                        days = int(context['period']['period_days'])
                        
                        # Always insert off days record for all employees, even if they already have other allowances
                        cursor.execute("""
                            INSERT INTO payroll (
                                payroll_period, payroll_emp, payroll_allw, payroll_duty_days,
                                payroll_allwrate, payroll_flg, payroll_arrears, payroll_allwamt,
                                payroll_emp_job, payroll_emp_deptt, payroll_emp_pop, payroll_emp_grd,
                                payroll_pay_subgrp, payroll_emptyp, payroll_emp_saltyp, payroll_emp_bank,
                                payroll_emp_bankacc, payroll_emp_paymode, payroll_emp_flg, payroll_emp_mgr
                            ) VALUES (
                                %s, %s, %s, %s,
                                0, 'N', 0, 0,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s
                            )
                        """, [
                            period_id, emp_no, off_day_allw_id, days,
                            job, deptt, duty_loc, grade,
                            pay_subgrp, emptyp, saltyp, bank,
                            bank_acc, pay_mode, emp_flg, emp_mgr
                        ])
                        
                        if emp_no not in employee_allowances:
                            employee_allowances[emp_no] = set()
                        employee_allowances[emp_no].add(off_day_allw_id)
                    
                    # Third pass: Update Off Days deductions based on attendance for all active employees
                    for emp_no, emp in all_active_employees.items():
                        cursor.execute("""
                            SELECT COUNT(*)
                            FROM att
                            WHERE att_emp = %s
                              AND att_period = %s
                              AND att_status = 'A'
                        """, [emp_no, period_id])
                        absent_days = cursor.fetchone()[0] or 0
                        
                        # Calculate off day deduction amount
                        off_day_deduction = Decimal('0.00')
                        if absent_days > 0:
                            total_earnings = employee_earnings.get(emp_no, Decimal('0.00'))
                            if total_earnings > 0:
                                daily_wage = total_earnings / Decimal('30')
                                off_day_deduction_amount = daily_wage * Decimal(absent_days)
                                # Round to nearest integer (no decimal places)
                                off_day_deduction_amount = off_day_deduction_amount.quantize(Decimal('1'), rounding='ROUND_HALF_UP')
                                off_day_deduction = -off_day_deduction_amount
                        
                        # Update the off days record for this employee (regardless of absent days)
                        cursor.execute("""
                            UPDATE payroll
                            SET payroll_allwamt = %s
                            WHERE payroll_period = %s
                            AND payroll_emp = %s
                            AND payroll_allw = %s
                        """, [
                            off_day_deduction,
                            period_id,
                            emp_no,
                            off_day_allw_id
                        ])
                        
                        if absent_days > 0:
                            print(f"Updated off days deduction for employee {emp_no}: {off_day_deduction} (absent days: {absent_days})")
                        else:
                            print(f"Set off days deduction to 0 for employee {emp_no} (no absent days)")
                    
                    # Fourth pass: Income Tax calculations
                    with connection.cursor() as tax_cursor:
                        for emp_no, emp in all_active_employees.items():
                            days = int(context['period']['period_days'])
                            
                            tax_cursor.execute("""
                                SELECT COUNT(*) 
                                FROM payroll
                                WHERE payroll_period = %s
                                AND payroll_emp = %s
                                AND payroll_allw = %s
                            """, [period_id, emp_no, income_tax_allw_id])
                            
                            tax_entry_exists = tax_cursor.fetchone()[0] > 0
                            
                            try:
                                tax_cursor.execute("""
                                    SELECT WSSCACC.Tax_Calc_V1(:period_id, :emp_no) AS tax_amount
                                    FROM dual
                                """, {
                                    'period_id': int(period_id), 
                                    'emp_no': int(emp_no)
                                })
                                
                                tax_result = tax_cursor.fetchone()
                                
                                print(f"Tax calculation for employee {emp_no}: {tax_result}")
                                
                                if tax_result and tax_result[0] is not None:
                                    tax_amount = Decimal(str(tax_result[0]))
                                else:
                                    tax_amount = Decimal('0.00')
                                    print(f"Warning: Tax calculation returned None for employee {emp_no}")
                            except Exception as e:
                                print(f"Error in tax calculation for employee {emp_no}: {str(e)}")
                                tax_amount = Decimal('0.00')
                            
                            if tax_amount == 0 and not tax_entry_exists:
                                continue
                            
                            tax_deduction = -tax_amount
                            
                            (emp_no, emp_name, job, deptt, duty_loc, grade,
                             pay_subgrp, emptyp, saltyp, bank,
                             bank_acc, pay_mode, emp_flg, emp_mgr) = emp
                            
                            if tax_entry_exists:
                                tax_cursor.execute("""
                                    UPDATE payroll
                                    SET payroll_allwamt = %s,
                                        payroll_duty_days = %s
                                    WHERE payroll_period = %s
                                    AND payroll_emp = %s
                                    AND payroll_allw = %s
                                """, [
                                    tax_deduction,
                                    days,
                                    period_id, 
                                    emp_no, 
                                    income_tax_allw_id
                                ])
                                print(f"Updated tax deduction for employee {emp_no}: {tax_deduction}")
                            else:
                                if emp_no not in employee_allowances:
                                    employee_allowances[emp_no] = set()
                                employee_allowances[emp_no].add(income_tax_allw_id)
                                
                                tax_cursor.execute("""
                                    INSERT INTO payroll (
                                        payroll_period, payroll_emp, payroll_allw, payroll_duty_days,
                                        payroll_allwrate, payroll_flg, payroll_arrears, payroll_allwamt,
                                        payroll_emp_job, payroll_emp_deptt, payroll_emp_pop, payroll_emp_grd,
                                        payroll_pay_subgrp, payroll_emptyp, payroll_emp_saltyp, payroll_emp_bank,
                                        payroll_emp_bankacc, payroll_emp_paymode, payroll_emp_flg, payroll_emp_mgr
                                    ) VALUES (
                                        %s, %s, %s, %s,
                                        0, 'N', 0, %s,
                                        %s, %s, %s, %s,
                                        %s, %s, %s, %s,
                                        %s, %s, %s, %s
                                    )
                                """, [
                                    period_id, emp_no, income_tax_allw_id, days,
                                    tax_deduction,
                                    job, deptt, duty_loc, grade,
                                    pay_subgrp, emptyp, saltyp, bank,
                                    bank_acc, pay_mode, emp_flg, emp_mgr
                                ])
                                print(f"Inserted tax deduction for employee {emp_no}: {tax_deduction}")
                    
                    # Fifth pass: Add missing active employees
                    for emp_no, emp in all_active_employees.items():
                        if emp_no not in employees_with_entries:
                            (emp_no, emp_name, job, deptt, duty_loc, grade,
                             pay_subgrp, emptyp, saltyp, bank,
                             bank_acc, pay_mode, emp_flg, emp_mgr) = emp
                            
                            days = int(context['period']['period_days'])
                            
                            cursor.execute("""
                                SELECT allw_id 
                                FROM allw 
                                WHERE allw_desc LIKE '%BASIC%' OR allw_desc LIKE '%Basic%' 
                                FETCH FIRST 1 ROW ONLY
                            """)
                            basic_allw_result = cursor.fetchone()
                            
                            if basic_allw_result:
                                basic_allw_id = basic_allw_result[0]
                                
                                if emp_no in employee_allowances and basic_allw_id in employee_allowances[emp_no]:
                                    continue
                                
                                if emp_no not in employee_allowances:
                                    employee_allowances[emp_no] = set()
                                employee_allowances[emp_no].add(basic_allw_id)
                                
                                cursor.execute("""
                                    INSERT INTO payroll (
                                        payroll_period, payroll_emp, payroll_allw, payroll_duty_days,
                                        payroll_allwrate, payroll_flg, payroll_arrears, payroll_allwamt,
                                        payroll_emp_job, payroll_emp_deptt, payroll_emp_pop, payroll_emp_grd,
                                        payroll_pay_subgrp, payroll_emptyp, payroll_emp_saltyp, payroll_emp_bank,
                                        payroll_emp_bankacc, payroll_emp_paymode, payroll_emp_flg, payroll_emp_mgr
                                    ) VALUES (
                                        %s, %s, %s, %s,
                                        0, 'N', 0, 0,
                                        %s, %s, %s, %s,
                                        %s, %s, %s, %s,
                                        %s, %s, %s, %s
                                    )
                                """, [
                                    period_id, emp_no, basic_allw_id, days,
                                    job, deptt, duty_loc, grade,
                                    pay_subgrp, emptyp, saltyp, bank,
                                    bank_acc, pay_mode, emp_flg, emp_mgr
                                ])
                                
                                print(f"Added missing active employee {emp_no} ({emp_name}) to payroll")

                messages.success(request, 'Payroll records initialized successfully with off days and income tax deductions.')
                context['records_exist'] = True
            except Exception as e:
                print(f"Error in payroll initialization: {str(e)}")
                messages.error(request, f'Error initializing payroll: {str(e)}')

        # Fetch payroll entries if records exist
        if context.get('records_exist', False):
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.payroll_emp, p.payroll_allw, p.payroll_allwamt, p.payroll_allwrate, 
                        p.payroll_flg, a.allw_earn_deduc, a.allw_desc, p.payroll_duty_days,
                        e.emp_name
                    FROM payroll p
                    JOIN allw a ON a.allw_id = p.payroll_allw
                    JOIN emp e ON e.emp_no = p.payroll_emp
                    WHERE p.payroll_period = %s
                    ORDER BY p.payroll_emp, p.payroll_allw
                """, [period_id])
                rows = cursor.fetchall()

                context['total_earning'] = Decimal('0.00')
                context['total_deduction'] = Decimal('0.00')
                context['employer_pension'] = Decimal('0.00')
                context['net_salary'] = Decimal('0.00')

                for row in rows:
                    emp_no = row[0]
                    pay_id = row[1]
                    amount = Decimal(row[2] or 0)
                    rate = Decimal(row[3] or 0)
                    flag = row[4]
                    
                    try:
                        earn_deduc = int(row[5])
                    except (ValueError, TypeError):
                        earn_deduc = 0
                        
                    pay_desc = row[6]
                    duty_days = row[7]
                    emp_name = row[8]
                    
                    total = amount

                    entry = {
                        'emp_no': emp_no,
                        'emp_name': emp_name,
                        'pay_id': pay_id,
                        'pay_desc': pay_desc,
                        'rate': rate,
                        'amount': amount,
                        'flag': flag,
                        'earn_deduc': earn_deduc,
                        'duty_days': duty_days,
                        'calc_mode': 'Monthly',
                        'total': total
                    }
                    
                    context['payroll_entries'].append(entry)

                    if earn_deduc == 0:
                        context['employer_pension'] += total
                    elif earn_deduc == 1:
                        context['total_earning'] += total
                    elif earn_deduc == -1:
                        context['total_deduction'] += abs(total)

                context['net_salary'] = context['total_earning'] - context['total_deduction']

        # Submit for approval
        submit_requested = 'submit_for_approval' in request.POST

        if request.method == 'POST' and submit_requested and context.get('records_exist', False):
            with connection.cursor() as cursor:
                cursor.execute("SELECT sal_period_flg FROM sal_period WHERE sal_period_id = %s", [period_id])
                flg = cursor.fetchone()[0]

                if flg == 'N':
                    cursor.execute("""
                        SELECT a.auth_mod_det_nxt_emp
                        FROM auth_mod_det a
                        WHERE a.auth_mod_det_mod = 12
                          AND a.auth_mod_det_flg = 'I'
                          AND a.auth_mod_det_emp = %s
                    """, [1500007])
                    result = cursor.fetchone()
                    nxt_emp = result[0] if result else None

                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    pay_track_id = cursor.fetchone()[0]

                    cursor.execute("""
                        UPDATE sal_period 
                        SET sal_period_flg = 'I',
                            sal_period_init_by = %s,
                            sal_period_init_dt = TRUNC(SYSDATE),
                            sal_period_approved_by = NULL,
                            sal_period_approved_dt = NULL,
                            sal_period_accepted_by = NULL,
                            sal_period_accepted_dt = NULL,
                            sal_period_fin_by = NULL,
                            sal_period_fin_dt = NULL,
                            sal_period_auth_by = NULL,
                            sal_period_auth_dt = NULL,
                            sal_period_run_by = NULL,
                            sal_period_run_dt = NULL
                        WHERE sal_period_id = %s
                    """, [1500007, period_id])

                    cursor.execute("""
                        INSERT INTO pay_track (
                            pay_track_id, 
                            pay_track_period, 
                            pay_track_flg, 
                            pay_track_flgfrom, 
                            pay_track_flgdt, 
                            pay_track_newflg, 
                            pay_track_newflgto,
                            pay_track_remarks
                        ) VALUES (
                            %s, %s, 
                            'N', %s, 
                            SYSDATE, 
                            'I', %s, 
                            'SUBMITTED FOR HR APPROVAL.'
                        )
                    """, [pay_track_id, period_id, 1500007, nxt_emp])

                    messages.success(request, 'Payroll submitted for HR approval.')
                    return redirect(request.path + f"?period_id={period_id}")

                else:
                    messages.warning(request, 'Invalid payroll status. Only payrolls in "N" state can be submitted.')

    return render(request, 'myapp/payroll_initiallization.html', context)

##################### Payroll History #################################

@login_required
def payroll_history_view(request):
    period_id = request.GET.get('period_id')

    if not period_id:
        return render(request, 'myapp/payroll_history.html', {'error': 'No period ID provided'})

    with connection.cursor() as cursor:
        # Get sal_period details
        cursor.execute("""
            SELECT sal_period_id, sal_period_month, sal_period_dayscount, sal_period_from, 
                   sal_period_to, sal_period_flg
            FROM sal_period
            WHERE sal_period_id = %s
        """, [period_id])
        period_row = cursor.fetchone()

        sal_period = None
        if period_row:
            sal_period = {
                'id': period_row[0],
                'month': period_row[1],
                'dayscount': period_row[2],
                'date_from': period_row[3],
                'date_to': period_row[4],
                'status': period_row[5]
            }

        # Get pay track entries with employee names
        cursor.execute("""
    SELECT
        pt.pay_track_id,
        pt.pay_track_flg,
        pt.pay_track_flgdt,
        ef.emp_name AS action_by_name,
        et.emp_name AS forwarded_to_name,
        pt.pay_track_remarks
    FROM pay_track pt
    LEFT JOIN emp ef ON pt.pay_track_flgfrom = ef.emp_no
    LEFT JOIN emp et ON pt.pay_track_newflgto = et.emp_no
    WHERE pt.pay_track_period = %s
    ORDER BY pt.pay_track_id
        """, [period_id])
        pay_tracks = cursor.fetchall()

        pay_track_list = []
        for row in pay_tracks:
            pay_track_list.append({
                'id': row[0],
                'flag': row[1],
                'flag_dt': row[2],
                'action_by': row[3],
                'forwarded_to': row[4],
                'remarks': row[5],
            })

    return render(request, 'myapp/payroll_history.html', {
        'sal_period': sal_period,
        'pay_tracks': pay_track_list
    })

######################## Employee Pay #################################
from django.views.decorators.http import require_http_methods
import logging

@login_required
def employee_pay_search(request):
    # Fetch all employees for the dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT emp_no, emp_name
            FROM EMP
            ORDER BY emp_name
        """)
        employees = [{'emp_no': row[0], 'emp_name': row[1]} for row in cursor.fetchall()]
    
    # Initialize empty context for empty form
    context = {
        'employees': employees,
        'show_empty': True,  # Flag to show empty cards/tables initially
    }
    
    if request.method == 'GET' and 'emp_no' in request.GET and request.GET.get('emp_no'):
        emp_no = request.GET.get('emp_no')
        # Validate that emp_no is numeric before proceeding
        try:
            # For Oracle, explicitly convert emp_no to ensure it's a valid number
            # This prevents ORA-01722 errors
            if emp_no.strip():  # Make sure it's not just whitespace
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM EMP WHERE EMP_NO = :emp_no", {'emp_no': emp_no})
                    count = cursor.fetchone()[0]
                
                if count > 0:
                    # Redirect to the employee pay details page
                    return redirect('employee_pay_table', emp_no=emp_no)
                else:
                    messages.error(request, f"Employee with ID {emp_no} not found.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid employee ID format.")
    
    # Render the search form with employees dropdown data
    return render(request, 'myapp/employee_pay_detail.html', context)

def employee_pay_table(request, emp_no):
    # Define the mapping dictionaries
    rate_mode_map = {
        'F': 'PRESENT RATE',
        'V': 'PREVAILING RATE',
        'P': 'EMPLOYER PENSION',
        'E': 'EMPLOYER PENSION',
        'R': 'RUNTIME VALUE',
        'D': 'RUNTIME DAILY RUNTIME'
    }
    
    earn_deduc_map = {
        -1: 'DEDUCTION',
        0: 'EMPLOYER FUND',
        1: 'EARNING'
    }
    
    # Fetch all employees for the dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT emp_no, emp_name
            FROM EMP
            ORDER BY emp_name
        """)
        employees = [{'emp_no': row[0], 'emp_name': row[1]} for row in cursor.fetchall()]
    
    # Fetch employee summary info using named parameters for Oracle
    emp_query = """
        SELECT 
            e.emp_no, 
            e.emp_name, 
            e.emp_fname, 
            j.job_desc as job_title,
            e.emp_typ,
            t.emp_typ_desc as emp_type,
            NVL((
                SELECT SUM(ep.emp_pay_allwrate)
                FROM emp_pay ep
                JOIN allw a ON ep.emp_pay_allw = a.allw_id
                WHERE ep.emp_pay_emp = e.emp_no
                AND a.allw_earn_deduc = 1
            ), 0) as gross_pay,
            NVL((
                SELECT SUM(ep.emp_pay_allwrate)
                FROM emp_pay ep
                JOIN allw a ON ep.emp_pay_allw = a.allw_id
                WHERE ep.emp_pay_emp = e.emp_no
                AND a.allw_earn_deduc = -1
            ), 0) as deduction,
            NVL((
                SELECT SUM(ep.emp_pay_allwrate)
                FROM emp_pay ep
                JOIN allw a ON ep.emp_pay_allw = a.allw_id
                WHERE ep.emp_pay_emp = e.emp_no
                AND a.allw_typ IN ('P', 'E')
            ), 0) as total_fund
        FROM 
            emp e
        JOIN 
            job j ON e.emp_job = j.job_id
        JOIN
            emp_typ t ON e.emp_typ = t.emp_typ_id
        WHERE 
            e.emp_no = :emp_no
    """

    # Helper to execute query and return dict rows
    def fetch_query(query, params=None):
        with connection.cursor() as cursor:
            cursor.execute(query, params or {})
            columns = [col[0].lower() for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    try:
        emp_data = fetch_query(emp_query, {'emp_no': emp_no})
        emp = emp_data[0] if emp_data else {}
        
        # Calculate net salary if we have employee data
        if emp:
            # Calculate net salary (gross_pay - deduction)
            emp['net_salary'] = emp['gross_pay'] - emp['deduction']

        # Modified query to use the correct fields as shown in your example query
        # This ensures we're getting the proper allw_saltyp and allw_typ for calculation mode
        common_query = """
            SELECT 
                ep.emp_pay_allw as id,
                a.allw_desc as description,
                ep.emp_pay_allwrule as calc_mode,
                a.allw_earn_deduc as earn_deduc_type,
                ep.emp_pay_allwrate as rate,
                ep.emp_pay_allwamt as amount,
                a.allw_id as allw_id,
                a.allw_typ as allw_typ,
                a.allw_saltyp as allw_saltyp
            FROM 
                emp_pay ep
            JOIN 
                allw a ON ep.emp_pay_allw = a.allw_id
            WHERE 
                ep.emp_pay_emp = :emp_no
                AND a.allw_earn_deduc = :earn_deduc_type
            ORDER BY 
                a.allw_desc
        """

        # Fetch the different types of earnings/deductions/funds
        earnings = fetch_query(common_query, {'emp_no': emp_no, 'earn_deduc_type': 1})
        deductions = fetch_query(common_query, {'emp_no': emp_no, 'earn_deduc_type': -1})
        funds = fetch_query(common_query, {'emp_no': emp_no, 'earn_deduc_type': 0})
        
        # Process the raw data to include human-readable values
        def process_records(records):
            for record in records:
                # Determine calculation mode display based on allw_typ and allw_saltyp
                # Use these fields instead of calc_mode for proper mapping
                if record['allw_typ'] in rate_mode_map:
                    record['calc_mode_display'] = rate_mode_map.get(record['allw_typ'])
                elif record['allw_saltyp'] in rate_mode_map:
                    record['calc_mode_display'] = rate_mode_map.get(record['allw_saltyp'])
                else:
                    # Fallback to calc_mode if neither allw_typ nor allw_saltyp match
                    record['calc_mode_display'] = rate_mode_map.get(record['calc_mode'], record['calc_mode'])
                
                # Add human-readable earn_deduc_type from the mapping
                record['earn_deduc_type_display'] = earn_deduc_map.get(record['earn_deduc_type'], str(record['earn_deduc_type']))
                
                # Mark if this is the default allw_id that should be highlighted
                record['is_default_allw'] = (record['id'] == record['allw_id'])
            
            return records
        
        # Process each category
        earnings = process_records(earnings)
        deductions = process_records(deductions)
        funds = process_records(funds)

    except Exception as e:
        # Log the error and provide a friendly message
        import logging
        logging.error(f"Error fetching employee data: {str(e)}")
        messages.error(request, f"Error retrieving employee data: {str(e)}")
        earnings = []
        deductions = []
        funds = []
        emp = {}

    # Pass all mappings to the template for potential use
    context = {
        'emp': emp,
        'earnings': earnings,
        'deductions': deductions,
        'funds': funds,
        'employees': employees,  # Pass employees list for the dropdown
    }
    
    return render(request, 'myapp/employee_pay_detail.html', context)

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def update_employee_pay_rate(request):
    try:
        # Parse JSON data
        data = json.loads(request.body)
        row_id = data.get('row_id')
        emp_no = data.get('emp_no')
        new_rate = data.get('new_rate')
        tab_type = data.get('tab_type', 'earning')
        
        # Validate required fields
        if not all([row_id, emp_no, new_rate]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: row_id, emp_no, and new_rate are required'
            }, status=400)
        
        # Validate and convert new_rate to float
        try:
            new_rate_float = float(new_rate)
            if new_rate_float < 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Rate cannot be negative'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid rate value. Must be a valid number'
            }, status=400)
        
        # Log the update attempt
        logger.info(f"Attempting to update pay rate for employee {emp_no}, "
                   f"allowance {row_id}, new rate: {new_rate_float}, tab: {tab_type}")
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                # First, verify that the record exists and belongs to the employee
                verify_query = """
                    SELECT ep.emp_pay_emp, ep.emp_pay_allwrate, a.allw_desc, a.allw_earn_deduc
                    FROM emp_pay ep
                    JOIN allw a ON ep.emp_pay_allw = a.allw_id
                    WHERE ep.emp_pay_allw = :row_id 
                    AND ep.emp_pay_emp = :emp_no
                """
                
                cursor.execute(verify_query, {
                    'row_id': row_id,
                    'emp_no': emp_no
                })
                
                result = cursor.fetchone()
                
                if not result:
                    return JsonResponse({
                        'success': False,
                        'error': 'Record not found or does not belong to the specified employee'
                    }, status=404)
                
                old_rate = result[1]
                allowance_desc = result[2]
                earn_deduc_type = result[3]
                
                # Update the rate in emp_pay table
                update_query = """
                    UPDATE emp_pay 
                    SET emp_pay_allwrate = :new_rate
                    WHERE emp_pay_allw = :row_id 
                    AND emp_pay_emp = :emp_no
                """
                
                cursor.execute(update_query, {
                    'new_rate': new_rate_float,
                    'row_id': row_id,
                    'emp_no': emp_no
                })
                
                # Check if the update was successful
                if cursor.rowcount == 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'No records were updated. Please check the data and try again.'
                    }, status=400)
                
                if earn_deduc_type == -1:  # Deduction - make it negative
                    amount_value = -abs(new_rate_float)
                else:  # Earning (1) or Fund (0) - keep it positive
                    amount_value = abs(new_rate_float)

                update_amount_query = """
                    UPDATE emp_pay 
                    SET emp_pay_allwamt = :amount_value
                    WHERE emp_pay_allw = :row_id 
                    AND emp_pay_emp = :emp_no
                """
                cursor.execute(update_amount_query, {
                    'amount_value': amount_value,
                    'row_id': row_id,
                    'emp_no': emp_no
                })

        # Log successful update
        logger.info(f"Successfully updated pay rate for employee {emp_no}, "
                   f"allowance {row_id} ({allowance_desc}) from {old_rate} to {new_rate_float}")
        
        # Determine the type description for response
        type_descriptions = {
            -1: 'Deduction',
            0: 'Employer Fund',
            1: 'Earning'
        }
        type_desc = type_descriptions.get(earn_deduc_type, 'Unknown')
        
        return JsonResponse({
            'success': True,
            'message': 'Rate updated successfully',
            'data': {
                'emp_no': emp_no,
                'allowance_id': row_id,
                'allowance_desc': allowance_desc,
                'old_rate': float(old_rate) if old_rate else 0,
                'new_rate': new_rate_float,
                'type': type_desc,
                'tab_type': tab_type
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Error updating employee pay rate: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while updating the rate: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_employee_pay_summary(request, emp_no):
    """
    Get updated summary data after rate changes
    This can be called after successful updates to refresh totals
    """
    try:
        with connection.cursor() as cursor:
            summary_query = """
                SELECT 
                    NVL((
                        SELECT SUM(ep.emp_pay_allwrate)
                        FROM emp_pay ep
                        JOIN allw a ON ep.emp_pay_allw = a.allw_id
                        WHERE ep.emp_pay_emp = :emp_no
                        AND a.allw_earn_deduc = 1
                    ), 0) as gross_pay,
                    NVL((
                        SELECT SUM(ep.emp_pay_allwrate)
                        FROM emp_pay ep
                        JOIN allw a ON ep.emp_pay_allw = a.allw_id
                        WHERE ep.emp_pay_emp = :emp_no
                        AND a.allw_earn_deduc = -1
                    ), 0) as deduction,
                    NVL((
                        SELECT SUM(ep.emp_pay_allwrate)
                        FROM emp_pay ep
                        JOIN allw a ON ep.emp_pay_allw = a.allw_id
                        WHERE ep.emp_pay_emp = :emp_no
                        AND a.allw_typ IN ('P', 'E')
                    ), 0) as total_fund
                FROM dual
            """
            
            cursor.execute(summary_query, {'emp_no': emp_no})
            result = cursor.fetchone()
            
            if result:
                gross_pay, deduction, total_fund = result
                net_salary = gross_pay - deduction
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'gross_pay': float(gross_pay),
                        'deduction': float(deduction),
                        'total_fund': float(total_fund),
                        'net_salary': float(net_salary)
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Employee not found'
                }, status=404)
                
    except Exception as e:
        logger.error(f"Error getting employee pay summary: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'An error occurred while fetching summary: {str(e)}'
        }, status=500)

logger = logging.getLogger(__name__)
@login_required
@csrf_exempt
def add_emp_allowance(request):
    if request.method == 'POST':
        emp_no = request.POST.get('emp_id')
        allowance_id = request.POST.get('allowance_id')
        
        logger.debug(f"Received POST data - emp_id: {emp_no}, allowance_id: {allowance_id}, user: {request.user}")

        if not emp_no or not allowance_id:
            logger.error("Missing emp_id or allowance_id in POST data")
            return render(request, 'myapp/employee_pay_detail.html', {
                'error': 'Employee ID or Allowance ID is missing.',
                'emp': {'emp_no': emp_no},
            })

        try:
            with connection.cursor() as cursor:
                # 🔹 Fetch ALLW_EARN_DEDUC value
                cursor.execute("""
                    SELECT ALLW_EARN_DEDUC FROM allw WHERE allw_id = :allw_id
                """, {'allw_id': allowance_id})
                result = cursor.fetchone()

                if result is None:
                    logger.error("No matching allowance found.")
                    raise Exception("Invalid allowance selected.")

                earn_deduc_value = result[0]

                # 🔹 Insert into emp_pay with fetched ALLW_EARN_DEDUC
                logger.debug("Executing insert query into emp_pay table...")
                cursor.execute("""
                    INSERT INTO emp_pay (
                        emp_pay_emp, emp_pay_allw, emp_pay_allwrate, emp_pay_allwrule,
                        emp_pay_acc, emp_pay_allwamt, emp_pay_postedby, emp_pay_authby
                    ) VALUES (
                        :emp_no, :allw_id, 0, :rule,
                        NULL, 0, :posted_by, NULL
                    )
                """, {
                    'emp_no': emp_no,
                    'allw_id': allowance_id,
                    'rule': earn_deduc_value,
                    'posted_by': request.user.id
                })
                logger.debug("Insert successful!")
           
            messages.success(request, 'Allowance successfully added to employee!')
            return redirect('employee_pay_table', emp_no=emp_no)

        except Exception as e:
            logger.error(f"Error inserting allowance: {e}", exc_info=True)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT allw_id as id, allw_desc as description
                    FROM allw
                    ORDER BY allw_id
                """)
                allw_list = [{'id': row[0], 'description': row[1]} for row in cursor.fetchall()]

            return render(request, 'myapp/employee_pay_detail.html', {
                'error': 'Error while inserting allowance: ' + str(e),
                'allw_list': allw_list,
                'emp': {'emp_no': emp_no},
            })

    logger.warning("Non-POST request to add_emp_allowance, redirecting to home")
    return redirect('home')

######################## Payroll Allowances #########################
@login_required
def get_allowances(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ALLW_ID, ALLW_DESC, ALLW_TYP, ALLW_EARN_DEDUC, ALLW_FLG 
            FROM ALLW 
            WHERE ALLW_EMPTYP = 1 order by 1
        """)
        rows = cursor.fetchall()
    
    # Mapping data
    rate_mode_map = {
        'F': 'PRESENT RATE',
        'V': 'PREVAILING RATE',
        'P': 'EMPLOYER PENSION',
        'E': 'EMPLOYER PENSION',
        'R': 'RUNTIME VALUE',
        'D': 'RUNTIME DAILY RUNTIME'
    }
    
    earn_deduc_map = {
        -1: 'DEDUCTION',
        0: 'EMPLOYER FUND',
        1: 'EARNING'
    }
    
    status_map = {
        'A': 'ACTIVE',
        'I': 'INACTIVE'
    }
    
    data = []
    for row in rows:
        allw_id, allw_desc, allw_typ, allw_earn_deduc, allw_flg = row
        data.append({
            'id': allw_id,
            'desc': allw_desc,
            'rate_mode': allw_typ,
            'rate_mode_display': rate_mode_map.get(allw_typ, ''),
            'earning_type': allw_earn_deduc,
            'earning_display': earn_deduc_map.get(allw_earn_deduc, ''),
            'status': allw_flg,
            'status_display': status_map.get(allw_flg, '')
        })
    
    return render(request, 'myapp/payroll_allowances.html', {
        'employee_type_id': 1,
        'employee_type_name': 'WSSC/TMA PAY ALLOWANCES',
        'allowances': data,
        'rate_mode_choices': rate_mode_map,
        'earn_deduc_choices': earn_deduc_map,
        'status_choices': status_map
    })

@login_required
def add_allowance(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            
            # Extract data from the request - using original field names from your code
            allw_id = data.get('id')
            allw_desc = data.get('desc')
            allw_typ = data.get('type')  # Original field name from frontend
            allw_saltyp = data.get('saltyp')
            allw_earn_deduc = data.get('earnDeduc')  # Original field name from frontend
            allw_flg = data.get('status')  # Original field name from frontend
            allw_emptyp = data.get('emptyp', 1)  # Default to 1 as specified
            
            # Debug logging
            print(f"Received allowance data: {data}")
            
            # Validate required fields
            if not all([allw_id is not None, allw_desc, allw_typ, allw_saltyp is not None, 
                        allw_earn_deduc is not None, allw_flg]):
                missing = []
                if allw_id is None: missing.append('id')
                if not allw_desc: missing.append('desc')
                if not allw_typ: missing.append('type')
                if allw_saltyp is None: missing.append('saltyp')
                if allw_earn_deduc is None: missing.append('earnDeduc')
                if not allw_flg: missing.append('status')
                
                return JsonResponse({
                    'status': 'error',
                    'message': f'Required fields missing: {", ".join(missing)}',
                    'received': data
                }, status=400)
            
            # Convert ID and numeric values to integers
            try:
                allw_id = int(allw_id)
                allw_earn_deduc = int(allw_earn_deduc)
                allw_saltyp = int(allw_saltyp)
                allw_emptyp = int(allw_emptyp)
            except (ValueError, TypeError) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Invalid numeric values: {str(e)}',
                    'received': data
                }, status=400)
            
            # Debug the actual values being used for the SQL query
            print(f"SQL parameters: {[allw_id, allw_desc, allw_typ, allw_saltyp, allw_earn_deduc, allw_flg, allw_emptyp]}")
            
            try:
                # Insert the new allowance into the database
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ALLW 
                        (ALLW_ID, ALLW_DESC, ALLW_TYP, ALLW_SALTYP, ALLW_EARN_DEDUC, ALLW_FLG, ALLW_EMPTYP)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [allw_id, allw_desc, allw_typ, allw_saltyp, allw_earn_deduc, allw_flg, allw_emptyp])
                    
                    # Commit the transaction
                    connection.commit()
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Database error: {str(db_error)}'
                }, status=500)
            
            # Return success response with the data
            return JsonResponse({
                'status': 'success',
                'message': 'Allowance added successfully',
                'data': {
                    'id': allw_id,
                    'desc': allw_desc,
                    'type': allw_typ,
                    'saltyp': allw_saltyp,
                    'earnDeduc': allw_earn_deduc,
                    'status': allw_flg
                }
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid JSON data: {str(e)}'
            }, status=400)
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(traceback.format_exc())
            
            return JsonResponse({
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }, status=500)
    
    # Return error for non-POST requests
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. Only POST is allowed.'
    }, status=405)

###################### Pay Track ######################################

@login_required
def payroll_tracking(request):
    selected_period_id = request.GET.get('period_id')

    with connection.cursor() as cursor:
        # Fetch all available payroll periods for dropdown
        cursor.execute("""
            SELECT sal_period_id, sal_period_month 
            FROM sal_period 
            ORDER BY    sal_period_id DESC 
            FETCH FIRST 5 ROWS ONLY
        """)
        periods = cursor.fetchall()
        period_list = [
            {'id': row[0], 'month': row[1]} for row in periods
        ]

        sal_period = None
        pay_track_list = []

        if selected_period_id:
            # Get selected payroll period details
            cursor.execute("""
                SELECT sal_period_id, sal_period_month, sal_period_dayscount, sal_period_from, 
                       sal_period_to, sal_period_flg
                FROM sal_period
                WHERE sal_period_id = %s
            """, [selected_period_id])
            row = cursor.fetchone()
            if row:
                sal_period = {
                    'id': row[0],
                    'month': row[1],
                    'dayscount': row[2],
                    'date_from': row[3],
                    'date_to': row[4],
                    'status': row[5]
                }

            # Fetch corresponding pay_track records
            cursor.execute("""
                SELECT
                    pt.pay_track_id,
                    pt.pay_track_flg,
                    pt.pay_track_flgdt,
                    ef.emp_name AS action_by_name,
                    et.emp_name AS forwarded_to_name,
                    pt.pay_track_remarks
                FROM pay_track pt
                LEFT JOIN emp ef ON pt.pay_track_flgfrom = ef.emp_no
                LEFT JOIN emp et ON pt.pay_track_newflgto = et.emp_no
                WHERE pt.pay_track_period = %s
                ORDER BY pt.pay_track_id
            """, [selected_period_id])
            pay_tracks = cursor.fetchall()
            pay_track_list = [{
                'id': row[0],
                'flag': row[1],
                'flag_dt': row[2],
                'action_by': row[3],
                'forwarded_to': row[4],
                'remarks': row[5],
            } for row in pay_tracks]

    return render(request, 'myapp/payroll_tracking.html', {
        'period_list': period_list,
        'sal_period': sal_period,
        'pay_tracks': pay_track_list,
        'selected_period_id': selected_period_id
    })

###################### Payroll Amedments #############################

@login_required
def payroll_amendment_search(request):
    """
    AJAX endpoint for employee search dropdown
    """
    term = request.GET.get('term', '').strip()
    employees = []
    
    if term and len(term) >= 1:  # Start searching after 1 character
        try:
            with connection.cursor() as cursor:
                # Search by employee ID or name
                cursor.execute("""
                    SELECT emp_no, emp_name
                    FROM emp
                    WHERE UPPER(emp_no) LIKE UPPER(:term)
                       OR UPPER(emp_name) LIKE UPPER(:term)
                    ORDER BY emp_name
                    FETCH FIRST 10 ROWS ONLY
                """, {'term': f'%{term}%'})
                
                results = cursor.fetchall()
                employees = [
                    {
                        'id': str(row[0]),  # Ensure it's a string
                        'name': row[1]
                    }
                    for row in results
                ]
        except Exception as e:
            print(f"DEBUG: Search employees error: {str(e)}")
            employees = []
    
    return JsonResponse(employees, safe=False)

@login_required
def payroll_amendment_view(request):
    emp_no = request.GET.get('emp_no')
    emp = None
    payroll_records = []
    
    print(f"DEBUG: Received emp_no: '{emp_no}' (type: {type(emp_no)})")  # Debug line
    
    if emp_no and emp_no.strip():  # Make sure it's not empty or whitespace
        try:
            with connection.cursor() as cursor:
                # Single query to get all employee and payroll information
                cursor.execute("""
                    SELECT 
                        e.emp_no, 
                        e.emp_name, 
                        e.emp_fname, 
                        j.job_desc as job_title,
                        e.emp_typ,
                        t.emp_typ_desc as emp_type,
                        NVL((
                            SELECT SUM(ep.emp_pay_allwrate)
                            FROM emp_pay ep
                            JOIN allw a ON ep.emp_pay_allw = a.allw_id
                            WHERE ep.emp_pay_emp = e.emp_no
                            AND a.allw_earn_deduc = 1
                        ), 0) as gross_pay,
                        NVL((
                            SELECT SUM(ep.emp_pay_allwrate)
                            FROM emp_pay ep
                            JOIN allw a ON ep.emp_pay_allw = a.allw_id
                            WHERE ep.emp_pay_emp = e.emp_no
                            AND a.allw_earn_deduc = -1
                        ), 0) as deduction,
                        NVL((
                            SELECT SUM(ep.emp_pay_allwrate)
                            FROM emp_pay ep
                            JOIN allw a ON ep.emp_pay_allw = a.allw_id
                            WHERE ep.emp_pay_emp = e.emp_no
                            AND a.allw_typ IN ('P', 'E')
                        ), 0) as total_fund
                    FROM 
                        emp e
                    JOIN 
                        job j ON e.emp_job = j.job_id
                    JOIN
                        emp_typ t ON e.emp_typ = t.emp_typ_id
                    WHERE 
                        e.emp_no = :emp_no
                """, {'emp_no': emp_no})
                
                row = cursor.fetchone()
                print(f"DEBUG: Query result: {row}")  # Debug line

                if row:
                    # Unpack all the values from the single query
                    emp_no_val, emp_name, emp_fname, job_title, emp_typ_id, emp_type, gross_pay, deduction, total_fund = row
                    
                    # Calculate net salary
                    net_salary = gross_pay - deduction
                    
                    emp = {
                        'emp_no': emp_no_val,
                        'emp_name': emp_name,
                        'emp_fname': emp_fname,
                        'job_title': job_title if job_title else 'N/A',
                        'emp_typ_id': emp_typ_id,
                        'emp_type': emp_type if emp_type else 'N/A',
                        'gross_pay': f"{gross_pay:.2f}",
                        'deduction': f"{deduction:.2f}",
                        'net_salary': f"{net_salary:.2f}",
                        'total_fund': f"{total_fund:.2f}",
                    }
                    
                    print(f"DEBUG: Employee object created: {emp}")  # Debug line
                    
                    # Now fetch payroll records for this employee
                    # Updated to use correct query with payroll table join and active sal_period filter
                    cursor.execute("""
                        SELECT  
                            p.emp_pay_emp, 
                            p.emp_pay_allw, 
                            a.allw_desc, 
                            -- Frequency mode
                            CASE 
                                WHEN t.emp_saltyp_freq = 1 THEN 'Monthly'
                                WHEN t.emp_saltyp_freq = 2 THEN 'Weekly'  
                                WHEN t.emp_saltyp_freq = 3 THEN 'Daily'
                                ELSE TO_CHAR(t.emp_saltyp_freq)
                            END AS pay_calc_mode,
                            -- Earning or Deduction type
                            CASE 
                                WHEN a.allw_earn_deduc = 1 THEN 'Earning'
                                WHEN a.allw_earn_deduc = -1 THEN 'Deduction'
                                WHEN a.allw_typ IN ('P', 'E') THEN 'Pension'
                                ELSE 'Other'
                            END AS earn_deduc_type,
                            -- Rate from emp_pay
                            ROUND(p.emp_pay_allwrate, 2) AS rate,
                            -- Actual amount from payroll for active sal_period
                            ROUND(NVL(pl.payroll_allwamt, 0), 2) AS amount,
                            -- Placeholder adjustment
                            0 AS adjustment,
                            -- Total = amount + adjustment
                            ROUND(NVL(pl.payroll_allwamt, 0), 2) AS total_amount
                        FROM emp_pay p
                        JOIN allw a ON p.emp_pay_allw = a.allw_id
                        JOIN emp e ON p.emp_pay_emp = e.emp_no
                        JOIN emp_saltyp t ON e.emp_saltyp = t.emp_saltyp_id
                        -- Join payroll and only fetch data from active sal_period
                        JOIN (
                            SELECT pr.*
                            FROM payroll pr
                            JOIN sal_period sp ON pr.payroll_period = sp.sal_period_id
                            WHERE sp.sal_period_flg = 'N'
                        ) pl ON pl.payroll_emp = p.emp_pay_emp AND pl.payroll_allw = p.emp_pay_allw
                        WHERE e.emp_flg = 'O'
                          AND p.emp_pay_allwrule = 1
                          AND e.emp_no = :emp_no
                          AND e.emp_no <> 1009999
                        ORDER BY p.emp_pay_allw
                    """, {'emp_no': emp_no})
                    
                    payroll_results = cursor.fetchall()
                    print(f"DEBUG: Payroll query results: {payroll_results}")  # Debug line
                    
                    payroll_records = []
                    for payroll_row in payroll_results:
                        payroll_records.append({
                            'emp_no': payroll_row[0],
                            'pay_allw_id': payroll_row[1],
                            'pay_description': payroll_row[2],
                            'pay_calc_mode': payroll_row[3],
                            'earn_deduc_type': payroll_row[4],
                            'rate': f"{payroll_row[5]:.2f}",
                            'amount': f"{payroll_row[6]:.2f}",
                            'adjustment': f"{payroll_row[7]:.2f}",
                            'total_amount': f"{payroll_row[8]:.2f}",
                        })
                    
                    print(f"DEBUG: Payroll records created: {len(payroll_records)}")  # Debug line
                else:
                    print(f"DEBUG: No employee found with ID {emp_no}")  # Debug line
                    emp = None
                    
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")  # Debug line
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            emp = None
            payroll_records = []
    else:
        print("DEBUG: No emp_no provided or empty")  # Debug line
        emp = None
        payroll_records = []

    print(f"DEBUG: Final context emp: {emp}")  # Debug line
    print(f"DEBUG: Final payroll records: {len(payroll_records)}")  # Debug line
    
    return render(request, 'myapp/payroll_amedments.html', {
        'emp': emp, 
        'payroll_records': payroll_records
    })

@login_required
@csrf_exempt
def save_payroll_adjustments(request):
    """
    AJAX endpoint to save payroll adjustments for the current payroll period
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        adjustments = data.get('adjustments', [])
        
        if not adjustments:
            return JsonResponse({'success': False, 'message': 'No adjustments provided'}, status=400)
        
        with connection.cursor() as cursor:
            # Get current active salary period
            cursor.execute("""
                SELECT sal_period_id
                FROM sal_period
                WHERE sal_period_flg = 'N'
            """)
            active_period = cursor.fetchone()
            
            if not active_period:
                return JsonResponse({'success': False, 'message': 'No active salary period found'}, status=400)
            
            active_period_id = active_period[0]
            updated_records = 0
            
            for adjustment in adjustments:
                emp_no = adjustment.get('emp_no')
                allw_id = adjustment.get('allw_id')
                adjustment_amount = float(adjustment.get('adjustment', 0))
                
                # Update payroll table
                cursor.execute("""
                    UPDATE payroll
                    SET payroll_allwamt = payroll_allwamt + :adjustment
                    WHERE payroll_emp = :emp_no
                    AND payroll_allw = :allw_id
                    AND payroll_period = :period_id
                """, {
                    'adjustment': adjustment_amount,
                    'emp_no': emp_no,
                    'allw_id': allw_id,
                    'period_id': active_period_id
                })
                
                if cursor.rowcount > 0:
                    updated_records += 1
            
            if updated_records > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully updated {updated_records} payroll record(s)'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No records were updated. Check employee ID, allowance ID, or period.'
                }, status=400)
                
    except Exception as e:
        print(f"DEBUG: Error saving adjustments: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error saving adjustments: {str(e)}'
        }, status=500)
    
########################  Loan Module  #################################
@login_required
def employee_search(request):
    emp_no = request.GET.get('emp_no')
    employee = None
    loan_details = None
    installments = []

    if emp_no:
        with connection.cursor() as cursor:
            # Fetch employee details
            cursor.execute("""
                SELECT E.EMP_NO, E.EMP_NAME, E.EMP_JOIN_DT, E.EMP_EXP_DT, D.DEPTT_DESC 
                FROM EMP E 
                JOIN DEPTT D ON D.DEPTT_ID = E.EMP_DEPTT
                WHERE E.EMP_NO = %s
            """, [emp_no])
            row = cursor.fetchone()

            if row:
                employee = {
                    'emp_no': row[0],
                    'emp_name': row[1],
                    'emp_join_dt': row[2].strftime('%Y-%m-%d') if row[2] else None,
                    'emp_exp_dt': row[3].strftime('%Y-%m-%d') if row[3] else None,
                    'deptt_desc': row[4]
                }

                # Fetch loan details (if any)
                cursor.execute("""
                    SELECT LOAN_ID, TOTAL_LOAN, START_DATE, TOTAL_INSTALLMENT, END_DATE, LOAN_STATUS
                    FROM LOAN_ALLOTMENT 
                    WHERE EMP_ID = %s
                    ORDER BY START_DATE DESC
                """, [emp_no])
                loan_row = cursor.fetchone()

                if loan_row:
                    loan_details = {
                        'loan_id': loan_row[0],
                        'total_loan': loan_row[1],
                        'start_date': loan_row[2].strftime('%Y-%m-%d'),
                        'total_installment': loan_row[3],
                        'end_date': loan_row[4].strftime('%Y-%m-%d'),
                        'loan_status': 'Active' if loan_row[5] == 'A' else 'Completed'
                    }

                    # Fetch installment details
                    cursor.execute("""
                        SELECT ID,INSTALLMENT_DATE, MONTHLY_PAY, STATUS 
                        FROM LOAN_INSTALLMENT 
                        WHERE LOAN_ID = %s
                        ORDER BY INSTALLMENT_DATE ASC
                    """, [loan_row[0]])
                    installments = [
                    {
                        'id': row[0],  # Add ID field
                        'installment_date': row[1].strftime('%Y-%m-%d'),
                        'monthly_pay': row[2],
                        'status': row[3]
                    }
                        for row in cursor.fetchall()
                    ]
                    
    # Fetch employees who have been allotted loans
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT E.EMP_NO, E.EMP_NAME, L.TOTAL_LOAN
            FROM EMP E
            JOIN LOAN_ALLOTMENT L ON E.EMP_NO = L.EMP_ID
        """)
        rows = cursor.fetchall()
        employees_with_loans = [{'id': row[0], 'name': row[1], 'total_loan': row[2]} for row in rows]

    return render(request, 'myapp/employee_loan_search_report.html', {
        'employee': employee,
        'loan_details': loan_details,
        'installments': installments,
        'employees_with_loans': employees_with_loans,
    })

@login_required
def search_employees(request):
    term = request.GET.get('term', '')
    employees = []

    if term:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EMP_NO, EMP_NAME 
                FROM EMP 
                WHERE EMP_NO LIKE %s
            """, [f"{term}%"])
            rows = cursor.fetchall()
            employees = [{'id': row[0], 'name': row[1]} for row in rows]

    return JsonResponse(employees, safe=False)

# Loan Allotment
@login_required
def loan_allotment(request):
    emp_no = request.GET.get("emp_no")
    employee = None
    max_loan_limit = 200000
    calculated_months = 24  # Default to 24 months initially

    if emp_no:
        try:
            with connection.cursor() as cursor:
                # Fetch Employee Info
                cursor.execute("""
                    SELECT E.EMP_NO, E.EMP_NAME, E.EMP_JOIN_DT, E.EMP_EXP_DT, E.EMP_LEAVING_DT, D.DEPTT_DESC 
                    FROM EMP E 
                    JOIN DEPTT D ON D.DEPTT_ID = E.EMP_DEPTT
                    WHERE E.EMP_NO = %s
                """, [emp_no])
                row = cursor.fetchone()

            if row:
                employee = {
                    "emp_no": row[0],
                    "emp_name": row[1],
                    "emp_join_dt": row[2].strftime("%Y-%m-%d") if row[2] else None,
                    "emp_exp_dt": row[3].strftime("%Y-%m-%d") if row[3] else None,
                    "emp_leaving_dt": row[4].strftime("%Y-%m-%d") if row[4] else None,
                    "deptt_desc": row[5]
                }

                if employee["emp_leaving_dt"]:
                    messages.error(request, "Loan cannot be allotted to an employee who has a leaving date.")
                    return redirect("loan_allotment")

                calculated_months = 24  # Always set to 24 when no leaving date

                # Fetch salary-based loan limit
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COALESCE(SUM(EMP_PAY.EMP_PAY_ALLWAMT) * 4, 0) 
                        FROM EMP_PAY 
                        JOIN ALLW ON EMP_PAY.EMP_PAY_ALLW = ALLW.ALLW_ID
                        WHERE EMP_PAY.EMP_PAY_EMP = %s AND ALLW.ALLW_EARN_DEDUC = 1
                    """, [emp_no])
                    salary_row = cursor.fetchone()
                    max_loan_limit = min(salary_row[0], 200000) if salary_row else 200000
            else:
                messages.error(request, "Employee not found. Please enter a valid Employee Number.")
                return redirect("loan_allotment")
        except Exception as e:
            messages.error(request, f"Error fetching employee data: {str(e)}")
            return redirect("loan_allotment")

    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM LOAN_ALLOTMENT 
                    WHERE EMP_ID = %s AND LOAN_STATUS = 'N'
                """, [employee["emp_no"]])
                existing_loan_count = cursor.fetchone()[0]
                if existing_loan_count > 0:
                    messages.error(request, "This employee already has an active loan. New loan cannot be allotted.")
                    return redirect("loan_allotment")

            loan_amount = request.POST.get("loan_amount")
            repay_option = request.POST.get("repay_option")
            start_date = request.POST.get("start_date")

            if not loan_amount or not repay_option or not start_date:
                messages.warning(request, "All fields are required.")
                return redirect("loan_allotment")

            loan_amount = float(loan_amount)
            if loan_amount <= 0:
                messages.error(request, "Loan amount must be greater than zero.")
                return redirect("loan_allotment")

            if loan_amount > max_loan_limit:
                messages.error(request, f"Loan amount exceeds employee limit of {max_loan_limit}.")
                return redirect("loan_allotment")

            if not employee:
                messages.error(request, "Invalid employee selection.")
                return redirect("loan_allotment")

            # Repayment plan
            remaining_amount = 0
            repay_duration = 24  # Always default to 24 months
            if repay_option == "duration":
                # Repayment duration is fixed to 24
                monthly_pay = round(loan_amount / repay_duration, 2)

            elif repay_option == "monthly":
                monthly_pay = request.POST.get("monthly_pay")
                if not monthly_pay or not monthly_pay.replace(".", "", 1).isdigit():
                    messages.error(request, "Invalid monthly payment amount.")
                    return redirect("loan_allotment")

                monthly_pay = float(monthly_pay)
                if monthly_pay <= 0:
                    messages.error(request, "Monthly payment must be greater than zero.")
                    return redirect("loan_allotment")

                months_decimal = loan_amount / monthly_pay
                repay_duration = int(months_decimal)
                remaining_amount = loan_amount - (repay_duration * monthly_pay)

                if remaining_amount > 0:
                    repay_duration += 1

                # Regardless, cap repayment to 24 months
                if repay_duration > 24:
                    messages.error(request, "Repayment period cannot exceed 24 months.")
                    return redirect("loan_allotment")
            else:
                messages.error(request, "Invalid repayment option selected.")
                return redirect("loan_allotment")

            # Get new LOAN_ID
            with connection.cursor() as cursor:
                cursor.execute("SELECT NVL(MAX(LOAN_ID), 0) + 1 FROM LOAN_ALLOTMENT")
                new_loan_id = cursor.fetchone()[0]

            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date_obj + relativedelta(months=repay_duration)

            # Insert into LOAN_ALLOTMENT
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO LOAN_ALLOTMENT 
                    (LOAN_ID, EMP_ID, TOTAL_LOAN, START_DATE, MONTHLY_PLAN, TOTAL_INSTALLMENT, END_DATE, LOAN_STATUS) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'N')
                """, [new_loan_id, employee["emp_no"], loan_amount, start_date_obj, monthly_pay, repay_duration, end_date])

            # Get next installment ID
            with connection.cursor() as cursor:
                cursor.execute("SELECT NVL(MAX(ID), 0) + 1 FROM LOAN_INSTALLMENT")
                next_installment_id = cursor.fetchone()[0]

            # Insert installments
            with connection.cursor() as cursor:
                current_month = start_date_obj
                for i in range(repay_duration):
                    is_last_month = (i == repay_duration - 1)
                    monthly_payment = monthly_pay
                    if is_last_month and remaining_amount > 0:
                        monthly_payment += remaining_amount
                    cursor.execute("""
                        INSERT INTO LOAN_INSTALLMENT 
                        (ID, LOAN_ID, INSTALLMENT_DATE, MONTHLY_PAY, STATUS)
                        VALUES (%s, %s, %s, %s, 'N')
                    """, [next_installment_id + i, new_loan_id, current_month, monthly_payment])
                    current_month += relativedelta(months=1)

            messages.success(request, "Loan successfully allotted and installments generated.")
            return redirect("loan_allotment")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("loan_allotment")

    return render(request, "myapp/loan_allotment.html", {
        "employee": employee,
        "max_loan_limit": max_loan_limit,
        "calculated_months": calculated_months
    })

from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph

def wrap_text(text, max_width, style):
    """Wrap text to fit within a specified width using ReportLab Paragraph."""
    paragraph = Paragraph(text, style)
    paragraph.wrap(max_width * inch, 0)
    return paragraph

@csrf_exempt  # Remove in production, use CSRF token properly
def update_installment_status(request):
    if request.method == "POST":
        try:
            print("✅ Received AJAX POST request!")

            # Decode JSON body
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                print("❌ Invalid JSON format!")
                return JsonResponse({"success": False, "message": "Invalid JSON format."})

            installment_id = data.get("installment_id")
            new_status = data.get("status")

            print(f"🔹 Installment ID: {installment_id}, New Status: {new_status}")

            if not installment_id or not new_status:
                return JsonResponse({"success": False, "message": "Missing installment ID or status."})

            with connection.cursor() as cursor:
                # Update current installment status
                cursor.execute(
                    "UPDATE loan_installment SET status = %s WHERE id = %s",
                    (new_status, installment_id)
                )

                # Fetch the updated monthly amount of the current installment
                cursor.execute(
                    "SELECT monthly_pay FROM loan_installment WHERE id = %s",
                    (installment_id,)
                )
                current_amount = cursor.fetchone()[0]

                # Handle overdue logic: add the overdue amount to the next unpaid installment
                next_monthly_amount = None
                if new_status == 'O':
                    cursor.execute(
    """SELECT id, monthly_pay 
       FROM (SELECT id, monthly_pay 
             FROM loan_installment 
             WHERE status = 'N' AND id > %s 
             ORDER BY id ASC) 
       WHERE ROWNUM = 1""",
    (installment_id,)
)
                    next_installment = cursor.fetchone()

                    if next_installment:
                        next_installment_id, next_amount = next_installment
                        next_monthly_amount = int(next_amount) + int(current_amount)

                        # Update the next installment's monthly pay
                        cursor.execute(
                            "UPDATE loan_installment SET monthly_pay = %s WHERE id = %s",
                            (next_monthly_amount, next_installment_id)
                        )
                        print(f"✅ Overdue handled: Added {current_amount} to installment ID {next_installment_id}.")

            print("✅ Database updated successfully!")

            # Return updated amounts to update the UI dynamically
            response_data = {
                "success": True,
                "message": "Status updated successfully.",
                "new_monthly_amount": current_amount,
                "next_monthly_amount": next_monthly_amount
            }
            return JsonResponse(response_data)

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return JsonResponse({"success": False, "message": "An error occurred: " + str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method."})

def get_installments(request):
    if request.method == "GET":
        try:
            with connection.cursor() as cursor:
                # Get all installments with their statuses
                cursor.execute("SELECT id, status, monthly_pay FROM loan_installment ORDER BY id ASC")
                installments = cursor.fetchall()

                # Find the first installment with status 'N'
                first_unpaid = None
                for installment in installments:
                    if installment[1] == 'N':  # Check status
                        first_unpaid = installment
                        break

                # Prepare the response
                response_data = {
                    "installments": installments,
                    "first_unpaid_id": first_unpaid[0] if first_unpaid else None
                }
                return JsonResponse(response_data)

        except Exception as e:
            print(f"❌ Exception: {str(e)}")  
            return JsonResponse({"success": False, "message": "An error occurred: " + str(e)})

    print("❌ Invalid request method (Not GET)")  

def generate_pdf(request, emp_no):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Header with logos and organization info
    header_data = [
        [ReportImage('C:/loan_allotment_django_project/loan_entry_project/myapp/templates/images/wssp_logo.jpg', width=70, height=70),
         Paragraph("WATER & SANITATION SERVICES PESHAWAR (WSSP)<br/>"
                   "LOCAL GOVERNMENT COMPLEX, KHYBER PAKHTUNKHWA<br/>"
                   "Plot # 33, Street No. 13, Sector E-8, Phase-VII, Hayatabad, Peshawar.<br/>"
                   "Office Phone # 091-9219098, Fax # 091-5890560",
                   ParagraphStyle(name='HeaderStyle', fontName='Times-Roman', fontSize=12, alignment=1)),
         ReportImage('C:/loan_allotment_django_project/loan_entry_project/myapp/templates/images/kpk_logo.jpg', width=70, height=70)]
    ]

    header_table = Table(header_data, colWidths=[100, doc.width - 200, 100])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    if emp_no:
        with connection.cursor() as cursor:
            # Fetch employee details
            cursor.execute("""
                SELECT E.EMP_NO, E.EMP_NAME, E.EMP_JOIN_DT, E.EMP_EXP_DT, D.DEPTT_DESC 
                FROM EMP E 
                JOIN DEPTT D ON D.DEPTT_ID = E.EMP_DEPTT
                WHERE E.EMP_NO = %s
            """, [emp_no])
            emp = cursor.fetchone()

            if emp:
                emp_no, emp_name, emp_join_dt, emp_exp_dt, deptt_desc = emp
                emp_name_paragraph = wrap_text(emp_name, 20, styles['Normal'])

                employee_data = [
                    ['Employee No', 'Employee Name', 'Department', 'Joining Date', 'Exit Date'],
                    [emp_no, emp_name_paragraph, deptt_desc,
                     emp_join_dt.strftime('%Y-%m-%d'),
                     emp_exp_dt.strftime('%Y-%m-%d') if emp_exp_dt else 'N/A']
                ]
                employee_table = Table(employee_data, colWidths=[doc.width / 5] * 5)
                employee_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(employee_table)
                elements.append(Spacer(1, 12))

                # Fetch loan details
                cursor.execute("""
                    SELECT LOAN_ID, TOTAL_LOAN, START_DATE, TOTAL_INSTALLMENT, END_DATE, LOAN_STATUS
                    FROM LOAN_ALLOTMENT 
                    WHERE EMP_ID = %s
                    ORDER BY START_DATE DESC
                """, [emp_no])
                loan = cursor.fetchone()

                if loan:
                    loan_id, total_loan, start_date, total_installment, end_date, loan_status = loan

                    loan_data = [
                        ['Loan ID', 'Total Loan', 'Start Date', 'End Date', 'Installments', 'Status'],
                        [loan_id, total_loan,
                         start_date.strftime('%Y-%m-%d'),
                         end_date.strftime('%Y-%m-%d'),
                         total_installment,
                         'Active' if loan_status == 'A' else 'Completed']
                    ]
                    loan_table = Table(loan_data, colWidths=[doc.width / 6] * 6)
                    loan_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(Paragraph("Loan Details:",
                                              ParagraphStyle(name='TitleStyle', fontName='Times-Roman', fontSize=14,
                                                             spaceAfter=6, textColor=colors.black, underline=True)))
                    elements.append(loan_table)
                    elements.append(Spacer(1, 12))

                    # Fetch installment details
                    cursor.execute("""
                        SELECT INSTALLMENT_DATE, MONTHLY_PAY, STATUS 
                        FROM LOAN_INSTALLMENT 
                        WHERE LOAN_ID = %s
                        ORDER BY INSTALLMENT_DATE ASC
                    """, [loan_id])
                    installments = cursor.fetchall()

                    installment_data = [['Installment Date', 'Monthly Pay', 'Status']]
                    for inst in installments:
                        inst_date, monthly_pay, status = inst
                        status_text = {'P': 'Paid', 'O': 'Overdue'}.get(status, 'Pending')
                        installment_data.append([inst_date.strftime('%Y-%m-%d'), monthly_pay, status_text])

                    installment_table = Table(installment_data, colWidths=[doc.width / 3] * 3)
                    installment_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(Paragraph("Installment Details:",
                                              ParagraphStyle(name='TitleStyle', fontName='Times-Roman', fontSize=14,
                                                             spaceAfter=6, textColor=colors.black, underline=True)))
                    elements.append(installment_table)
                else:
                    elements.append(Paragraph("No loan details available.", styles['Normal']))
            else:
                elements.append(Paragraph("Employee not found.", styles['Normal']))
    else:
        elements.append(Paragraph("Employee number is required.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employee_report.pdf"'
    return response

###################################### Access Control #######################################

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import connection
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ViewsAccess, UserViewPermission
import json
from django.urls import get_resolver
from django.urls.exceptions import Resolver404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

def only_master_admin(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if str(request.user.id) == '1009999':
            return view_func(request, *args, **kwargs)
        return redirect('no_access')
    return _wrapped_view

def user_has_view_permission(user_id, view_name):
    """
    Utility function to check if user has permission for a specific view
    Usage: if user_has_view_permission(request.user.id, 'payroll_summary'):
    """
    try:
        view_obj = ViewsAccess.objects.get(view_name=view_name)
        return UserViewPermission.objects.filter(
            user_id=user_id, 
            view=view_obj
        ).exists()
    except ViewsAccess.DoesNotExist:
        return True  # If view not in system, allow access

def get_user_allowed_views(user_id):
    """
    Get list of view names user has access to
    """
    return UserViewPermission.objects.filter(
        user_id=user_id
    ).values_list('view__view_name', flat=True)

def user_permissions(request):
    """
    Add user permissions to template context
    """
    if request.user.is_authenticated:
        allowed_views = get_user_allowed_views(request.user.id)
        return {
            'user_allowed_views': list(allowed_views),
        }
    return {}

def is_admin_user(user):
    """Check if user is admin/superuser"""
    return user.is_authenticated and (user.is_superuser or user.is_staff)

def get_all_users():
    """Get all users from custom users table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT USER_ID, USER_DESC 
            FROM USERS 
            ORDER BY USER_DESC
        """)
        rows = cursor.fetchall()
        return [{'id': r[0], 'name': r[1]} for r in rows]

def get_user_permissions(user_id):
    """Get current permissions for a user"""
    return UserViewPermission.objects.filter(user_id=user_id).values_list('view_id', flat=True)

def get_all_view_names():
    """Get all valid view names from Django URL configuration"""
    resolver = get_resolver()
    view_names = set()
    
    def extract_view_names(url_patterns, namespace=''):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include() pattern
                extract_view_names(pattern.url_patterns, pattern.namespace)
            elif hasattr(pattern, 'callback') and hasattr(pattern, 'name'):
                # This is a regular URL pattern with a name
                if pattern.name:
                    full_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
                    view_names.add(full_name)
                    view_names.add(pattern.name)  # Also add without namespace
    
    extract_view_names(resolver.url_patterns)
    return view_names

@login_required
@user_passes_test(is_admin_user)
@only_master_admin
def system_access_control(request):
    """Main access control management view"""
    users = get_all_users()
    views = ViewsAccess.objects.all().order_by('view_name')

    selected_user_id = request.GET.get('user_id')
    selected_user = None
    current_permissions = []

    if selected_user_id:
        current_permissions = list(get_user_permissions(selected_user_id))
        selected_user = next((u for u in users if u['id'] == int(selected_user_id)), None)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # Add New View
        if action == 'add':
            view_name = request.POST.get('view_name', '').strip()
            view_desc = request.POST.get('view_desc', '').strip()
            
            if not view_name:
                messages.error(request, "View name is required.")
            else:
                # Validate if view name exists in Django URL configuration
                valid_view_names = get_all_view_names()
                
                if view_name not in valid_view_names:
                    messages.error(request, f"Invalid view name '{view_name}'. Please ensure the view exists in your URL configuration.")
                else:
                    # Check if view already exists in database
                    if ViewsAccess.objects.filter(view_name=view_name).exists():
                        messages.error(request, f"View '{view_name}' already exists in the system.")
                    else:
                        try:
                            ViewsAccess.objects.create(
                                view_name=view_name,
                                view_desc=view_desc,
                                is_active=True
                            )
                            messages.success(request, f"View '{view_name}' added successfully.")
                        except Exception as e:
                            messages.error(request, f"Error adding view: {str(e)}")

        # Toggle Activation
        elif action == 'toggle':
            view_id = request.POST.get('view_id')
            try:
                view = ViewsAccess.objects.get(view_id=view_id)
                view.is_active = not view.is_active
                view.save()
                status = "activated" if view.is_active else "deactivated"
                messages.success(request, f"View '{view.view_name}' {status}.")
            except ViewsAccess.DoesNotExist:
                messages.error(request, "View not found.")
            except Exception as e:
                messages.error(request, f"Error updating view: {str(e)}")

        # Update Permissions
        else:
            user_id = request.POST.get('user_id')
            selected_views = request.POST.getlist('views')

            if not user_id:
                messages.error(request, "Please select a user.")
                return redirect('system_access_control')

            try:
                UserViewPermission.objects.filter(user_id=user_id).delete()
                for view_id in selected_views:
                    UserViewPermission.objects.create(
                        user_id=user_id,
                        view_id=view_id,
                        granted_by=request.user.id
                    )
                user_name = next((u['name'] for u in users if u['id'] == int(user_id)), f"User {user_id}")
                messages.success(request, f"Permissions updated successfully for {user_name}.")
            except Exception as e:
                messages.error(request, f"Error updating permissions: {str(e)}")

            return redirect(f"{reverse('system_access_control')}?user_id={user_id}")

    # Get valid view names for frontend validation (optional)
    valid_view_names = list(get_all_view_names())
    
    context = {
        'users': users,
        'views': views,
        'current_permissions': current_permissions,
        'selected_user': selected_user,
        'selected_user_id': selected_user_id,
        'valid_view_names': valid_view_names,  # For potential frontend validation
    }
    return render(request, 'myapp/system_access_control.html', context)

@login_required
@user_passes_test(is_admin_user)
@only_master_admin
def get_user_permissions_ajax(request, user_id):
    """AJAX endpoint to get user permissions"""
    permissions = list(get_user_permissions(user_id))
    return JsonResponse({'permissions': permissions})

def no_access(request):
    """No access page"""
    return render(request, 'myapp/no_access.html')

######################### PAY CLASSIFICATION ####################################

@login_required
def pay_classification_view(request):
    with connection.cursor() as cursor:
        # Fetch Pay Classes
        cursor.execute("SELECT pay_class_id, pay_class_desc FROM pay_class ORDER BY pay_class_id")
        pay_classes = cursor.fetchall()

        # Initialize empty lists (will be populated via AJAX)
        pay_groups = []
        pay_subgroups = []

    return render(request, 'myapp/pay_classification.html', {
        'pay_classes': pay_classes,
        'pay_groups': pay_groups,
        'pay_subgroups': pay_subgroups,
    })

@login_required
@require_http_methods(["GET"])
def get_pay_groups(request):
    """AJAX endpoint to get pay groups for a specific class"""
    pay_class_id = request.GET.get('pay_class_id')
    if not pay_class_id:
        return JsonResponse({'status': 'error', 'message': 'Pay class ID is required'})
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pay_grp_id, pay_grp_desc 
            FROM pay_grp 
            WHERE pay_grp_class = %s 
            ORDER BY pay_grp_id
        """, [pay_class_id])
        pay_groups = cursor.fetchall()
    
    return JsonResponse({
        'status': 'success',
        'pay_groups': [{'id': pg[0], 'desc': pg[1]} for pg in pay_groups]
    })

@login_required
@require_http_methods(["GET"])
def get_pay_subgroups(request):
    """AJAX endpoint to get pay subgroups for a specific group"""
    pay_grp_id = request.GET.get('pay_grp_id')
    if not pay_grp_id:
        return JsonResponse({'status': 'error', 'message': 'Pay group ID is required'})
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pay_subgrp_id, pay_subgrp_desc 
            FROM pay_subgrp 
            WHERE pay_subgrp_grp = %s 
            ORDER BY pay_subgrp_id
        """, [pay_grp_id])
        pay_subgroups = cursor.fetchall()
    
    return JsonResponse({
        'status': 'success',
        'pay_subgroups': [{'id': ps[0], 'desc': ps[1]} for ps in pay_subgroups]
    })

@login_required
@require_http_methods(["POST"])
def add_pay_class(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT NVL(MAX(pay_class_id), 10) + 1 FROM pay_class")
        new_id = cursor.fetchone()[0]
        class_desc = request.POST.get('pay_class_desc', '')
        cursor.execute(
            "INSERT INTO pay_class (pay_class_id, pay_class_desc) VALUES (%s, %s)",
            [new_id, class_desc]
        )
    return JsonResponse({'status': 'success', 'pay_class_id': new_id})

@login_required
@require_http_methods(["POST"])
def add_pay_group(request):
    with connection.cursor() as cursor:
        pay_class_id = request.POST.get('pay_class_id')
        cursor.execute(
            "SELECT %s || LPAD(NVL(MAX(SUBSTR(pay_grp_id, 3, 2)), 0) + 1, 2, '0') FROM pay_grp WHERE pay_grp_class = %s",
            [pay_class_id, pay_class_id]
        )
        new_id = cursor.fetchone()[0]
        group_desc = request.POST.get('pay_grp_desc', '')
        cursor.execute(
            "INSERT INTO pay_grp (pay_grp_id, pay_grp_class, pay_grp_desc) VALUES (%s, %s, %s)",
            [new_id, pay_class_id, group_desc]
        )
    return JsonResponse({'status': 'success', 'pay_grp_id': new_id})

@login_required
@require_http_methods(["POST"])
def add_pay_subgroup(request):
    with connection.cursor() as cursor:
        pay_grp_id = request.POST.get('pay_grp_id')
        cursor.execute(
            "SELECT %s || LPAD(NVL(MAX(SUBSTR(pay_subgrp_id, 5, 2)), 0) + 1, 2, '0') FROM pay_subgrp WHERE pay_subgrp_grp = %s",
            [pay_grp_id, pay_grp_id]
        )
        new_id = cursor.fetchone()[0]
        subgrp_desc = request.POST.get('pay_subgrp_desc', '')
        cursor.execute(
            "INSERT INTO pay_subgrp (pay_subgrp_id, pay_subgrp_grp, pay_subgrp_desc) VALUES (%s, %s, %s)",
            [new_id, pay_grp_id, subgrp_desc]
        )
    return JsonResponse({'status': 'success', 'pay_subgrp_id': new_id})

################## Allowance Prevailing Rate ###########

@login_required
def allowance_prevailing_rate(request):
    allowance_rates = []
    current_period = None
    
    if request.method == 'GET':
        with connection.cursor() as cursor:
            # Fetch existing allowance rates (non-editable) - only completed periods
            cursor.execute("""
                SELECT ar.allw_period, 
                       TO_CHAR(sp.sal_period_month, 'MM-YYYY') AS period_month, 
                       TO_CHAR(sp.sal_period_from, 'DD-MON-YYYY') AS start_date, 
                       TO_CHAR(sp.sal_period_to, 'DD-MON-YYYY') AS end_date, 
                       ar.allw_id, 
                       a.allw_desc, 
                       ar.allw_rate,
                       sp.sal_period_flg
                FROM allw_rate ar
                JOIN sal_period sp ON ar.allw_period = sp.sal_period_id
                JOIN allw a ON ar.allw_id = a.allw_id
                WHERE ar.allw_id = 1009  -- Only show FUEL allowance
                ORDER BY ar.allw_period DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                allowance_rates.append({
                    'allw_period': row[0],
                    'period_month': row[1],
                    'start_date': row[2],
                    'end_date': row[3],
                    'allw_id': row[4],
                    'allw_desc': row[5],
                    'allw_rate': row[6],
                    'period_status': row[7],
                    'is_editable': row[7] == 'N'  # Only current period is editable
                })

            # Fetch current open period (status 'N' - under processing)
            cursor.execute("""
                SELECT sal_period_id, 
                       TO_CHAR(sal_period_month, 'MM-YYYY') AS period_month, 
                       TO_CHAR(sal_period_from, 'DD-MON-YYYY') AS start_date, 
                       TO_CHAR(sal_period_to, 'DD-MON-YYYY') AS end_date,
                       sal_period_flg
                FROM sal_period
                WHERE sal_period_flg = 'N'
                ORDER BY sal_period_id DESC
            """)
            current_period_row = cursor.fetchone()
            if current_period_row:
                current_period = {
                    'sal_period_id': current_period_row[0],
                    'period_month': current_period_row[1],
                    'start_date': current_period_row[2],
                    'end_date': current_period_row[3],
                    'status': current_period_row[4]
                }
                
                # Check if current period already has a fuel allowance rate
                cursor.execute("""
                    SELECT allw_rate 
                    FROM allw_rate 
                    WHERE allw_period = %s AND allw_id = 1009
                """, [current_period['sal_period_id']])
                existing_rate = cursor.fetchone()
                if existing_rate:
                    current_period['existing_rate'] = existing_rate[0]
                else:
                    current_period['existing_rate'] = None

        return render(request, 'myapp/allowance_prevailing_rate.html', {
            'allowance_rates': allowance_rates,
            'current_period': current_period
        })

@login_required
@csrf_exempt
def save_allowance_rate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            allw_period = data.get('allw_period')
            allw_id = data.get('allw_id')
            allw_rate = data.get('allw_rate')

            # Validate input
            if not allw_period or not allw_id or not allw_rate:
                return JsonResponse({'success': False, 'message': 'All fields are required'})

            # Validate allw_id is 1009 (FUEL)
            if int(allw_id) != 1009:
                return JsonResponse({'success': False, 'message': 'Allowance ID must be 1009 (FUEL)'})

            # Validate rate is positive
            if float(allw_rate) <= 0:
                return JsonResponse({'success': False, 'message': 'Rate must be a positive number'})

            with connection.cursor() as cursor:
                # Verify the period is currently open (status 'N')
                cursor.execute("""
                    SELECT sal_period_flg, TO_CHAR(sal_period_month, 'MM-YYYY') AS period_month
                    FROM sal_period 
                    WHERE sal_period_id = %s
                """, [allw_period])
                period_info = cursor.fetchone()
                
                if not period_info:
                    return JsonResponse({'success': False, 'message': 'Invalid salary period'})
                
                if period_info[0] != 'N':
                    return JsonResponse({'success': False, 'message': 'Can only modify rates for current open period (under processing)'})

                # Check if record already exists
                cursor.execute("""
                    SELECT allw_rate 
                    FROM allw_rate 
                    WHERE allw_period = %s AND allw_id = %s
                """, [allw_period, allw_id])
                existing_record = cursor.fetchone()

                if existing_record:
                    # Update existing record
                    cursor.execute("""
                        UPDATE allw_rate 
                        SET allw_rate = %s 
                        WHERE allw_period = %s AND allw_id = %s
                    """, [allw_rate, allw_period, allw_id])
                    message = f'Allowance rate updated successfully for period {period_info[1]}'
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO allw_rate (allw_period, allw_id, allw_rate)
                        VALUES (%s, %s, %s)
                    """, [allw_period, allw_id, allw_rate])
                    message = f'Allowance rate added successfully for period {period_info[1]}'

                # Update emp_pay table for active employees (emp_flg = 'O')
                # This updates the allowance amount based on the new rate
                cursor.execute("""
                    UPDATE emp_pay
                    SET emp_pay_allwamt = emp_pay_allwrate * %s
                    WHERE emp_pay_allw = %s
                    AND emp_pay_emp IN (SELECT emp_no FROM emp WHERE emp_flg = 'O')
                """, [allw_rate, allw_id])
                
                affected_employees = cursor.rowcount

            return JsonResponse({
                'success': True, 
                'message': message,
                'affected_employees': affected_employees,
                'period_month': period_info[1]
            })
            
        except ValueError as e:
            return JsonResponse({'success': False, 'message': 'Invalid number format'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

#################### PAY_TYP-HR ########################

def salary_type_view(request):
    message = ""
    rows = []

    if request.method == "POST":
        desc = request.POST.get("emp_saltyp_desc")
        freq_input = request.POST.get("emp_saltyp_freq")

        # Map frequency: 1 for MONTHLY, 30 for DAILY
        freq = int(freq_input) if freq_input in ["1", "30"] else None

        if not desc:
            message = "Description is required."
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM emp_saltyp WHERE UPPER(emp_saltyp_desc) = UPPER(%s)", [desc])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, "Error: Duplicate record not allowed.")
                else:
                    cursor.execute("SELECT NVL(MAX(emp_saltyp_id), 0) + 1 FROM emp_saltyp")
                    next_id = cursor.fetchone()[0]
                    cursor.execute("""
                        INSERT INTO emp_saltyp (emp_saltyp_id, emp_saltyp_desc, emp_saltyp_freq)
                        VALUES (%s, %s, %s)
                    """, [next_id, desc, freq])
                    messages.success(request, "Record added successfully!")
                    
                # Always redirect after POST to prevent form resubmission
                return redirect(request.path)

    # Fetch data for display
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT emp_saltyp_id, emp_saltyp_desc, emp_saltyp_freq
            FROM emp_saltyp
            ORDER BY emp_saltyp_id
        """)
        rows = cursor.fetchall()

    return render(request, "myapp/salary_type_HR.html", {
        "rows": rows,
    })

################### PAY_TYPE-FIN #######################

def pay_type_fin_view(request):
    message = ""
    rows = []

    if request.method == "POST":
        desc = request.POST.get("fin_paytyp_desc")

        if not desc:
            message = "Description is required."
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM fin_paytyp WHERE UPPER(fin_paytyp_desc) = UPPER(%s)", [desc])
                if cursor.fetchone()[0] > 0:
                    message = "Error::Duplicate record not allowed..."
                else:
                    cursor.execute("SELECT NVL(MAX(fin_paytyp_id), 0) + 1 FROM fin_paytyp")
                    next_id = cursor.fetchone()[0]
                    cursor.execute("""
                        INSERT INTO fin_paytyp (fin_paytyp_id, fin_paytyp_desc)
                        VALUES (%s, %s)
                    """, [next_id, desc])
                    message = "Record added successfully."
                    messages.success(request, message)
                    return redirect('pay_type_fin_view')  # Redirect after successful POST

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT fin_paytyp_id, fin_paytyp_desc
            FROM fin_paytyp
            ORDER BY fin_paytyp_id
        """)
        rows = cursor.fetchall()

    # Mimic Oracle record navigation (placeholder for now)
    if request.GET.get("action") == "next":
        pass  # Enhance with pagination if needed

    return render(request, "myapp/pay_type_fin.html", {
        "rows": rows,
        "message": message,
        "default_desc": ""  # Reset description on reload
    })

################### TAX SLAB ###########################

@login_required
def tax_slab(request):
    tax_slabs = []
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, min_salary, max_salary, fix_tax, sal_percent
                FROM tax_slab
                ORDER BY id
            """)
            rows = cursor.fetchall()
            for row in rows:
                tax_slabs.append({
                    'id': row[0],
                    'min_salary': row[1],
                    'max_salary': row[2],
                    'fix_tax': row[3],
                    'sal_percent': row[4]
                })
        return render(request, 'myapp/tax_slab.html', {'tax_slabs': tax_slabs})

@login_required
@csrf_exempt
def save_tax_slab(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            min_salary = data.get('min_salary')
            max_salary = data.get('max_salary')
            fix_tax = data.get('fix_tax')
            sal_percent = data.get('sal_percent')

            # Validate all required fields (matching Oracle Forms behavior)
            if not min_salary:
                return JsonResponse({'success': False, 'message': 'Minimum salary is required'})
            if not max_salary:
                return JsonResponse({'success': False, 'message': 'Maximum salary is required'})
            if fix_tax is None or fix_tax == '':
                return JsonResponse({'success': False, 'message': 'Fixed tax is required'})
            if sal_percent is None or sal_percent == '':
                return JsonResponse({'success': False, 'message': 'Salary percentage is required'})

            # Validate salary range logic
            if float(min_salary) >= float(max_salary):
                return JsonResponse({'success': False, 'message': 'Maximum salary must be greater than minimum salary'})

            with connection.cursor() as cursor:
                # Check for duplicate or overlapping range (matching Oracle Forms duplicate check)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tax_slab 
                    WHERE (min_salary <= %s AND max_salary >= %s)
                    OR (min_salary <= %s AND max_salary >= %s)
                    OR (%s <= min_salary AND %s >= max_salary)
                """, [min_salary, min_salary, max_salary, max_salary, min_salary, max_salary])
                
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Duplicate or overlapping salary range not allowed'})

                # Auto-generate next ID (matching Oracle Forms sequence logic)
                cursor.execute("""
                    SELECT NVL(MAX(id), 0) + 1
                    FROM tax_slab
                """)
                new_id = cursor.fetchone()[0]

                # Insert new record
                cursor.execute("""
                    INSERT INTO tax_slab (id, min_salary, max_salary, fix_tax, sal_percent)
                    VALUES (%s, %s, %s, %s, %s)
                """, [new_id, float(min_salary), float(max_salary), float(fix_tax), float(sal_percent)])

            return JsonResponse({
                'success': True, 
                'message': 'Tax slab saved successfully',
                'new_id': new_id
            })
            
        except ValueError as e:
            return JsonResponse({'success': False, 'message': 'Invalid numeric values provided'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Database error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

################## Payroll Recommendation HR ################

logger = logging.getLogger(__name__)

@login_required
def payroll_recommendation_hr(request):
    selected_period_id = request.GET.get('period_id')
    active_periods, summary_data, period_info = [], [], {}
    remarks = request.GET.get('remarks', '')
    user_authorized = False
    show_no_pending_popup = False
    buttons_enabled = {
        'recommend': False, 'return': False, 'approve': False,
        'pay_report': False, 'pay_history': False,
        'employee_amends': False, 'overtime_details': False
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM auth_mod_det 
                WHERE auth_mod_det_mod = 12 
                AND auth_mod_det_emp = %s 
                AND auth_mod_det_flg = 'V'
            """, [request.user.id])
            user_authorized = cursor.fetchone()[0] > 0
    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        return render(request, 'myapp/no_access.html')

    if not user_authorized:
        return render(request, 'myapp/no_access.html')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, 
                       TO_CHAR(sal_period_month, 'Mon-YYYY'),
                       sal_period_flg,
                       TO_CHAR(sal_period_from, 'DD-Mon-YYYY'),
                       TO_CHAR(sal_period_to, 'DD-Mon-YYYY'),
                       sal_period_dayscount
                FROM sal_period 
                ORDER BY sal_period_id DESC
            """)
            all_periods = cursor.fetchall()
            active_periods = [p for p in all_periods if p[2] in ('N', 'I')]

            if not active_periods:
                show_no_pending_popup = True
                
    except Exception as e:
        logger.error(f"Period fetch failed: {e}")

    try:
        selected_period_id_int = int(selected_period_id) if selected_period_id else None
    except (TypeError, ValueError):
        selected_period_id_int = None

    if selected_period_id_int:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sal_period_id, 
                           TO_CHAR(sal_period_month, 'Mon-YYYY'),
                           sal_period_dayscount, 
                           TO_CHAR(sal_period_from, 'DD-Mon-YYYY'),
                           TO_CHAR(sal_period_to, 'DD-Mon-YYYY'), 
                           sal_period_flg 
                    FROM sal_period 
                    WHERE sal_period_id = %s
                """, [selected_period_id_int])
                row = cursor.fetchone()
                if row:
                    period_info = {
                        'id': row[0],
                        'month': row[1],
                        'days': row[2],
                        'from': row[3],
                        'to': row[4],
                        'status': 'NEW' if row[5] == 'N' else 'INITIATED' if row[5] == 'I' else 'APPROVED BY HR' if row[5] == 'V' else 'In progress',
                        'flg': row[5]
                    }

                    if row[5] not in ('N', 'I'):
                        show_no_pending_popup = True
                    else:
                        cursor.execute("""
                            SELECT NVL(MAX(pay_track_id), 0)
                            FROM pay_track
                            WHERE pay_track_period = %s
                            AND pay_track_flg = 'N'
                        """, [selected_period_id_int])
                        check_pay_flg = cursor.fetchone()[0]

                        if row[5] == 'N' or 'I':
                            buttons_enabled.update({
                                'recommend': True,
                                'employee_amends': True,
                                'overtime_details': True,
                                'recommend': True,
                                'return': True,
                                'pay_report': True,
                                'pay_history': True
                            })
                            if check_pay_flg != 0:
                                buttons_enabled['approve'] = True

                        # Load summary data
                        cursor.execute("""
                            SELECT z.zone_desc, pav.Staff, pav.TOT_STAFF,
                                   pav.GROSS_SALARY, pav.DEDUCTIONS, pav.NET_SALARY
                            FROM payroll_approval_view pav
                            JOIN zone z ON z.zone_id = pav.zone
                            WHERE pav.PERIOD = %s
                            ORDER BY zone, pav.Staff
                        """, [selected_period_id_int])
                        current_data = cursor.fetchall()

                        cursor.execute("""
                            SELECT z.zone_desc, pav.Staff, pav.TOT_STAFF,
                                   pav.GROSS_SALARY, pav.DEDUCTIONS, pav.NET_SALARY
                            FROM payroll_approval_view pav
                            JOIN zone z ON z.zone_id = pav.zone
                            WHERE pav.PERIOD = %s
                            ORDER BY zone, pav.Staff
                        """, [selected_period_id_int - 1])
                        previous_data = cursor.fetchall()

                        prev_lookup = {
                            f"{r[0]}_{r[1]}": {
                                'tot_staff': r[2] or 0,
                                'gross_salary': float(r[3] or 0),
                                'deductions': float(r[4] or 0),
                                'net_salary': float(r[5] or 0)
                            }
                            for r in previous_data
                        }

                        for row_data in current_data:
                            zone_desc, staff_type, tot_staff, gross, ded, net = row_data
                            key = f"{zone_desc}_{staff_type}"
                            prev = prev_lookup.get(key, {
                                'tot_staff': 0, 'gross_salary': 0.0,
                                'deductions': 0.0, 'net_salary': 0.0
                            })
                            current = {
                                'tot_staff': tot_staff or 0,
                                'gross_salary': float(gross or 0),
                                'deductions': float(ded or 0),
                                'net_salary': float(net or 0)
                            }
                            differences = {
                                k: current[k] - prev[k]
                                for k in ('tot_staff', 'gross_salary', 'deductions', 'net_salary')
                            }
                            summary_data.append({
                                'zone': zone_desc,
                                'staff_type': staff_type,
                                'current': current,
                                'previous': prev,
                                'differences': differences
                            })

        except Exception as e:
            logger.error(f"Payroll processing error: {e}")
            messages.error(request, f"Error loading payroll data: {e}")

    # === Totals Calculation ===
    totals = {
        'prev_staff': 0, 'prev_gross': 0.0, 'prev_deductions': 0.0, 'prev_net': 0.0,
        'curr_staff': 0, 'curr_gross': 0.0, 'curr_deductions': 0.0, 'curr_net': 0.0,
        'diff_staff': 0, 'diff_gross': 0.0, 'diff_deductions': 0.0, 'diff_net': 0.0
    }

    for row in summary_data:
        totals['prev_staff'] += row['previous']['tot_staff']
        totals['prev_gross'] += row['previous']['gross_salary']
        totals['prev_deductions'] += row['previous']['deductions']
        totals['prev_net'] += row['previous']['net_salary']

        totals['curr_staff'] += row['current']['tot_staff']
        totals['curr_gross'] += row['current']['gross_salary']
        totals['curr_deductions'] += row['current']['deductions']
        totals['curr_net'] += row['current']['net_salary']

        totals['diff_staff'] += row['differences']['tot_staff']
        totals['diff_gross'] += row['differences']['gross_salary']
        totals['diff_deductions'] += row['differences']['deductions']
        totals['diff_net'] += row['differences']['net_salary']

    return render(request, 'myapp/payroll_recomendation_hr.html', {
        'active_periods': active_periods,
        'selected_period_id': selected_period_id,
        'period_info': period_info,
        'summary_data': summary_data,
        'remarks': remarks,
        'buttons_enabled': buttons_enabled,
        'user_authorized': user_authorized,
        'show_no_pending_popup': show_no_pending_popup,
        'totals': totals
    })

logger = logging.getLogger(__name__)

@login_required
def payroll_recommendation_action(request):
    if request.method == 'POST':
        action = request.POST.get('action_type')  # Fixed field name
        period_id = request.POST.get('period_id')
        remarks = request.POST.get('remarks', '')

        logger.info(f"Received POST data: {dict(request.POST)}")

        if not action:
            return JsonResponse({'success': False, 'message': 'Action is required'})
        if not period_id:
            return JsonResponse({'success': False, 'message': 'Period ID is required'})
        if action in ['recommend', 'approve', 'return'] and not remarks.strip():
            return JsonResponse({'success': False, 'message': 'Remarks are required for this action'})

        try:
            period_id_int = int(period_id)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid period ID'})

        try:
            with connection.cursor() as cursor:
                # Authorization check
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auth_mod_det 
                    WHERE auth_mod_det_mod = 12 
                      AND auth_mod_det_emp = %s 
                      AND auth_mod_det_flg = 'V'
                """, [request.user.id])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'You are not authorized to perform this action'})

                if action == 'recommend':
                    cursor.execute("SELECT sal_period_flg FROM sal_period WHERE sal_period_id = %s", [period_id_int])
                    current_status_result = cursor.fetchone()

                    if not current_status_result:
                        return JsonResponse({'success': False, 'message': 'Period not found'})

                    current_status = current_status_result[0]
                    logger.info(f"Current period status: {current_status}")

                    # Generate next PAY_TRACK_ID
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    next_id = cursor.fetchone()[0]

                    if current_status == 'N':
                        # Initial recommendation insert
                        cursor.execute("""
                            INSERT INTO pay_track (
                                pay_track_id, pay_track_period, 
                                pay_track_flg, pay_track_flgfrom, 
                                pay_track_flgdt, pay_track_remarks
                            )
                            VALUES (%s, %s, 'I', %s, SYSDATE, %s)
                        """, [next_id, period_id_int, request.user.id, remarks])

                        # Update sal_period status to 'V' with approved by and approved date
                        cursor.execute("""
                            UPDATE sal_period 
                            SET sal_period_flg = 'V',
                                sal_period_init_by = %s,
                                sal_period_init_dt = SYSDATE,
                                sal_period_approved_by = %s,
                                sal_period_approved_dt = TRUNC(SYSDATE)
                            WHERE sal_period_id = %s
                        """, [request.user.id, request.user.id, period_id_int])

                        connection.commit()
                        return JsonResponse({'success': True, 'message': 'Payroll recommended successfully. Period status updated to VERIFIED.'})

                    elif current_status == 'I':
                        # Recommendation from HR to Finance — add pay_track_newflg and pay_track_newflgto
                        cursor.execute("""
                            INSERT INTO pay_track (
                                pay_track_id, pay_track_period, 
                                pay_track_flg, pay_track_newflg, pay_track_newflgto,
                                pay_track_flgfrom, pay_track_flgdt, pay_track_remarks
                            )
                            VALUES (%s, %s, 'I', 'V', '1400001', %s, SYSDATE, %s)
                        """, [next_id, period_id_int, request.user.id, remarks])

                        # Update sal_period status to 'V' with approved by and approved date
                        cursor.execute("""
                            UPDATE sal_period 
                            SET sal_period_flg = 'V',
                                sal_period_approved_by = %s,
                                sal_period_approved_dt = TRUNC(SYSDATE)
                            WHERE sal_period_id = %s
                        """, [request.user.id, period_id_int])

                        connection.commit()
                        return JsonResponse({'success': True, 'message': 'New payroll recommendation recorded successfully. Period status updated to VERIFIED.'})

                    else:
                        return JsonResponse({'success': False, 'message': f'Invalid period status ({current_status}) for recommendation'})

                elif action == 'approve':
                    cursor.execute("""
                        UPDATE pay_track 
                        SET pay_track_flg = 'A',
                            pay_track_approved_by = %s,
                            pay_track_approved_dt = SYSDATE,
                            pay_track_remarks = %s
                        WHERE pay_track_period = %s 
                          AND pay_track_flgdt = (
                              SELECT MAX(pay_track_flgdt) 
                              FROM pay_track 
                              WHERE pay_track_period = %s
                          )
                    """, [request.user.id, remarks, period_id_int, period_id_int])

                    if cursor.rowcount == 0:
                        return JsonResponse({'success': False, 'message': 'No record found to approve or update failed'})

                    connection.commit()
                    return JsonResponse({'success': True, 'message': 'Payroll approved successfully.'})

                elif action == 'return':
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    next_id = cursor.fetchone()[0]

                    cursor.execute("""
                        INSERT INTO pay_track (
                            pay_track_id, pay_track_period, pay_track_flg, pay_track_flgfrom,
                            pay_track_flgdt, pay_track_remarks
                        )
                        VALUES (%s, %s, 'R', %s, SYSDATE, %s)
                    """, [next_id, period_id_int, request.user.id, remarks])

                    cursor.execute("""
                        UPDATE sal_period 
                        SET sal_period_flg = 'N'
                        WHERE sal_period_id = %s
                    """, [period_id_int])

                    connection.commit()
                    return JsonResponse({'success': True, 'message': 'Payroll returned for corrections successfully.'})

                else:
                    return JsonResponse({'success': False, 'message': f'Unknown action: {action}'})

        except Exception as e:
            try:
                connection.rollback()
            except:
                pass
            logger.error(f"Error in payroll action: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': f'Database error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

##################### Payroll Recommendation Finance #######################

logger = logging.getLogger(__name__)

@login_required
def payroll_recommendation_finance(request):
    selected_period_id = request.GET.get('period_id')
    active_periods, summary_data, period_info = [], [], {}
    remarks = request.GET.get('remarks', '')
    user_authorized = False
    show_no_pending_popup = False
    buttons_enabled = {
        'recommend': False, 'return': False, 'approve': False,
        'pay_report': False, 'pay_history': False,
        'employee_amends': False, 'overtime_details': False
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM auth_mod_det 
                WHERE auth_mod_det_mod = 12 
                AND auth_mod_det_emp = %s 
                AND auth_mod_det_flg = 'F'
            """, [request.user.id])
            user_authorized = cursor.fetchone()[0] > 0
    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        return render(request, 'myapp/no_access.html')

    if not user_authorized:
        return render(request, 'myapp/no_access.html')

    try:
        with connection.cursor() as cursor:
            # Fetch periods with 'V' flag for FIN recommendation
            cursor.execute("""
                SELECT sal_period_id, 
                       TO_CHAR(sal_period_month, 'Mon-YYYY'),
                       sal_period_flg,
                       TO_CHAR(sal_period_from, 'DD-Mon-YYYY'),
                       TO_CHAR(sal_period_to, 'DD-Mon-YYYY'),
                       sal_period_dayscount
                FROM sal_period 
                WHERE sal_period_flg = 'V' 
                ORDER BY sal_period_id DESC
            """)
            active_periods = cursor.fetchall()
            
            # Check if no active periods found - this is where the popup should trigger
            if not active_periods:
                show_no_pending_popup = True
                
    except Exception as e:
        logger.error(f"Period fetch failed: {e}")

    try:
        selected_period_id_int = int(selected_period_id) if selected_period_id else None
    except (TypeError, ValueError):
        selected_period_id_int = None

    if selected_period_id_int:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sal_period_id, 
                           TO_CHAR(sal_period_month, 'Mon-YYYY'),
                           sal_period_dayscount, 
                           TO_CHAR(sal_period_from, 'DD-Mon-YYYY'),
                           TO_CHAR(sal_period_to, 'DD-Mon-YYYY'), 
                           sal_period_flg 
                    FROM sal_period 
                    WHERE sal_period_id = %s
                """, [selected_period_id_int])
                row = cursor.fetchone()
                if row:
                    period_flg = row[5]
                    period_info = {
                        'id': row[0],
                        'month': row[1],
                        'days': row[2],
                        'from': row[3],
                        'to': row[4],
                        'status': 'APPROVED BY HR' if period_flg == 'V' else 
                                 'FINALIZED BY FIN' if period_flg == 'F' else 'In progress',
                        'flg': period_flg
                    }

                    # Button enabling logic based on period status
                    if period_flg == 'V':  # HR Approved - ready for FIN recommendation
                        buttons_enabled.update({
                            'recommend': True,
                            'pay_report': True,
                            'pay_history': True,
                            'employee_amends': True,
                            'overtime_details': True,
                            'return': True,
                            'pay_report': True,
                            'pay_history': True
                        })
                        
                        # Check if there's a valid pay_track record for approval
                        cursor.execute("""
                            SELECT COUNT(*)
                            FROM pay_track
                            WHERE pay_track_period = %s
                            AND pay_track_flg = 'V'
                            AND pay_track_newflg = 'F'
                        """, [selected_period_id_int])
                        if cursor.fetchone()[0] > 0:
                            buttons_enabled['approve'] = True

                    # Load summary data if period is valid
                    if period_flg in ('V', 'F'):
                        cursor.execute("""
                            SELECT z.zone_desc, pav.Staff, pav.TOT_STAFF,
                                   pav.GROSS_SALARY, pav.DEDUCTIONS, pav.NET_SALARY
                            FROM payroll_approval_view pav
                            JOIN zone z ON z.zone_id = pav.zone
                            WHERE pav.PERIOD = %s
                            ORDER BY zone, pav.Staff
                        """, [selected_period_id_int])
                        current_data = cursor.fetchall()

                        cursor.execute("""
                            SELECT z.zone_desc, pav.Staff, pav.TOT_STAFF,
                                   pav.GROSS_SALARY, pav.DEDUCTIONS, pav.NET_SALARY
                            FROM payroll_approval_view pav
                            JOIN zone z ON z.zone_id = pav.zone
                            WHERE pav.PERIOD = %s
                            ORDER BY zone, pav.Staff
                        """, [selected_period_id_int - 1])
                        previous_data = cursor.fetchall()

                        prev_lookup = {
                            f"{r[0]}_{r[1]}": {
                                'tot_staff': r[2] or 0,
                                'gross_salary': float(r[3] or 0),
                                'deductions': float(r[4] or 0),
                                'net_salary': float(r[5] or 0)
                            }
                            for r in previous_data
                        }

                        for row_data in current_data:
                            zone_desc, staff_type, tot_staff, gross, ded, net = row_data
                            key = f"{zone_desc}_{staff_type}"
                            prev = prev_lookup.get(key, {
                                'tot_staff': 0, 'gross_salary': 0.0,
                                'deductions': 0.0, 'net_salary': 0.0
                            })
                            current = {
                                'tot_staff': tot_staff or 0,
                                'gross_salary': float(gross or 0),
                                'deductions': float(ded or 0),
                                'net_salary': float(net or 0)
                            }
                            differences = {
                                k: current[k] - prev[k]
                                for k in ('tot_staff', 'gross_salary', 'deductions', 'net_salary')
                            }
                            summary_data.append({
                                'zone': zone_desc,
                                'staff_type': staff_type,
                                'current': current,
                                'previous': prev,
                                'differences': differences
                            })

        except Exception as e:
            logger.error(f"Payroll processing error: {e}")
            messages.error(request, f"Error loading payroll data: {e}")

    # === Totals Calculation ===
    totals = {
        'prev_staff': 0, 'prev_gross': 0.0, 'prev_deductions': 0.0, 'prev_net': 0.0,
        'curr_staff': 0, 'curr_gross': 0.0, 'curr_deductions': 0.0, 'curr_net': 0.0,
        'diff_staff': 0, 'diff_gross': 0.0, 'diff_deductions': 0.0, 'diff_net': 0.0
    }

    for row in summary_data:
        totals['prev_staff'] += row['previous']['tot_staff']
        totals['prev_gross'] += row['previous']['gross_salary']
        totals['prev_deductions'] += row['previous']['deductions']
        totals['prev_net'] += row['previous']['net_salary']

        totals['curr_staff'] += row['current']['tot_staff']
        totals['curr_gross'] += row['current']['gross_salary']
        totals['curr_deductions'] += row['current']['deductions']
        totals['curr_net'] += row['current']['net_salary']

        totals['diff_staff'] += row['differences']['tot_staff']
        totals['diff_gross'] += row['differences']['gross_salary']
        totals['diff_deductions'] += row['differences']['deductions']
        totals['diff_net'] += row['differences']['net_salary']

    return render(request, 'myapp/payroll_recommendation_finance.html', {
        'active_periods': active_periods,
        'selected_period_id': selected_period_id,
        'period_info': period_info,
        'summary_data': summary_data,
        'remarks': remarks,
        'buttons_enabled': buttons_enabled,
        'user_authorized': user_authorized,
        'show_no_pending_popup': show_no_pending_popup,
        'totals': totals
    })

logger = logging.getLogger(__name__)

@login_required
def payroll_recommendation_finance_action(request):
    if request.method == 'POST':
        action = request.POST.get('action_type')  # Fixed field name
        period_id = request.POST.get('period_id')
        remarks = request.POST.get('remarks', '')

        logger.info(f"Received POST data: {dict(request.POST)}")

        if not action:
            return JsonResponse({'success': False, 'message': 'Action is required'})
        if not period_id:
            return JsonResponse({'success': False, 'message': 'Period ID is required'})
        if action in ['recommend', 'approve', 'return'] and not remarks.strip():
            return JsonResponse({'success': False, 'message': 'Remarks are required for this action'})

        try:
            period_id_int = int(period_id)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid period ID'})

        try:
            with connection.cursor() as cursor:
                # Authorization check
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auth_mod_det 
                    WHERE auth_mod_det_mod = 12 
                      AND auth_mod_det_emp = %s 
                      AND auth_mod_det_flg = 'F'
                """, [request.user.id])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'You are not authorized to perform this action'})

                if action == 'recommend':
                    cursor.execute("SELECT sal_period_flg FROM sal_period WHERE sal_period_id = %s", [period_id_int])
                    current_status_result = cursor.fetchone()

                    if not current_status_result:
                        return JsonResponse({'success': False, 'message': 'Period not found'})

                    current_status = current_status_result[0]
                    logger.info(f"Current period status: {current_status}")

                    # Generate next PAY_TRACK_ID
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    next_id = cursor.fetchone()[0]

                    if current_status == 'V':
                        # FIN recommendation insert
                        cursor.execute("""
                            INSERT INTO pay_track (
                                pay_track_id, pay_track_period, 
                                pay_track_flg, pay_track_newflg, pay_track_newflgto,
                                pay_track_flgfrom, pay_track_flgdt, pay_track_remarks
                            )
                            VALUES (%s, %s, 'V', 'F', '1100004', %s, SYSDATE, %s)
                        """, [next_id, period_id_int, request.user.id, remarks])

                        # Update sal_period with FIN details
                        cursor.execute("""
                            UPDATE sal_period 
                            SET sal_period_flg = 'F',
                                sal_period_fin_by = %s,
                                sal_period_fin_dt = TRUNC(SYSDATE)
                            WHERE sal_period_id = %s
                        """, [request.user.id, period_id_int])

                        connection.commit()
                        return JsonResponse({'success': True, 'message': 'Payroll recommended by FIN successfully. Period status updated to FINALIZED.'})

                    else:
                        return JsonResponse({'success': False, 'message': f'Invalid period status ({current_status}) for FIN recommendation'})

                elif action == 'approve':
                    cursor.execute("""
                        UPDATE pay_track 
                        SET pay_track_flg = 'A',
                            pay_track_approved_by = %s,
                            pay_track_approved_dt = SYSDATE,
                            pay_track_remarks = %s
                        WHERE pay_track_period = %s 
                          AND pay_track_flgdt = (
                              SELECT MAX(pay_track_flgdt) 
                              FROM pay_track 
                              WHERE pay_track_period = %s
                          )
                    """, [request.user.id, remarks, period_id_int, period_id_int])

                    if cursor.rowcount == 0:
                        return JsonResponse({'success': False, 'message': 'No record found to approve or update failed'})

                    connection.commit()
                    return JsonResponse({'success': True, 'message': 'Payroll approved successfully.'})

                elif action == 'return':
                    # Check current period status
                    cursor.execute("SELECT sal_period_flg FROM sal_period WHERE sal_period_id = %s", [period_id_int])
                    current_status_result = cursor.fetchone()
                    
                    if not current_status_result:
                        return JsonResponse({'success': False, 'message': 'Period not found'})
                    
                    current_status = current_status_result[0]

                    # Generate next PAY_TRACK_ID
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    next_id = cursor.fetchone()[0]

                    # Insert return record with your specified format
                    cursor.execute("""
                        INSERT INTO pay_track (
                            pay_track_id, pay_track_period, pay_track_flg, pay_track_flgfrom,
                            pay_track_newflg, pay_track_newflgto, pay_track_flgdt, pay_track_remarks
                        )
                        VALUES (%s, %s, 'V', %s, 'J', '1300001', SYSDATE, %s)
                    """, [next_id, period_id_int, request.user.id, remarks])

                    # Update sal_period - reset to 'I' and clear approval fields, but keep FIN fields
                    cursor.execute("""
                        UPDATE sal_period 
                        SET sal_period_flg = 'I',
                            sal_period_approved_by = NULL
                        WHERE sal_period_id = %s
                    """, [period_id_int])

                    connection.commit()
                    return JsonResponse({'success': True, 'message': 'Payroll returned for corrections successfully. Period status reset to INITIATED.'})

                else:
                    return JsonResponse({'success': False, 'message': f'Unknown action: {action}'})

        except Exception as e:
            try:
                connection.rollback()
            except:
                pass
            logger.error(f"Error in payroll action: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': f'Database error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

######################## RECOMMENDATION CEO ########################

logger = logging.getLogger(__name__)

@login_required
def payroll_recommendation_ceo(request):
    selected_period_id = request.GET.get('period_id')
    active_periods, summary_data, period_info = [], [], {}
    remarks = request.GET.get('remarks', '')
    user_authorized = False
    show_no_pending_popup = False
    buttons_enabled = {
        'recommend': False, 'return': False, 'approve': False,
        'pay_report': False, 'pay_history': False,
        'employee_amends': False, 'overtime_details': False
    }

    try:
        with connection.cursor() as cursor:
            # Check CEO authorization (assuming module 13 for CEO or adjust as needed)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM auth_mod_det 
                WHERE auth_mod_det_mod = 12 
                AND auth_mod_det_emp = %s 
                AND auth_mod_det_flg = 'Z'
            """, [request.user.id])
            user_authorized = cursor.fetchone()[0] > 0
    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        return render(request, 'myapp/no_access.html')

    if not user_authorized:
        return render(request, 'myapp/no_access.html')

    try:
        with connection.cursor() as cursor:
            # Fetch periods with 'F' flag for CEO recommendation
            cursor.execute("""
                SELECT sal_period_id, 
                       TO_CHAR(sal_period_month, 'Mon-YYYY'),
                       sal_period_flg,
                       TO_CHAR(sal_period_from, 'DD-Mon-YYYY'),
                       TO_CHAR(sal_period_to, 'DD-Mon-YYYY'),
                       sal_period_dayscount
                FROM sal_period 
                WHERE sal_period_flg = 'F' 
                ORDER BY sal_period_id DESC
            """)
            active_periods = cursor.fetchall()
            
            # Check if no active periods found - this is where the popup should trigger
            if not active_periods:
                show_no_pending_popup = True
                
    except Exception as e:
        logger.error(f"Period fetch failed: {e}")

    try:
        selected_period_id_int = int(selected_period_id) if selected_period_id else None
    except (TypeError, ValueError):
        selected_period_id_int = None

    if selected_period_id_int:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sal_period_id, 
                           TO_CHAR(sal_period_month, 'Mon-YYYY'),
                           sal_period_dayscount, 
                           TO_CHAR(sal_period_from, 'DD-Mon-YYYY'),
                           TO_CHAR(sal_period_to, 'DD-Mon-YYYY'), 
                           sal_period_flg 
                    FROM sal_period 
                    WHERE sal_period_id = %s
                """, [selected_period_id_int])
                row = cursor.fetchone()
                if row:
                    period_flg = row[5]
                    period_info = {
                        'id': row[0],
                        'month': row[1],
                        'days': row[2],
                        'from': row[3],
                        'to': row[4],
                        'status': 'RECOMMENDED BY FIN' if period_flg == 'F' else 
                                 'AUTHORIZED BY CEO' if period_flg == 'Z' else 'In progress',
                        'flg': period_flg
                    }

                    # Button enabling logic based on period status
                    if period_flg == 'F':  # FIN Finalized - ready for CEO recommendation
                        buttons_enabled.update({
                            'recommend': True,
                            'pay_report': True,
                            'pay_history': True,
                            'employee_amends': True,
                            'overtime_details': True,
                            'return': True,
                        })
                        
                        # Check if there's a valid pay_track record for approval
                        cursor.execute("""
                            SELECT COUNT(*)
                            FROM pay_track
                            WHERE pay_track_period = %s
                            AND pay_track_flg = 'F'
                            AND pay_track_newflg = 'Z'
                        """, [selected_period_id_int])
                        if cursor.fetchone()[0] > 0:
                            buttons_enabled['approve'] = True

                    # Load summary data if period is valid
                    if period_flg in ('F', 'Z'):
                        cursor.execute("""
                            SELECT z.zone_desc, pav.Staff, pav.TOT_STAFF,
                                   pav.GROSS_SALARY, pav.DEDUCTIONS, pav.NET_SALARY
                            FROM payroll_approval_view pav
                            JOIN zone z ON z.zone_id = pav.zone
                            WHERE pav.PERIOD = %s
                            ORDER BY zone, pav.Staff
                        """, [selected_period_id_int])
                        current_data = cursor.fetchall()

                        cursor.execute("""
                            SELECT z.zone_desc, pav.Staff, pav.TOT_STAFF,
                                   pav.GROSS_SALARY, pav.DEDUCTIONS, pav.NET_SALARY
                            FROM payroll_approval_view pav
                            JOIN zone z ON z.zone_id = pav.zone
                            WHERE pav.PERIOD = %s
                            ORDER BY zone, pav.Staff
                        """, [selected_period_id_int - 1])
                        previous_data = cursor.fetchall()

                        prev_lookup = {
                            f"{r[0]}_{r[1]}": {
                                'tot_staff': r[2] or 0,
                                'gross_salary': float(r[3] or 0),
                                'deductions': float(r[4] or 0),
                                'net_salary': float(r[5] or 0)
                            }
                            for r in previous_data
                        }

                        for row_data in current_data:
                            zone_desc, staff_type, tot_staff, gross, ded, net = row_data
                            key = f"{zone_desc}_{staff_type}"
                            prev = prev_lookup.get(key, {
                                'tot_staff': 0, 'gross_salary': 0.0,
                                'deductions': 0.0, 'net_salary': 0.0
                            })
                            current = {
                                'tot_staff': tot_staff or 0,
                                'gross_salary': float(gross or 0),
                                'deductions': float(ded or 0),
                                'net_salary': float(net or 0)
                            }
                            differences = {
                                k: current[k] - prev[k]
                                for k in ('tot_staff', 'gross_salary', 'deductions', 'net_salary')
                            }
                            summary_data.append({
                                'zone': zone_desc,
                                'staff_type': staff_type,
                                'current': current,
                                'previous': prev,
                                'differences': differences
                            })

        except Exception as e:
            logger.error(f"Payroll processing error: {e}")
            messages.error(request, f"Error loading payroll data: {e}")

    # === Totals Calculation ===
    totals = {
        'prev_staff': 0, 'prev_gross': 0.0, 'prev_deductions': 0.0, 'prev_net': 0.0,
        'curr_staff': 0, 'curr_gross': 0.0, 'curr_deductions': 0.0, 'curr_net': 0.0,
        'diff_staff': 0, 'diff_gross': 0.0, 'diff_deductions': 0.0, 'diff_net': 0.0
    }

    for row in summary_data:
        totals['prev_staff'] += row['previous']['tot_staff']
        totals['prev_gross'] += row['previous']['gross_salary']
        totals['prev_deductions'] += row['previous']['deductions']
        totals['prev_net'] += row['previous']['net_salary']

        totals['curr_staff'] += row['current']['tot_staff']
        totals['curr_gross'] += row['current']['gross_salary']
        totals['curr_deductions'] += row['current']['deductions']
        totals['curr_net'] += row['current']['net_salary']

        totals['diff_staff'] += row['differences']['tot_staff']
        totals['diff_gross'] += row['differences']['gross_salary']
        totals['diff_deductions'] += row['differences']['deductions']
        totals['diff_net'] += row['differences']['net_salary']

    return render(request, 'myapp/payroll_recommendation_ceo.html', {
        'active_periods': active_periods,
        'selected_period_id': selected_period_id,
        'period_info': period_info,
        'summary_data': summary_data,
        'remarks': remarks,
        'buttons_enabled': buttons_enabled,
        'user_authorized': user_authorized,
        'show_no_pending_popup': show_no_pending_popup,
        'totals': totals
    })

logger = logging.getLogger(__name__)

@login_required
def payroll_recommendation_ceo_action(request):
    if request.method == 'POST':
        action = request.POST.get('action_type')
        period_id = request.POST.get('period_id')
        remarks = request.POST.get('remarks', '')

        logger.info(f"CEO Action - Received POST data: {dict(request.POST)}")

        if not action:
            return JsonResponse({'success': False, 'message': 'Action is required'})
        if not period_id:
            return JsonResponse({'success': False, 'message': 'Period ID is required'})
        if action in ['recommend', 'approve', 'return'] and not remarks.strip():
            return JsonResponse({'success': False, 'message': 'Remarks are required for this action'})

        try:
            period_id_int = int(period_id)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid period ID'})

        try:
            with connection.cursor() as cursor:
                # Authorization check for CEO (adjust module number as needed)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auth_mod_det 
                    WHERE auth_mod_det_mod = 12
                      AND auth_mod_det_emp = %s 
                      AND auth_mod_det_flg = 'Z'
                """, [request.user.id])
                if cursor.fetchone()[0] == 0:
                    return JsonResponse({'success': False, 'message': 'You are not authorized to perform this action'})

                if action == 'recommend':
                    cursor.execute("SELECT sal_period_flg FROM sal_period WHERE sal_period_id = %s", [period_id_int])
                    current_status_result = cursor.fetchone()

                    if not current_status_result:
                        return JsonResponse({'success': False, 'message': 'Period not found'})

                    current_status = current_status_result[0]
                    logger.info(f"Current period status: {current_status}")

                    # Generate next PAY_TRACK_ID
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    next_id = cursor.fetchone()[0]

                    if current_status == 'F':
                        # CEO recommendation insert with your specified values
                        cursor.execute("""
                            INSERT INTO pay_track (
                                pay_track_id, pay_track_period, 
                                pay_track_flg, pay_track_newflg, pay_track_newflgto,
                                pay_track_flgfrom, pay_track_flgdt, pay_track_remarks
                            )
                            VALUES (%s, %s, 'F', 'Z', '1500001', %s, SYSDATE, %s)
                        """, [next_id, period_id_int, request.user.id, remarks])

                        # Update sal_period with CEO details
                        cursor.execute("""
                            UPDATE sal_period 
                            SET sal_period_flg = 'Z',
                                sal_period_auth_by = %s,
                                sal_period_auth_dt = TRUNC(SYSDATE)
                            WHERE sal_period_id = %s
                        """, [request.user.id, period_id_int])

                        connection.commit()
                        return JsonResponse({'success': True, 'message': 'Payroll recommended by CEO successfully. Period status updated to AUTHORIZED.'})

                    else:
                        return JsonResponse({'success': False, 'message': f'Invalid period status ({current_status}) for CEO recommendation'})

                elif action == 'approve':
                    cursor.execute("""
                        UPDATE pay_track 
                        SET pay_track_flg = 'A',
                            pay_track_approved_by = %s,
                            pay_track_approved_dt = SYSDATE,
                            pay_track_remarks = %s
                        WHERE pay_track_period = %s 
                          AND pay_track_flgdt = (
                              SELECT MAX(pay_track_flgdt) 
                              FROM pay_track 
                              WHERE pay_track_period = %s
                          )
                    """, [request.user.id, remarks, period_id_int, period_id_int])

                    if cursor.rowcount == 0:
                        return JsonResponse({'success': False, 'message': 'No record found to approve or update failed'})

                    connection.commit()
                    return JsonResponse({'success': True, 'message': 'Payroll approved by CEO successfully.'})

                elif action == 'return':
                    # Check current period status
                    cursor.execute("SELECT sal_period_flg FROM sal_period WHERE sal_period_id = %s", [period_id_int])
                    current_status_result = cursor.fetchone()
                    
                    if not current_status_result:
                        return JsonResponse({'success': False, 'message': 'Period not found'})
                    
                    current_status = current_status_result[0]

                    # Generate next PAY_TRACK_ID
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    next_id = cursor.fetchone()[0]

                    # Insert return record with CEO specific format
                    cursor.execute("""
                        INSERT INTO pay_track (
                            pay_track_id, pay_track_period, pay_track_flg, pay_track_flgfrom,
                            pay_track_newflg, pay_track_newflgto, pay_track_flgdt, pay_track_remarks
                        )
                        VALUES (%s, %s, 'F', %s, 'V', '1100004', SYSDATE, %s)
                    """, [next_id, period_id_int, request.user.id, remarks])

                    # Update sal_period - reset to 'V' (back to FIN approved status) and clear CEO fields
                    cursor.execute("""
                        UPDATE sal_period 
                        SET sal_period_flg = 'V',
                            sal_period_auth_by = NULL,
                            sal_period_auth_dt = NULL
                        WHERE sal_period_id = %s
                    """, [period_id_int])

                    connection.commit()
                    return JsonResponse({'success': True, 'message': 'Payroll returned to FIN successfully. Period status reset to APPROVED BY HR.'})

                else:
                    return JsonResponse({'success': False, 'message': f'Unknown action: {action}'})

        except Exception as e:
            try:
                connection.rollback()
            except:
                pass
            logger.error(f"Error in CEO payroll action: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': f'Database error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

##################### Payroll Run ###############

@csrf_exempt
@login_required
def payroll_run(request):
    context = {
        'periods': [],
        'payroll_entries': [],
        'period': {},
        'total_earning': Decimal('0.00'),
        'total_deduction': Decimal('0.00'),
        'gross_salary': Decimal('0.00'),
        'net_salary': Decimal('0.00'),
        'employer_pension': Decimal('0.00'),
        'records_exist': False,
        'can_run_payroll': False
    }

    # Check if user is authorized to run payroll (auth_mod_det with mod=12 and flg='P')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM auth_mod_det m
            WHERE m.auth_mod_det_mod = 12
            AND m.auth_mod_det_emp = %s
            AND m.auth_mod_det_flg = 'P'
        """, [request.user.id])  # Replace with actual user ID logic
        auth_count = cursor.fetchone()[0]
        
        if auth_count == 0:
            messages.error(request, 'YOU ARE NOT AUTHORIZED TO RUN PAYROLL.')
            return render(request, 'myapp/payroll_run.html', context)

    # Fetch periods with status 'Z' (approved by CEO, ready for final processing)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sal_period_id, TO_CHAR(sal_period_month, 'Mon-YYYY'), sal_period_flg
            FROM (
                SELECT sal_period_id, sal_period_month, sal_period_flg
                FROM sal_period 
                WHERE sal_period_flg = 'Z'  
                ORDER BY sal_period_id DESC
            )
            WHERE ROWNUM <= 10
        """)
        context['periods'] = cursor.fetchall()

    period_id = request.GET.get('period_id') or request.POST.get('period_id')
    payroll_run_requested = 'payroll_run' in request.POST

    if period_id:
        # Load selected period details
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_month, sal_period_dayscount, sal_period_from, 
                       sal_period_to, sal_period_flg
                FROM sal_period 
                WHERE sal_period_id = %s
            """, [period_id])
            row = cursor.fetchone()

        if row:
            context['period'] = {
                'period_id': period_id,
                'period_month': row[0].strftime('%Y-%m-%d'),
                'period_days': row[1],
                'period_from': row[2].strftime('%Y-%m-%d'),
                'period_to': row[3].strftime('%Y-%m-%d'),
                'period_flg': row[4]
            }

        # Check if payroll records exist for this period
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM payroll WHERE payroll_period = %s", [period_id])
            record_count = cursor.fetchone()[0]
            context['records_exist'] = record_count > 0
            
            # Can run payroll only if records exist and status is 'Z'
            context['can_run_payroll'] = record_count > 0 and context['period'].get('period_flg') == 'Z'

        # Handle Payroll Run Request
        if request.method == 'POST' and payroll_run_requested and context['can_run_payroll']:
            try:
                with connection.cursor() as cursor:
                    # Update sal_period status to 'P' (Processed)
                    cursor.execute("""
                        UPDATE sal_period 
                        SET sal_period_flg = 'P',
                            sal_period_run_by = %s,
                            sal_period_run_dt = TRUNC(SYSDATE)
                        WHERE sal_period_id = %s
                    """, [request.user.id, period_id])  # Replace with actual user ID logic

                    # Get next pay_track_id
                    cursor.execute("SELECT NVL(MAX(pay_track_id), 0) + 1 FROM pay_track")
                    pay_track_id = cursor.fetchone()[0]

                    # Insert pay_track record
                    cursor.execute("""
                        INSERT INTO pay_track (
                            pay_track_id, pay_track_period, pay_track_flg, 
                            pay_track_flgfrom, pay_track_flgdt, pay_track_newflg, 
                            pay_track_newflgto, pay_track_remarks
                        ) VALUES (
                            %s, %s, 'Z', %s, SYSDATE, 'P', NULL, 'PAYROLL PROCESSED'
                        )
                    """, [pay_track_id, period_id, request.user.id])

                    # Update context to reflect new status
                    context['period']['period_flg'] = 'P'
                    context['can_run_payroll'] = False

                messages.success(request, 'CURRENT PAYROLL HAS BEEN PROCESSED SUCCESSFULLY.')
                return redirect(request.path + f"?period_id={period_id}")

            except Exception as e:
                print(f"Error in payroll processing: {str(e)}")
                messages.error(request, f'ERROR WHILE PROCESSING CURRENT PAYROLL: {str(e)}')

        # Fetch payroll entries if records exist
        if context['records_exist']:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.payroll_emp, e.emp_name, p.payroll_allw, a.allw_typ, 
                        a.allw_desc, a.allw_earn_deduc, p.payroll_allwrate, 
                        p.payroll_allwamt, p.payroll_duty_days, p.payroll_flg
                    FROM payroll p
                    JOIN allw a ON a.allw_id = p.payroll_allw
                    JOIN emp e ON e.emp_no = p.payroll_emp
                    WHERE p.payroll_period = %s
                    ORDER BY p.payroll_emp, p.payroll_allw
                """, [period_id])
                rows = cursor.fetchall()

                # Initialize totals
                context['total_earning'] = Decimal('0.00')
                context['total_deduction'] = Decimal('0.00')
                context['employer_pension'] = Decimal('0.00')
                context['gross_salary'] = Decimal('0.00')
                context['net_salary'] = Decimal('0.00')

                for row in rows:
                    emp_no = row[0]
                    emp_name = row[1]
                    allw_id = row[2]
                    allw_typ = row[3]
                    allw_desc = row[4]
                    earn_deduc = row[5]
                    rate = Decimal(row[6] or 0)
                    amount = Decimal(row[7] or 0)
                    duty_days = row[8]
                    payroll_flg = row[9]
                    
                    # Calculate individual totals based on earn_deduc flag
                    payroll_earning = Decimal('0.00')
                    payroll_deduction = Decimal('0.00')
                    payroll_employer_pension = Decimal('0.00')
                    
                    try:
                        earn_deduc_val = int(earn_deduc)
                    except (ValueError, TypeError):
                        earn_deduc_val = 0
                    
                    if earn_deduc_val == 0:  # Employer pension
                        payroll_employer_pension = amount
                        payroll_deduction = Decimal('0.00')
                        payroll_earning = Decimal('0.00')
                    elif earn_deduc_val == 1:  # Earning
                        payroll_employer_pension = Decimal('0.00')
                        payroll_deduction = Decimal('0.00')
                        payroll_earning = amount
                    elif earn_deduc_val == -1:  # Deduction
                        payroll_employer_pension = Decimal('0.00')
                        payroll_deduction = abs(amount)  # Make deductions positive for display
                        payroll_earning = Decimal('0.00')

                    entry = {
                        'emp_no': emp_no,
                        'emp_name': emp_name,
                        'allw_id': allw_id,
                        'allw_typ': allw_typ,
                        'allw_desc': allw_desc,
                        'earn_deduc': earn_deduc_val,
                        'rate': rate,
                        'amount': amount,
                        'duty_days': duty_days,
                        'payroll_flg': payroll_flg,
                        'payroll_earning': payroll_earning,
                        'payroll_deduction': payroll_deduction,
                        'payroll_employer_pension': payroll_employer_pension
                    }
                    
                    context['payroll_entries'].append(entry)

                    # Add to totals
                    context['total_earning'] += payroll_earning
                    context['total_deduction'] += payroll_deduction
                    context['employer_pension'] += payroll_employer_pension

                # Calculate gross and net salary
                context['gross_salary'] = context['total_earning'] + context['employer_pension']
                context['net_salary'] = context['total_earning'] - context['total_deduction']

    return render(request, 'myapp/payroll_run.html', context)

#################### Attendence Submission #################

@login_required
def attendance_submission(request):
    """Main attendance submission view"""
    context = {
        'show_empty': True,
        'active_period': None,
        'available_dates': [],
        'selected_date': None,
        'selected_employee': None,
        'date_info': None,
        'employees_data': [],
        'leave_types': [],
        'search_term': '',
        'show_all_employees': False
    }
    
    # Get active salary period
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, sal_period_from, sal_period_to, 
                       sal_period_month, sal_period_flg
                FROM sal_period 
                WHERE sal_period_flg = 'N'
            """)
            
            period_row = cursor.fetchone()
            if not period_row:
                messages.error(request, "NEW PAY PERIOD NOT INITIALIZED YET.")
                return render(request, 'myapp/attendance_submission.html', context)
            
            period_id, period_from, period_to, period_month, period_flg = period_row
            
            # Convert to date objects if they're datetime objects
            if hasattr(period_from, 'date'):
                period_from = period_from.date()
            if hasattr(period_to, 'date'):
                period_to = period_to.date()
            
            context['active_period'] = {
                'id': period_id,
                'from': period_from,
                'to': period_to,
                'month': period_month,
                'flag': period_flg
            }
            
            # Generate available dates within the period
            available_dates = []
            current_date = period_from
            while current_date <= period_to:
                available_dates.append({
                    'date': current_date,
                    'day_name': current_date.strftime('%A').upper(),
                    'formatted_date': current_date.strftime('%d-%m-%Y')
                })
                current_date += timedelta(days=1)
            
            context['available_dates'] = available_dates
            
            # Get leave types
            cursor.execute("SELECT leav_typid, leav_typdesc FROM leav_typ")
            context['leave_types'] = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
    except Exception as e:
        messages.error(request, f"Database error: {str(e)}")
        return render(request, 'myapp/attendance_submission.html', context)
    
    # Handle date selection
    if request.method == 'POST' and 'selected_date' in request.POST:
        selected_date_str = request.POST.get('selected_date')
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            
            # Validate date is within period
            if period_from <= selected_date <= period_to:
                context['selected_date'] = selected_date
                context['date_info'] = {
                    'date': selected_date,
                    'day_name': selected_date.strftime('%A').upper(),
                    'formatted_date': selected_date.strftime('%d-%m-%Y'),
                    'period_from': period_from.strftime('%d-%m-%Y'),
                    'period_to': period_to.strftime('%d-%m-%Y'),
                    'period_month': period_month.strftime('%m-%Y') if hasattr(period_month, 'strftime') else str(period_month),
                    'period_status': 'NEW'
                }
                
                # Check if attendance already exists for this date
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM att 
                        WHERE att_period = %s AND att_dt = %s 
                        AND att_emp IN (SELECT emp_no FROM emp WHERE emp_mgr = %s)
                    """, [period_id, selected_date, request.user.id])
                    
                    count = cursor.fetchone()[0]
                    context['attendance_exists'] = count > 0
                    
                    if count > 0:
                        cursor.execute("""
                            SELECT DISTINCT att_flg 
                            FROM att 
                            WHERE att_period = %s AND att_dt = %s 
                            AND att_emp IN (SELECT emp_no FROM emp WHERE emp_mgr = %s)
                        """, [period_id, selected_date, request.user.id])
                        
                        flag_row = cursor.fetchone()
                        context['attendance_flag'] = flag_row[0] if flag_row else 'N'
                    else:
                        context['attendance_flag'] = 'N'
                
                # Load all employees for this date
                context['employees_data'] = get_employees_attendance_data(request.user.id, selected_date, period_id)
                context['show_all_employees'] = True
                    
            else:
                messages.error(request, f"ATTENDANCE DATE MUST BE BETWEEN {period_from.strftime('%d-%m-%Y')} AND {period_to.strftime('%d-%m-%Y')}")
                
        except ValueError:
            messages.error(request, "Invalid date format")
    
    # Handle employee search with date
    if request.method == 'POST' and 'search_employee' in request.POST and context['selected_date']:
        search_term = request.POST.get('search_term', '').strip()
        context['search_term'] = search_term
        
        if search_term:
            # Filter employees based on search term
            context['employees_data'] = get_employees_attendance_data(
                request.user.id, 
                context['selected_date'], 
                period_id, 
                search_term
            )
            context['show_all_employees'] = True
        else:
            # Show all employees if search term is empty
            context['employees_data'] = get_employees_attendance_data(request.user.id, context['selected_date'], period_id)
            context['show_all_employees'] = True

    return render(request, 'myapp/attendance_submission.html', context)

def get_employees_attendance_data(manager_id, att_date, period_id, search_term=None):
    """Get all employees with their attendance data for a specific date"""
    try:
        with connection.cursor() as cursor:
            # Base query for employees under manager
            base_query = """
                SELECT e.emp_no, e.emp_name, e.emp_fname,
                       COALESCE(a.att_status, 'P') as att_status,
                       COALESCE(a.att_leave_typ, 0) as att_leave_typ,
                       COALESCE(a.att_overtime_typ, 'N') as att_overtime_typ,
                       COALESCE(a.att_flg, 'N') as att_flg,
                       COALESCE(h.holiday_typ, 'N') as holiday_typ,
                       COALESCE(el.emp_leav_typ, 0) as approved_leave_typ
                FROM emp e
                LEFT JOIN att a ON e.emp_no = a.att_emp AND a.att_period = %s AND a.att_dt = %s
                LEFT JOIN holiday h ON h.holiday_dt = %s
                LEFT JOIN emp_leav el ON e.emp_no = el.emp_leav_emp 
                    AND el.emp_leav_from <= %s 
                    AND el.emp_leav_to >= %s 
                    AND el.emp_leav_flg = 'A'
                WHERE e.emp_flg = 'O' 
                  AND e.emp_att_flg = 'Y' 
                  AND e.emp_mgr = %s
                  AND e.emp_join_dt <= %s
            """
            
            params = [period_id, att_date, att_date, att_date, att_date, manager_id, att_date]
            
            # Add search filter if provided
            if search_term:
                base_query += """
                    AND (
                        UPPER(e.emp_name) LIKE UPPER(%s) 
                        OR UPPER(e.emp_fname) LIKE UPPER(%s)
                        OR TO_CHAR(e.emp_no) LIKE %s
                    )
                """
                params.extend([f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'])
            
            base_query += " ORDER BY e.emp_name"
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            employees_data = []
            for row in rows:
                emp_no, emp_name, emp_fname, att_status, att_leave_typ, att_overtime_typ, att_flg, holiday_typ, approved_leave_typ = row
                
                # Determine default status based on conditions
                default_status = att_status
                if approved_leave_typ and approved_leave_typ != 0:
                    default_status = 'L'
                elif holiday_typ and holiday_typ != 'N':
                    default_status = 'H'
                
                employees_data.append({
                    'emp_no': emp_no,
                    'emp_name': f"{emp_name} S/O {emp_fname}",
                    'att_status': default_status,
                    'att_leave_typ': approved_leave_typ if approved_leave_typ != 0 else att_leave_typ,
                    'att_overtime_typ': att_overtime_typ,
                    'att_flg': att_flg,
                    'holiday_typ': holiday_typ,
                    'has_approved_leave': bool(approved_leave_typ and approved_leave_typ != 0),
                    'is_holiday': bool(holiday_typ and holiday_typ != 'N'),
                    'is_existing_record': bool(att_status != 'P' or att_leave_typ != 0 or att_overtime_typ != 'N')
                })
            
            return employees_data
            
    except Exception as e:
        logger.error(f"Error getting employees attendance data: {str(e)}")
        return []

@login_required
def search_employees_ajax(request):
    """AJAX endpoint for employee search"""
    term = request.GET.get('term', '').strip()
    user_id = request.user.id

    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if len(term) < 2:
        return JsonResponse([], safe=False)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT emp_no, emp_name, emp_fname
                FROM emp 
                WHERE emp_flg = 'O' 
                  AND emp_att_flg = 'Y' 
                  AND emp_mgr = %s
                  AND (
                    UPPER(emp_name) LIKE UPPER(%s) 
                    OR UPPER(emp_fname) LIKE UPPER(%s)
                    OR TO_CHAR(emp_no) LIKE %s
                )
                ORDER BY emp_name
                FETCH FIRST 10 ROWS ONLY
            """, [user_id, f'%{term}%', f'%{term}%', f'%{term}%'])

            rows = cursor.fetchall()
            employees = [
                {'emp_no': row[0], 'name': f"{row[1]} S/O {row[2]}", 'id': row[0]}
                for row in rows
            ]

        return JsonResponse(employees, safe=False)

    except Exception as e:
        return JsonResponse({'error': 'Error searching employee'}, status=500)

@login_required
@csrf_exempt
def submit_attendance(request):
    """Submit attendance for approval"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        emp_no = data.get('emp_no')
        att_date = datetime.strptime(data.get('att_date'), '%Y-%m-%d').date()
        att_status = data.get('att_status')
        leave_type = data.get('leave_type', 0)
        overtime_type = data.get('overtime_type', 'N')
        
        if not emp_no:
            return JsonResponse({'error': 'Employee number is required'}, status=400)
        
        with connection.cursor() as cursor:
            # Get active period
            cursor.execute("""
                SELECT sal_period_id, sal_period_from, sal_period_to
                FROM sal_period 
                WHERE sal_period_flg = 'N'
            """)
            
            period_row = cursor.fetchone()
            if not period_row:
                return JsonResponse({'error': 'No active period found'}, status=400)
            
            period_id, period_from, period_to = period_row
            
            if hasattr(period_from, 'date'):
                period_from = period_from.date()
            if hasattr(period_to, 'date'):
                period_to = period_to.date()
            
            if not (period_from <= att_date <= period_to):
                return JsonResponse({'error': 'Date outside valid range'}, status=400)
            
            # Check if employee is valid
            cursor.execute("""
                SELECT COUNT(*) 
                FROM emp 
                WHERE emp_no = %s 
                AND emp_flg = 'O' 
                AND emp_att_flg = 'Y' 
                AND emp_mgr = %s
                AND emp_join_dt <= %s
            """, [emp_no, request.user.id, att_date])
            
            if cursor.fetchone()[0] == 0:
                return JsonResponse({'error': 'Invalid employee or not authorized'}, status=400)
            
            # Check if attendance already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM att 
                WHERE att_period = %s AND att_dt = %s AND att_emp = %s
            """, [period_id, att_date, emp_no])
            
            exists = cursor.fetchone()[0] > 0
            
            # Get holiday type
            cursor.execute("""
                SELECT COALESCE(holiday_typ, 'N') 
                FROM holiday 
                WHERE holiday_dt = %s
            """, [att_date])
            
            holiday_row = cursor.fetchone()
            holiday_type = holiday_row[0] if holiday_row else 'N'
            
            if att_status == 'L' and (not leave_type or leave_type == 0):
                return JsonResponse({'error': 'Leave type is required for leave status'}, status=400)
            
            # Insert or update attendance
            if exists:
                cursor.execute("""
                    UPDATE att 
                    SET att_status = %s, 
                        att_leave_typ = %s, 
                        att_overtime_typ = %s,
                        att_holiday_typ = %s,
                        att_posted_by = %s
                    WHERE att_period = %s AND att_dt = %s AND att_emp = %s
                """, [att_status, leave_type, overtime_type, holiday_type, request.user.id, period_id, att_date, emp_no])
            else:
                cursor.execute("""
                    INSERT INTO att (
                        att_period, att_dt, att_emp, att_status, 
                        att_holiday_typ, att_leave_typ, att_overtime_typ, 
                        att_posted_by, att_flg
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'N')
                """, [period_id, att_date, emp_no, att_status, holiday_type, leave_type, overtime_type, request.user.id])
            
        return JsonResponse({'success': True, 'message': 'Attendance updated successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
def submit_attendance_for_approval(request):
    """Submit all attendance for a date for approval"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        att_date = datetime.strptime(data.get('att_date'), '%Y-%m-%d').date()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id
                FROM sal_period 
                WHERE sal_period_flg = 'N'
            """)
            
            period_row = cursor.fetchone()
            if not period_row:
                return JsonResponse({'error': 'No active period found'}, status=400)
            
            period_id = period_row[0]
            
            cursor.execute("""
                UPDATE att 
                SET att_flg = 'I'
                WHERE att_period = %s 
                AND att_dt = %s 
                AND att_flg IN ('N', 'J')
                AND att_emp IN (SELECT emp_no FROM emp WHERE emp_mgr = %s)
            """, [period_id, att_date, request.user.id])
            
            rows_updated = cursor.rowcount
            
            if rows_updated == 0:
                return JsonResponse({'error': 'No attendance records found to submit'}, status=400)
        
        return JsonResponse({
            'success': True, 
            'message': f'Attendance dated {att_date.strftime("%d-%m-%Y")} submitted for approval'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

###################### Attendence PDF ##################

from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import BytesIO
from datetime import timedelta, datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus.flowables import Image as ReportImage

@login_required
def attendance_report_view(request):
    context = {}
    user_id = request.user.username  # Manager ID from current user

    if request.method == 'POST':
        selected_period_id = request.POST.get('sal_period_id')
        
        if selected_period_id:
            # Generate PDF and return as download
            pdf_response = generate_attendance_pdf(selected_period_id, user_id)
            return pdf_response

    # Fetch top 5 periods for dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sal_period_id, sal_period_month, sal_period_yr
            FROM sal_period
            ORDER BY sal_period_id DESC 
            FETCH FIRST 5 ROWS ONLY
        """)
        periods = cursor.fetchall()

    context['periods'] = periods
    return render(request, 'myapp/attendance_report.html', context)

def generate_attendance_pdf(selected_period_id, manager_id):
    """Generate PDF report for attendance data"""
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.platypus.frames import Frame
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
    from reportlab.lib.units import inch
    from io import BytesIO
    from datetime import datetime, timedelta
    from django.db import connection
    from django.http import HttpResponse
    
    buffer = BytesIO()
    
    # Custom document template with footer
    class CustomDocTemplate(BaseDocTemplate):
        def __init__(self, filename, **kwargs):
            BaseDocTemplate.__init__(self, filename, **kwargs)
            
        def afterPage(self):
            """Add footer to every page"""
            self.canv.saveState()
            # Footer text (centered)
            footer_text = "This Computer generated Report doesn't require any Signature."
            self.canv.setFont("Helvetica", 8)
            self.canv.drawCentredString(self.pagesize[0] / 2, 20, footer_text)
            
            # Page number (bottom right)
            page_num = f"Page {self.canv.getPageNumber()}"
            self.canv.setFont("Helvetica", 8)
            self.canv.drawRightString(self.pagesize[0] - 30, 20, page_num)
            
            self.canv.restoreState()
    
    doc = CustomDocTemplate(buffer, pagesize=landscape(A4), 
                           rightMargin=15, leftMargin=15, 
                           topMargin=15, bottomMargin=30)  # Increased bottom margin for footer
    
    # Create frame for content
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='main')
    template = PageTemplate(id='main', frames=[frame])
    doc.addPageTemplates([template])
    
    elements = []
    styles = getSampleStyleSheet()

    # Fetch period details
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sal_period_id, sal_period_from, sal_period_to, 
                   sal_period_dayscount, sal_period_flg, sal_period_month, sal_period_yr
            FROM sal_period
            WHERE sal_period_id = %s
        """, [selected_period_id])
        period_info = cursor.fetchone()

    if not period_info:
        # Return error response if period not found
        response = HttpResponse("Period not found", status=404)
        return response

    # Fetch attendance data using your query with department name
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ATT.ATT_POSTED_BY, ATT.ATT_APPROVED_BY, ATT.ATT_EMP, 
                   EMP.EMP_NAME, EMP.EMP_EXP_DT, D.DEPTT_DESC, 
                   ATT.ATT_DT ATT_DATE, ATT.ATT_STATUS||ATT.ATT_OVERTIME_TYP ATT_STAT, 
                   ATT.ATT_ACCEPTED_BY
            FROM EMP, ATT, DEPTT D
            WHERE ATT.ATT_PERIOD = %s
              AND ATT.ATT_POSTED_BY = %s
              AND ATT.ATT_FLG IN ('I', 'V', 'C')
              AND ATT.ATT_EMP = EMP.EMP_NO
              AND EMP.EMP_DEPTT = D.DEPTT_ID
            ORDER BY ATT.ATT_EMP, ATT.ATT_DT
        """, [selected_period_id, manager_id])
        attendance_data = cursor.fetchall()

    # Get employee details for signatures
    def get_employee_details(emp_id):
        if not emp_id:
            return "N/A", "N/A"
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EMP_NO, EMP_NAME 
                FROM EMP 
                WHERE EMP_NO = %s
            """, [emp_id])
            result = cursor.fetchone()
            return result if result else (emp_id, "N/A")

    # FIXED: Format attendance month using sal_period_month and sal_period_yr
    def safe_convert_to_int(value):
        """Safely convert value to int, handling datetime objects"""
        if value is None:
            return None
        if isinstance(value, datetime):
            # If it's a datetime object, extract the relevant part
            # For month, get the month; for year, get the year
            return value.month if hasattr(value, 'month') else None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    if period_info[5] and period_info[6]:  # sal_period_month and sal_period_yr
        # Safely convert month and year to integers
        month_int = safe_convert_to_int(period_info[5])
        year_int = safe_convert_to_int(period_info[6])
        
        if isinstance(period_info[6], datetime):
            year_int = period_info[6].year
        
        if month_int and year_int:
            # Convert month number to month name
            months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            month_name = months[month_int] if 1 <= month_int <= 12 else 'Unknown'
            attendance_month = f"{month_name} {year_int}"
        else:
            attendance_month = "N/A"
    else:
        attendance_month = "N/A"

    # ─── Header with Logos ─────────────────────────────────────────────────────────
    header_data = [
        [
            ReportImage('C:/loan_allotment_django_project/loan_entry_project/myapp/templates/images/wssp_logo.jpg', 
                       width=50, height=50),
            Paragraph("WATER & SANITATION SERVICES PESHAWAR (WSSP)<br/>"
                     "LOCAL GOVERNMENT COMPLEX, KHYBER PAKHTUNKHWA<br/>"
                     "Plot # 33, Street No. 13, Sector E-8, Phase-VII, Hayatabad, Peshawar.<br/>"
                     "Office Phone # 091-9219098, Fax # 091-5890560<br/>"
                     f"<b>Attendance Report: {attendance_month}</b>",
                     ParagraphStyle(name='HeaderCenter', fontName='Times-Roman', fontSize=11, alignment=1)),
            ReportImage('C:/loan_allotment_django_project/loan_entry_project/myapp/templates/images/kpk_logo.jpg', 
                       width=50, height=50)
        ]
    ]

    header_table = Table(header_data, colWidths=[70, doc.width - 140, 70])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))

    # ─── Calculate column widths for attendance table first ────────────────────────
    if attendance_data and period_info[3]:
        # Generate actual dates for the salary period
        period_from = period_info[1]  # sal_period_from
        period_to = period_info[2]    # sal_period_to
        
        # Create list of actual dates
        actual_dates = []
        date_to_day_mapping = {}  # Maps actual date to day number for data lookup
        
        if period_from and period_to:
            current_date = period_from
            day_counter = 1
            
            while current_date <= period_to:
                actual_dates.append(current_date)
                date_to_day_mapping[current_date.day] = current_date
                current_date += timedelta(days=1)
                day_counter += 1
        else:
            # Fallback if dates are not available
            actual_dates = list(range(1, period_info[3] + 1))
        
        # Calculate column widths to fit page strictly
        available_width = doc.width - 10  # Small buffer for margins
        
        # Fixed columns widths (increased for better text wrapping)
        emp_no_width = 35
        emp_name_width = 80  # Increased for better name display
        exp_date_width = 50
        dept_width = 70      # Increased for better department display
        
        # Summary columns widths (reduced)
        summary_cols = 6  # Present, Leave, Absent, Overtime, D. Duty, W. Days
        summary_width = 20
        
        # Calculate remaining width for day columns
        fixed_width = emp_no_width + emp_name_width + exp_date_width + dept_width + (summary_cols * summary_width)
        remaining_width = available_width - fixed_width
        
        # Ensure we don't exceed available width
        if remaining_width > 0:
            day_width = remaining_width / len(actual_dates) if actual_dates else 15
            # Set minimum and maximum day column width
            day_width = max(12, min(day_width, 20))
        else:
            # If not enough space, adjust columns but keep reasonable sizes
            day_width = 12
            emp_name_width = 70  # Keep reasonable size for names
            dept_width = 60      # Keep reasonable size for departments
            summary_width = 18
        
        # Create column widths list
        col_widths = [emp_no_width, emp_name_width, exp_date_width, dept_width]
        col_widths.extend([day_width] * len(actual_dates))
        col_widths.extend([summary_width] * summary_cols)
        
        # Ensure total width doesn't exceed available width
        total_width = sum(col_widths)
        if total_width > available_width:
            # Scale down all columns proportionally
            scale_factor = available_width / total_width
            col_widths = [width * scale_factor for width in col_widths]
        
        # Store the total table width for signature table
        attendance_table_width = sum(col_widths)
    else:
        attendance_table_width = doc.width - 10

    # ─── Signature Details Section (Same width as attendance table) ────────────────
    if attendance_data:
        # Get unique values for signatures
        posted_by_id = attendance_data[0][0] if attendance_data else ''
        approved_by_id = attendance_data[0][1] if attendance_data else ''
        accepted_by_id = attendance_data[0][8] if attendance_data else ''
        
        # Get employee details
        posted_emp_no, posted_emp_name = get_employee_details(posted_by_id)
        approved_emp_no, approved_emp_name = get_employee_details(approved_by_id)
        accepted_emp_no, accepted_emp_name = get_employee_details(accepted_by_id)
        
        # Create formatted signature content with better styling
        def create_signature_content(emp_id, emp_name):
            return f"<b>ID:</b> {emp_id}<br/><b>Name:</b> {emp_name}"
        
        signature_data = [
            ['Prepared By', 'Approved By', 'Accepted By'],
            [
                Paragraph(create_signature_content(posted_emp_no, posted_emp_name), 
                         ParagraphStyle(name='SignatureStyle', fontName='Helvetica', fontSize=8, 
                                      alignment=1, leading=9, spaceAfter=1)),
                Paragraph(create_signature_content(approved_emp_no, approved_emp_name), 
                         ParagraphStyle(name='SignatureStyle', fontName='Helvetica', fontSize=8, 
                                      alignment=1, leading=9, spaceAfter=1)),
                Paragraph(create_signature_content(accepted_emp_no, accepted_emp_name), 
                         ParagraphStyle(name='SignatureStyle', fontName='Helvetica', fontSize=8, 
                                      alignment=1, leading=9, spaceAfter=1))
            ]
        ]
    else:
        signature_data = [
            ['Prepared By', 'Approved By', 'Accepted By'],
            [
                Paragraph("<b>ID:</b> N/A<br/><b>Name:</b> N/A", 
                         ParagraphStyle(name='SignatureStyle', fontName='Helvetica', fontSize=8, 
                                      alignment=1, leading=9, spaceAfter=1)),
                Paragraph("<b>ID:</b> N/A<br/><b>Name:</b> N/A", 
                         ParagraphStyle(name='SignatureStyle', fontName='Helvetica', fontSize=8, 
                                      alignment=1, leading=9, spaceAfter=1)),
                Paragraph("<b>ID:</b> N/A<br/><b>Name:</b> N/A", 
                         ParagraphStyle(name='SignatureStyle', fontName='Helvetica', fontSize=8, 
                                      alignment=1, leading=9, spaceAfter=1))
            ]
        ]

    # Use the same width as attendance table and reduce height
    signature_col_width = attendance_table_width / 3
    signature_table = Table(signature_data, 
                           colWidths=[signature_col_width] * 3, 
                           rowHeights=[20, 25])  # Reduced height from [28, 40]
    
    signature_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),  # Reduced from 10
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 3),    # Reduced from 5
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Reduced from 5
        ('LEFTPADDING', (0, 0), (-1, -1), 2),    # Reduced from 3
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),   # Reduced from 3
    ]))
    elements.append(signature_table)
    elements.append(Spacer(1, 10))  # Reduced spacing

    # ─── Attendance Table ──────────────────────────────────────────────────────────
    if attendance_data and period_info[3]:
        # Create header row with actual dates
        header = ['Emp.\nNo.', 'Employee Name', 'Exp.\nDate', 'Dept']
        
        # Add actual dates as column headers
        if period_from and period_to:
            for date in actual_dates:
                # Format date as DD or DD\nMM for better readability
                if isinstance(date, datetime):
                    header.append(f"{date.day}\n{date.strftime('%b')}")
                else:
                    header.append(str(date))
        else:
            # Fallback to day numbers
            header.extend([str(day) for day in actual_dates])
        
        header.extend(['Pres', 'Leave', 'Abs', 'OT', 'DD', 'WD'])
        rows = [header]

        # Process attendance data
        emp_data = {}
        for row in attendance_data:
            posted_by, approved_by, emp_no, emp_name, exp_date, dept_desc, att_date, att_status, accepted_by = row
            
            if emp_no not in emp_data:
                emp_data[emp_no] = {
                    'name': emp_name,  # Keep full name
                    'exp_date': exp_date,
                    'dept': dept_desc,  # Keep full department name
                    'days': {},
                    'stats': {'Present': 0, 'Leave': 0, 'Absent': 0, 'Overtime': 0, 'D_Duty': 0, 'Working_Days': 0},
                    'posted_by': posted_by,
                    'approved_by': approved_by,
                    'accepted_by': accepted_by
                }
            
            # Use the actual attendance date for mapping
            att_date_key = att_date.strftime('%Y-%m-%d') if hasattr(att_date, 'strftime') else str(att_date)
            emp_data[emp_no]['days'][att_date_key] = att_status[:1] if att_status else ''
            
            # Count attendance statistics
            if att_status.startswith('P'):
                emp_data[emp_no]['stats']['Present'] += 1
            elif att_status.startswith('L'):
                emp_data[emp_no]['stats']['Leave'] += 1
            elif att_status.startswith('A'):
                emp_data[emp_no]['stats']['Absent'] += 1
            
            if 'O' in att_status:
                emp_data[emp_no]['stats']['Overtime'] += 1
            if 'D' in att_status:
                emp_data[emp_no]['stats']['D_Duty'] += 1
            
            # Count working days (all days except Sundays)
            if hasattr(att_date, 'weekday') and att_date.weekday() != 6:  # Sunday = 6
                emp_data[emp_no]['stats']['Working_Days'] += 1

        # Build table rows
        for emp_no, data in emp_data.items():
            # Create Paragraph objects for wrapping long text
            name_para = Paragraph(data['name'], ParagraphStyle(
                name='NameStyle',
                fontName='Helvetica',
                fontSize=5,
                leading=6,
                alignment=1,  # Center alignment
                wordWrap='CJK'
            ))
            
            dept_para = Paragraph(data['dept'], ParagraphStyle(
                name='DeptStyle',
                fontName='Helvetica',
                fontSize=5,
                leading=6,
                alignment=1,  # Center alignment
                wordWrap='CJK'
            ))
            
            row = [
                str(emp_no),
                name_para,  # Use Paragraph for wrapping
                data['exp_date'].strftime('%d-%b-%y') if data['exp_date'] else 'N/A',
                dept_para   # Use Paragraph for wrapping
            ]
            
            # Add day-wise attendance using actual dates
            if period_from and period_to:
                for date in actual_dates:
                    if isinstance(date, datetime):
                        date_key = date.strftime('%Y-%m-%d')
                        row.append(data['days'].get(date_key, ''))
                    else:
                        row.append(data['days'].get(str(date), ''))
            else:
                # Fallback to day numbers
                for day in actual_dates:
                    row.append(data['days'].get(str(day), ''))
            
            # Add summary statistics - FIXED: Use actual working days count
            row.extend([
                str(data['stats']['Present']),
                str(data['stats']['Leave']),
                str(data['stats']['Absent']),
                str(data['stats']['Overtime']),
                str(data['stats']['D_Duty']),
                str(data['stats']['Working_Days'])  # Now counts all days except Sundays
            ])
            rows.append(row)

        # Create attendance table with calculated widths
        attendance_table = Table(rows, colWidths=col_widths, repeatRows=1)
        attendance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 5),  # Reduced font size
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(attendance_table)
        
        # Add total employees count at the end
        elements.append(Spacer(1, 10))
        total_employees = len(emp_data)
        total_paragraph = Paragraph(f"<b>Total Number of Employees: {total_employees}</b>", 
                                   ParagraphStyle(name='TotalStyle', 
                                                fontName='Helvetica-Bold', 
                                                fontSize=10, 
                                                alignment=2,  # Right alignment
                                                spaceAfter=5))
        elements.append(total_paragraph)
    else:
        elements.append(Paragraph("No attendance data found for the selected period.", styles['Normal']))

    # ─── Build PDF ─────────────────────────────────────────────────────────────────
    doc.build(elements)
    buffer.seek(0)
    
    # Return PDF as HTTP response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Attendance_Report.pdf"'
    return response

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required
def get_period_details(request, period_id):
    """AJAX endpoint to fetch period details"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, sal_period_from, sal_period_to, 
                       sal_period_dayscount, sal_period_flg
                FROM sal_period
                WHERE sal_period_id = %s
            """, [period_id])
            period_info = cursor.fetchone()
        
        if period_info:
            return JsonResponse({
                'success': True,
                'period_id': period_info[0],
                'period_from': period_info[1].strftime('%d-%b-%Y') if period_info[1] else 'N/A',
                'period_to': period_info[2].strftime('%d-%b-%Y') if period_info[2] else 'N/A',
                'days_count': period_info[3] if period_info[3] else 'N/A',
                'status': period_info[4] if period_info[4] else 'N/A'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Period not found'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
      
#################### Payroll Reports ##################

import logging
import requests
from urllib.parse import urlencode
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import socket
import subprocess
import os
from urllib.parse import urlencode, quote_plus
from urllib.parse import urlencode, quote_plus
from urllib.parse import urlencode, quote_plus

from urllib.parse import urlencode, quote_plus
from urllib.parse import urlencode, quote_plus

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PayrollReportHandler:
    """Class to handle all payroll report operations with enhanced debugging"""
    
    def __init__(self):
        self.report_buttons = [
            {'name': 'Payroll Breakups', 'icon': 'fas fa-chart-pie', 'color': 'primary'},
            {'name': 'Cheque Payments', 'icon': 'fas fa-money-check', 'color': 'success'},
            {'name': 'Bank Credit Adv.', 'icon': 'fas fa-university', 'color': 'info'},
            {'name': 'Payroll - Excel', 'icon': 'fas fa-file-excel', 'color': 'success'},
            # {'name': 'Payroll Earning Comp', 'icon': 'fas fa-coins', 'color': 'warning'},
            {'name': 'EOBI - Loan', 'icon': 'fas fa-hand-holding-usd', 'color': 'danger'},
            {'name': 'Payroll Detail', 'icon': 'fas fa-list-alt', 'color': 'primary'},
            # {'name': 'Payroll Sub-Grouping', 'icon': 'fas fa-layer-group', 'color': 'secondary'},
            {'name': 'PaySlip', 'icon': 'fas fa-receipt', 'color': 'info'},
            #{'name': 'Range Payroll - XL', 'icon': 'fas fa-table', 'color': 'success'},
            {'name': 'Overtime Details', 'icon': 'fas fa-clock', 'color': 'warning'},
            {'name': 'Leave Balances', 'icon': 'fas fa-calendar-alt', 'color': 'primary'},
            {'name': 'Leave Details - Period', 'icon': 'fas fa-calendar-check', 'color': 'info'},
            {'name': 'Leave Details - FY', 'icon': 'fas fa-calendar-year', 'color': 'secondary'},
            {'name': 'Payroll Summary', 'icon': 'fas fa-chart-bar', 'color': 'primary'},
            {'name': 'Negative Amounts', 'icon': 'fas fa-minus-circle', 'color': 'danger'},
            {'name': 'Initialized Payroll Report', 'icon': 'fas fa-play-circle', 'color': 'success'},
            {'name': 'Allowance Wise Summary', 'icon': 'fas fa-gift', 'color': 'warning'},
            {'name': 'Note Sheet Summary', 'icon': 'fas fa-sticky-note', 'color': 'info'},
            {'name': 'Banks Summary', 'icon': 'fas fa-landmark', 'color': 'primary'},
            {'name': 'Earning Change Track', 'icon': 'fas fa-arrow-up', 'color': 'success'},
            {'name': 'Deduction Change Track', 'icon': 'fas fa-arrow-down', 'color': 'danger'},
            {'name': 'Exit Employee Details', 'icon': 'fas fa-sign-out-alt', 'color': 'secondary'},
            {'name': 'Payroll - Excel Overall', 'icon': 'fas fa-file-csv', 'color': 'success'},
        ]
    
    def debug_oracle_reports_connection(self):
        """Debug Oracle Reports server connection"""
        debug_info = {
            'server_reachable': False,
            'port_open': False,
            'ping_successful': False,
            'error_details': []
        }
        
        try:
            # Test if server is reachable
            response = requests.get("http://localhost:8889", timeout=5)
            debug_info['server_reachable'] = True
            logger.info("Oracle Reports server is reachable")
        except requests.exceptions.ConnectionError:
            debug_info['error_details'].append("Connection refused to localhost:8889")
            logger.error("Cannot connect to Oracle Reports server")
        except requests.exceptions.Timeout:
            debug_info['error_details'].append("Connection timeout to localhost:8889")
            logger.error("Timeout connecting to Oracle Reports server")
        except Exception as e:
            debug_info['error_details'].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error connecting to Oracle Reports: {e}")
        
        # Test port availability
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 8889))
            if result == 0:
                debug_info['port_open'] = True
                logger.info("Port 8889 is open")
            else:
                debug_info['error_details'].append("Port 8889 is closed or not responding")
                logger.warning("Port 8889 is not accessible")
            sock.close()
        except Exception as e:
            debug_info['error_details'].append(f"Port check failed: {str(e)}")
            logger.error(f"Port check failed: {e}")
        
        return debug_info
    
    def check_rdf_file_existence(self, report_name="PayrollDeptt.rdf"):
        """Check if RDF file exists and is accessible"""
        debug_info = {
            'file_exists': False,
            'file_path': None,
            'file_readable': False,
            'possible_locations': [],
            'error_details': []
        }
        
        # Common Oracle Reports locations
        possible_paths = [
            f"C:/wsscacc/{report_name}",
            f"../reports/{report_name}"
        ]
        
        for path in possible_paths:
            debug_info['possible_locations'].append(path)
            try:
                if os.path.exists(path):
                    debug_info['file_exists'] = True
                    debug_info['file_path'] = path
                    if os.access(path, os.R_OK):
                        debug_info['file_readable'] = True
                        logger.info(f"Found RDF file at: {path}")
                        break
                    else:
                        debug_info['error_details'].append(f"File exists but not readable: {path}")
            except Exception as e:
                debug_info['error_details'].append(f"Error checking path {path}: {str(e)}")
        
        if not debug_info['file_exists']:
            debug_info['error_details'].append(f"RDF file '{report_name}' not found in any common location")
            logger.error(f"RDF file not found: {report_name}")
        
        return debug_info
    
    def test_oracle_reports_url(self, report_url):
        """Test if the Oracle Reports URL is accessible"""
        debug_info = {
            'url_accessible': False,
            'response_code': None,
            'response_content': None,
            'error_details': []
        }
        
        try:
            logger.info(f"Testing Oracle Reports URL: {report_url}")
            response = requests.get(report_url, timeout=300)
            debug_info['response_code'] = response.status_code
            debug_info['response_content'] = response.text[:500]  # First 500 chars
            
            if response.status_code == 200:
                debug_info['url_accessible'] = True
                logger.info("Oracle Reports URL is accessible")
            else:
                debug_info['error_details'].append(f"HTTP {response.status_code}: {response.text[:200]}")
                logger.warning(f"Oracle Reports returned HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError as e:
            debug_info['error_details'].append(f"Connection error: {str(e)}")
            logger.error(f"Connection error testing Oracle Reports URL: {e}")
        except requests.exceptions.Timeout as e:
            debug_info['error_details'].append(f"Timeout error: {str(e)}")
            logger.error(f"Timeout testing Oracle Reports URL: {e}")
        except Exception as e:
            debug_info['error_details'].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error testing Oracle Reports URL: {e}")
        
        return debug_info
    
    def get_payroll_periods(self):
        """Fetch all payroll periods"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, sal_period_month, sal_period_dayscount,
                    TO_CHAR(TRUNC(sal_period_from), 'DD-MON-YYYY'),
                    TO_CHAR(TRUNC(sal_period_to), 'DD-MON-YYYY'),
                    sal_period_flg,
                    SAL_PERIOD_YR
                FROM sal_period
                ORDER BY sal_period_id DESC
            """)
            return cursor.fetchall()
    
    def get_selected_period(self, period_id):
        """Get specific period by ID"""
        if not period_id:
            return None
            
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, sal_period_month, sal_period_dayscount,
                       TO_CHAR(TRUNC(sal_period_from), 'DD-MON-YYYY'), 
                       TO_CHAR(TRUNC(sal_period_to), 'DD-MON-YYYY'), 
                       sal_period_flg
                FROM sal_period
                WHERE sal_period_id = %s
            """, [period_id])
            return cursor.fetchone()

    def get_zones(self):
        """Fetch all zones from the database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT zone_id, zone_desc
                    FROM zone
                    ORDER BY zone_id
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching zones: {str(e)}")
            return []
    
    def get_selected_zone(self, zone_id):
        """Get specific zone by ID"""
        if not zone_id:
            return None
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT zone_id, zone_desc
                    FROM zone
                    WHERE zone_id = %s
                """, [zone_id])
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching zone {zone_id}: {str(e)}")
            return None

    ######### Payroll Breakup ######### 
    def handle_payroll_breakups(self, period_id,zone_id=None):
        """Handle Payroll Breakups report with comprehensive debugging"""
        logger.info(f"Starting Payroll Breakups report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollDeptt.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
        "P_2": "P"  
    }
        
        report_path = "C:/wsscacc/PayrollDeptt.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollDeptt.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Breakups report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######### Cheque Payments #######
    def handle_cheque_payments(self, period_id,zone_id=None):
        """Handle Payroll Cheque Payment with comprehensive debugging"""
        logger.info(f"Starting Cheque payments report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollCheqPaid.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id  
    }
        
        report_path = "C:/wsscacc/PayrollCheqPaid.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure Cheque Payment.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Cheque Payment report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ####### Bank Credit adv #######
    def handle_bank_credit_adv(self, period_id,zone_id=None):
        """Handle Payroll Bank Credit report with comprehensive debugging"""
        logger.info(f"Starting Payroll Breakups report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollBankList.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id  
    }
        
        report_path = "C:/wsscacc/PayrollBankList.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure Bank_Credit.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Bank Credit report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    ####### Payroll Excel ######
    def handle_payroll_excel(self, period_id,zone_id=None):
        """Handle Payroll Excel with comprehensive debugging"""
        logger.info(f"Starting PayRollXL report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayRollXL.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id  
    }
        
        report_path = "C:/wsscacc/PayRollXL.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayRollXL.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'PayRollXL report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    #
    def handle_payroll_earning_comp(self, period_id,zone_id=None):
        """Handle Payroll Earning Component report"""
        return {
            'success': True,
            'message': f'Generating Payroll Earning Component report for period {period_id}',
            'redirect_url': f'/payroll/earning-comp/{period_id}/'
        }
    #

    ####### EOBI LOAN ######
    def handle_eobi_loan(self, period_id,zone_id=None):
        """Handle Payroll EOBI report with comprehensive debugging"""
        logger.info(f"Starting Payroll EOBI report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollFin.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/PayrollFin.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollFin.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll EOBI report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######## Payroll Detail ########
    def handle_payroll_detail(self, period_id,zone_id=None):
        """Handle Payroll Detail report with comprehensive debugging"""
        logger.info(f"Starting Payroll Breakups report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollEmpTyp.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
        "P_2": 'P'
    }
        
        report_path = "C:/wsscacc/PayrollEmpTyp.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollEmpTyp.rdft exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Detail report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    ######### Payroll Sub-Grouping ######
    def handle_payroll_sub_grouping(self, period_id,zone_id=None):
        """Handle Payroll Sub-Grouping report with comprehensive debugging"""
        logger.info(f"Starting Payroll Sub-Grouping report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayGrouping.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/PayGrouping.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayGrouping.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Detail report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######### Pay Slip #######
    def handle_payslip(self, period_id, employee_id, zone_id=None):
        """Handle Payroll PaySlip_ind.rdf with comprehensive debugging"""
        logger.info(f"Starting Payroll PaySlip report generation for period: {period_id}, employee: {employee_id}")
    
     # Initialize debug information
        debug_info = {
        'period_id': period_id,
        'employee_id': employee_id,  # Add employee_id to debug info
        'timestamp': str(datetime.now()),
        'connection_test': {},
        'file_check': {},
        'url_test': {},
        'parameters': {},
        'final_url': None
    }
    
        # Step 1: Validate required parameters
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
    
        if not employee_id:
            error_msg = "Employee ID is required"
            logger.error(error_msg)
            return {
            'success': False,
            'error': error_msg,
            'debug_info': debug_info
            }
    
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
    
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PaySlip_ind.rdf")
    
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
            "userid": "wsscacc/wsscacc01@orclv11",
            "desformat": "pdf",
            "destype": "cache",
            "server": "wssp",
            "P_1": period_id,
            "P_4": employee_id,  # Add employee_id as second parameter
      }
    
        report_path = "C:/wsscacc/PaySlip_ind.rdf"
    
        # Add full parameters to debug log
        debug_info['parameters'] = {"report": report_path, **params}
    
        # Construct final URL
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url
    
        logger.info(f"Generated report URL: {report_url}")        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayGrouping.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Detail report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    
    def handle_range_payroll_xl(self, period_id,zone_id=None):
        """Handle Payroll Sub-Grouping report with comprehensive debugging"""
        logger.info(f"Starting Payroll Sub-Grouping report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayGrouping.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/PayGrouping.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayGrouping.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Detail report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }    #

    ######### Overtime Details ########
    def handle_overtime_details(self, period_id,zone_id=None):
        """Handle Payroll OverTime Details report with comprehensive debugging"""
        logger.info(f"Starting Payroll Overtime Detail report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("EmpOvertime.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/EmpOvertime.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure EmpOvertime.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll overtime detail report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######### Handle Leave Balances ######
    def handle_leave_balances(self, period_id,zone_id=None):
        """Handle Payroll OverTime Details report with comprehensive debugging"""
        logger.info(f"Starting Payroll Overtime Detail report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("EmpLeaveBal.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/EmpLeaveBal.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure EmpOvertime.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll overtime detail report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######### Leave Details Period Report ##########
    def handle_leave_details_period(self, period_id,zone_id=None):
        """Handle Payroll Leave Details Period Report report with comprehensive debugging"""
        logger.info(f"Starting Payroll Leave Period Details Report  report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("EmpLeaveCount.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/EmpLeaveCount.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure EmpOvertime.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Leave Details Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    ######### Leave Details FY #######
    def handle_leave_details_fy(self, period_id,zone_id=None):
        """Handle Payroll Leave Details FY Report report with comprehensive debugging"""
        logger.info(f"Starting Payroll Leave Period FY Report  report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("EmpLeaveCountFY.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
        "P_2": '202425'
    }
        
        report_path = "C:/wsscacc/EmpLeaveCountFY.rdf"

# Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

# Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure EmpLeaveCountFY.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Leave Details FY Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######### Payroll Summary ########
    def handle_payroll_summary(self, period_id,zone_id=None):
        """Handle Payroll Summary Report report with comprehensive debugging"""
        logger.info(f"Starting Payroll Summary Report  report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PAYROLL_SUMMARY_DASHBOARD.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id
    }
        
        report_path = "C:/wsscacc/PAYROLL_SUMMARY_DASHBOARD.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PAYROLL_SUMMARY_DASHBOARD.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Summary Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######## Handle Negative Amounts REPORT #####
    def handle_negative_amounts(self, period_id,zone_id=None):
        """Handle NEGATIVE_SALARY Report with comprehensive debugging"""
        logger.info(f"Starting Payroll NEGATIVE_SALARY Report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("NEGATIVE_SALARY.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id
    }
        
        report_path = "C:/wsscacc/NEGATIVE_SALARY.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure NEGATIVE_SALARY.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Negative Amount Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######## Initiallized Payroll Report ######
    def handle_initialized_payroll_report(self, period_id,zone_id):
        """Handle Initiallized Payroll Report with comprehensive debugging"""
        logger.info(f"Starting Payroll Breakups report generation for period: {period_id}, zone: {zone_id}")
        
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'zone_id' : zone_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        if not zone_id:
            error_msg = "Zone ID is required for Payroll Breakups"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollDeptt_int.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
        "P_2": 'P',
        "P_3": zone_id,
    }
        
        report_path = "C:/wsscacc/PayrollDeptt_int.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollDeptt_int.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Summary Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######## Allowance wise summary #######
    def handle_allowance_wise_summary(self, period_id,zone_id):
        """Handle Allowance wise summary Report with comprehensive debugging"""
        logger.info(f"Starting Allowance wise summary Report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollSumm_AllwWise.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
        "P_2": 'P',
        "P_3": zone_id,
        "P_4": 1009999
    }
        
        report_path = "C:/wsscacc/PayrollSumm_AllwWise.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollSumm_AllwWise.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Summary Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    ######## Notesheet Summary ########
    def handle_note_sheet_summary(self, period_id,zone_id=None):
        """Handle PayrollSumm_Notesheet with comprehensive debugging"""
        logger.info(f"Starting PayrollSumm_Notesheet Report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollSumm_Notesheet.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/PayrollSumm_Notesheet.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollSumm_Notesheet.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Summary Notesheet Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######## Banks Summary ######
    def handle_banks_summary(self, period_id,zone_id=None):
        """Handle PayrollSumm_BANK SUMMARY with comprehensive debugging"""
        logger.info(f"Starting BANK SUMARY Report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayrollSumm_BANK_SUMM.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
    }
        
        report_path = "C:/wsscacc/PayrollSumm_BANK_SUMM.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayrollSumm_BANK_SUMM.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Summary Notesheet Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }
    
    ######## Earning Change  Track ######
    def handle_earning_change_track(self, request, zone_id=None):
        period_id = request.GET.get('period_id')

        if not period_id:
            return HttpResponse("Period ID is required", status=400)

        # Fetch allowances for that period
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT allw_id, allw_desc 
                FROM allw
                WHERE ALLW_EARN_DEDUC = 1
            """)
            allowances = [{'id': row[0], 'desc': row[1]} for row in cursor.fetchall()]

        return render(request, 'myapp/earning_change_selection.html', {
            'period_id': period_id,
            'allowances': allowances
        })

    def generate_earning_change_report(self, request):
        if request.method == "POST":
            period_id = request.POST.get('period_id')
            allowance_str = request.POST.get('selected_allowances_list')

            if not period_id or not allowance_str:
                return HttpResponse("Missing period or allowances", status=400)

            report_url = (
                "http://192.168.35.202:8889/reports/rwservlet?"
                f"report=C:/wsscacc/Change_Track_Earning.rdf"
                f"&userid=wsscacc/wsscacc01@orclv11"
                f"&desformat=pdf"
                f"&destype=cache"
                f"&server=wssp"
                f"&P_1={period_id}"
                f"&P_2={allowance_str}"
            )

            return redirect(report_url)

        return HttpResponse("Invalid request method", status=405)
    
    ######## Deduction Change  Track ######
    def handle_deduction_change_track(self, request, zone_id=None):
        period_id = request.GET.get('period_id')

        if not period_id:
            return HttpResponse("Period ID is required", status=400)

        # Fetch allowances for that period
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT allw_id, allw_desc 
                FROM allw
                WHERE ALLW_EARN_DEDUC = -1
            """)
            allowances = [{'id': row[0], 'desc': row[1]} for row in cursor.fetchall()]

        return render(request, 'myapp/deduction_change_selection.html', {
            'period_id': period_id,
            'allowances': allowances
        })

    def generate_deduction_change_report(self, request):
        if request.method == "POST":
            period_id = request.POST.get('period_id')
            allowance_str = request.POST.get('selected_allowances_list')

            if not period_id or not allowance_str:
                return HttpResponse("Missing period or allowances", status=400)

            report_url = (
                "http://192.168.35.202:8889/reports/rwservlet?"
                f"report=C:/wsscacc/Change_Track_Deduction.rdf"
                f"&userid=wsscacc/wsscacc01@orclv11"
                f"&desformat=pdf"
                f"&destype=cache"
                f"&server=wssp"
                f"&P_1={period_id}"
                f"&P_2={allowance_str}"
            )

            return redirect(report_url)

        return HttpResponse("Invalid request method", status=405)

    ######### Exit Employee #######
    def handle_exit_employee_details(self, period_id,zone_id=None):
        """Handle EXIT EMPLOYEE with comprehensive debugging"""
        logger.info(f"Starting EXIT EMPLOYEE Report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("EXIT_EMP.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "SAL_PERIOD": period_id,
    }
        
        report_path = "C:/wsscacc/EXIT_EMP.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure EXIT_EMP.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'Payroll Summary Notesheet Report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    ######### Payroll Overall Report #####
    def handle_payroll_excel_overall(self, period_id,zone_id):
        """Handle EXIT EMPLOYEE with comprehensive debugging"""
        logger.info(f"Starting EXIT EMPLOYEE Report generation for period: {period_id}")
        
        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'zone_id' : zone_id,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }
        
        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }

        if not zone_id:
            error_msg = "Zone ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }
            
        
        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()
        
        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence("PayRollXL_OVERALL1.rdf")
        
        # Step 4: Build report URL with parameters
        base_url = "http://192.168.35.203:8889/reports/rwservlet"
        params = {
        # keep report separate so it's not encoded
        "userid": "wsscacc/wsscacc01@orclv11",
        "desformat": "pdf",
        "destype": "cache",
        "server": "wssp",
        "P_1": period_id,
        "P_2": zone_id
    }
        
        report_path = "C:/wsscacc/PayRollXL_OVERALL1.rdf"

    # Add full parameters to debug log (including report)
        debug_info['parameters'] = {"report": report_path, **params}

    # Construct final URL (append report manually to avoid encoding / and :)
        report_url = f"{base_url}?report={report_path}&{urlencode(params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")
        
        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)
        
        # Step 6: Determine success/failure based on tests
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL (http://localhost:8889)',
                    'Check network connectivity'
                ]
            }
        
        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    'Ensure PayRollXL_OVERALL1.rdf exists in Reports directory'
                ]
            }
        
        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }
        
        # If all tests pass, return success
        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'PayRollXL_OVERALL1 report generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    def get_report_handler_map(self):
        """Map report names to their respective handler methods"""
        return {
            'Payroll Breakups': self.handle_payroll_breakups,
            'Cheque Payments': self.handle_cheque_payments,
            'Bank Credit Adv.': self.handle_bank_credit_adv,
            'Payroll - Excel': self.handle_payroll_excel,
            'Payroll Earning Comp': self.handle_payroll_earning_comp,

            'EOBI - Loan': self.handle_eobi_loan,
            #'EOBI \u002D Loan': self.handle_eobi_loan,  # Unicode escaped version

            'Payroll Detail': self.handle_payroll_detail,
            'Payroll Sub-Grouping': self.handle_payroll_sub_grouping,
            'PaySlip': self.handle_payslip,
            'Range Payroll - XL': self.handle_range_payroll_xl,
            'Overtime Details': self.handle_overtime_details,
            'Leave Balances': self.handle_leave_balances,
            'Leave Details - Period': self.handle_leave_details_period,
            'Leave Details - FY': self.handle_leave_details_fy,
            'Payroll Summary': self.handle_payroll_summary,
            'Negative Amounts': self.handle_negative_amounts,
            'Initialized Payroll Report': self.handle_initialized_payroll_report,
            'Allowance Wise Summary': self.handle_allowance_wise_summary,
            'Note Sheet Summary': self.handle_note_sheet_summary,
            'Banks Summary': self.handle_banks_summary,
            'Earning Change Track': self.handle_earning_change_track,
            'Deduction Change Track': self.handle_deduction_change_track,
            'Exit Employee Details': self.handle_exit_employee_details,
            'Payroll - Excel Overall': self.handle_payroll_excel_overall,
        }
        
    def process_report_request(self, report_name, period_id, employee_id=None, zone_id=None):
        """Process a report request using the appropriate handler with zone support"""
        logger.info(f"Processing report request: {report_name} for period: {period_id}, zone: {zone_id}")
    
        # Normalize the report name to handle Unicode escapes
        normalized_report_name = report_name.encode('utf-8').decode('unicode_escape')
        logger.info(f"Normalized report name: {normalized_report_name}")
    
        handler_map = self.get_report_handler_map()
    
        # List of reports that require zone_id
        zone_required_reports = [
        'Initialized Payroll Report',
        'Allowance Wise Summary',
        'Payroll - Excel Overall',
        ]
    
        # Validate zone_id for reports that require it
        if report_name in zone_required_reports and not zone_id:
            error_msg = f'Zone ID is required for {report_name}'
            logger.error(error_msg)
            return {
            'success': False,
            'error': error_msg,
            'available_reports': list(handler_map.keys())
            }
    
        # Try both original and normalized names
        if report_name in handler_map:
            result = handler_map[report_name](period_id, zone_id=zone_id)
            logger.info(f"Report handler result: {result}")
            return result
        if report_name == "PaySlip":
            return self.handle_payslip(period_id, employee_id)  
        
        elif normalized_report_name in handler_map:
            result = handler_map[normalized_report_name](period_id, zone_id=zone_id)
            logger.info(f"Report handler result: {result}")
            return result
        
        else:
            error_msg = f'Unknown report type: {report_name} (normalized: {normalized_report_name})'
            logger.error(error_msg)
            return {
            'success': False,
            'error': error_msg,
            'available_reports': list(handler_map.keys())
        }   
 
# Import datetime for debug info
from datetime import datetime

payroll_handler = PayrollReportHandler()


@login_required
def payroll_reports(request):
    """Main view for payroll reports with zone support"""
    payroll_handler = PayrollReportHandler()
    periods = payroll_handler.get_payroll_periods()
    zones = payroll_handler.get_zones()
    
    # Add debug logging
    logger.info(f"Fetched {len(zones)} zones: {zones}")
    
    selected_period = None
    selected_zone = None
    if request.method == 'POST':
        period_id = request.POST.get('sal_period')
        zone_id = request.POST.get('zone_id')
        selected_period = payroll_handler.get_selected_period(period_id)
        selected_zone = payroll_handler.get_selected_zone(zone_id) if zone_id else None

    return render(request, 'myapp/payroll_reports.html', {
        'periods': periods,
        'zones': zones,
        'selected_period': selected_period,
        'selected_zone': selected_zone,
        'report_buttons': payroll_handler.report_buttons
    })

@csrf_exempt
def handle_report_action(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_name = data.get('report_name')
            period_id = data.get('period_id')
            zone_id = data.get('zone_id')

            logger.info(f"Received report request - Report: {report_name}, Period: {period_id}, Zone: {zone_id}")

            if not report_name or not period_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing report_name or period_id'
                })

            handler = PayrollReportHandler()

            # Redirect logic
            if report_name == "Earning Change Track":
                return JsonResponse({
                    'success': True,
                    'redirect': True,
                    'redirect_url': f"/payroll/earning-change/?period_id={period_id}"
                })
            if report_name == "Deduction Change Track":
                return JsonResponse({
                    'success': True,
                    'redirect': True,
                    'redirect_url': f"/payroll/deduction-change/?period_id={period_id}"
                })
            # Inside handle_report_action
            if report_name == "PaySlip":
                 return JsonResponse({
                'success': True,
                'redirect': True,
                'redirect_url': f"/payroll/payslip/input/{period_id}/"
            })

            
            employee_id = data.get('employee_id') 
            result = handler.process_report_request(report_name, period_id,employee_id=employee_id, zone_id=zone_id)
            return JsonResponse(result)

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f"Invalid JSON: {str(e)}"})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Unexpected error: {str(e)}"})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


########### Payroll Reports Earning & Deduction Change #########
def handle_earning_change_view(request):
    return payroll_handler.handle_earning_change_track(request)

def generate_earning_change_report_view(request):
    return payroll_handler.generate_earning_change_report(request)

def handle_deduction_change_view(request):
    return payroll_handler.handle_deduction_change_track(request)

def generate_deduction_change_report_view(request):
    return payroll_handler.generate_deduction_change_report(request)

################## Pay Slip Report ################

logger = logging.getLogger(__name__)

def payslip_input_view(request, period_id):
    """
    Display the payslip input form where user enters employee ID
    """
    # You might want to validate that the period_id exists
    context = {
        'period_id': period_id,
        'page_title': 'Generate Pay Slip Report'
    }
    return render(request, 'myapp/pay_slip_input.html', context)

def generate_payslip_report(request):
    """
    Process the payslip generation request
    """
    if request.method == 'POST':
        period_id = request.POST.get('period_id')
        employee_id = request.POST.get('employee_id')
        
        # Validate inputs
        if not period_id:
            messages.error(request, 'Period ID is required')
            return redirect('payroll_reports')
        
        if not employee_id:
            messages.error(request, 'Employee ID is required')
            return redirect('payslip_input', period_id=period_id)
        
        # Clean employee ID (remove spaces, convert to uppercase if needed)
        employee_id = employee_id.strip().upper()
        
        try:
            # Initialize your PayrollHandler
            payroll_handler = PayrollReportHandler()  # Adjust this based on your implementation
            
            # Call the handle_payslip method with both parameters
            result = payroll_handler.handle_payslip(period_id, employee_id)
            
            if result['success']:
                # If successful, redirect to the report URL
                return redirect(result['report_url'])
            else:
                # If failed, show error message and redirect back to input form
                error_message = result.get('error', 'Unknown error occurred')
                messages.error(request, f'Error generating payslip: {error_message}')
                
                # Log debug information for troubleshooting
                logger.error(f"Payslip generation failed: {result}")
                
                return redirect('payslip_input', period_id=period_id)
                
        except Exception as e:
            logger.error(f"Exception in payslip generation: {str(e)}")
            messages.error(request, 'An unexpected error occurred while generating the payslip')
            return redirect('payslip_input', period_id=period_id)
    
    # If GET request, redirect to payroll reports
    return redirect('payroll_reports')

@require_http_methods(["POST"])
def validate_employee_id(request):
    """
    AJAX endpoint to validate employee ID (optional)
    """
    employee_id = request.POST.get('employee_id', '').strip()
    
    if not employee_id:
        return JsonResponse({
            'valid': False,
            'message': 'Employee ID is required'
        })
    
    if len(employee_id) < 2:
        return JsonResponse({
            'valid': False,
            'message': 'Employee ID must be at least 2 characters long'
        })
    
    # Add your custom validation logic here
    # For example, check if employee exists in database
    try:
        # Example validation - replace with your actual logic
        # employee_exists = Employee.objects.filter(employee_id=employee_id).exists()
        # if not employee_exists:
        #     return JsonResponse({
        #         'valid': False,
        #         'message': 'Employee not found'
        #     })
        
        return JsonResponse({
            'valid': True,
            'message': 'Employee ID is valid'
        })
    except Exception as e:
        logger.error(f"Error validating employee ID: {str(e)}")
        return JsonResponse({
            'valid': False,
            'message': 'Error validating employee ID'
        })

def payslip_report_direct(request, period_id, employee_id):
    """
    Direct URL for payslip generation (optional - for bookmarking/direct access)
    """
    try:
        payroll_handler = PayrollReportHandler()
        result = payroll_handler.handle_payslip(period_id, employee_id)
        
        if result['success']:
            return redirect(result['report_url'])
        else:
            messages.error(request, f'Error generating payslip: {result.get("error", "Unknown error")}')
            return redirect('payslip_input', period_id=period_id)
            
    except Exception as e:
        logger.error(f"Exception in direct payslip generation: {str(e)}")
        messages.error(request, 'An unexpected error occurred')
        return redirect('payroll_reports')


####################### Finance Reports #########################

import logging
import requests
from urllib.parse import urlencode, quote_plus
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import socket
import os
from urllib.parse import urlencode, quote_plus
from datetime import datetime
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FinanceReportHandler:
    """Class to handle all finance report operations with enhanced debugging"""
    
    def __init__(self):
        self.report_buttons = [
            {'name': 'Payroll Report - PDF', 'icon': 'fas fa-file-pdf', 'color': 'danger'},
            {'name': 'Payroll - Excel', 'icon': 'fas fa-file-excel', 'color': 'success'},
            {'name': 'Bank Credit Adv.', 'icon': 'fas fa-university', 'color': 'info'},
            {'name': 'Payroll Detail', 'icon': 'fas fa-list-alt', 'color': 'primary'},
            {'name': 'Payroll Summary', 'icon': 'fas fa-chart-bar', 'color': 'primary'},
            {'name': 'JV Posting', 'icon': 'fas fa-book', 'color': 'secondary'},
            {'name': 'Tax Report', 'icon': 'fas fa-receipt', 'color': 'warning'},
            {'name': 'BOK Report', 'icon': 'fas fa-landmark', 'color': 'info'},
            {'name': 'KMB Report', 'icon': 'fas fa-credit-card', 'color': 'success'},
            {'name': 'RTGS Report', 'icon': 'fas fa-exchange-alt', 'color': 'primary'},
            {'name': 'Earning Change Track', 'icon': 'fas fa-arrow-up', 'color': 'success'},
            {'name': 'Deduction Change Track', 'icon': 'fas fa-arrow-down', 'color': 'danger'},
            {'name': 'EOBI - Loan', 'icon': 'fas fa-hand-holding-usd', 'color': 'danger'},
            {'name': 'JV Posting 2', 'icon': 'fas fa-book-open', 'color': 'secondary'},
            {'name': 'Cheque Payments', 'icon': 'fas fa-money-check', 'color': 'success'},
            {'name': 'Combine JV', 'icon': 'fas fa-layer-group', 'color': 'info'},
            {'name': 'WSSP - Loan', 'icon': 'fas fa-piggy-bank', 'color': 'warning'},
            {'name': 'Allowance Wise Summ...', 'icon': 'fas fa-gift', 'color': 'warning'},
            {'name': 'Payroll Breakups', 'icon': 'fas fa-chart-pie', 'color': 'primary'},
            {'name': 'Banks Summary', 'icon': 'fas fa-landmark', 'color': 'primary'},
        ]
    
    def debug_oracle_reports_connection(self):
        """Debug Oracle Reports server connection"""
        debug_info = {
            'server_reachable': False,
            'port_open': False,
            'ping_successful': False,
            'error_details': []
        }
        
        try:
            # Test if server is reachable
            response = requests.get("http://192.168.35.203:8889", timeout=5)
            debug_info['server_reachable'] = True
            logger.info("Oracle Reports server is reachable")
        except requests.exceptions.ConnectionError:
            debug_info['error_details'].append("Connection refused to 192.168.35.203:8889")
            logger.error("Cannot connect to Oracle Reports server")
        except requests.exceptions.Timeout:
            debug_info['error_details'].append("Connection timeout to 192.168.35.203:8889")
            logger.error("Timeout connecting to Oracle Reports server")
        except Exception as e:
            debug_info['error_details'].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error connecting to Oracle Reports: {e}")
        
        # Test port availability
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('192.168.35.203', 8889))
            if result == 0:
                debug_info['port_open'] = True
                logger.info("Port 8889 is open")
            else:
                debug_info['error_details'].append("Port 8889 is closed or not responding")
                logger.warning("Port 8889 is not accessible")
            sock.close()
        except Exception as e:
            debug_info['error_details'].append(f"Port check failed: {str(e)}")
            logger.error(f"Port check failed: {e}")
        
        return debug_info
    
    def check_rdf_file_existence(self, report_name):
        """Check if RDF file exists and is accessible"""
        debug_info = {
            'file_exists': False,
            'file_path': None,
            'file_readable': False,
            'possible_locations': [],
            'error_details': []
        }
        
        # Common Oracle Reports locations
        possible_paths = [
            f"C:/wsscacc/{report_name}",
            f"../reports/{report_name}"
        ]
        
        for path in possible_paths:
            debug_info['possible_locations'].append(path)
            try:
                if os.path.exists(path):
                    debug_info['file_exists'] = True
                    debug_info['file_path'] = path
                    if os.access(path, os.R_OK):
                        debug_info['file_readable'] = True
                        logger.info(f"Found RDF file at: {path}")
                        break
                    else:
                        debug_info['error_details'].append(f"File exists but not readable: {path}")
            except Exception as e:
                debug_info['error_details'].append(f"Error checking path {path}: {str(e)}")
        
        if not debug_info['file_exists']:
            debug_info['error_details'].append(f"RDF file '{report_name}' not found in any common location")
            logger.error(f"RDF file not found: {report_name}")
        
        return debug_info
    
    def test_oracle_reports_url(self, report_url):
        """Test if the Oracle Reports URL is accessible"""
        debug_info = {
            'url_accessible': False,
            'response_code': None,
            'response_content': None,
            'error_details': []
        }
        
        try:
            logger.info(f"Testing Oracle Reports URL: {report_url}")
            response = requests.get(report_url, timeout=300)
            debug_info['response_code'] = response.status_code
            debug_info['response_content'] = response.text[:500]  # First 500 chars
            
            if response.status_code == 200:
                debug_info['url_accessible'] = True
                logger.info("Oracle Reports URL is accessible")
            else:
                debug_info['error_details'].append(f"HTTP {response.status_code}: {response.text[:200]}")
                logger.warning(f"Oracle Reports returned HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError as e:
            debug_info['error_details'].append(f"Connection error: {str(e)}")
            logger.error(f"Connection error testing Oracle Reports URL: {e}")
        except requests.exceptions.Timeout as e:
            debug_info['error_details'].append(f"Timeout error: {str(e)}")
            logger.error(f"Timeout testing Oracle Reports URL: {e}")
        except Exception as e:
            debug_info['error_details'].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error testing Oracle Reports URL: {e}")
        
        return debug_info
    
    def get_payroll_periods(self):
        """Fetch all payroll periods"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, sal_period_month, sal_period_dayscount,
                    TO_CHAR(TRUNC(sal_period_from), 'DD-MON-YYYY'),
                    TO_CHAR(TRUNC(sal_period_to), 'DD-MON-YYYY'),
                    sal_period_flg,
                    SAL_PERIOD_YR
                FROM sal_period
                ORDER BY sal_period_id DESC
            """)
            return cursor.fetchall()
    
    def get_selected_period(self, period_id):
        """Get specific period by ID"""
        if not period_id:
            return None
            
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sal_period_id, sal_period_month, sal_period_dayscount,
                       TO_CHAR(TRUNC(sal_period_from), 'DD-MON-YYYY'), 
                       TO_CHAR(TRUNC(sal_period_to), 'DD-MON-YYYY'), 
                       sal_period_flg
                FROM sal_period
                WHERE sal_period_id = %s
            """, [period_id])
            return cursor.fetchone()

    def get_zones(self):
        """Fetch all zones from the database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT zone_id, zone_desc
                    FROM zone
                    ORDER BY zone_id
                """)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching zones: {str(e)}")
            return []
    
    def get_selected_zone(self, zone_id):
        """Get specific zone by ID"""
        if not zone_id:
            return None
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT zone_id, zone_desc
                    FROM zone
                    WHERE zone_id = %s
                """, [zone_id])
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching zone {zone_id}: {str(e)}")
            return None



    logger = logging.getLogger(__name__)


    def handle_payroll_report_pdf(self, period_id, zone_id=None, rdf_filename="PayrollDeptt_int.rdf", report_display_name="Payroll Report", parameters=None):
        """Generic handler for finance reports - just change the rdf_filename for each report"""

        logger.info(f"Starting {rdf_filename} generation for period: {period_id}")

        # Initialize debug information
        debug_info = {
            'period_id': period_id,
            'zone_id': zone_id,
            'rdf_filename': rdf_filename,
            'timestamp': str(datetime.now()),
            'connection_test': {},
            'file_check': {},
            'url_test': {},
            'parameters': {},
            'final_url': None
        }

        # Step 1: Validate period_id
        if not period_id:
            error_msg = "Period ID is required"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'debug_info': debug_info
            }

        # Step 2: Test Oracle Reports server connection
        debug_info['connection_test'] = self.debug_oracle_reports_connection()

        # Step 3: Check RDF file existence
        debug_info['file_check'] = self.check_rdf_file_existence(rdf_filename)

        # Step 4: Build report URL with parameters
        default_params = {
            "userid": self.userid,
            "desformat": "pdf",
            "destype": "cache",
            "server": "wssp",
            "P_1": period_id
        }

        if parameters:
            default_params.update(parameters)

        if zone_id:
            default_params["P_3"] = zone_id

        report_path = f"{self.report_directory}/{rdf_filename}"
        debug_info['parameters'] = {"report": report_path, **default_params}

        report_url = f"{self.report_server_url}?report={report_path}&{urlencode(default_params, quote_via=quote_plus)}"
        debug_info['final_url'] = report_url

        logger.info(f"Generated report URL: {report_url}")

        # Step 5: Test the report URL
        debug_info['url_test'] = self.test_oracle_reports_url(report_url)

        # Step 6: Determine success/failure
        if not debug_info['connection_test']['server_reachable']:
            return {
                'success': False,
                'error': 'Oracle Reports server is not reachable',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check if Oracle Reports server is running',
                    'Verify the server URL',
                    'Check network connectivity'
                ]
            }

        if not debug_info['file_check']['file_exists']:
            return {
                'success': False,
                'error': 'RDF file not found',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Verify RDF file location',
                    'Check file permissions',
                    f'Ensure {rdf_filename} exists in Reports directory'
                ]
            }

        if not debug_info['url_test']['url_accessible']:
            return {
                'success': False,
                'error': 'Report URL is not accessible',
                'debug_info': debug_info,
                'suggested_actions': [
                    'Check Oracle Reports configuration',
                    'Verify database connection parameters',
                    'Check report parameters validity'
                ]
            }

        logger.info("All validation tests passed. Report should be accessible.")
        return {
            'success': True,
            'message': f'{report_display_name} generated successfully for period {period_id}',
            'report_url': report_url,
            'debug_info': debug_info
        }

    def handle_payroll_excel(self, period_id, zone_id=None):
        """Handle Payroll Excel - just change RDF filename"""
        return self.handle_generic_report(
            period_id=period_id,
            rdf_filename="PayrollExcel.rdf",  # Change this RDF filename
            report_display_name="Payroll Excel",
            zone_id=zone_id
        )

    def handle_bank_credit_adv(self, period_id, zone_id=None):
        """Handle Bank Credit Advance - just change RDF filename"""
        return self.handle_generic_report(
            period_id=period_id,
            rdf_filename="BankCreditAdv.rdf",  # Change this RDF filename
            report_display_name="Bank Credit Advance",
            zone_id=zone_id
        )

    def handle_jv_posting(self, period_id, zone_id=None):
        """Handle JV Posting - just change RDF filename"""
        return self.handle_generic_report(
            period_id=period_id,
            rdf_filename="JVPosting.rdf",  # Change this RDF filename
            report_display_name="JV Posting",
            parameters={"P_2": "P"},  # Add any extra parameters here
            zone_id=zone_id
        )

    def handle_tax_report(self, period_id, zone_id=None):
        """Handle Tax Report - just change RDF filename"""
        return self.handle_generic_report(
            period_id=period_id,
            rdf_filename="TaxReport.rdf",  # Change this RDF filename
            report_display_name="Tax Report",
            zone_id=zone_id
        )


    def get_report_handler_map(self):
        """Map report names to their respective handler methods"""
        return {
            'Payroll Report - PDF': self.handle_payroll_report_pdf,
            'Payroll - Excel': self.handle_payroll_excel,
            'Bank Credit Adv.': self.handle_bank_credit_adv,
            'JV Posting': self.handle_jv_posting,
            'Tax Report': self.handle_tax_report,
            # Add more mappings as you create more handlers
        }
        
    def process_report_request(self, report_name, period_id, zone_id=None):
        """Process a report request using the appropriate handler with zone support"""
        logger.info(f"Processing finance report request: {report_name} for period: {period_id}, zone: {zone_id}")
    
        handler_map = self.get_report_handler_map()
    
        # List of reports that require zone_id (add report names that need zones)
        zone_required_reports = [
            'Allowance Wise Summary',
            'Payroll Breakups',
            # Add more reports that require zone_id
        ]
    
        # Validate zone_id for reports that require it
        if report_name in zone_required_reports and not zone_id:
            error_msg = f'Zone ID is required for {report_name}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'available_reports': list(handler_map.keys())
            }
    
        if report_name in handler_map:
            result = handler_map[report_name](period_id, zone_id=zone_id)
            logger.info(f"Finance report handler result: {result}")
            return result
        else:
            error_msg = f'Unknown finance report type: {report_name}'
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'available_reports': list(handler_map.keys())
            }   

# Initialize the handler
finance_handler = FinanceReportHandler()

@login_required
def finance_reports(request):
    """Main view for finance reports with zone support"""
    finance_handler = FinanceReportHandler()
    periods = finance_handler.get_payroll_periods()
    zones = finance_handler.get_zones()
    
    # Add debug logging
    logger.info(f"Fetched {len(zones)} zones: {zones}")
    
    selected_period = None
    selected_zone = None
    if request.method == 'POST':
        period_id = request.POST.get('sal_period')
        zone_id = request.POST.get('zone_id')
        selected_period = finance_handler.get_selected_period(period_id)
        selected_zone = finance_handler.get_selected_zone(zone_id) if zone_id else None

    return render(request, 'myapp/finance_reports.html', {
        'periods': periods,
        'zones': zones,
        'selected_period': selected_period,
        'selected_zone': selected_zone,
        'report_buttons': finance_handler.report_buttons
    })

@csrf_exempt
def handle_finance_report_action(request):
    """Handle finance report generation requests"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_name = data.get('report_name')
            period_id = data.get('period_id')
            zone_id = data.get('zone_id')

            logger.info(f"Received finance report request - Report: {report_name}, Period: {period_id}, Zone: {zone_id}")

            if not report_name or not period_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing report_name or period_id'
                })

            handler = FinanceReportHandler()
            result = handler.process_report_request(report_name, period_id, zone_id=zone_id)
            return JsonResponse(result)

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f"Invalid JSON: {str(e)}"})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Unexpected error: {str(e)}"})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})