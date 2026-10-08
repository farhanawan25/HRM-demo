from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),      
    path('logout/', views.logout_view, name='logout'),
    path('employee-pay/', views.employee_pay_view, name='employee_pay'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('payroll-period/', views.payroll_period_view, name='sal_period_list'),
    path('update-attendance/<int:sal_period_id>/', views.update_attendance, name='update_attendance'),
    path('attendance-marking/', views.attendance_marking_view, name='attendance_marking'),
    path('attendance/detail/<int:emp_no>/<str:month>/', views.attendance_detail_view, name='attendance_detail'),
    path('attendance/acceptance/', views.attendance_acceptance_view, name='attendance_acceptance'),
    path('attendance/summary/<int:manager_id>/<int:period_id>/', views.attendance_summary_detail, name='attendance_summary_detail'),

    path('employee-search/', views.employee_search, name='employee_search'),
    path('search-employees/', views.search_employees, name='search_employees'),
    path('loan-entry/', views.loan_allotment, name='loan_allotment'),
    path('employee/<int:emp_no>/report/', views.generate_pdf, name='generate_pdf'),
    path("update-installment-status/", views.update_installment_status, name="update_installment_status"),
    path('get_installments/<str:employee_id>/', views.get_installments, name='get_installments'),

    path('payroll_initialize/', views.payroll_initialize_view, name='payroll_initialize'),
    path('payroll/history/', views.payroll_history_view, name='payroll_history'),

    path('employee/pay/', views.employee_pay_search, name='employee_pay_search'),
    path('employee/pay/search/', views.employee_pay_search, name='employee_pay_search_alt'),
    path('employee/pay/<str:emp_no>/', views.employee_pay_table, name='employee_pay_table'),
    path('employee/add-allowance/', views.add_emp_allowance, name='add_emp_allowance'),

    path('search-employees/', views.search_employees, name='search_employees'),   
    path('pay_allowances/', views.get_allowances, name='pay_allowances'),
    path('add-allowance/', views.add_allowance, name='add_allowance'),
    path('payroll/track/', views.payroll_tracking, name='payroll_tracking'),

    path('attendance/approval/', views.attendance_approval_summary, name='attendance_approval_summary'),
    path('approve-attendance/', views.approve_attendance, name='approve_attendance'),
    path('return-for-correction/', views.return_for_correction, name='return_for_correction'),

    ####### Payroll Amendments ######
    path('payroll-amendment/', views.payroll_amendment_view, name='payroll_amendment'),
    path('search-employees/', views.payroll_amendment_search, name='payroll_amendment_search'),
    path('save-payroll-adjustments/', views.save_payroll_adjustments, name='save_payroll_adjustments'),

    ####### Access control ##########
    path('access-control/', views.system_access_control, name='system_access_control'),
    path('api/user-permissions/<int:user_id>/', views.get_user_permissions_ajax, name='get_user_permissions'),
    path('no-access/', views.no_access, name='no_access'),

    path('update-employee-pay-rate/', views.update_employee_pay_rate, name='update_employee_pay_rate'),
    path('employee-pay-summary/<str:emp_no>/', views.get_employee_pay_summary, name='get_employee_pay_summary'),

    ####### Pay classification #######
    path('pay-classification/', views.pay_classification_view, name='pay_classification'),
    path('add-pay-class/', views.add_pay_class, name='add_pay_class'),
    path('add-pay-group/', views.add_pay_group, name='add_pay_group'),
    path('add-pay-subgroup/', views.add_pay_subgroup, name='add_pay_subgroup'),
    path('get-pay-groups/', views.get_pay_groups, name='get_pay_groups'),
    path('get-pay-subgroups/', views.get_pay_subgroups, name='get_pay_subgroups'),

    ####### Allowance Prevailing Rate ######
    path('allowance-prevailing-rate/', views.allowance_prevailing_rate, name='allowance_prevailing_rate'),
    path('save-allowance-rate/', views.save_allowance_rate, name='save_allowance_rate'),
    
    ########## Pay Types ############
    path('salary-type/', views.salary_type_view, name='salary-type'),
    path('pay-type-fin/', views.pay_type_fin_view, name='pay_type_fin_view'),

    ########## Tax Slab #############
    path('tax-slab/', views.tax_slab, name='tax_slab'),
    path('save-tax-slab/', views.save_tax_slab, name='save_tax_slab'),


### --- ###
    ########## Payroll Recommendation - HR ##########
    path('payroll/recommendation/hr/', views.payroll_recommendation_hr, name='payroll_recommendation_hr'),
    path('payroll/recommendation/action/', views.payroll_recommendation_action, name='payroll_recommendation_action'),

    
    ########## Payroll Recommendation - FIN ##########
    path('payroll/recommendation/fin/', views.payroll_recommendation_finance, name='payroll_recommendation_finance'),
    path('payroll/recommendation/fin/action/', views.payroll_recommendation_finance_action, name='payroll_recommendation_finance_action'),


    ########## CEO Payroll Recommendation URLs ########
    path('payroll/recommendation/ceo/', views.payroll_recommendation_ceo, name='payroll_recommendation_ceo'),
    path('payroll/recommendation/ceo/action/', views.payroll_recommendation_ceo_action, name='payroll_recommendation_ceo_action'),
    

    ########### Payroll Run #############

     path('payroll-run/', views.payroll_run, name='payroll_run'),

    ########### Attendence Submission #########
    
    path('attendance-submission/', views.attendance_submission, name='attendance_submission'),
    path('submit-attendance/', views.submit_attendance, name='submit_attendance'),
    path('submit-attendance-for-approval/', views.submit_attendance_for_approval, name='submit_attendance_for_approval'),
    path('search-employees-ajax/', views.search_employees_ajax, name='search_employees_ajax'),
    # path('get-employees-for-date/', views.get_employees_for_date, name='get_employees_for_date'),

    ########## Attendence Reports ######### 
    path('attendance-report/', views.attendance_report_view, name='attendance_report'),
    path('get-period-details/<int:period_id>/', views.get_period_details, name='get_period_details'),

 
    ########## Payroll Reports ##########
    path('payroll/reports/', views.payroll_reports, name='payroll_reports'),
    path('payroll/handle-action/', views.handle_report_action, name='handle_report_action'),
    # path('download-payroll-excel/', views.download_payroll_excel, name='download_payroll_excel'),

    path('payroll/earning-change/', views.handle_earning_change_view, name='handle_earning_change_track'),
    path('payroll/generate-earning-report/', views.generate_earning_change_report_view, name='generate_earning_change_report'),

    path('payroll/deduction-change/', views.handle_deduction_change_view, name='handle_deduction_change_track'),
    path('payroll/generate-deduction-report/', views.generate_deduction_change_report_view, name='generate_deduction_change_report'),
    

    path('payroll/payslip/input/<str:period_id>/', views.payslip_input_view, name='payslip_input'),
    path('payroll/payslip/generate/', views.generate_payslip_report, name='generate_payslip_report'),
    path('payroll/payslip/validate-employee/', views.validate_employee_id, name='validate_employee_id'),
    path('payroll/payslip/direct/<str:period_id>/<str:employee_id>/', views.payslip_report_direct, name='payslip_direct'),
    
    ###### Finance Reports #####
    path('finance/reports/', views.finance_reports, name='finance_reports'),
    path('finance/reports/action/', views.handle_finance_report_action, name='handle_finance_report_action'),

]
