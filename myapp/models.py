# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth import get_user_model  # Correct import for User
from django.contrib.contenttypes.models import ContentType 

class Abcd(models.Model):
    tube_id = models.IntegerField(primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'abcd'


class Acc(models.Model):
    acc_id = models.IntegerField(primary_key=True)  # This field type is a guess.
    acc_desc = models.CharField(max_length=80)  # This field type is a guess.
    acc_subgrp = models.IntegerField() # This field type is a guess.
    acc_flg = models.CharField(max_length=1)  # This field type is a guess.
    acc_ref = models.IntegerField(null=True, blank=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc'


class AccBudgt(models.Model):
    acc_budgt_yr = models.IntegerField()   # This field type is a guess.
    acc_budgt_subgrp = models.CharField(max_length=50, primary_key=True) # This field type is a guess.
    acc_budgt_amt = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_budgt'


class AccCat(models.Model):
    acc_cat_id = models.IntegerField(primary_key=True)   # This field type is a guess.
    acc_cat_desc =models.CharField(max_length=60)  # This field type is a guess.
    acc_cat_cr_db = models.CharField(max_length=1)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_cat'


class AccClosingStatus(models.Model):
    acc_closing_month = models.DateField()  # This field type is a guess.
    acc_closing_date = models.DateField()  # This field type is a guess.
    acc_closing_acc = models.IntegerField()  # This field type is a guess.
    acc_closing_flg = models.CharField(max_length=1)   # This field type is a guess.
    acc_closing_year = models.IntegerField(primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_closing_status'


class AccGrp(models.Model):
    acc_grp_id = models.IntegerField(primary_key=True)   # This field type is a guess.
    acc_grp_desc = models.CharField(max_length=60)  # This field type is a guess.
    acc_grp_flg = models.CharField(max_length=1, blank=True, null=True)   # This field type is a guess.
    acc_grp_cat = models.IntegerField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_grp'


class AccGrpBugt(models.Model):
    acc_grp_bugt_year = models.IntegerField(blank=True, null=True)  # This field type is a guess.
    acc_grp_bugt_grp = models.IntegerField(primary_key=True)  # This field type is a guess.
    acc_grp_bugt_amt = models.FloatField(blank=True, null=True)  # This field type is a guess.
    acc_grp_bugt_cr = models.FloatField(blank=True, null=True)  # This field type is a guess.
    acc_grp_bugt_dr = models.FloatField(blank=True, null=True)   # This field type is a guess.
    acc_grp_bugt_bal = models.FloatField(blank=True, null=True)  # This field type is a guess.
    acc_grp_bugt_flg = models.CharField(max_length=1)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_grp_bugt'


class AccHis(models.Model):
    acc_his_month = models.DateField(blank=True, null=True, primary_key=True)  # This field type is a guess.
    acc_his_date = models.DateField(blank=True, null=True) # This field type is a guess.
    acc_his_acc = models.IntegerField(blank=True, null=True)   # This field type is a guess.
    acc_his_opn_bal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # This field type is a guess.
    acc_his_cr = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # This field type is a guess.
    acc_his_db = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # This field type is a guess.
    acc_his_cls_bal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # This field type is a guess.
    acc_his_flg = models.CharField(max_length=1, blank=True, null=True)  # This field type is a guess.
    acc_his_yeay = models.IntegerField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_his'


class AccSubgrp(models.Model):
    acc_subgrp_id = models.IntegerField(primary_key=True)  # This field type is a guess.
    acc_subgrp_desc = models.CharField(max_length=70)  # This field type is a guess.
    acc_subgrp_flg = models.CharField(max_length=1, blank=True, null=True)  # This field type is a guess.
    acc_subgrp_grp = models.IntegerField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_subgrp'


class AccYear(models.Model):
    acc_year = models.IntegerField(blank=True, null=True, primary_key=True)  # This field type is a guess.
    acc_year_from = models.DateField()  # This field type is a guess.
    acc_year_to = models.DateField()  # This field type is a guess.
    acc_year_flg = models.CharField(max_length=1)  # This field type is a guess.
    acc_year_dt = models.DateField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'acc_year'


class AllowCalc(models.Model):
    allow_calc_flg = models.CharField(max_length=1, blank=True, null=True, primary_key=True)  # This field type is a guess.
    allow_calc_desc = models.CharField(max_length=30)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'allow_calc'


class Allw(models.Model):
    allw_id = models.IntegerField(primary_key=True)  # This field type is a guess.
    allw_saltyp = models.CharField(max_length=10)  # This field type is a guess.
    allw_desc = models.CharField(max_length=100)  # This field type is a guess.
    allw_flg = models.CharField(max_length=1, blank=True, null=True)  # This field type is a guess.
    allw_emptyp = models.CharField(max_length=10)  # This field type is a guess.
    allw_earn_deduc = models.IntegerField()  # This field type is a guess.
    allw_typ = models.CharField(max_length=10)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'allw'


class AllwRate(models.Model):
    allw_period = models.IntegerField(primary_key=True)  # This field type is a guess.
    allw_id = models.IntegerField()  # This field type is a guess.
    allw_rate = models.DecimalField(max_digits=8, decimal_places=2)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'allw_rate'


class AllwTemp(models.Model):
    allw_id = allw_id = models.IntegerField(primary_key=True)   # This field type is a guess.
    allw_desc = models.CharField(max_length=200)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'allw_temp'


class ApChecksAll(models.Model):
    id = models.IntegerField(primary_key=True)  # This field type is a guess.
    payee_name = models.CharField(max_length=100, blank=True, null=True)  # This field type is a guess.
    pay_date = models.DateField(blank=True, null=True)  # This field type is a guess.
    amount = models.BigIntegerField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'ap_checks_all'


class Area(models.Model):
    area_id = models.IntegerField(primary_key=True)  # This field type is a guess.
    area_desc = models.CharField(max_length=150)  # This field type is a guess.
    area_uc = models.IntegerField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'area'


class Area1(models.Model):
    area_id = models.CharField(max_length=3, primary_key=True)   # This field type is a guess.
    area_desc = models.CharField(max_length=240)  # This field type is a guess.
    area_uc = models.CharField(max_length=240) # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'area1'


class AreaBkp(models.Model):
    area_id = models.IntegerField(primary_key=True)  # This field type is a guess.
    area_desc = models.CharField(max_length=150)  # This field type is a guess.
    area_uc = models.IntegerField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'area_bkp'


class Att(models.Model):
    att_period = models.IntegerField()  # NUMBER(4)
    att_dt = models.DateField()  # DATE
    att_emp = models.IntegerField()  # NUMBER(7)
    att_status = models.CharField(max_length=1)  # CHAR(1 BYTE)
    att_holiday_typ = models.CharField(max_length=1)  # CHAR(1 BYTE)
    att_leave_typ = models.IntegerField()  # NUMBER(3)
    att_overtime_typ = models.CharField(max_length=1)  # CHAR(1 BYTE), NOT NULL
    att_posted_by = models.IntegerField()  # NUMBER(7)
    att_approved_by = models.IntegerField()  # NUMBER(7)
    att_accepted_by = models.IntegerField()  # NUMBER(7)
    att_flg = models.CharField(max_length=1)  # CHAR(1 BYTE)
    att_remarks = models.CharField(max_length=500)  # VARCHAR2(500 BYTE)

    class Meta:
        managed = False
        db_table = 'att'


class Att1(models.Model):
    att_period = models.IntegerField()  # NUMBER(4)
    att_dt = models.DateField()  # DATE
    att_emp = models.IntegerField()  # NUMBER(7)
    att_status = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    att_holiday_typ = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    att_leave_typ = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    att_overtime_typ = models.CharField(max_length=1)  # CHAR(1 BYTE), NOT NULL
    att_posted_by = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    att_approved_by = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    att_accepted_by = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    att_flg = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    att_renarks = models.CharField(max_length=500, blank=True, null=True)  # VARCHAR2(500 BYTE)

    class Meta:
        managed = False
        db_table = 'att1'


class Att09052023(models.Model):
    ATT_PERIOD = models.IntegerField()  # NUMBER(4)
    ATT_DT = models.DateField()  # DATE
    ATT_EMP = models.IntegerField()  # NUMBER(7)
    ATT_STATUS = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    ATT_HOLIDAY_TYP = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    ATT_LEAVE_TYP = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    ATT_OVERTIME_TYP = models.CharField(max_length=1)  # CHAR(1 BYTE) NOT NULL
    ATT_POSTED_BY = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    ATT_APPROVED_BY = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    ATT_ACCEPTED_BY = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    ATT_FLG = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    ATT_RENARKS = models.CharField(max_length=500, blank=True, null=True)  # VARCHAR2(500 BYTE)

    class Meta:
        managed = False
        db_table = 'att_09052023'


class AttBiotimeSummary(models.Model):
    ZONE = models.CharField(max_length=2, blank=True, null=True)  # VARCHAR2(2 BYTE)
    PERSONNEL_NO = models.CharField(max_length=9, blank=True, null=True)  # VARCHAR2(9 BYTE)
    FIRST_NAME = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    LAST_NAME = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    POSITION = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    DEPARTMENT = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    ATT_DATE = models.CharField(max_length=20, blank=True, null=True)  # VARCHAR2(20 BYTE)
    WEEKDAY = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    EXCEPTION = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    TIMETABLE_NAME = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    CHECK_IN = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    CHECK_OUT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    CHECK_IN_TIME = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    CHECK_OUT_TIME = models.CharField(max_length=40, blank=True, null=True)  # VARCHAR2(40 BYTE)
    TOTAL_TIME = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    BREAK_OUT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    BREAK_IN = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    ACTUAL_BREAK_TIME = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    LATE = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    EARLY_LEAVE = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    ABSENT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    TOTAL_TIME_WORKED = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    LEAVE = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    TRAINING = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    SHORT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    TIMETABLE = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    BREAK_TIME_DURATION = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    NORMAL_OT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    WEEKEND_OT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    HOLIDAY_OT = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)

    class Meta:
        managed = False
        db_table = 'att_biotime_summary'


class AttSummary(models.Model):
    EMP_NO = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)
    EMP_NAME = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)
    EMP_DESG = models.CharField(max_length=50, blank=True, null=True)  # VARCHAR2(50 BYTE)
    EMP_DEPT = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)
    EMP_ATT_DT = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)
    EMP_WEEKDAY = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)
    EMP_CHECK_IN = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)
    EXCEPTION = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    EMP_CHECK_OUT = models.CharField(max_length=30, blank=True, null=True)  # VARCHAR2(30 BYTE)

    class Meta:
        managed = False
        db_table = 'att_summary'


class AuditEmp(models.Model):
    AUDIT_EMP_SEQ = models.BigIntegerField(blank=True, null=True,primary_key=True)  # NUMBER(12)
    AUDIT_EMP_NO = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    AUDIT_EMP_NAME = models.CharField(max_length=80, blank=True, null=True)  # VARCHAR2(80 BYTE)
    AUDIT_EMP_CNIC = models.CharField(max_length=15, blank=True, null=True)  # VARCHAR2(15 BYTE)
    AUDIT_EMP_DEPTT = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_JOIN_DT = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_JOB = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_GRADE = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_ADDRESS1 = models.CharField(max_length=200, blank=True, null=True)  # VARCHAR2(200 BYTE)
    AUDIT_EMP_ADDRESS2 = models.CharField(max_length=500, blank=True, null=True)  # VARCHAR2(500 BYTE)
    AUDIT_EMP_CELL1 = models.CharField(max_length=20, blank=True, null=True)  # VARCHAR2(20 BYTE)
    AUDIT_EMP_CELL2 = models.CharField(max_length=20, blank=True, null=True)  # VARCHAR2(20 BYTE)
    AUDIT_EMP_EMAIL = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    AUDIT_EMP_FLG = models.CharField(max_length=1, blank=True, null=True)  # VARCHAR2(1 BYTE)
    AUDIT_EMP_TYP = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_FNAME = models.CharField(max_length=80, blank=True, null=True)  # VARCHAR2(80 BYTE)
    AUDIT_EMP_MARRIED = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    AUDIT_EMP_DUTY_LOC = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_DOB = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_GENDER = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    AUDIT_EMP_SALTYP = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_BANK = models.IntegerField(blank=True, null=True)  # NUMBER(4)
    AUDIT_EMP_BANK_ACC = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    AUDIT_EMP_CONT_PERSON = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    AUDIT_EMP_CONT_PERSON_CELL = models.CharField(max_length=20, blank=True, null=True)  # VARCHAR2(20 BYTE)
    AUDIT_EMP_LEAVING_DT = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_PAY_MODE = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    AUDIT_EMP_PAY_SUBGRP = models.IntegerField(blank=True, null=True)  # NUMBER
    AUDIT_EMP_EXP_DT = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_MGR = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    AUDIT_EMP_ATT_FLG = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    AUDIT_EMP_REPATRIAT_DT = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_PERSONAL_EMAIL = models.CharField(max_length=100, blank=True, null=True)  # VARCHAR2(100 BYTE)
    AUDIT_EMP_CHANGTYP = models.CharField(max_length=1, blank=True, null=True)  # CHAR(1 BYTE)
    AUDIT_EMP_CHANGBY = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    AUDIT_EMP_AUTHBY = models.IntegerField(blank=True, null=True)  # NUMBER(7)
    AUDIT_EMP_TIME = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_AUDITFLG = models.CharField(max_length=1)  # CHAR(1 BYTE) NOT NULL
    AUDIT_EMP_QUOTA = models.IntegerField(blank=True, null=True)  # NUMBER(3)
    AUDIT_EMP_PEC_REG = models.CharField(max_length=15, blank=True, null=True)  # VARCHAR2(15 BYTE)
    AUDIT_EMP_QUALIFICATION = models.CharField(max_length=80, blank=True, null=True)  # VARCHAR2(80 BYTE)
    AUDIT_EMP_INSTITUTE = models.CharField(max_length=300, blank=True, null=True)  # VARCHAR2(300 BYTE)
    AUDIT_EMP_YR_GRADUATE = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_BLOOD = models.CharField(max_length=5, blank=True, null=True)  # VARCHAR2(5 BYTE)
    AUDIT_EMP_DOMICILE = models.CharField(max_length=60, blank=True, null=True)  # VARCHAR2(60 BYTE)
    AUDIT_EMP_NXT_KIN = models.CharField(max_length=80, blank=True, null=True)  # VARCHAR2(80 BYTE)
    AUDIT_EMP_EXCH_NO = models.CharField(max_length=15, blank=True, null=True)  # VARCHAR2(15 BYTE)
    AUDIT_EMP_EXCH_DT = models.DateField(blank=True, null=True)  # DATE
    AUDIT_EMP_EOBI_NO = models.CharField(max_length=12, blank=True, null=True)  # VARCHAR2(12 BYTE)
    AUDIT_EMP_WAIVER_BILL = models.BigIntegerField(blank=True, null=True)  # NUMBER(9)
    AUDIT_EMP_WEEK_DAYS = models.IntegerField(blank=True, null=True)  # NUMBER(1)

    class Meta:
        managed = False
        db_table = 'audit_emp'


class AuditEmpBkp(models.Model):
    audit_emp_seq = models.BigIntegerField()  # NUMBER(12)
    audit_emp_no = models.IntegerField()  # NUMBER(7)
    audit_emp_name = models.CharField(max_length=80)  # VARCHAR2(80 BYTE)
    audit_emp_cnic = models.CharField(max_length=15)  # VARCHAR2(15 BYTE)
    audit_emp_deptt = models.IntegerField()  # NUMBER(3)
    audit_emp_join_dt = models.DateField()  # DATE
    audit_emp_job = models.IntegerField()  # NUMBER(3)
    audit_emp_grade = models.IntegerField()  # NUMBER(3)
    audit_emp_address1 = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    audit_emp_address2 = models.CharField(max_length=500)  # VARCHAR2(500 BYTE)
    audit_emp_cell1 = models.CharField(max_length=20)  # VARCHAR2(20 BYTE)
    audit_emp_cell2 = models.CharField(max_length=20)  # VARCHAR2(20 BYTE)
    audit_emp_email = models.CharField(max_length=100)  # VARCHAR2(100 BYTE)
    audit_emp_flg = models.CharField(max_length=1)  # VARCHAR2(1 BYTE)
    audit_emp_typ = models.IntegerField()  # NUMBER(3)
    audit_emp_fname = models.CharField(max_length=80)  # VARCHAR2(80 BYTE)
    audit_emp_married = models.CharField(max_length=1)  # CHAR(1 BYTE)
    audit_emp_duty_loc = models.IntegerField()  # NUMBER(3)
    audit_emp_dob = models.DateField()  # DATE
    audit_emp_gender = models.CharField(max_length=1)  # CHAR(1 BYTE)
    audit_emp_saltyp = models.IntegerField()  # NUMBER(3)
    audit_emp_bank = models.IntegerField()  # NUMBER(4)
    audit_emp_bank_acc = models.CharField(max_length=20)  # VARCHAR2(20 BYTE)
    audit_emp_cont_person = models.CharField(max_length=100)  # VARCHAR2(100 BYTE)
    audit_emp_cont_person_cell = models.CharField(max_length=20)  # VARCHAR2(20 BYTE)
    audit_emp_leaving_dt = models.DateField(null=True, blank=True)  # DATE
    audit_emp_pay_mode = models.CharField(max_length=1)  # CHAR(1 BYTE)
    audit_emp_pay_subgrp = models.BigIntegerField()  # NUMBER
    audit_emp_exp_dt = models.DateField(null=True, blank=True)  # DATE
    audit_emp_mgr = models.IntegerField()  # NUMBER(7)
    audit_emp_att_flg = models.CharField(max_length=1)  # CHAR(1 BYTE)
    audit_emp_repatriat_dt = models.DateField(null=True, blank=True)  # DATE
    audit_emp_personal_email = models.CharField(max_length=100)  # VARCHAR2(100 BYTE)
    audit_emp_changtyp = models.CharField(max_length=1)  # CHAR(1 BYTE)
    audit_emp_changby = models.IntegerField()  # NUMBER(7)
    audit_emp_authby = models.IntegerField()  # NUMBER(7)
    audit_emp_time = models.DateTimeField()  # DATE (Assuming timestamp)
    audit_emp_auditflg = models.CharField(max_length=1)  # CHAR(1 BYTE) NOT NULL
    audit_emp_quota = models.IntegerField()  # NUMBER(3)
    audit_emp_pec_reg = models.CharField(max_length=15)  # VARCHAR2(15 BYTE)
    audit_emp_qualification = models.CharField(max_length=80)  # VARCHAR2(80 BYTE)
    audit_emp_institute = models.CharField(max_length=300)  # VARCHAR2(300 BYTE)
    audit_emp_yr_graduate = models.DateField(null=True, blank=True)  # DATE
    audit_emp_blood = models.CharField(max_length=5)  # VARCHAR2(5 BYTE)
    audit_emp_domicile = models.CharField(max_length=60)  # VARCHAR2(60 BYTE)
    audit_emp_nxt_kin = models.CharField(max_length=80)  # VARCHAR2(80 BYTE)
    audit_emp_exch_no = models.CharField(max_length=15)  # VARCHAR2(15 BYTE)
    audit_emp_exch_dt = models.DateField(null=True, blank=True)  # DATE
    audit_emp_eobi_no = models.CharField(max_length=12)  # VARCHAR2(12 BYTE)
    audit_emp_waiver_bill = models.BigIntegerField()  # NUMBER(9)
    audit_emp_week_days = models.IntegerField()  # NUMBER(1)

    class Meta:
        managed = False
        db_table = 'audit_emp_bkp'


class AuditEmppay(models.Model):
    emp_pay_emp = models.IntegerField()  # NUMBER(7)
    emp_pay_allw = models.IntegerField()  # NUMBER(5)
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # NUMBER(12,2) NOT NULL
    emp_pay_allwrule = models.IntegerField()  # NUMBER(1)
    emp_pay_acc = models.IntegerField()  # NUMBER(9)
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # NUMBER(10,2)
    emp_pay_changtyp = models.CharField(max_length=1)  # CHAR(1 BYTE)
    emp_pay_changby = models.IntegerField()  # NUMBER(7)
    emp_pay_authby = models.IntegerField()  # NUMBER(7)
    emp_pay_time = models.DateField()  # DATE
    emp_pay_auditflg = models.CharField(max_length=1)  # CHAR(1 BYTE) NOT NULL
    emp_pay_seq = models.BigIntegerField()  # NUMBER(12)

    class Meta:
        managed = False
        db_table = 'audit_emppay'


class AuditEmppayOldval(models.Model):
    emp_pay_emp = models.IntegerField()  # NUMBER(7)
    emp_pay_allw = models.IntegerField()  # NUMBER(5)
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # NUMBER(12,2) NOT NULL
    emp_pay_allwrule = models.IntegerField()  # NUMBER(1)
    emp_pay_acc = models.IntegerField()  # NUMBER(9)
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # NUMBER(10,2)
    emp_pay_changtyp = models.CharField(max_length=1, null=True, blank=True)  # CHAR(1 BYTE)
    emp_pay_changby = models.IntegerField(null=True, blank=True)  # NUMBER(7)
    emp_pay_authby = models.IntegerField(null=True, blank=True)  # NUMBER(7)
    emp_pay_time = models.DateField(null=True, blank=True)  # DATE
    emp_pay_auditflg = models.CharField(max_length=1)  # CHAR(1 BYTE) NOT NULL
    emp_pay_seq = models.BigIntegerField()  # NUMBER(12)

    class Meta:
        managed = False
        db_table = 'audit_emppay_oldval'


class AuthGroup(models.Model):
    id = models.AutoField(primary_key=True)  # Matches NUMBER(11) with sequence
    name = models.CharField(max_length=150)  # Matches NVARCHAR2(150)

    class Meta:
        managed = False
        db_table = 'auth_group'
        unique_together = (('name', 'name'),)


class AuthGroupPermissions(models.Model):
    id = models.AutoField(primary_key=True)  # Matches NUMBER(19) with sequence
    group_id = models.BigIntegerField()  # Matches NUMBER(11)
    permission_id = models.BigIntegerField()  # Matches NUMBER(11)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('permission_id', 'group_id', 'group_id', 'permission_id'),)


class AuthHis(models.Model):
    auth_his_no = models.BigIntegerField(primary_key=True)  # Matches NUMBER(8)
    auth_his_dt = models.DateField()  # Matches DATE
    auth_his_mod = models.IntegerField()  # Matches NUMBER(3)
    auth_his_from = models.BigIntegerField()  # Matches NUMBER(7)
    auth_his_from_flg = models.CharField(max_length=1)  # Matches CHAR(1 BYTE)
    auth_his_from_comments = models.CharField(max_length=200)  # Matches VARCHAR2(200 BYTE)
    auth_his_to = models.BigIntegerField()  # Matches NUMBER(7)
    auth_his_to_flg = models.CharField(max_length=1)  # Matches CHAR(1 BYTE)
    auth_his_to_comments = models.CharField(max_length=200)  # Matches VARCHAR2(200 BYTE)

    class Meta:
        managed = False
        db_table = 'auth_his'


class AuthMod(models.Model):
    auth_mod_id = models.IntegerField(primary_key=True)  # Matches NUMBER(3)
    auth_mod_desc = models.CharField(max_length=50)  # Matches VARCHAR2(50 BYTE)

    class Meta:
        managed = False
        db_table = 'auth_mod'


class AuthModDet(models.Model):
    auth_mod_det_mod = models.IntegerField()  # Matches NUMBER(3)
    auth_mod_det_flg = models.CharField(max_length=1)  # Matches CHAR(1 BYTE)
    auth_mod_det_emp = models.IntegerField()  # Matches NUMBER(7)
    auth_mod_det_nxt_emp = models.IntegerField()  # Matches NUMBER(7)

    class Meta:
        managed = False
        db_table = 'auth_mod_det'


class AuthPermission(models.Model):
    id = models.AutoField(primary_key=True)  # Matches NUMBER(11) with sequence
    name = models.CharField(max_length=255)  # Matches NVARCHAR2(255)
    content_type_id = models.IntegerField()  # Matches NUMBER(11) NOT NULL
    codename = models.CharField(max_length=100)  # Matches NVARCHAR2(100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('codename', 'content_type_id', 'content_type_id', 'codename'),)


class AuthUser(models.Model):
    id = models.AutoField(primary_key=True)  # Maps to NUMBER(11) with sequence
    password = models.CharField(max_length=128)  # Matches NVARCHAR2(128)
    last_login = models.DateTimeField(null=True, blank=True)  # Matches TIMESTAMP(6)
    is_superuser = models.BooleanField(default=False)  # Maps to NUMBER(1) NOT NULL
    username = models.CharField(max_length=150, unique=True)  # Matches NVARCHAR2(150)
    first_name = models.CharField(max_length=150, blank=True)  # Matches NVARCHAR2(150)
    last_name = models.CharField(max_length=150, blank=True)  # Matches NVARCHAR2(150)
    email = models.EmailField(max_length=254, unique=True)  # Matches NVARCHAR2(254)
    is_staff = models.BooleanField(default=False)  # Maps to NUMBER(1) NOT NULL
    is_active = models.BooleanField(default=True)  # Maps to NUMBER(1) NOT NULL
    date_joined = models.DateTimeField(auto_now_add=True)  # Matches TIMESTAMP(6) NOT NULL

    class Meta:
        managed = False
        db_table = 'auth_user'
        unique_together = (('username', 'username'),)


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)  # Assuming ID is an auto-incrementing primary key
    user_id = models.BigIntegerField()  # Assuming user_id is a numeric field
    group_id = models.BigIntegerField()  # Assuming group_id is a numeric field

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('group_id', 'user_id', 'user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)  # Auto-incrementing primary key
    user_id = models.BigIntegerField()  # Numeric User ID
    permission_id = models.BigIntegerField()  # Numeric Permission ID

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('permission_id', 'user_id', 'user_id', 'permission_id'),)


class Bank(models.Model):
    bank_id = models.PositiveSmallIntegerField(primary_key=True)  # Assuming BANK_ID is a small number
    bank_desc = models.CharField(max_length=150)  # BANK_DESC as a required string field
    bank_acc = models.BigIntegerField(null=True, blank=True)  # BANK_ACC as a numeric field (optional)

    class Meta:
        managed = False
        db_table = 'bank'


class BankBr(models.Model):
    bank_br_id = models.PositiveSmallIntegerField(primary_key=True)  # Assuming BANK_BR_ID is a small number
    bank_br_desc = models.CharField(max_length=250)  # BANK_BR_DESC as a required string field
    bank_br_bank = models.PositiveSmallIntegerField(null=True, blank=True)  # BANK_BR_BANK as a numeric field (optional)

    class Meta:
        managed = False
        db_table = 'bank_br'


class BankBrbkp(models.Model):
    bank_br_id = models.PositiveSmallIntegerField(primary_key=True)  # BANK_BR_ID as a small positive integer (4 digits)
    bank_br_desc = models.CharField(max_length=250)  # BANK_BR_DESC as a required string field
    bank_br_bank = models.PositiveSmallIntegerField()  # BANK_BR_BANK as a small positive integer (3 digits)

    class Meta:
        managed = False
        db_table = 'bank_brbkp'

class Bill(models.Model):
    bill_period = models.PositiveIntegerField()  # NUMBER(6) - Part of Primary Key
    bill_acc = models.PositiveIntegerField(primary_key=True)  # NUMBER(9) - Part of Primary Key
    bill_charg1_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg2_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg3_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg4_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg5_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg6_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg7_amt = models.IntegerField(null=True, blank=True)  # NUMBER(8)
    bill_charg8_amt = models.BigIntegerField(null=True, blank=True)  # NUMBER(9)
    bill_recov_amt = models.BigIntegerField(null=True, blank=True)  # NUMBER(9)
    bill_no = models.BigIntegerField(unique=True)  # NUMBER(15) - Unique
    bill_charg9_amt = models.BigIntegerField(null=True, blank=True)  # NUMBER(10)
    bill_charg10_amt = models.BigIntegerField(null=True, blank=True)  # NUMBER(10)
    bill_paid_dt = models.DateField(null=True, blank=True)  # DATE
    bill_bank = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(3)
    bill_flg = models.CharField(max_length=1, null=True, blank=True)  # CHAR(1 BYTE)
    bill_posted_by = models.PositiveSmallIntegerField()  # NUMBER(4) - Non-null
    bill_charg11_amt = models.BigIntegerField(null=True, blank=True)  # NUMBER(9)

    class Meta:
        managed = False  # Because this table is already in Oracle
        db_table = 'BILL'
        constraints = [
            models.UniqueConstraint(fields=['bill_no'], name='BILL_UNIQ'),
            models.UniqueConstraint(fields=['bill_period', 'bill_acc'], name='BILL_PK'),  # Simulating composite PK
        ]

    def __str__(self):
        return f"Bill No: {self.bill_no}, Period: {self.bill_period}, Account: {self.bill_acc}"



class CarMon(models.Model):
    emp_no = models.BigIntegerField(primary_key=True)  # NUMBER - Employee Number
    amount = models.CharField(max_length=40)  # VARCHAR2(40 BYTE) - Amount as String

    class Meta:
        managed = False
        db_table = 'car_mon'


class CaseInfo(models.Model):
    case_id = models.BigIntegerField(primary_key=True)  # NUMBER - Case ID
    case_title = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    type_court = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    court_name = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    suite_wp_no = models.CharField(max_length=100)  # VARCHAR2(100 BYTE)
    case_nature = models.CharField(max_length=300)  # VARCHAR2(300 BYTE)
    c_date = models.DateField(null=True, blank=True)  # DATE
    case_status = models.CharField(max_length=300)  # VARCHAR2(300 BYTE)
    type_of_case = models.CharField(max_length=100)  # VARCHAR2(100 BYTE)
    case_flag = models.CharField(max_length=50)  # VARCHAR2(50 BYTE)

    class Meta:
        managed = False
        db_table = 'case_info'


class CaseInfo12232024Bkp(models.Model):
    case_id = models.BigAutoField(primary_key=True)  # NUMBER - Assuming it's a primary key
    case_title = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    type_court = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    court_name = models.CharField(max_length=200)  # VARCHAR2(200 BYTE)
    suite_wp_no = models.CharField(max_length=100, null=True, blank=True)  # VARCHAR2(100 BYTE)
    case_nature = models.CharField(max_length=300, null=True, blank=True)  # VARCHAR2(300 BYTE)
    c_date = models.DateField(null=True, blank=True)  # DATE
    case_status = models.CharField(max_length=300, null=True, blank=True)  # VARCHAR2(300 BYTE)
    type_of_case = models.CharField(max_length=100, null=True, blank=True)  # VARCHAR2(100 BYTE)
    case_flag = models.CharField(max_length=50, null=True, blank=True)  # VARCHAR2(50 BYTE)

    class Meta:
        managed = False
        db_table = 'case_info_12232024bkp'


class CaseProcceding(models.Model):
    p_no = models.BigAutoField(primary_key=True)  # Assuming it's a primary key
    case_id = models.BigIntegerField()  # Foreign Key reference to CourtCase (without constraint)
    p_date = models.DateField(null=True, blank=True)  # DATE
    next_hearing = models.DateField(null=True, blank=True)  # DATE
    proceeding_remarks = models.CharField(max_length=300, null=True, blank=True)  # VARCHAR2(300 BYTE)
    last_hearing = models.DateField(null=True, blank=True)  # DATE

    class Meta:
        managed = False
        db_table = 'case_procceding'


class CaseProcceding12232024Bkp(models.Model):
    p_no = models.BigAutoField(primary_key=True)  # Assuming P_NO is a unique primary key
    case_id = models.BigIntegerField()  # Foreign key reference (without constraint)
    p_date = models.DateField(null=True, blank=True)  # DATE
    next_hearing = models.DateField(null=True, blank=True)  # DATE
    proceeding_remarks = models.CharField(max_length=300, null=True, blank=True)  # VARCHAR2(300 BYTE)
    last_hearing = models.DateField(null=True, blank=True)  # DATE

    class Meta:
        managed = False
        db_table = 'case_procceding_12232024bkp'


class City(models.Model):
    city_id = models.BigIntegerField(primary_key=True)  # NUMBER(6) - NOT NULL
    city_desc = models.CharField(max_length=80, null=True, blank=True)  # VARCHAR2(80 BYTE)
    city_dist = models.BigIntegerField(null=True, blank=True)  # NUMBER(6)

    class Meta:
        managed = False
        db_table = 'city'


class Companey(models.Model):
    comp_id = models.BigIntegerField(primary_key=True)  # NUMBER(6) - Assuming it's a unique ID
    comp_desc = models.CharField(max_length=40, null=True, blank=True)  # VARCHAR2(40 BYTE)
    comp_owner1 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_owner2 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_owner3 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_addr_lin1 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_addr_lin2 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_addr_lin3 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_cell1 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_cell2 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_ph1 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_ph2 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_fax1 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_fax2 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_email = models.EmailField(max_length=40, null=True, blank=True)  # VARCHAR2(40 BYTE)
    comp_logo = models.BinaryField(null=True, blank=True)  # BLOB (For storing images or files)
    kp_logo = models.BinaryField(null=True, blank=True)  # BLOB (Another image/file field)

    class Meta:
        managed = False
        db_table = 'companey'


class CompanyBkp(models.Model):
    comp_id = models.BigIntegerField(primary_key=True)  # NUMBER(6) - Assuming it's a unique identifier
    comp_desc = models.CharField(max_length=40, null=True, blank=True)  # VARCHAR2(40 BYTE)
    comp_owner1 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_owner2 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_owner3 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_addr_lin1 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_addr_lin2 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_addr_lin3 = models.CharField(max_length=30, null=True, blank=True)  # VARCHAR2(30 BYTE)
    comp_cell1 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_cell2 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_ph1 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_ph2 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_fax1 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_fax2 = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15 BYTE)
    comp_email = models.EmailField(max_length=40, null=True, blank=True)  # VARCHAR2(40 BYTE)

    class Meta:
        managed = False
        db_table = 'company_bkp'


class CustTyp(models.Model):
    cust_typ_id = models.PositiveSmallIntegerField(primary_key=True)  # NUMBER(3) - Small integer for ID
    cust_typ_desc = models.CharField(max_length=25, null=True, blank=True)  # VARCHAR2(25 BYTE)

    class Meta:
        managed = False
        db_table = 'cust_typ'


class DateRanges(models.Model):
    id = models.BigAutoField(primary_key=True)  # NUMBER - Assuming it's an auto-incrementing primary key
    start_date = models.DateField(null=True, blank=True)  # DATE - Allows NULL values
    end_date = models.DateField(null=True, blank=True)  # DATE - Allows NULL values

    class Meta:
        managed = False
        db_table = 'date_ranges'


class Deptt(models.Model):
    deptt_id = models.PositiveSmallIntegerField(primary_key=True)  # NUMBER(3) - Small integer, NOT NULL
    deptt_desc = models.CharField(max_length=80)  # VARCHAR2(80 BYTE) - NOT NULL
    deptt_head = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(7) - Can be NULL

    class Meta:
        managed = False
        db_table = 'deptt'


class DepttBkp1(models.Model):
    deptt_id = models.PositiveSmallIntegerField(primary_key=True)  # NUMBER(3) - NOT NULL
    deptt_desc = models.CharField(max_length=80)  # VARCHAR2(80 BYTE) - NOT NULL
    deptt_head = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(7) - Can be NULL

    class Meta:
        managed = False
        db_table = 'deptt_bkp1'


class DepttBkp07102024(models.Model):
    deptt_id = models.PositiveSmallIntegerField(primary_key=True)  # NUMBER(3) - NOT NULL
    deptt_desc = models.CharField(max_length=80)  # VARCHAR2(80 BYTE) - NOT NULL
    deptt_head = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(7) - Nullable

    class Meta:
        managed = False
        db_table = 'deptt_bkp_07102024'


User = get_user_model()

class DjangoAdminLog(models.Model):
    id = models.BigAutoField(primary_key=True)  # NUMBER(11) with auto-increment
    action_time = models.DateTimeField(auto_now_add=True)  # TIMESTAMP(6), auto-filled
    object_id = models.TextField(null=True, blank=True)  # NCLOB
    object_repr = models.CharField(max_length=200)  # NVARCHAR2(200)
    action_flag = models.IntegerField()  # NUMBER(11), required
    change_message = models.TextField(null=True, blank=True)  # NCLOB
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)  # Foreign key to content type
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.BigAutoField(primary_key=True)  # NUMBER(11) with auto-increment
    app_label = models.CharField(max_length=100, null=True, blank=True)  # NVARCHAR2(100)
    model = models.CharField(max_length=100, null=True, blank=True)  # NVARCHAR2(100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('model', 'app_label', 'app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)  # NUMBER(19) with auto-increment
    app = models.CharField(max_length=255, null=True, blank=True)  # NVARCHAR2(255)
    name = models.CharField(max_length=255, null=True, blank=True)  # NVARCHAR2(255)
    applied = models.DateTimeField()  # TIMESTAMP(6) - Not Null

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(max_length=40, primary_key=True)  # NVARCHAR2(40) - Not Null
    session_data = models.TextField(null=True, blank=True)  # NCLOB - Can be Null
    expire_date = models.DateTimeField()  # TIMESTAMP(6) - Not Null

    class Meta:
        managed = False
        db_table = 'django_session'


class Emp(models.Model):
    emp_no = models.PositiveIntegerField(primary_key=True)  # NUMBER(7)
    emp_name = models.CharField(max_length=80)  # VARCHAR2(80) - NOT NULL
    emp_cnic = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15)
    emp_deptt = models.PositiveSmallIntegerField()  # NUMBER(3) - NOT NULL
    emp_join_dt = models.DateField(null=True, blank=True)  # DATE
    emp_job = models.PositiveSmallIntegerField()  # NUMBER(3) - NOT NULL
    emp_grade = models.PositiveSmallIntegerField()  # NUMBER(3) - NOT NULL
    emp_address1 = models.CharField(max_length=200, null=True, blank=True)  # VARCHAR2(200)
    emp_address2 = models.CharField(max_length=500, null=True, blank=True)  # VARCHAR2(500)
    emp_cell1 = models.CharField(max_length=20, null=True, blank=True)  # VARCHAR2(20)
    emp_cell2 = models.CharField(max_length=20, null=True, blank=True)  # VARCHAR2(20)
    emp_email = models.CharField(max_length=100, null=True, blank=True)  # VARCHAR2(100)
    emp_flg = models.CharField(max_length=1)  # VARCHAR2(1) - NOT NULL
    emp_typ = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(3)
    emp_fname = models.CharField(max_length=80, null=True, blank=True)  # VARCHAR2(80)
    emp_married = models.CharField(max_length=1, null=True, blank=True)  # CHAR(1)
    emp_duty_loc = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(3)
    emp_dob = models.DateField(null=True, blank=True)  # DATE
    emp_gender = models.CharField(max_length=1, null=True, blank=True)  # CHAR(1)
    emp_saltyp = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(3)
    emp_bank = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(4)
    emp_bank_acc = models.CharField(max_length=100, null=True, blank=True)  # VARCHAR2(100)
    emp_cont_person = models.CharField(max_length=100, null=True, blank=True)  # VARCHAR2(100)
    emp_cont_person_cell = models.CharField(max_length=20, null=True, blank=True)  # VARCHAR2(20)
    emp_leaving_dt = models.DateField(null=True, blank=True)  # DATE
    emp_pay_mode = models.CharField(max_length=1, null=True, blank=True)  # CHAR(1)
    emp_pay_subgrp = models.PositiveIntegerField(null=True, blank=True)  # NUMBER
    emp_exp_dt = models.DateField(null=True, blank=True)  # DATE
    emp_mgr = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(7)
    emp_att_flg = models.CharField(max_length=1, null=True, blank=True)  # CHAR(1)
    emp_repatriat_dt = models.DateField(null=True, blank=True)  # DATE
    emp_personal_email = models.CharField(max_length=100, null=True, blank=True)  # VARCHAR2(100)
    emp_postedby = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(7)
    emp_authby = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(7)
    emp_quota = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(3)
    emp_pec_reg = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15)
    emp_qualification = models.CharField(max_length=80, null=True, blank=True)  # VARCHAR2(80)
    emp_institute = models.CharField(max_length=300, null=True, blank=True)  # VARCHAR2(300)
    emp_yr_graduate = models.DateField(null=True, blank=True)  # DATE
    emp_blood = models.CharField(max_length=5, null=True, blank=True)  # VARCHAR2(5)
    emp_domicile = models.CharField(max_length=60, null=True, blank=True)  # VARCHAR2(60)
    emp_nxt_kin = models.CharField(max_length=80, null=True, blank=True)  # VARCHAR2(80)
    emp_exch_no = models.CharField(max_length=15, null=True, blank=True)  # VARCHAR2(15)
    emp_exch_dt = models.DateField(null=True, blank=True)  # DATE
    emp_eobi_no = models.CharField(max_length=12, null=True, blank=True)  # VARCHAR2(12)
    emp_waiver_bill = models.PositiveIntegerField(null=True, blank=True)  # NUMBER(9)
    emp_week_days = models.PositiveSmallIntegerField(null=True, blank=True)  # NUMBER(1)
    zone_id = models.IntegerField(default=1)  # INTEGER DEFAULT 1

    class Meta:
        managed = False
        db_table = 'emp'


class Emp1(models.Model):
    emp_no = models.CharField(max_length=240, primary_key=True)  # Should be NUMBER, but stored as string
    emp_name = models.CharField(max_length=240)
    emp_cnic = models.CharField(max_length=240, null=True, blank=True)
    emp_deptt = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_join_dt = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_job = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_grade = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_address1 = models.CharField(max_length=240, null=True, blank=True)
    emp_address2 = models.CharField(max_length=240, null=True, blank=True)
    emp_cell1 = models.CharField(max_length=240, null=True, blank=True)
    emp_cell2 = models.CharField(max_length=240, null=True, blank=True)
    emp_email = models.CharField(max_length=240, null=True, blank=True)
    emp_flg = models.CharField(max_length=240, null=True, blank=True)
    emp_typ = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_fname = models.CharField(max_length=240, null=True, blank=True)
    emp_married = models.CharField(max_length=240, null=True, blank=True)
    emp_duty_loc = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_dob = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_gender = models.CharField(max_length=240, null=True, blank=True)
    emp_saltyp = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_bank = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_bank_acc = models.CharField(max_length=240, null=True, blank=True)
    emp_cont_person = models.CharField(max_length=240, null=True, blank=True)
    emp_cont_person_cell = models.CharField(max_length=240, null=True, blank=True)
    emp_leaving_dt = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_pay_mode = models.CharField(max_length=240, null=True, blank=True)
    emp_pay_subgrp = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_exp_dt = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_mgr = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_att_flg = models.CharField(max_length=240, null=True, blank=True)
    emp_repatriat_dt = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_personal_email = models.CharField(max_length=240, null=True, blank=True)
    emp_postedby = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_authby = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_quota = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_pec_reg = models.CharField(max_length=240, null=True, blank=True)
    emp_qualification = models.CharField(max_length=240, null=True, blank=True)
    emp_institute = models.CharField(max_length=240, null=True, blank=True)
    emp_yr_graduate = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_blood = models.CharField(max_length=240, null=True, blank=True)
    emp_domicile = models.CharField(max_length=240, null=True, blank=True)
    emp_nxt_kin = models.CharField(max_length=240, null=True, blank=True)
    emp_exch_no = models.CharField(max_length=240, null=True, blank=True)
    emp_exch_dt = models.CharField(max_length=240, null=True, blank=True)  # Should be DATE
    emp_eobi_no = models.CharField(max_length=240, null=True, blank=True)
    emp_waiver_bill = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    emp_week_days = models.CharField(max_length=240, null=True, blank=True)  # Should be NUMBER
    zone_id = models.CharField(max_length=240, default="1")  # Should be NUMBER, DEFAULT 1

    class Meta:
        managed = False
        db_table = 'emp1'


class Emp2(models.Model):
    emp_no = models.CharField(max_length=240, primary_key=True)  # Should be Number
    emp_name = models.CharField(max_length=240)
    emp_cnic = models.CharField(max_length=240, null=True, blank=True)
    emp_deptt = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_join_dt = models.DateField(null=True, blank=True)  # Convert Manually in Views
    emp_job = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_grade = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_address1 = models.CharField(max_length=240, null=True, blank=True)
    emp_address2 = models.CharField(max_length=240, null=True, blank=True)
    emp_cell1 = models.CharField(max_length=240, null=True, blank=True)
    emp_cell2 = models.CharField(max_length=240, null=True, blank=True)
    emp_email = models.CharField(max_length=240, null=True, blank=True)
    emp_flg = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_typ = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_fname = models.CharField(max_length=240, null=True, blank=True)
    emp_married = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_duty_loc = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_dob = models.DateField(null=True, blank=True)  # Convert Manually
    emp_gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    emp_saltyp = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_bank = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_bank_acc = models.CharField(max_length=240, null=True, blank=True)
    emp_cont_person = models.CharField(max_length=240, null=True, blank=True)
    emp_cont_person_cell = models.CharField(max_length=240, null=True, blank=True)
    emp_leaving_dt = models.DateField(null=True, blank=True)  # Convert Manually
    emp_pay_mode = models.CharField(max_length=1, choices=[('C', 'Cash'), ('B', 'Bank')], null=True, blank=True)
    emp_pay_subgrp = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_exp_dt = models.DateField(null=True, blank=True)  # Convert Manually
    emp_mgr = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_att_flg = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_repatriat_dt = models.DateField(null=True, blank=True)  # Convert Manually
    emp_personal_email = models.CharField(max_length=240, null=True, blank=True)
    emp_postedby = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_authby = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_quota = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_pec_reg = models.CharField(max_length=240, null=True, blank=True)
    emp_qualification = models.CharField(max_length=240, null=True, blank=True)
    emp_institute = models.CharField(max_length=240, null=True, blank=True)
    emp_yr_graduate = models.DateField(null=True, blank=True)  # Convert Manually
    emp_blood = models.CharField(max_length=240, null=True, blank=True)
    emp_domicile = models.CharField(max_length=240, null=True, blank=True)
    emp_nxt_kin = models.CharField(max_length=240, null=True, blank=True)
    emp_exch_no = models.CharField(max_length=240, null=True, blank=True)
    emp_exch_dt = models.DateField(null=True, blank=True)  # Convert Manually
    emp_eobi_no = models.CharField(max_length=240, null=True, blank=True)
    emp_waiver_bill = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    emp_week_days = models.CharField(max_length=240, null=True, blank=True)  # Should be Number
    zone_id = models.CharField(max_length=240, default="1")

    class Meta:
        managed = False
        db_table = 'emp2'


class Emp05062023(models.Model):
    emp_no = models.IntegerField(primary_key=True)  # Primary Key
    emp_name = models.CharField(max_length=80)
    emp_cnic = models.CharField(max_length=15, null=True, blank=True)
    emp_deptt = models.IntegerField()
    emp_join_dt = models.DateField(null=True, blank=True)
    emp_job = models.IntegerField()
    emp_grade = models.IntegerField()
    emp_address1 = models.CharField(max_length=200, null=True, blank=True)
    emp_address2 = models.CharField(max_length=500, null=True, blank=True)
    emp_cell1 = models.CharField(max_length=20, null=True, blank=True)
    emp_cell2 = models.CharField(max_length=20, null=True, blank=True)
    emp_email = models.CharField(max_length=100, null=True, blank=True)
    emp_flg = models.CharField(max_length=1)  # Active/Inactive Flag
    emp_typ = models.IntegerField(null=True, blank=True)
    emp_fname = models.CharField(max_length=80, null=True, blank=True)
    emp_married = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_duty_loc = models.IntegerField(null=True, blank=True)
    emp_dob = models.DateField(null=True, blank=True)
    emp_gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    emp_saltyp = models.IntegerField(null=True, blank=True)
    emp_bank = models.IntegerField(null=True, blank=True)
    emp_bank_acc = models.CharField(max_length=100, null=True, blank=True)
    emp_cont_person = models.CharField(max_length=100, null=True, blank=True)
    emp_cont_person_cell = models.CharField(max_length=20, null=True, blank=True)
    emp_leaving_dt = models.DateField(null=True, blank=True)
    emp_pay_mode = models.CharField(max_length=1, choices=[('C', 'Cash'), ('B', 'Bank')], null=True, blank=True)
    emp_pay_subgrp = models.IntegerField(null=True, blank=True)
    emp_exp_dt = models.DateField(null=True, blank=True)
    emp_mgr = models.IntegerField(null=True, blank=True)
    emp_att_flg = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_repatriat_dt = models.DateField(null=True, blank=True)
    emp_personal_email = models.CharField(max_length=100, null=True, blank=True)
    emp_postedby = models.IntegerField(null=True, blank=True)
    emp_authby = models.IntegerField(null=True, blank=True)
    emp_quota = models.IntegerField(null=True, blank=True)
    emp_pec_reg = models.CharField(max_length=15, null=True, blank=True)
    emp_qualification = models.CharField(max_length=80, null=True, blank=True)
    emp_institute = models.CharField(max_length=300, null=True, blank=True)
    emp_yr_graduate = models.DateField(null=True, blank=True)
    emp_blood = models.CharField(max_length=5, null=True, blank=True)
    emp_domicile = models.CharField(max_length=60, null=True, blank=True)
    emp_nxt_kin = models.CharField(max_length=80, null=True, blank=True)
    emp_exch_no = models.CharField(max_length=15, null=True, blank=True)
    emp_exch_dt = models.DateField(null=True, blank=True)
    emp_eobi_no = models.CharField(max_length=12, null=True, blank=True)
    emp_waiver_bill = models.IntegerField(null=True, blank=True)
    emp_week_days = models.IntegerField(null=True, blank=True)
    zone_id = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'emp_05062023'


class Emp22022023(models.Model):
    emp_no = models.IntegerField(primary_key=True)  # Primary Key
    emp_name = models.CharField(max_length=80)
    emp_cnic = models.CharField(max_length=15, null=True, blank=True)
    emp_deptt = models.IntegerField()
    emp_join_dt = models.DateField(null=True, blank=True)
    emp_job = models.IntegerField()
    emp_grade = models.IntegerField()
    emp_address1 = models.CharField(max_length=200, null=True, blank=True)
    emp_address2 = models.CharField(max_length=500, null=True, blank=True)
    emp_cell1 = models.CharField(max_length=20, null=True, blank=True)
    emp_cell2 = models.CharField(max_length=20, null=True, blank=True)
    emp_email = models.CharField(max_length=100, null=True, blank=True)
    emp_flg = models.CharField(max_length=1)  # Active/Inactive Flag
    emp_typ = models.IntegerField(null=True, blank=True)
    emp_fname = models.CharField(max_length=80, null=True, blank=True)
    emp_married = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_duty_loc = models.IntegerField(null=True, blank=True)
    emp_dob = models.DateField(null=True, blank=True)
    emp_gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    emp_saltyp = models.IntegerField(null=True, blank=True)
    emp_bank = models.IntegerField(null=True, blank=True)
    emp_bank_acc = models.CharField(max_length=100, null=True, blank=True)
    emp_cont_person = models.CharField(max_length=100, null=True, blank=True)
    emp_cont_person_cell = models.CharField(max_length=20, null=True, blank=True)
    emp_leaving_dt = models.DateField(null=True, blank=True)
    emp_pay_mode = models.CharField(max_length=1, choices=[('C', 'Cash'), ('B', 'Bank')], null=True, blank=True)
    emp_pay_subgrp = models.IntegerField(null=True, blank=True)
    emp_exp_dt = models.DateField(null=True, blank=True)
    emp_mgr = models.IntegerField(null=True, blank=True)
    emp_att_flg = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, blank=True)
    emp_repatriat_dt = models.DateField(null=True, blank=True)
    emp_personal_email = models.CharField(max_length=100, null=True, blank=True)
    emp_postedby = models.IntegerField(null=True, blank=True)
    emp_authby = models.IntegerField(null=True, blank=True)
    emp_quota = models.IntegerField(null=True, blank=True)
    emp_pec_reg = models.CharField(max_length=15, null=True, blank=True)
    emp_qualification = models.CharField(max_length=80, null=True, blank=True)
    emp_institute = models.CharField(max_length=300, null=True, blank=True)
    emp_yr_graduate = models.DateField(null=True, blank=True)
    emp_blood = models.CharField(max_length=5, null=True, blank=True)
    emp_domicile = models.CharField(max_length=60, null=True, blank=True)
    emp_nxt_kin = models.CharField(max_length=80, null=True, blank=True)
    emp_exch_no = models.CharField(max_length=15, null=True, blank=True)
    emp_exch_dt = models.DateField(null=True, blank=True)
    emp_eobi_no = models.CharField(max_length=12, null=True, blank=True)
    emp_waiver_bill = models.IntegerField(null=True, blank=True)
    emp_week_days = models.IntegerField(null=True, blank=True)
    zone_id = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'emp_22022023'


class EmpAuthtyp(models.Model):
    emp_authtyp_id = models.IntegerField(primary_key=True)  # Primary Key
    emp_authtyp_desc = models.CharField(max_length=80)  # Description

    class Meta:
        managed = False
        db_table = 'emp_authtyp'


class EmpBackupCnic(models.Model):
    emp_no = models.IntegerField(primary_key=True)  # Employee Number (Primary Key)
    emp_name = models.CharField(max_length=80)  # Employee Name
    emp_cnic = models.CharField(max_length=15, blank=True, null=True)  # CNIC
    emp_deptt = models.IntegerField()  # Department ID (Foreign Key - Add Relation if Needed)
    emp_join_dt = models.DateField(blank=True, null=True)  # Joining Date
    emp_job = models.IntegerField()  # Job ID (Foreign Key if applicable)
    emp_grade = models.IntegerField()  # Grade
    emp_address1 = models.CharField(max_length=200, blank=True, null=True)  # Address 1
    emp_address2 = models.CharField(max_length=500, blank=True, null=True)  # Address 2
    emp_cell1 = models.CharField(max_length=20, blank=True, null=True)  # Cell Number 1
    emp_cell2 = models.CharField(max_length=20, blank=True, null=True)  # Cell Number 2
    emp_email = models.EmailField(max_length=100, blank=True, null=True)  # Email
    emp_flg = models.CharField(max_length=1)  # Status Flag (Active/Inactive)
    emp_typ = models.IntegerField(blank=True, null=True)  # Employee Type
    emp_fname = models.CharField(max_length=80, blank=True, null=True)  # Father's Name
    emp_married = models.CharField(max_length=1, blank=True, null=True)  # Marital Status
    emp_duty_loc = models.IntegerField(blank=True, null=True)  # Duty Location
    emp_dob = models.DateField(blank=True, null=True)  # Date of Birth
    emp_gender = models.CharField(max_length=1, blank=True, null=True)  # Gender
    emp_saltyp = models.IntegerField(blank=True, null=True)  # Salary Type
    emp_bank = models.IntegerField(blank=True, null=True)  # Bank ID
    emp_bank_acc = models.CharField(max_length=20, blank=True, null=True)  # Bank Account
    emp_cont_person = models.CharField(max_length=100, blank=True, null=True)  # Emergency Contact Person
    emp_cont_person_cell = models.CharField(max_length=20, blank=True, null=True)  # Emergency Contact Cell
    emp_leaving_dt = models.DateField(blank=True, null=True)  # Leaving Date
    emp_pay_mode = models.CharField(max_length=1, blank=True, null=True)  # Payment Mode
    emp_pay_subgrp = models.IntegerField(blank=True, null=True)  # Pay Subgroup
    emp_exp_dt = models.DateField(blank=True, null=True)  # Experience Date
    emp_mgr = models.IntegerField(blank=True, null=True)  # Manager ID (Foreign Key if applicable)
    emp_att_flg = models.CharField(max_length=1, blank=True, null=True)  # Attendance Flag
    emp_repatriat_dt = models.DateField(blank=True, null=True)  # Repatriation Date
    emp_personal_email = models.EmailField(max_length=100, blank=True, null=True)  # Personal Email
    emp_postedby = models.IntegerField(blank=True, null=True)  # Posted By (User ID)
    emp_authby = models.IntegerField(blank=True, null=True)  # Authorized By (User ID)
    emp_quota = models.IntegerField(blank=True, null=True)  # Employee Quota
    emp_pec_reg = models.CharField(max_length=15, blank=True, null=True)  # PEC Registration
    emp_qualification = models.CharField(max_length=80, blank=True, null=True)  # Qualification
    emp_institute = models.CharField(max_length=300, blank=True, null=True)  # Institute
    emp_yr_graduate = models.DateField(blank=True, null=True)  # Year of Graduation
    emp_blood = models.CharField(max_length=5, blank=True, null=True)  # Blood Group
    emp_domicile = models.CharField(max_length=60, blank=True, null=True)  # Domicile
    emp_nxt_kin = models.CharField(max_length=80, blank=True, null=True)  # Next of Kin
    emp_exch_no = models.CharField(max_length=15, blank=True, null=True)  # Exchange Number
    emp_exch_dt = models.DateField(blank=True, null=True)  # Exchange Date
    emp_eobi_no = models.CharField(max_length=12, blank=True, null=True)  # EOBI Number
    emp_waiver_bill = models.IntegerField(blank=True, null=True)  # Waiver Bill
    emp_week_days = models.IntegerField(blank=True, null=True)  # Work Week Days
    zone_id = models.IntegerField(blank=True, null=True)  # Zone ID

    class Meta:
        managed = False
        db_table = 'emp_backup_cnic'


class EmpBehaviour(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    m_id = models.IntegerField()  # Foreign Key reference if applicable
    description = models.CharField(max_length=200, blank=True, null=True)  # Description field
    numbers = models.IntegerField(blank=True, null=True)  # Numeric field

    class Meta:
        managed = False
        db_table = 'emp_behaviour'


class EmpBkp(models.Model):
    emp_no = models.IntegerField(primary_key=True)  # Employee Number (PK)
    emp_name = models.CharField(max_length=80)  # Employee Name
    emp_cnic = models.CharField(max_length=15, blank=True, null=True)  # CNIC (Optional)
    emp_deptt = models.IntegerField()  # Department ID (FK Reference if applicable)
    emp_join_dt = models.DateField(blank=True, null=True)  # Joining Date
    emp_job = models.IntegerField()  # Job Type ID (FK Reference if applicable)
    emp_grade = models.IntegerField()  # Grade ID
    emp_address1 = models.CharField(max_length=200, blank=True, null=True)  # Address Line 1
    emp_address2 = models.CharField(max_length=500, blank=True, null=True)  # Address Line 2
    emp_cell1 = models.CharField(max_length=20, blank=True, null=True)  # Primary Cell Number
    emp_cell2 = models.CharField(max_length=20, blank=True, null=True)  # Secondary Cell Number
    emp_email = models.EmailField(max_length=100, blank=True, null=True)  # Official Email
    emp_flg = models.CharField(max_length=1)  # Status Flag (Active/Inactive)
    emp_typ = models.IntegerField(blank=True, null=True)  # Employee Type
    emp_fname = models.CharField(max_length=80, blank=True, null=True)  # Father's Name
    emp_married = models.CharField(max_length=1, blank=True, null=True)  # Marital Status
    emp_duty_loc = models.IntegerField(blank=True, null=True)  # Duty Location
    emp_dob = models.DateField(blank=True, null=True)  # Date of Birth
    emp_gender = models.CharField(max_length=1, blank=True, null=True)  # Gender (M/F)
    emp_saltyp = models.IntegerField(blank=True, null=True)  # Salary Type
    emp_bank = models.IntegerField(blank=True, null=True)  # Bank ID
    emp_bank_acc = models.CharField(max_length=20, blank=True, null=True)  # Bank Account Number
    emp_cont_person = models.CharField(max_length=100, blank=True, null=True)  # Emergency Contact Person
    emp_cont_person_cell = models.CharField(max_length=20, blank=True, null=True)  # Emergency Contact Number
    emp_leaving_dt = models.DateField(blank=True, null=True)  # Leaving Date
    emp_pay_mode = models.CharField(max_length=1, blank=True, null=True)  # Payment Mode
    emp_pay_subgrp = models.IntegerField(blank=True, null=True)  # Payment Subgroup
    emp_exp_dt = models.DateField(blank=True, null=True)  # Contract Expiry Date
    emp_mgr = models.IntegerField(blank=True, null=True)  # Manager ID
    emp_att_flg = models.CharField(max_length=1, blank=True, null=True)  # Attendance Flag
    emp_repatriat_dt = models.DateField(blank=True, null=True)  # Repatriation Date
    emp_personal_email = models.EmailField(max_length=100, blank=True, null=True)  # Personal Email
    emp_postedby = models.IntegerField(blank=True, null=True)  # Posted By (User ID)
    emp_authby = models.IntegerField(blank=True, null=True)  # Authorized By (User ID)
    emp_quota = models.IntegerField(blank=True, null=True)  # Employee Quota
    emp_pec_reg = models.CharField(max_length=15, blank=True, null=True)  # PEC Registration No.
    emp_qualification = models.CharField(max_length=80, blank=True, null=True)  # Qualification
    emp_institute = models.CharField(max_length=300, blank=True, null=True)  # Institute Name
    emp_yr_graduate = models.DateField(blank=True, null=True)  # Graduation Year
    emp_blood = models.CharField(max_length=5, blank=True, null=True)  # Blood Group
    emp_domicile = models.CharField(max_length=60, blank=True, null=True)  # Domicile
    emp_nxt_kin = models.CharField(max_length=80, blank=True, null=True)  # Next of Kin
    emp_exch_no = models.CharField(max_length=15, blank=True, null=True)  # Exchange No.
    emp_exch_dt = models.DateField(blank=True, null=True)  # Exchange Date
    emp_eobi_no = models.CharField(max_length=12, blank=True, null=True)  # EOBI Number
    emp_waiver_bill = models.IntegerField(blank=True, null=True)  # Waiver Bill
    emp_week_days = models.IntegerField(blank=True, null=True)  # Working Days

    class Meta:
        managed = False
        db_table = 'emp_bkp'


class EmpBkp07102024(models.Model):
    emp_no = models.IntegerField(primary_key=True)  # Employee Number (Primary Key)
    emp_name = models.CharField(max_length=80)  # Employee Name (Required)
    emp_cnic = models.CharField(max_length=15, blank=True, null=True)  # CNIC
    emp_deptt = models.IntegerField()  # Department ID
    emp_join_dt = models.DateField(blank=True, null=True)  # Joining Date
    emp_job = models.IntegerField()  # Job Type ID
    emp_grade = models.IntegerField()  # Grade ID
    emp_address1 = models.CharField(max_length=200, blank=True, null=True)  # Address Line 1
    emp_address2 = models.CharField(max_length=500, blank=True, null=True)  # Address Line 2
    emp_cell1 = models.CharField(max_length=20, blank=True, null=True)  # Primary Contact
    emp_cell2 = models.CharField(max_length=20, blank=True, null=True)  # Secondary Contact
    emp_email = models.EmailField(max_length=100, blank=True, null=True)  # Official Email
    emp_flg = models.CharField(max_length=1)  # Status Flag (Active/Inactive)
    emp_typ = models.IntegerField(blank=True, null=True)  # Employee Type
    emp_fname = models.CharField(max_length=80, blank=True, null=True)  # Father's Name
    emp_married = models.CharField(max_length=1, blank=True, null=True)  # Marital Status
    emp_duty_loc = models.IntegerField(blank=True, null=True)  # Duty Location
    emp_dob = models.DateField(blank=True, null=True)  # Date of Birth
    emp_gender = models.CharField(max_length=1, blank=True, null=True)  # Gender (M/F)
    emp_saltyp = models.IntegerField(blank=True, null=True)  # Salary Type
    emp_bank = models.IntegerField(blank=True, null=True)  # Bank ID
    emp_bank_acc = models.CharField(max_length=100, blank=True, null=True)  # Bank Account
    emp_cont_person = models.CharField(max_length=100, blank=True, null=True)  # Emergency Contact Name
    emp_cont_person_cell = models.CharField(max_length=20, blank=True, null=True)  # Emergency Contact Number
    emp_leaving_dt = models.DateField(blank=True, null=True)  # Leaving Date
    emp_pay_mode = models.CharField(max_length=1, blank=True, null=True)  # Payment Mode
    emp_pay_subgrp = models.IntegerField(blank=True, null=True)  # Payment Subgroup
    emp_exp_dt = models.DateField(blank=True, null=True)  # Contract Expiry Date
    emp_mgr = models.IntegerField(blank=True, null=True)  # Manager ID
    emp_att_flg = models.CharField(max_length=1, blank=True, null=True)  # Attendance Flag
    emp_repatriat_dt = models.DateField(blank=True, null=True)  # Repatriation Date
    emp_personal_email = models.EmailField(max_length=100, blank=True, null=True)  # Personal Email
    emp_postedby = models.IntegerField(blank=True, null=True)  # Posted By (User ID)
    emp_authby = models.IntegerField(blank=True, null=True)  # Authorized By (User ID)
    emp_quota = models.IntegerField(blank=True, null=True)  # Employee Quota
    emp_pec_reg = models.CharField(max_length=15, blank=True, null=True)  # PEC Registration No.
    emp_qualification = models.CharField(max_length=80, blank=True, null=True)  # Qualification
    emp_institute = models.CharField(max_length=300, blank=True, null=True)  # Institute Name
    emp_yr_graduate = models.DateField(blank=True, null=True)  # Graduation Year
    emp_blood = models.CharField(max_length=5, blank=True, null=True)  # Blood Group
    emp_domicile = models.CharField(max_length=60, blank=True, null=True)  # Domicile
    emp_nxt_kin = models.CharField(max_length=80, blank=True, null=True)  # Next of Kin
    emp_exch_no = models.CharField(max_length=15, blank=True, null=True)  # Exchange No.
    emp_exch_dt = models.DateField(blank=True, null=True)  # Exchange Date
    emp_eobi_no = models.CharField(max_length=12, blank=True, null=True)  # EOBI Number
    emp_waiver_bill = models.IntegerField(blank=True, null=True)  # Waiver Bill
    emp_week_days = models.IntegerField(blank=True, null=True)  # Working Days
    zone_id = models.IntegerField(blank=True, null=True)  # Zone ID

    class Meta:
        managed = False
        db_table = 'emp_bkp_07102024'


class EmpBkp31102024(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee Number (Foreign Key Reference to Employee)
    emp_pay_allw = models.IntegerField()  # Allowance Type ID
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule ID
    emp_pay_acc = models.IntegerField()  # Payroll Account Number
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount
    emp_pay_postedby = models.IntegerField()  # Posted By (User ID)
    emp_pay_authby = models.IntegerField()  # Authorized By (User ID)

    class Meta:
        managed = False
        db_table = 'emp_bkp_31102024'


class EmpBkpFinal(models.Model):
    emp_no = models.IntegerField(primary_key=True)  # Employee Number (Primary Key)
    emp_name = models.CharField(max_length=80)  # Employee Name
    emp_cnic = models.CharField(max_length=15, blank=True, null=True)  # CNIC (Optional)
    emp_deptt = models.IntegerField()  # Department ID (Foreign Key can be added if needed)
    emp_join_dt = models.DateField(blank=True, null=True)  # Joining Date
    emp_job = models.IntegerField()  # Job ID
    emp_grade = models.IntegerField()  # Grade ID
    emp_address1 = models.CharField(max_length=200, blank=True, null=True)  # Address 1
    emp_address2 = models.CharField(max_length=500, blank=True, null=True)  # Address 2
    emp_cell1 = models.CharField(max_length=20, blank=True, null=True)  # Cell 1
    emp_cell2 = models.CharField(max_length=20, blank=True, null=True)  # Cell 2
    emp_email = models.EmailField(max_length=100, blank=True, null=True)  # Email
    emp_flg = models.CharField(max_length=1)  # Flag (Status Indicator)
    emp_typ = models.IntegerField(blank=True, null=True)  # Employee Type
    emp_fname = models.CharField(max_length=80, blank=True, null=True)  # Father's Name
    emp_married = models.CharField(max_length=1, blank=True, null=True)  # Marital Status
    emp_duty_loc = models.IntegerField(blank=True, null=True)  # Duty Location
    emp_dob = models.DateField(blank=True, null=True)  # Date of Birth
    emp_gender = models.CharField(max_length=1, blank=True, null=True)  # Gender
    emp_saltyp = models.IntegerField(blank=True, null=True)  # Salary Type
    emp_bank = models.IntegerField(blank=True, null=True)  # Bank ID
    emp_bank_acc = models.CharField(max_length=100, blank=True, null=True)  # Bank Account
    emp_cont_person = models.CharField(max_length=100, blank=True, null=True)  # Emergency Contact Person
    emp_cont_person_cell = models.CharField(max_length=20, blank=True, null=True)  # Contact Person Cell
    emp_leaving_dt = models.DateField(blank=True, null=True)  # Leaving Date
    emp_pay_mode = models.CharField(max_length=1, blank=True, null=True)  # Payment Mode
    emp_pay_subgrp = models.IntegerField(blank=True, null=True)  # Pay Sub Group
    emp_exp_dt = models.DateField(blank=True, null=True)  # Experience Date
    emp_mgr = models.IntegerField(blank=True, null=True)  # Manager ID
    emp_att_flg = models.CharField(max_length=1, blank=True, null=True)  # Attendance Flag
    emp_repatriat_dt = models.DateField(blank=True, null=True)  # Repatriation Date
    emp_personal_email = models.EmailField(max_length=100, blank=True, null=True)  # Personal Email
    emp_postedby = models.IntegerField(blank=True, null=True)  # Posted By User ID
    emp_authby = models.IntegerField(blank=True, null=True)  # Authorized By User ID
    emp_quota = models.IntegerField(blank=True, null=True)  # Quota Type
    emp_pec_reg = models.CharField(max_length=15, blank=True, null=True)  # PEC Registration
    emp_qualification = models.CharField(max_length=80, blank=True, null=True)  # Qualification
    emp_institute = models.CharField(max_length=300, blank=True, null=True)  # Institute Name
    emp_yr_graduate = models.DateField(blank=True, null=True)  # Graduation Year
    emp_blood = models.CharField(max_length=5, blank=True, null=True)  # Blood Group
    emp_domicile = models.CharField(max_length=60, blank=True, null=True)  # Domicile
    emp_nxt_kin = models.CharField(max_length=80, blank=True, null=True)  # Next of Kin
    emp_exch_no = models.CharField(max_length=15, blank=True, null=True)  # Exchange Number
    emp_exch_dt = models.DateField(blank=True, null=True)  # Exchange Date
    emp_eobi_no = models.CharField(max_length=12, blank=True, null=True)  # EOBI Number
    emp_waiver_bill = models.IntegerField(blank=True, null=True)  # Waiver Bill
    emp_week_days = models.IntegerField(blank=True, null=True)  # Working Days
    zone_id = models.IntegerField(blank=True, null=True)  # Zone ID

    class Meta:
        managed = False
        db_table = 'emp_ev'


class EmpGrd(models.Model):
    emp_grd_id = models.CharField(max_length=10, primary_key=True)  # Assuming ID is a short code (e.g., "G1", "G2")
    emp_grd_desc = models.CharField(max_length=255)  # Grade Description
    emp_grd_minsal = models.DecimalField(max_digits=12, decimal_places=2)  # Minimum Salary
    emp_grd_maxsal = models.DecimalField(max_digits=12, decimal_places=2)  # Maximum Salary

    class Meta:
        managed = False
        db_table = 'emp_grd'


class EmpHeadoffice(models.Model):
    emp_no = models.AutoField(primary_key=True)  # Auto-increment Employee Number
    emp_name = models.CharField(max_length=80)
    emp_cnic = models.CharField(max_length=15, unique=True, null=True, blank=True)  # CNIC should be unique
    emp_deptt = models.IntegerField()  # Department ID
    emp_join_dt = models.DateField(null=True, blank=True)
    emp_job = models.IntegerField()
    emp_grade = models.IntegerField()
    emp_address1 = models.CharField(max_length=200, null=True, blank=True)
    emp_address2 = models.CharField(max_length=500, null=True, blank=True)
    emp_cell1 = models.CharField(max_length=20, null=True, blank=True)
    emp_cell2 = models.CharField(max_length=20, null=True, blank=True)
    emp_email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    emp_flg = models.CharField(max_length=1)  # Status flag (Active/Inactive)
    emp_typ = models.IntegerField(null=True, blank=True)
    emp_fname = models.CharField(max_length=80, null=True, blank=True)  # Father's Name
    emp_married = models.CharField(max_length=1, null=True, blank=True)  # 'Y' or 'N'
    emp_duty_loc = models.IntegerField(null=True, blank=True)
    emp_dob = models.DateField(null=True, blank=True)
    emp_gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    emp_saltyp = models.IntegerField(null=True, blank=True)
    emp_bank = models.IntegerField(null=True, blank=True)
    emp_bank_acc = models.CharField(max_length=100, null=True, blank=True)
    emp_cont_person = models.CharField(max_length=100, null=True, blank=True)
    emp_cont_person_cell = models.CharField(max_length=20, null=True, blank=True)
    emp_leaving_dt = models.DateField(null=True, blank=True)
    emp_pay_mode = models.CharField(max_length=1, null=True, blank=True)
    emp_pay_subgrp = models.IntegerField(null=True, blank=True)
    emp_exp_dt = models.DateField(null=True, blank=True)
    emp_mgr = models.IntegerField(null=True, blank=True)  # Manager's EMP_NO
    emp_att_flg = models.CharField(max_length=1, null=True, blank=True)  # Attendance flag
    emp_repatriat_dt = models.DateField(null=True, blank=True)
    emp_personal_email = models.EmailField(max_length=100, null=True, blank=True)
    emp_postedby = models.IntegerField(null=True, blank=True)
    emp_authby = models.IntegerField(null=True, blank=True)
    emp_quota = models.IntegerField(null=True, blank=True)
    emp_pec_reg = models.CharField(max_length=15, null=True, blank=True)  # PEC Registration
    emp_qualification = models.CharField(max_length=80, null=True, blank=True)
    emp_institute = models.CharField(max_length=300, null=True, blank=True)
    emp_yr_graduate = models.DateField(null=True, blank=True)
    emp_blood = models.CharField(max_length=5, null=True, blank=True)
    emp_domicile = models.CharField(max_length=60, null=True, blank=True)
    emp_nxt_kin = models.CharField(max_length=80, null=True, blank=True)  # Next of Kin
    emp_exch_no = models.CharField(max_length=15, null=True, blank=True)
    emp_exch_dt = models.DateField(null=True, blank=True)
    emp_eobi_no = models.CharField(max_length=12, null=True, blank=True)
    emp_waiver_bill = models.IntegerField(null=True, blank=True)
    emp_week_days = models.IntegerField(null=True, blank=True)
    zone_id = models.IntegerField(null=True, blank=True)  # Zoning Information

    class Meta:
        managed = False
        db_table = 'emp_headoffice'


class EmpLeav(models.Model):
    emp_leav_dt = models.DateField(null=True, blank=True)  # Leave Application Date
    emp_leav_emp = models.IntegerField()  # Employee ID (ForeignKey can be added)
    emp_leav_from = models.DateField()  # Leave Start Date
    emp_leav_to = models.DateField()  # Leave End Date
    emp_leav_typ = models.IntegerField()  # Leave Type ID
    emp_leav_desc = models.CharField(max_length=300, null=True, blank=True)  # Leave Description
    emp_leav_flg = models.CharField(max_length=1, null=True, blank=True)  # Leave Status Flag (e.g., 'A' for Approved)
    emp_leav_authby = models.IntegerField(null=True, blank=True)  # Authorized By (EMP_NO)
    emp_leav_auth_dt = models.DateField(null=True, blank=True)  # Leave Authorization Date
    emp_leav_remarks = models.CharField(max_length=300, null=True, blank=True)  # Remarks

    class Meta:
        managed = False
        db_table = 'emp_leav'


class EmpLeavBkp(models.Model):
    emp_leav_dt = models.DateField(null=True, blank=True)  
    emp_leav_emp = models.IntegerField()  
    emp_leav_from = models.DateField()  
    emp_leav_to = models.DateField()  
    emp_leav_typ = models.IntegerField()  
    emp_leav_desc = models.CharField(max_length=300, null=True, blank=True)  
    emp_leav_flg = models.CharField(max_length=1, null=True, blank=True)  
    emp_leav_authby = models.IntegerField(null=True, blank=True)  
    emp_leav_auth_dt = models.DateField(null=True, blank=True)  
    emp_leav_remarks = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'emp_leav_bkp'


class EmpNoGrp(models.Model):
    emp_no_grp_id = models.IntegerField(primary_key=True)  # Assuming it's a primary key
    emp_no_grp_code = models.CharField(max_length=2, unique=True)  
    emp_no_grp_desc = models.CharField(max_length=80) 

    class Meta:
        managed = False
        db_table = 'emp_no_grp'


class EmpNoGrp1(models.Model):
    emp_no_grp_id = models.IntegerField(primary_key=True)  # Assuming it's the primary key
    emp_no_grp_code = models.CharField(max_length=2, unique=True)
    emp_no_grp_desc = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = 'emp_no_grp1'


class EmpNoGrpBkp(models.Model):
    emp_no_grp_id = models.PositiveSmallIntegerField(primary_key=True)  # NUMBER(2) fits PositiveSmallIntegerField
    emp_no_grp_code = models.CharField(max_length=2, unique=True)  # VARCHAR2(2 BYTE)
    emp_no_grp_desc = models.CharField(max_length=80)  # VARCHAR2(80 BYTE)

    class Meta:
        managed = False
        db_table = 'emp_no_grp_bkp'


class EmpPay(models.Model):
    emp_pay_emp = models.PositiveIntegerField(primary_key=True)  # NUMBER(7)
    emp_pay_allw = models.PositiveIntegerField()  # NUMBER(5)
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # NUMBER(12,2)
    emp_pay_allwrule = models.PositiveSmallIntegerField()  # NUMBER(1)
    emp_pay_acc = models.PositiveIntegerField()  # NUMBER(9)
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # NUMBER(10,2)
    emp_pay_postedby = models.PositiveIntegerField()  # NUMBER(7)
    emp_pay_authby = models.PositiveIntegerField()  # NUMBER(7)

    class Meta:
        managed = False
        db_table = 'emp_pay'


class EmpPay19042023(models.Model):
    emp_pay_emp = models.IntegerField()  # NUMBER(7)
    emp_pay_allw = models.IntegerField()  # NUMBER(5)
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # NUMBER(12,2)
    emp_pay_allwrule = models.IntegerField()  # NUMBER(1)
    emp_pay_acc = models.IntegerField()  # NUMBER(9)
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # NUMBER(10,2)
    emp_pay_postedby = models.IntegerField()  # NUMBER(7)
    emp_pay_authby = models.IntegerField()  # NUMBER(7)

    class Meta:
        managed = False
        db_table = 'emp_pay19042023'


class EmpPay10052023(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Allowance Type (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted by (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized by (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_10052023'


class EmpPay17032023(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Allowance Type (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted by (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized by (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_17032023'


class EmpPayBkp01282024(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Allowance Type (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted by (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized by (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_bkp01282024'


class EmpPayBkp21112023(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Allowance Type (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted by (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized by (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_bkp21112023'


class EmpPayBkp20032024(models.Model):
    emp_pay_emp = models.IntegerField()  
    emp_pay_allw = models.IntegerField()  
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  
    emp_pay_allwrule = models.IntegerField()  
    emp_pay_acc = models.IntegerField()  
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  
    emp_pay_postedby = models.IntegerField()  
    emp_pay_authby = models.IntegerField()  

    class Meta:
        managed = False
        db_table = 'emp_pay_bkp_20032024'


class EmpPayBkp231224(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee Number (7 digits)
    emp_pay_allw = models.IntegerField()  # Allowance Code (5 digits)
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (12,2)
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (1 digit)
    emp_pay_acc = models.IntegerField()  # Account Number (9 digits)
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (10,2)
    emp_pay_postedby = models.IntegerField()  # Posted By (7 digits)
    emp_pay_authby = models.IntegerField()  # Authorized By (7 digits)

    class Meta:
        managed = False
        db_table = 'emp_pay_bkp_231224'


class EmpPayBkp26072024(models.Model):
    emp_pay_emp = models.IntegerField()  # Example: Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Example: Allowance (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted By (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized By (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_bkp_26072024'


class EmpPayBkp261024(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Allowance (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted By (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized By (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_bkp_261024'


class EmpPayDed(models.Model):
    emp_pay_emp = models.IntegerField()  # Employee ID (NUMBER(7))
    emp_pay_allw = models.IntegerField()  # Allowance (NUMBER(5))
    emp_pay_allwrate = models.DecimalField(max_digits=12, decimal_places=2)  # Allowance Rate (NUMBER(12,2))
    emp_pay_allwrule = models.IntegerField()  # Allowance Rule (NUMBER(1))
    emp_pay_acc = models.IntegerField()  # Account Number (NUMBER(9))
    emp_pay_allwamt = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance Amount (NUMBER(10,2))
    emp_pay_postedby = models.IntegerField()  # Posted By (NUMBER(7))
    emp_pay_authby = models.IntegerField()  # Authorized By (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'emp_pay_ded'


class EmpPerformance(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER)
    m_id = models.IntegerField()  # M_ID (NUMBER)
    description = models.CharField(max_length=200)  # DESCRIPTION (VARCHAR2(200 BYTE))
    numbers = models.IntegerField()  # NUMBERS (NUMBER)

    class Meta:
        managed = False
        db_table = 'emp_performance'


class EmpQuota(models.Model):
    emp_quota_id = models.IntegerField(primary_key=True)  # EMP_QUOTA_ID (NUMBER(3))
    emp_quota_desc = models.CharField(max_length=80)  # EMP_QUOTA_DESC (VARCHAR2(80 BYTE))

    class Meta:
        managed = False
        db_table = 'emp_quota'


class EmpReqauth(models.Model):
    emp_authreq_typ = models.IntegerField()  # EMP_AUTHREQ_TYP (NUMBER(3))
    emp_authreq_authby = models.IntegerField()  # EMP_AUTHREQ_AUTHBY (NUMBER(7))
    emp_authreq_authby_flg = models.CharField(max_length=1)  # EMP_AUTHREQ_AUTHBY_FLG (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'emp_reqauth'


class EmpSaltyp(models.Model):
    emp_saltyp_id = models.IntegerField(primary_key=True)  # EMP_SALTYP_ID (NUMBER) - Not Null
    emp_saltyp_desc = models.CharField(max_length=80)  # EMP_SALTYP_DESC (VARCHAR2(80 BYTE)) - Not Null
    emp_saltyp_freq = models.IntegerField(null=True, blank=True)  # EMP_SALTYP_FREQ (NUMBER), optional

    class Meta:
        managed = False
        db_table = 'emp_saltyp'


class EmpScores(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER)
    score_range = models.CharField(max_length=50)  # SCORE_RANGE (VARCHAR2(50 BYTE))
    rating = models.CharField(max_length=100)  # RATING (VARCHAR2(100 BYTE))

    class Meta:
        managed = False
        db_table = 'emp_scores'


class EmpTransfer(models.Model):
    transfer_id = models.IntegerField(primary_key=True)  # TRANSFER_ID (NUMBER)
    emp_id = models.IntegerField()  # EMP_ID (NUMBER)
    transfer_date = models.DateField()  # TRANSFER_DATE (DATE)
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    transfer_from = models.CharField(max_length=50)  # TRANSFER_FROM (VARCHAR2(50 BYTE))
    transfer_to = models.CharField(max_length=50)  # TRANSFER_TO (VARCHAR2(50 BYTE))

    class Meta:
        managed = False
        db_table = 'emp_transfer'


class EmpTyp(models.Model):
    emp_typ_id = models.IntegerField()  # EMP_TYP_ID (NUMBER(3)) - Not Null
    emp_typ_desc = models.CharField(max_length=80)  # EMP_TYP_DESC (VARCHAR2(80 BYTE))
    emp_typ_wage = models.CharField(max_length=1)  # EMP_TYP_WAGE (CHAR(1 BYTE))
    emp_typ_exp_months = models.IntegerField(null=True, blank=True)  # EMP_TYP_EXP_MONTHS (NUMBER(3)), optional

    class Meta:
        managed = False
        db_table = 'emp_typ'


class EmpTyp1(models.Model):
    emp_typ_id = models.IntegerField()  # EMP_TYP_ID (NUMBER(3)) - Not Null
    emp_typ_desc = models.CharField(max_length=80)  # EMP_TYP_DESC (VARCHAR2(80 BYTE))
    emp_typ_wage = models.CharField(max_length=1)  # EMP_TYP_WAGE (CHAR(1 BYTE))
    emp_typ_exp_months = models.IntegerField(null=True, blank=True)  # EMP_TYP_EXP_MONTHS (NUMBER(3)), optional

    class Meta:
        managed = False
        db_table = 'emp_typ1'


class EmpTypBkp(models.Model):
    emp_typ_id = models.IntegerField()  # EMP_TYP_ID (NUMBER(3)) - Not Null
    emp_typ_desc = models.CharField(max_length=80)  # EMP_TYP_DESC (VARCHAR2(80 BYTE))
    emp_typ_wage = models.CharField(max_length=1)  # EMP_TYP_WAGE (CHAR(1 BYTE))
    emp_typ_exp_months = models.IntegerField(null=True, blank=True)  # EMP_TYP_EXP_MONTHS (NUMBER(3))

    class Meta:
        managed = False
        db_table = 'emp_typ_bkp'


class FaCategory(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER) - Not Null
    name = models.CharField(max_length=50)  # NAME (VARCHAR2(50 BYTE))

    class Meta:
        managed = False
        db_table = 'fa_category'


class FaSubCategory(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(4)) - Not Null
    sub_cat = models.CharField(max_length=100)  # SUB_CAT (VARCHAR2(100 BYTE)) - Not Null
    cat_id = models.IntegerField()  # CAT_ID (NUMBER(4)) - Not Null

    class Meta:
        managed = False
        db_table = 'fa_sub_category'


class FaTransaction(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER) - Not Null
    sub_category = models.IntegerField()  # SUB_CATEGORY (NUMBER) - Not Null
    item_name = models.CharField(max_length=150, null=True, blank=True)  # ITEM_NAME (VARCHAR2(150 BYTE))
    items_description = models.CharField(max_length=150, null=True, blank=True)  # ITEMS_DESCRIPTION (VARCHAR2(150 BYTE))
    registration_no = models.CharField(max_length=50, null=True, blank=True)  # REGISTRATION_NO (VARCHAR2(50 BYTE))
    engine_no = models.CharField(max_length=50, null=True, blank=True)  # ENGINE_NO (VARCHAR2(50 BYTE))
    chassis_no = models.CharField(max_length=50, null=True, blank=True)  # CHASSIS_NO (VARCHAR2(50 BYTE))
    location = models.IntegerField(null=True, blank=True)  # LOCATION (NUMBER)
    department = models.IntegerField(null=True, blank=True)  # DEPARTMENT (NUMBER)
    purchase_year = models.CharField(max_length=10, null=True, blank=True)  # PURCHASE_YEAR (VARCHAR2(10 BYTE))
    purchased_by = models.CharField(max_length=100, null=True, blank=True)  # PURCAHSED_BY (VARCHAR2(100 BYTE))
    supplier_name = models.CharField(max_length=150, null=True, blank=True)  # SUPPLIER_NAME (VARCHAR2(150 BYTE))
    date_acquisition = models.DateField(null=True, blank=True)  # DATE_ACQUISITION (DATE)
    grn_no = models.CharField(max_length=50, null=True, blank=True)  # GRN_NO (VARCHAR2(50 BYTE))
    grn_date = models.DateField(null=True, blank=True)  # GRN_DATE (DATE)
    purchase_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # PURCHASE_VALUE (NUMBER)
    quantity = models.IntegerField(null=True, blank=True)  # QUANTITY (NUMBER)
    condition = models.CharField(max_length=50, null=True, blank=True)  # CONDITION (VARCHAR2(50 BYTE))
    remarks = models.TextField(null=True, blank=True)  # REMARKS (VARCHAR2(2000 BYTE))
    serial_no = models.CharField(max_length=100, null=True, blank=True)  # SERIAL_NO (VARCHAR2(100 BYTE))
    sub_location = models.CharField(max_length=200, null=True, blank=True)  # SUB_LOCATION (VARCHAR2(200 BYTE))

    class Meta:
        managed = False
        db_table = 'fa_transaction'


class FinPaytyp(models.Model):
    fin_paytyp_id = models.IntegerField(primary_key=True)  # FIN_PAYTYP_ID (NUMBER(3)) - Not Null
    fin_paytyp_desc = models.CharField(max_length=80)  # FIN_PAYTYP_DESC (VARCHAR2(80 BYTE))

    class Meta:
        managed = False
        db_table = 'fin_paytyp'


class Hodays1(models.Model):
    holiday_id = models.IntegerField(primary_key=True)  # HOLIDAY_ID (NUMBER(6))
    holiday_dt = models.DateField()  # HOLIDAY_DT (DATE)
    holiday_typ = models.CharField(max_length=1)  # HOLIDAY_TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'hodays1'


class Holiday(models.Model):
    holiday_id = models.IntegerField(primary_key=True)  # HOLIDAY_ID (NUMBER(6))
    holiday_dt = models.DateField()  # HOLIDAY_DT (DATE)
    holiday_typ = models.CharField(max_length=1)  # HOLIDAY_TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'holiday'
        unique_together = (('holiday_dt', 'holiday_dt'),)


class IncDec24(models.Model):
    emp_no = models.IntegerField()  # EMP_NO (NUMBER)
    bas_sal = models.DecimalField(max_digits=12, decimal_places=2)  # BAS_SAL (NUMBER)
    h_rent = models.DecimalField(max_digits=12, decimal_places=2)  # H_RENT (NUMBER)
    utility = models.DecimalField(max_digits=12, decimal_places=2)  # UTILITY (NUMBER)

    class Meta:
        managed = False
        db_table = 'inc_dec_24'


class Job(models.Model):
    job_id = models.IntegerField(primary_key=True)  # JOB_ID (NUMBER(3)) - Not Null
    job_desc = models.CharField(max_length=80)  # JOB_DESC (VARCHAR2(80 BYTE))

    class Meta:
        managed = False
        db_table = 'job'


class JobBkp(models.Model):
    job_id = models.IntegerField(primary_key=True)  # JOB_ID (NUMBER(3)) - Not Null
    job_desc = models.CharField(max_length=80)  # JOB_DESC (VARCHAR2(80 BYTE))

    class Meta:
        managed = False
        db_table = 'job_bkp'


class JobHis(models.Model):
    job_his_emp = models.IntegerField()  # JOB_HIS_EMP (NUMBER(7)) - Not Null
    job_his_job = models.IntegerField()  # JOB_HIS_JOB (NUMBER(3)) - Not Null
    job_his_start_dt = models.DateField(null=True, blank=True)  # JOB_HIS_START_DT (DATE)
    job_his_end_dt = models.DateField(null=True, blank=True)  # JOB_HIS_END_DT (DATE)
    job_his_deptt = models.IntegerField(null=True, blank=True)  # JOB_HIS_DEPTT (NUMBER(3))

    class Meta:
        managed = False
        db_table = 'job_his'


class LeavTyp(models.Model):
    leav_typid = models.IntegerField(primary_key=True)  # LEAV_TYPID (NUMBER(3))
    leav_typdesc = models.CharField(max_length=50)  # LEAV_TYPDESC (VARCHAR2(50 BYTE))
    leav_type_limit = models.IntegerField()  # LEAV_TYPE_LIMIT (NUMBER(6))

    class Meta:
        managed = False
        db_table = 'leav_typ'


class LoanAllotment(models.Model):
    loan_id = models.IntegerField(primary_key=True)  # LOAN_ID (NUMBER)
    emp_id = models.IntegerField()  # EMP_ID (NUMBER)
    total_loan = models.DecimalField(max_digits=12, decimal_places=2)  # TOTAL_LOAN (NUMBER)
    start_date = models.DateField()  # START_DATE (DATE)
    monthly_plan = models.CharField(max_length=50)  # MONTHLY_PLAN (VARCHAR2(50 BYTE))
    total_installment = models.IntegerField()  # TOTAL_INSTALLMENT (NUMBER)
    end_date = models.DateField()  # END_DATE (DATE)
    loan_status = models.CharField(max_length=1)  # LOAN_STATUS (CHAR(1 BYTE))
    loan_allotment = models.CharField(max_length=50)  # LOAN_ALLOTMENT (VARCHAR2(50 BYTE))

    class Meta:
        managed = False
        db_table = 'loan_allotment'


class LoanInstallment(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER)
    loan_id = models.IntegerField()  # LOAN_ID (NUMBER)
    installment_date = models.DateField()  # INSTALLMENT_DATE (DATE)
    monthly_pay = models.DecimalField(max_digits=12, decimal_places=2)  # MONTHLY_PAY (NUMBER)
    status = models.CharField(max_length=50)  # STATUS (VARCHAR2(50 BYTE))

    class Meta:
        managed = False
        db_table = 'loan_installment'


class Menu(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(5))
    label = models.CharField(max_length=128)  # LABEL (VARCHAR2(128 BYTE))
    icon = models.CharField(max_length=40)  # ICON (VARCHAR2(40 BYTE))
    master = models.IntegerField()  # MASTER (NUMBER(5))
    status = models.IntegerField()  # STATUS (NUMBER(1))
    value = models.CharField(max_length=128)  # VALUE (VARCHAR2(128 BYTE))
    typ = models.CharField(max_length=1)  # TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'menu'


class MenuBkp(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(5))
    label = models.CharField(max_length=128)  # LABEL (VARCHAR2(128 BYTE))
    icon = models.CharField(max_length=40)  # ICON (VARCHAR2(40 BYTE))
    master = models.IntegerField()  # MASTER (NUMBER(5))
    status = models.IntegerField()  # STATUS (NUMBER(1))
    value = models.CharField(max_length=128)  # VALUE (VARCHAR2(128 BYTE))
    typ = models.CharField(max_length=1)  # TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'menu_bkp'


class MenuBkp02052024(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(5))
    label = models.CharField(max_length=128)  # LABEL (VARCHAR2(128 BYTE))
    icon = models.CharField(max_length=40)  # ICON (VARCHAR2(40 BYTE))
    master = models.IntegerField()  # MASTER (NUMBER(5))
    status = models.IntegerField()  # STATUS (NUMBER(1))
    value = models.CharField(max_length=128)  # VALUE (VARCHAR2(128 BYTE))
    typ = models.CharField(max_length=1)  # TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'menu_bkp_02052024'


class MenuBkp10092024(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(5))
    label = models.CharField(max_length=128)  # LABEL (VARCHAR2(128 BYTE))
    icon = models.CharField(max_length=40)  # ICON (VARCHAR2(40 BYTE))
    master = models.IntegerField()  # MASTER (NUMBER(5))
    status = models.IntegerField()  # STATUS (NUMBER(1))
    value = models.CharField(max_length=128)  # VALUE (VARCHAR2(128 BYTE))
    typ = models.CharField(max_length=1)  # TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'menu_bkp_10092024'


class MenuBkp25112024(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(5))
    label = models.CharField(max_length=128)  # LABEL (VARCHAR2(128 BYTE))
    icon = models.CharField(max_length=40)  # ICON (VARCHAR2(40 BYTE))
    master = models.IntegerField()  # MASTER (NUMBER(5))
    status = models.IntegerField()  # STATUS (NUMBER(1))
    value = models.CharField(max_length=128)  # VALUE (VARCHAR2(128 BYTE))
    typ = models.CharField(max_length=1)  # TYP (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'menu_bkp_25112024'


class MenuRoles(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER(5))
    role = models.CharField(max_length=30)  # ROLE (VARCHAR2(30 BYTE))

    class Meta:
        managed = False
        db_table = 'menu_roles'


class MyappDepartment(models.Model):
    deptt_id = models.BigIntegerField(primary_key=True)  # DEPTT_ID (NUMBER(11)), with auto-increment behavior handled by database sequence
    deptt_desc = models.CharField(max_length=255)  # DEPTT_DESC (NVARCHAR2(255))

    class Meta:
        managed = False
        db_table = 'myapp_department'


class MyappEmployee(models.Model):
    emp_no = models.BigIntegerField(primary_key=True)  # EMP_NO (NUMBER(11)), NOT NULL
    emp_name = models.CharField(max_length=255)  # EMP_NAME (NVARCHAR2(255))
    emp_join_dt = models.DateField()  # EMP_JOIN_DT (DATE), NOT NULL
    emp_exp_dt = models.DateField(null=True, blank=True)  # EMP_EXP_DT (DATE), nullable
    gross_salary = models.FloatField()  # GROSS_SALARY (FLOAT(126)), NOT NULL
    emp_deptt_id = models.BigIntegerField()  # EMP_DEPTT_ID (NUMBER(11)), NOT NULL

    class Meta:
        managed = False
        db_table = 'myapp_employee'


class MyappLoanallotment(models.Model):
    loan_id = models.BigIntegerField(primary_key=True)  # LOAN_ID (NUMBER(11)), NOT NULL
    loan_amount = models.FloatField()  # LOAN_AMOUNT (FLOAT(126)), NOT NULL
    repay_duration = models.BigIntegerField()  # REPAY_DURATION (NUMBER(11)), NOT NULL
    monthly_pay = models.FloatField()  # MONTHLY_PAY (FLOAT(126)), NOT NULL
    loan_start_date = models.DateField()  # LOAN_START_DATE (DATE), NOT NULL
    loan_end_date = models.DateField()  # LOAN_END_DATE (DATE), NOT NULL
    emp_id = models.BigIntegerField()  # EMP_ID (NUMBER(11)), NOT NULL

    class Meta:
        managed = False
        db_table = 'myapp_loanallotment'


class MyappLoaninstallment(models.Model):
    installment_id = models.BigIntegerField(primary_key=True)  # INSTALLMENT_ID (NUMBER(11)), NOT NULL
    installment_date = models.DateField()  # INSTALLMENT_DATE (DATE), NOT NULL
    installment_amount = models.FloatField()  # INSTALLMENT_AMOUNT (FLOAT(126)), NOT NULL
    is_paid = models.BooleanField()  # IS_PAID (NUMBER(1)), stores boolean (True/False)
    loan_id = models.BigIntegerField()  # LOAN_ID (NUMBER(11)), NOT NULL

    class Meta:
        managed = False
        db_table = 'myapp_loaninstallment'


class OtPeriod(models.Model):
    ot_period_id = models.IntegerField(primary_key=True)  # OT_PERIOD_ID (NUMBER(4))
    ot_period_from = models.DateField()  # OT_PERIOD_FROM (DATE)
    ot_period_to = models.DateField()  # OT_PERIOD_TO (DATE)
    ot_period_flg = models.CharField(max_length=1)  # OT_PERIOD_FLG (CHAR(1 BYTE))
    ot_period_dt = models.DateField()  # OT_PERIOD_DT (DATE)
    ot_period_month = models.DateField()  # OT_PERIOD_MONTH (DATE)
    ot_period_dayscount = models.IntegerField()  # OT_PERIOD_DAYSCOUNT (NUMBER(3))
    ot_period_init_by = models.IntegerField()  # OT_PERIOD_INIT_BY (NUMBER(7))
    ot_period_init_dt = models.DateField()  # OT_PERIOD_INIT_DT (DATE)
    ot_period_approved_by = models.IntegerField()  # OT_PERIOD_APPROVED_BY (NUMBER(7))
    ot_period_approved_dt = models.DateField()  # OT_PERIOD_APPROVED_DT (DATE)
    ot_period_accepted_by = models.IntegerField()  # OT_PERIOD_ACCEPTED_BY (NUMBER(7))
    ot_period_accepted_dt = models.DateField()  # OT_PERIOD_ACCEPTED_DT (DATE)
    ot_period_auth_by = models.IntegerField()  # OT_PERIOD_AUTH_BY (NUMBER(7))
    ot_period_auth_dt = models.DateField()  # OT_PERIOD_AUTH_DT (DATE)
    ot_period_fin_by = models.IntegerField()  # OT_PERIOD_FIN_BY (NUMBER(7))
    ot_period_fin_dt = models.DateField()  # OT_PERIOD_FIN_DT (DATE)
    ot_period_run_by = models.IntegerField()  # OT_PERIOD_RUN_BY (NUMBER(7))
    ot_period_run_dt = models.DateField()  # OT_PERIOD_RUN_DT (DATE)
    ot_period_yr = models.CharField(max_length=7)  # OT_PERIOD_YR (VARCHAR2(7 BYTE))

    class Meta:
        managed = False
        db_table = 'ot_period'


class Overtime(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER)
    emp_id = models.IntegerField()  # EMP_ID (NUMBER)
    overtime_date = models.DateField()  # OVERTIME_DATE (DATE)
    overtime_type = models.CharField(max_length=100)  # OVERTIME_TYPE (VARCHAR2(100 BYTE))
    posted_by = models.IntegerField()  # POSTED_BY (NUMBER)
    status = models.CharField(max_length=50)  # STATUS (VARCHAR2(50 BYTE))
    ot_period = models.IntegerField()  # OT_PERIOD (NUMBER)
    trips = models.IntegerField()  # TRIPS (NUMBER)
    zone = models.CharField(max_length=50)  # ZONE (VARCHAR2(50 BYTE))

    class Meta:
        managed = False
        db_table = 'overtime'


class OvertimePay(models.Model):
    id = models.AutoField(primary_key=True)  # ID (NUMBER)
    emp_no = models.IntegerField()  # EMP_NO (NUMBER)
    overtime_type = models.CharField(max_length=200)  # OVERTIME_TYPE (VARCHAR2(200 BYTE))
    b_salary = models.DecimalField(max_digits=12, decimal_places=2)  # B_SALARY (NUMBER)
    tot_days = models.IntegerField()  # TOT_DAYS (NUMBER)
    p_day = models.DecimalField(max_digits=12, decimal_places=2)  # P_DAY (NUMBER)
    ot_amount = models.DecimalField(max_digits=12, decimal_places=2)  # OT_AMOUNT (NUMBER)
    ot_posted_by = models.IntegerField()  # OT_POSTED_BY (NUMBER)
    ot_att_posted_by = models.IntegerField()  # OT_ATT_POSTED_BY (NUMBER)
    ot_status = models.CharField(max_length=200)  # OT_STATUS (VARCHAR2(200 BYTE))
    overtime_date = models.DateField()  # OVERTIME_DATE (VARCHAR2(100 BYTE)), changed to DateField
    zone = models.CharField(max_length=200)  # ZONE (VARCHAR2(200 BYTE))
    ot_period = models.IntegerField()  # OT_PERIOD (NUMBER)
    trips = models.IntegerField()  # TRIPS (NUMBER)

    class Meta:
        managed = False
        db_table = 'overtime_pay'


class PayClass(models.Model):
    pay_class_id = models.IntegerField(primary_key=True)  # PAY_CLASS_ID (NUMBER)
    pay_class_desc = models.CharField(max_length=60)  # PAY_CLASS_DESC (VARCHAR2(60 BYTE))

    class Meta:
        managed = False
        db_table = 'pay_class'


class PayGrp(models.Model):
    pay_grp_id = models.IntegerField(primary_key=True)  # PAY_GRP_ID (NUMBER)
    pay_grp_desc = models.CharField(max_length=60)  # PAY_GRP_DESC (VARCHAR2(60 BYTE))
    pay_grp_class = models.IntegerField()  # PAY_GRP_CLASS (NUMBER)

    class Meta:
        managed = False
        db_table = 'pay_grp'


class PayGrpBkp(models.Model):
    pay_grp_id = models.IntegerField(primary_key=True)  # PAY_GRP_ID (NUMBER)
    pay_grp_desc = models.CharField(max_length=60)  # PAY_GRP_DESC (VARCHAR2(60 BYTE))
    pay_grp_class = models.IntegerField()  # PAY_GRP_CLASS (NUMBER)

    class Meta:
        managed = False
        db_table = 'pay_grp_bkp'


class PayParam(models.Model):
    pay_param_attapprover_ops = models.IntegerField()  # PAY_PARAM_ATTAPPROVER_OPS (NUMBER(7))
    pay_param_attapprover_adm = models.IntegerField()  # PAY_PARAM_ATTAPPROVER_ADM (NUMBER(7))
    pay_param_deducmode = models.CharField(max_length=1)  # PAY_PARAM_DEDUCMODE (CHAR(1 BYTE))
    pay_param_deducfixedrate = models.DecimalField(max_digits=10, decimal_places=0)  # PAY_PARAM_DEDUCFIXEDRATE (NUMBER(10))
    pay_param_overtimemode = models.CharField(max_length=1)  # PAY_PARAM_OVERTIMEMODE (CHAR(1 BYTE))
    pay_param_overtimefixedrate = models.DecimalField(max_digits=10, decimal_places=0)  # PAY_PARAM_OVERTIMEFIXEDRATE (NUMBER(10))
    pay_param_od = models.IntegerField()  # PAY_PARAM_OD (NUMBER(4))
    pay_param_dt = models.IntegerField()  # PAY_PARAM_DT (NUMBER(4))
    pay_param_ot = models.IntegerField()  # PAY_PARAM_OT (NUMBER(4))
    pay_param_lwop = models.IntegerField()  # PAY_PARAM_LWOP (NUMBER(4))

    class Meta:
        managed = False
        db_table = 'pay_param'


class PaySubgrp(models.Model):
    pay_subgrp_id = models.IntegerField(primary_key=True)  # PAY_SUBGRP_ID (NUMBER)
    pay_subgrp_desc = models.CharField(max_length=80)  # PAY_SUBGRP_DESC (VARCHAR2(80 BYTE))
    pay_subgrp_grp = models.IntegerField()  # PAY_SUBGRP_GRP (NUMBER)

    class Meta:
        managed = False
        db_table = 'pay_subgrp'


class PaySubgrpBkp(models.Model):
    pay_subgrp_id = models.IntegerField(primary_key=True)  # PAY_SUBGRP_ID (NUMBER)
    pay_subgrp_desc = models.CharField(max_length=80)  # PAY_SUBGRP_DESC (VARCHAR2(80 BYTE)) - NOT NULL
    pay_subgrp_grp = models.IntegerField()  # PAY_SUBGRP_GRP (NUMBER)

    class Meta:
        managed = False
        db_table = 'pay_subgrp_bkp'


class PayTrack(models.Model):
    pay_track_id = models.IntegerField(primary_key=True)  # PAY_TRACK_ID (NUMBER(6))
    pay_track_period = models.IntegerField()  # PAY_TRACK_PERIOD (NUMBER(4))
    pay_track_flg = models.CharField(max_length=1)  # PAY_TRACK_FLG (CHAR(1 BYTE))
    pay_track_flgfrom = models.IntegerField()  # PAY_TRACK_FLGFROM (NUMBER(7))
    pay_track_flgdt = models.DateField()  # PAY_TRACK_FLGDT (DATE)
    pay_track_newflg = models.CharField(max_length=1)  # PAY_TRACK_NEWFLG (CHAR(1 BYTE))
    pay_track_newflgto = models.IntegerField()  # PAY_TRACK_NEWFLGTO (NUMBER(7))
    pay_track_remarks = models.CharField(max_length=500)  # PAY_TRACK_REMARKS (VARCHAR2(500 BYTE))

    class Meta:
        managed = False
        db_table = 'pay_track'


class PayTrack04052023(models.Model):
    pay_track_id = models.IntegerField(primary_key=True)  # PAY_TRACK_ID (NUMBER(6))
    pay_track_period = models.IntegerField()  # PAY_TRACK_PERIOD (NUMBER(4))
    pay_track_flg = models.CharField(max_length=1)  # PAY_TRACK_FLG (CHAR(1 BYTE))
    pay_track_flgfrom = models.IntegerField()  # PAY_TRACK_FLGFROM (NUMBER(7))
    pay_track_flgdt = models.DateField()  # PAY_TRACK_FLGDT (DATE)
    pay_track_newflg = models.CharField(max_length=1)  # PAY_TRACK_NEWFLG (CHAR(1 BYTE))
    pay_track_newflgto = models.IntegerField()  # PAY_TRACK_NEWFLGTO (NUMBER(7))
    pay_track_remarks = models.CharField(max_length=500)  # PAY_TRACK_REMARKS (VARCHAR2(500 BYTE))

    class Meta:
        managed = False
        db_table = 'pay_track_04052023'


class PayTrackBkp29042024(models.Model):
    pay_track_id = models.IntegerField(primary_key=True)  # PAY_TRACK_ID (NUMBER(6))
    pay_track_period = models.IntegerField()  # PAY_TRACK_PERIOD (NUMBER(4))
    pay_track_flg = models.CharField(max_length=1)  # PAY_TRACK_FLG (CHAR(1 BYTE))
    pay_track_flgfrom = models.IntegerField()  # PAY_TRACK_FLGFROM (NUMBER(7))
    pay_track_flgdt = models.DateField()  # PAY_TRACK_FLGDT (DATE)
    pay_track_newflg = models.CharField(max_length=1)  # PAY_TRACK_NEWFLG (CHAR(1 BYTE))
    pay_track_newflgto = models.IntegerField()  # PAY_TRACK_NEWFLGTO (NUMBER(7))
    pay_track_remarks = models.CharField(max_length=500)  # PAY_TRACK_REMARKS (VARCHAR2(500 BYTE))

    class Meta:
        managed = False
        db_table = 'pay_track_bkp_29042024'


class PayrolBkp225(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1, null=True)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField(null=True)  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField(null=True)  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1, null=True)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payrol_bkp_225'


class Payroll(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4)), not null
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7)), not null
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5)), not null
    payroll_duty_days = models.IntegerField(null=True)  # PAYROLL_DUTY_DAYS (NUMBER(3)), nullable
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2)), not null
    payroll_flg = models.CharField(max_length=1, null=True)  # PAYROLL_FLG (CHAR(1 BYTE)), nullable
    payroll_arrears = models.IntegerField(null=True)  # PAYROLL_ARREARS (NUMBER(10)), nullable
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2)), not null
    payroll_emp_job = models.IntegerField(null=True)  # PAYROLL_EMP_JOB (NUMBER(3)), nullable
    payroll_emp_deptt = models.IntegerField(null=True)  # PAYROLL_EMP_DEPTT (NUMBER(3)), nullable
    payroll_emp_pop = models.IntegerField(null=True)  # PAYROLL_EMP_POP (NUMBER(3)), nullable
    payroll_emp_grd = models.IntegerField(null=True)  # PAYROLL_EMP_GRD (NUMBER(3)), nullable
    payroll_pay_subgrp = models.IntegerField(null=True)  # PAYROLL_PAY_SUBGRP (NUMBER), nullable
    payroll_emptyp = models.IntegerField(null=True)  # PAYROLL_EMPTYP (NUMBER(3)), nullable
    payroll_emp_saltyp = models.IntegerField(null=True)  # PAYROLL_EMP_SALTYP (NUMBER(3)), nullable
    payroll_emp_bank = models.IntegerField(null=True)  # PAYROLL_EMP_BANK (NUMBER(4)), nullable
    payroll_emp_bankacc = models.CharField(max_length=30, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE)), nullable
    payroll_emp_paymode = models.CharField(max_length=1, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE)), nullable
    payroll_emp_flg = models.CharField(max_length=1, null=True)  # PAYROLL_EMP_FLG (CHAR(1 BYTE)), nullable
    payroll_emp_mgr = models.IntegerField(null=True)  # PAYROLL_EMP_MGR (NUMBER(7)), nullable

    class Meta:
        managed = False
        db_table = 'payroll'


class Payroll03102023(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4)), not null
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7)), not null
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5)), not null
    payroll_duty_days = models.IntegerField(null=True)  # PAYROLL_DUTY_DAYS (NUMBER(3)), nullable
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2)), not null
    payroll_flg = models.CharField(max_length=1, null=True)  # PAYROLL_FLG (CHAR(1 BYTE)), nullable
    payroll_arrears = models.IntegerField(null=True)  # PAYROLL_ARREARS (NUMBER(10)), nullable
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2)), not null
    payroll_emp_job = models.IntegerField(null=True)  # PAYROLL_EMP_JOB (NUMBER(3)), nullable
    payroll_emp_deptt = models.IntegerField(null=True)  # PAYROLL_EMP_DEPTT (NUMBER(3)), nullable
    payroll_emp_pop = models.IntegerField(null=True)  # PAYROLL_EMP_POP (NUMBER(3)), nullable
    payroll_emp_grd = models.IntegerField(null=True)  # PAYROLL_EMP_GRD (NUMBER(3)), nullable
    payroll_pay_subgrp = models.IntegerField(null=True)  # PAYROLL_PAY_SUBGRP (NUMBER), nullable
    payroll_emptyp = models.IntegerField(null=True)  # PAYROLL_EMPTYP (NUMBER(3)), nullable
    payroll_emp_saltyp = models.IntegerField(null=True)  # PAYROLL_EMP_SALTYP (NUMBER(3)), nullable
    payroll_emp_bank = models.IntegerField(null=True)  # PAYROLL_EMP_BANK (NUMBER(4)), nullable
    payroll_emp_bankacc = models.CharField(max_length=30, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE)), nullable
    payroll_emp_paymode = models.CharField(max_length=1, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE)), nullable
    payroll_emp_flg = models.CharField(max_length=1, null=True)  # PAYROLL_EMP_FLG (CHAR(1 BYTE)), nullable
    payroll_emp_mgr = models.IntegerField(null=True)  # PAYROLL_EMP_MGR (NUMBER(7)), nullable

    class Meta:
        managed = False
        db_table = 'payroll_03102023'


class Payroll05062023(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_05062023'


class Payroll06052023(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_06052023'


class Payroll10052023(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_10052023'


class Payroll20042023(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_20042023'


class PayrollBkp26072024(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_bkp_26072024'


class PayrollBkp28122023(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4))
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7))
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5))
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2))
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2))
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_bkp_28122023'


class PayrollBkp31102024(models.Model):
    payroll_period = models.IntegerField()  # PAYROLL_PERIOD (NUMBER(4)) - Not null
    payroll_emp = models.IntegerField()  # PAYROLL_EMP (NUMBER(7)) - Not null
    payroll_allw = models.IntegerField()  # PAYROLL_ALLW (NUMBER(5)) - Not null
    payroll_duty_days = models.IntegerField(null=True, blank=True)  # PAYROLL_DUTY_DAYS (NUMBER(3))
    payroll_allwrate = models.DecimalField(max_digits=10, decimal_places=2)  # PAYROLL_ALLWRATE (NUMBER(10,2)) - Not null
    payroll_flg = models.CharField(max_length=1)  # PAYROLL_FLG (CHAR(1 BYTE))
    payroll_arrears = models.IntegerField(null=True, blank=True)  # PAYROLL_ARREARS (NUMBER(10))
    payroll_allwamt = models.DecimalField(max_digits=16, decimal_places=2)  # PAYROLL_ALLWAMT (NUMBER(16,2)) - Not null
    payroll_emp_job = models.IntegerField()  # PAYROLL_EMP_JOB (NUMBER(3))
    payroll_emp_deptt = models.IntegerField()  # PAYROLL_EMP_DEPTT (NUMBER(3))
    payroll_emp_pop = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_POP (NUMBER(3))
    payroll_emp_grd = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_GRD (NUMBER(3))
    payroll_pay_subgrp = models.IntegerField(null=True, blank=True)  # PAYROLL_PAY_SUBGRP (NUMBER)
    payroll_emptyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMPTYP (NUMBER(3))
    payroll_emp_saltyp = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_SALTYP (NUMBER(3))
    payroll_emp_bank = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_BANK (NUMBER(4))
    payroll_emp_bankacc = models.CharField(max_length=30, blank=True, null=True)  # PAYROLL_EMP_BANKACC (VARCHAR2(30 BYTE))
    payroll_emp_paymode = models.CharField(max_length=1, blank=True, null=True)  # PAYROLL_EMP_PAYMODE (CHAR(1 BYTE))
    payroll_emp_flg = models.CharField(max_length=1)  # PAYROLL_EMP_FLG (CHAR(1 BYTE))
    payroll_emp_mgr = models.IntegerField(null=True, blank=True)  # PAYROLL_EMP_MGR (NUMBER(7))

    class Meta:
        managed = False
        db_table = 'payroll_bkp_31102024'


class Purchse(models.Model):
    purchase_no = models.IntegerField()  # PURCHASE_NO (NUMBER(6))
    purchase_dt = models.DateField()  # PURCHASE_DT (DATE)
    purchase_supp = models.IntegerField()  # PURCHASE_SUPP (NUMBER(3))
    purchase_inv_no = models.CharField(max_length=20)  # PURCHASE_INV_NO (VARCHAR2(20 BYTE))
    purchase_inv_dt = models.DateField()  # PURCHASE_INV_DT (DATE)
    purchase_desc = models.CharField(max_length=150)  # PURCHASE_DESC (VARCHAR2(150 BYTE))
    purchase_amt = models.DecimalField(max_digits=16, decimal_places=2)  # PURCHASE_AMT (NUMBER(16))
    purchase_exp_acc = models.IntegerField()  # PURCHASE_EXP_ACC (NUMBER(9))
    purchase_flg = models.CharField(max_length=1)  # PURCHASE_FLG (CHAR(1 BYTE))
    purchase_posted_by = models.IntegerField()  # PURCHASE_POSTED_BY (NUMBER(4)) - Not null

    class Meta:
        managed = False
        db_table = 'purchse'


class SalPeriod(models.Model):
    sal_period_id = models.IntegerField(primary_key=True)  # SAL_PERIOD_ID (NUMBER(4))
    sal_period_from = models.DateField()  # SAL_PERIOD_FROM (DATE)
    sal_period_to = models.DateField()  # SAL_PERIOD_TO (DATE)
    sal_period_flg = models.CharField(max_length=1)  # SAL_PERIOD_FLG (CHAR(1 BYTE))
    sal_period_dt = models.DateField()  # SAL_PERIOD_DT (DATE)
    sal_period_month = models.DateField()  # SAL_PERIOD_MONTH (DATE)
    sal_period_dayscount = models.IntegerField()  # SAL_PERIOD_DAYSCOUNT (NUMBER(3))
    sal_period_init_by = models.IntegerField()  # SAL_PERIOD_INIT_BY (NUMBER(7))
    sal_period_init_dt = models.DateField()  # SAL_PERIOD_INIT_DT (DATE)
    sal_period_approved_by = models.IntegerField()  # SAL_PERIOD_APPROVED_BY (NUMBER(7))
    sal_period_approved_dt = models.DateField()  # SAL_PERIOD_APPROVED_DT (DATE)
    sal_period_accepted_by = models.IntegerField()  # SAL_PERIOD_ACCEPTED_BY (NUMBER(7))
    sal_period_accepted_dt = models.DateField()  # SAL_PERIOD_ACCEPTED_DT (DATE)
    sal_period_auth_by = models.IntegerField()  # SAL_PERIOD_AUTH_BY (NUMBER(7))
    sal_period_auth_dt = models.DateField()  # SAL_PERIOD_AUTH_DT (DATE)
    sal_period_fin_by = models.IntegerField()  # SAL_PERIOD_FIN_BY (NUMBER(7))
    sal_period_fin_dt = models.DateField()  # SAL_PERIOD_FIN_DT (DATE)
    sal_period_run_by = models.IntegerField()  # SAL_PERIOD_RUN_BY (NUMBER(7))
    sal_period_run_dt = models.DateField()  # SAL_PERIOD_RUN_DT (DATE)
    sal_period_yr = models.CharField(max_length=7)  # SAL_PERIOD_YR (VARCHAR2(7 BYTE))

    class Meta:
        managed = False
        db_table = 'sal_period'
        unique_together = (('sal_period_month', 'sal_period_month'),)


class Supplier(models.Model):
    supp_id = models.IntegerField(primary_key=True)  # SUPP_ID (NUMBER)
    supp_desc = models.CharField(max_length=200)  # SUPP_DESC (VARCHAR2(200 BYTE))
    supp_add1 = models.CharField(max_length=150)  # SUPP_ADD1 (VARCHAR2(150 BYTE))
    supp_add2 = models.CharField(max_length=150)  # SUPP_ADD2 (VARCHAR2(150 BYTE))
    supp_add3 = models.CharField(max_length=100)  # SUPP_ADD3 (VARCHAR2(100 BYTE))
    supp_ph = models.CharField(max_length=11)  # SUPP_PH (VARCHAR2(11 BYTE))
    supp_cont = models.CharField(max_length=80)  # SUPP_CONT (VARCHAR2(80 BYTE))
    supp_cont_cell = models.CharField(max_length=11)  # SUPP_CONT_CELL (VARCHAR2(11 BYTE))
    supp_email = models.EmailField(max_length=80)  # SUPP_EMAIL (VARCHAR2(80 BYTE))
    supp_acc = models.IntegerField()  # SUPP_ACC (NUMBER(9))
    supp_flg = models.CharField(max_length=1)  # SUPP_FLG (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'supplier'


class SysCtrl(models.Model):
    sys_comp_id = models.IntegerField(primary_key=True)  # SYS_COMP_ID (NUMBER(6))
    sys_step_no = models.IntegerField()  # SYS_STEP_NO (NUMBER(2))
    sys_today_dt = models.DateField()  # SYS_TODAY_DT (DATE)
    sys_prev_dat = models.DateField()  # SYS_PREV_DAT (DATE)
    sys_nxt_dt = models.DateField()  # SYS_NXT_DT (DATE)
    sys_bal_flg = models.CharField(max_length=1)  # SYS_BAL_FLG (VARCHAR2(1 BYTE))
    sys_gst = models.DecimalField(max_digits=4, decimal_places=2)  # SYS_GST (NUMBER(4,2))
    sys_inv_printer = models.CharField(max_length=30)  # SYS_INV_PRINTER (VARCHAR2(30 BYTE))
    ctrl_dual_ctrl = models.CharField(max_length=1)  # CTRL_DUAL_CTRL (CHAR(1 BYTE))
    cash_subgrp = models.IntegerField()  # CASH_SUBGRP (NUMBER(6))
    bank_subgrp = models.IntegerField()  # BANK_SUBGRP (NUMBER(6))
    ctrl_tax_flg = models.CharField(max_length=1)  # CTRL_TAX_FLG (CHAR(1 BYTE))
    ctrl_tax_slab = models.IntegerField()  # CTRL_TAX_SLAB (NUMBER(10))
    ctrl_tax_rate = models.DecimalField(max_digits=6, decimal_places=2)  # CTRL_TAX_RATE (NUMBER(6,2))
    ctrl_tax_acc = models.IntegerField()  # CTRL_TAX_ACC (NUMBER(9))
    ctrl_sal_payable = models.IntegerField()  # CTRL_SAL_PAYABLE (NUMBER(9))
    ctrl_rep_pdf_path = models.CharField(max_length=400)  # CTRL_REP_PDF_PATH (VARCHAR2(400 BYTE))
    ctrl_rep_xls_path = models.CharField(max_length=400)  # CTRL_REP_XLS_PATH (VARCHAR2(400 BYTE))
    ctrl_rep_pdflan_path = models.CharField(max_length=300)  # CTRL_REP_PDFLAN_PATH (VARCHAR2(300 BYTE))
    ctrl_rep_xslan_path = models.CharField(max_length=300)  # CTRL_REP_XLSLAN_PATH (VARCHAR2(300 BYTE))

    class Meta:
        managed = False
        db_table = 'sys_ctrl'


class TaBill(models.Model):
    ta_bill_no = models.BigIntegerField(primary_key=True)  # TA_BILL_NO (NUMBER(8))
    ta_bill_emp = models.IntegerField()  # TA_BILL_EMP (NUMBER(7))
    ta_bill_dt = models.DateField()  # TA_BILL_DT (DATE)
    ta_bill_hrapprvby = models.IntegerField()  # TA_BILL_HRAPPRVBY (NUMBER(7))
    ta_bill_hrapprvdt = models.DateField()  # TA_BILL_HRAPPRVDT (DATE)
    ta_bill_fiapprvby = models.IntegerField()  # TA_BILL_FIAPPRVBY (NUMBER(7))
    ta_bill_fiapprvdt = models.DateField()  # TA_BILL_FIAPPRVDT (DATE)
    ta_bill_authby = models.IntegerField()  # TA_BILL_AUTHBY (NUMBER)
    ta_bill_authdt = models.CharField(max_length=20)  # TA_BILL_AUTHDT (VARCHAR2(20 BYTE))
    ta_bill_flg = models.CharField(max_length=1)  # TA_BILL_FLG (CHAR(1 BYTE))

    class Meta:
        managed = False
        db_table = 'ta_bill'


class TabillDet(models.Model):
    tabill_det_bill = models.BigIntegerField()  # TABILL_DET_BILL (NUMBER(8))
    tabill_det_travel = models.BigIntegerField()  # TABILL_DET_TRAVEL (NUMBER(8))
    tabill_det_trip = models.IntegerField()  # TABILL_DET_TRIP (NUMBER(4))
    tabill_det_triptp = models.CharField(max_length=1)  # TABILL_DET_TRIPTYP (CHAR(1 BYTE))
    tabill_det_trip_from = models.IntegerField(null=True, blank=True)  # TABILL_DET_TRIP_FROM (NUMBER(6))
    tabill_det_trip_fromdt = models.DateField(null=True, blank=True)  # TABILL_DET_TRIP_FROMDT (DATE)
    tabill_det_trip_fromti = models.DateField(null=True, blank=True)  # TABILL_DET_TRIP_FROMTI (DATE)
    tabill_det_trip_to = models.IntegerField(null=True, blank=True)  # TABILL_DET_TRIP_TO (NUMBER(6))
    tabill_det_trip_todt = models.DateField(null=True, blank=True)  # TABILL_DET_TRIP_TODT (DATE)
    tabill_det_trip_toti = models.DateField(null=True, blank=True)  # TABILL_DET_TRIP_TOTI (DATE)
    tabill_det_trip_dist = models.BigIntegerField(null=True, blank=True)  # TABILL_DET_TRIP_DIST (NUMBER(8))
    tabill_det_trip_incity_dist = models.IntegerField(null=True, blank=True)  # TABILL_DET_TRIP_INCITY_DIST (NUMBER(6))

    class Meta:
        managed = False
        db_table = 'tabill_det'


class Tarif(models.Model):
    tarif_id = models.IntegerField(primary_key=True)  # TARIF_ID (NUMBER(3))
    tarif_desc = models.CharField(max_length=50)  # TARIF_DESC (VARCHAR2(50 BYTE))
    tarif_cat = models.IntegerField()  # TARIF_CAT (NUMBER(3))
    tarif_metered = models.CharField(max_length=1, null=True, blank=True)  # TARIF_METERED (VARCHAR2(1 BYTE))

    class Meta:
        managed = False
        db_table = 'tarif'


class TarifCat(models.Model):
    tarif_cat_id = models.IntegerField(primary_key=True)  # TARIF_CAT_ID (NUMBER(3))
    tarif_cat_desc = models.CharField(max_length=50)  # TARIF_CAT_DESC (VARCHAR2(50 BYTE))

    class Meta:
        managed = False
        db_table = 'tarif_cat'


class TaxSlab(models.Model):
    id = models.BigIntegerField(primary_key=True)  # ID (NUMBER(7))
    min_salary = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  # MIN_SALARY (NUMBER(20))
    max_salary = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  # MAX_SALARY (NUMBER(20))
    fix_tax = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  # FIX_TAX (NUMBER(20))
    sal_percent = models.FloatField(null=True, blank=True)  # SAL_PERCENT (FLOAT(10))

    class Meta:
        managed = False
        db_table = 'tax_slab'


class TaxableSalary(models.Model):
    id = models.BigIntegerField(primary_key=True)  # ID (NUMBER(10))
    tax_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # TAX_SALAR (NUMBER(10))

    class Meta:
        managed = False
        db_table = 'taxable_salary'


class Tehsil(models.Model):
    tehsil_id = models.IntegerField(primary_key=True)  # TEHSIL_ID (NUMBER(3))
    tehsil_desc = models.CharField(max_length=30)  # TEHSIL_DESC (VARCHAR2(30 BYTE))

    class Meta:
        managed = False
        db_table = 'tehsil'


class TempTaxCalcArrear(models.Model):
    emp_no = models.IntegerField()  # EMP_NO (NUMBER)
    amount_year = models.IntegerField()  # AMOUNT_YEAR (NUMBER)
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # AMOUNT (NUMBER)

    class Meta:
        managed = False
        db_table = 'temp_tax_calc_arrear'


class TrInf(models.Model):
    name = models.CharField(max_length=100)  # NAME (VARCHAR2(100 BYTE))
    descc = models.TextField()  # DESCC (VARCHAR2(500 BYTE))

    class Meta:
        managed = False
        db_table = 'tr_inf'


class TrainingAgency(models.Model):
    agency_id = models.IntegerField(primary_key=True)  # AGENCY_ID (NUMBER)
    agency_name = models.CharField(max_length=100)  # AGENCY_NAME (VARCHAR2(100 BYTE))

    class Meta:
        managed = False
        db_table = 'training_agency'


class TrainingDefBkp270324(models.Model):
    tran_id = models.IntegerField()  # TRAN_ID (NUMBER)
    tran_desc = models.CharField(max_length=100)  # TRAN_DESC (VARCHAR2(100 BYTE))
    tran_location = models.CharField(max_length=100)  # TRAN_LOCATION (VARCHAR2(100 BYTE))
    tran_start_date = models.DateField()  # TRAN_START_DATE (DATE)
    tran_end_date = models.DateField()  # TRAN_END_DATE (DATE)
    tran_days = models.IntegerField()  # TRAN_DAYS (NUMBER)

    class Meta:
        managed = False
        db_table = 'training_def_bkp270324'


class TrainingDefinition(models.Model):
    tran_id = models.IntegerField(primary_key=True)  # TRAN_ID (NUMBER)
    tran_desc = models.CharField(max_length=200)  # TRAN_DESC (VARCHAR2(200 BYTE))
    tran_location = models.CharField(max_length=100)  # TRAN_LOCATION (VARCHAR2(100 BYTE))
    tran_start_date = models.DateField()  # TRAN_START_DATE (DATE)
    tran_end_date = models.DateField()  # TRAN_END_DATE (DATE)
    tran_days = models.IntegerField()  # TRAN_DAYS (NUMBER)
    training_field = models.CharField(max_length=50)  # TRAINING_FIELD (VARCHAR2(50 BYTE))
    mode_training = models.CharField(max_length=50)  # MODE_TRAINING (VARCHAR2(50 BYTE))
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    email = models.EmailField(max_length=50)  # EMAIL (VARCHAR2(50 BYTE))
    institute_id = models.IntegerField()  # INSTITUTE_ID (NUMBER)
    agency_id = models.IntegerField()  # AGENCY_ID (NUMBER)

    class Meta:
        managed = False
        db_table = 'training_definition'


class TrainingDefinitionBkp27824(models.Model):
    tran_id = models.IntegerField()  # TRAN_ID (NUMBER)
    tran_desc = models.CharField(max_length=200)  # TRAN_DESC (VARCHAR2(200 BYTE))
    tran_location = models.CharField(max_length=100)  # TRAN_LOCATION (VARCHAR2(100 BYTE))
    tran_start_date = models.DateField()  # TRAN_START_DATE (DATE)
    tran_end_date = models.DateField()  # TRAN_END_DATE (DATE)
    tran_days = models.IntegerField()  # TRAN_DAYS (NUMBER)
    training_field = models.CharField(max_length=50)  # TRAINING_FIELD (VARCHAR2(50 BYTE))
    mode_training = models.CharField(max_length=50)  # MODE_TRAINING (VARCHAR2(50 BYTE))
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    email = models.CharField(max_length=50)  # EMAIL (VARCHAR2(50 BYTE))
    institute_id = models.IntegerField()  # INSTITUTE_ID (NUMBER)
    agency_id = models.IntegerField()  # AGENCY_ID (NUMBER)

    class Meta:
        managed = False
        db_table = 'training_definition_bkp27824'


class TrainingDetail(models.Model):
    id = models.AutoField(primary_key=True)  # ID (auto-incremented primary key)
    emp_id = models.IntegerField()  # EMP_ID (NUMBER)
    t_date = models.DateField()  # T_DATE (DATE)
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    m_id = models.IntegerField()  # M_ID (NUMBER)
    d_status = models.CharField(max_length=10, default='un')  # D_STATUS (VARCHAR2(10 BYTE), default 'un')

    class Meta:
        managed = False
        db_table = 'training_detail'


class TrainingDetailBkp27824(models.Model):
    id = models.AutoField(primary_key=True)  # ID (auto-incremented primary key)
    emp_id = models.IntegerField()  # EMP_ID (NUMBER)
    t_date = models.DateField()  # T_DATE (DATE)
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    m_id = models.IntegerField()  # M_ID (NUMBER)
    d_status = models.CharField(max_length=10)  # D_STATUS (VARCHAR2(10 BYTE))

    class Meta:
        managed = False
        db_table = 'training_detail_bkp_27824'


class TrainingInstitute(models.Model):
    institute_id = models.AutoField(primary_key=True)  # INSTITUTE_ID (auto-incremented primary key)
    institute_name = models.CharField(max_length=100)  # INSTITUTE_NAME (VARCHAR2(100 BYTE))

    class Meta:
        managed = False
        db_table = 'training_institute'


class TrainingMaster(models.Model):
    m_id = models.IntegerField()  # M_ID (NUMBER, not null)
    tran_id = models.IntegerField(null=True)  # TRAN_ID (NUMBER, nullable)
    t_date = models.DateField()  # T_DATE (DATE)
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    m_status = models.CharField(max_length=2, default='un')  # M_STATUS (VARCHAR2(2 BYTE), default 'un')

    class Meta:
        managed = False
        db_table = 'training_master'


class TrainingMasterBkp27824(models.Model):
    m_id = models.IntegerField()  # M_ID (NUMBER, not null)
    tran_id = models.IntegerField(null=True)  # TRAN_ID (NUMBER, nullable)
    t_date = models.DateField()  # T_DATE (DATE)
    remarks = models.CharField(max_length=50)  # REMARKS (VARCHAR2(50 BYTE))
    m_status = models.CharField(max_length=2)  # M_STATUS (VARCHAR2(2 BYTE))

    class Meta:
        managed = False
        db_table = 'training_master_bkp27824'


class Tran(models.Model):
    tran_dt = models.DateField()  # TRAN_DT (DATE, not null)
    tran_no = models.IntegerField(primary_key=True)  # TRAN_NO (NUMBER(6), not null)
    tran_acc = models.IntegerField()  # TRAN_ACC (NUMBER(9), not null)
    tran_typ = models.IntegerField()  # TRAN_TYP (NUMBER(2), not null)
    tran_cr_db = models.IntegerField()  # TRAN_CR_DB (NUMBER(2), not null)
    tran_desc = models.CharField(max_length=100)  # TRAN_DESC (VARCHAR2(100 BYTE), not null)
    tran_ref_no = models.CharField(max_length=15, null=True)  # TRAN_REF_NO (VARCHAR2(15 BYTE), nullable)
    tran_amt = models.DecimalField(max_digits=16, decimal_places=2)  # TRAN_AMT (NUMBER(16,2), not null)
    tran_status = models.CharField(max_length=1)  # TRAN_STATUS (CHAR(1 BYTE), not null)
    tran_month = models.DateField()  # TRAN_MONTH (DATE, not null)
    tran_vchr_no = models.IntegerField()  # TRAN_VCHR_NO (NUMBER(8), not null)
    tran_posted_by = models.IntegerField()  # TRAN_POSTED_BY (NUMBER(7), not null)
    tran_cont_acc = models.IntegerField()  # TRAN_CONT_ACC (NUMBER(9), not null)
    tran_year = models.IntegerField()  # TRAN_YEAR (NUMBER(6), not null)
    tran_sup_by = models.IntegerField(null=True)  # TRAN_SUP_BY (NUMBER(7), nullable)

    class Meta:
        managed = False
        db_table = 'tran'


class TranTyp(models.Model):
    tran_typ_id = models.IntegerField()  # TRAN_TYP_ID (NUMBER(2))
    tran_typ_desc = models.CharField(max_length=20)  # TRAN_TYP_DESC (VARCHAR2(20 BYTE), not null)

    class Meta:
        managed = False
        db_table = 'tran_typ'


class Transactions(models.Model):
    id = models.IntegerField(primary_key=True)  # ID (NUMBER)
    emp_no = models.IntegerField()  # EMP_NO (NUMBER)
    tran_id = models.IntegerField()  # TRAN_ID (NUMBER)

    class Meta:
        managed = False
        db_table = 'transactions'


class TravelReq(models.Model):
    travel_req_id = models.IntegerField(primary_key=True)  # TRAVEL_REQ_ID (NUMBER)
    travel_req_emp = models.IntegerField(null=True)  # TRAVEL_REQ_EMP (NUMBER)
    travel_req_dt = models.DateField(null=True)  # TRAVEL_REQ_DT (DATE)
    travel_req_desc = models.CharField(max_length=300, null=True)  # TRAVEL_REQ_DESC (VARCHAR2(300 BYTE))
    travel_req_flg = models.CharField(max_length=1, null=True)  # TRAVEL_REQ_FLG (VARCHAR2(1 BYTE))
    travel_req_approve_by = models.IntegerField(null=True)  # TRAVEL_REQ_APPROVE_BY (NUMBER)
    travel_req_approve_dt = models.DateField(null=True)  # TRAVEL_REQ_APPROVE_DT (DATE)
    travel_req_auth_by = models.IntegerField(null=True)  # TRAVEL_REQ_AUTH_BY (NUMBER)
    travel_req_auth_dt = models.DateField(null=True)  # TRAVEL_REQ_AUTH_DT (DATE)
    travel_req_hrapprv_by = models.IntegerField(null=True)  # TRAVEL_REQ_HRAPPRV_BY (NUMBER)
    travel_req_hrapprv_dt = models.DateField(null=True)  # TRAVEL_REQ_HRAPPRV_DT (DATE)
    travel_req_bill_flg = models.CharField(max_length=1, null=True)  # TRAVEL_REQ_BILL_FLG (CHAR(1 BYTE))
    travel_req_from = models.IntegerField(null=True)  # TRAVEL_REQ_FROM (NUMBER(6))
    travel_req_to = models.IntegerField(null=True)  # TRAVEL_REQ_TO (NUMBER(6))
    travel_req_from_dt = models.DateField(null=True)  # TRAVEL_REQ_FROM_DT (DATE)
    travel_req_to_dt = models.DateField(null=True)  # TRAVEL_REQ_TO_DT (DATE)

    class Meta:
        managed = False
        db_table = 'travel_req'


class TravelreqAuth(models.Model):
    travelreq_auth_id = models.IntegerField(primary_key=True)  # TRAVELREQ_AUTH_ID (NUMBER)
    travelreq_auth_reqid = models.IntegerField(null=True)  # TRAVEREQ_AUTH_REQID (NUMBER)
    travelreq_auth_flg = models.CharField(max_length=1, null=True)  # TRAVELREQ_AUTH_FLG (VARCHAR2(1 BYTE))
    travelreq_auth_flgfrom = models.IntegerField(null=True)  # TRAVELREQ_AUTH_FLGFROM (NUMBER)
    travelreq_auth_flgdt = models.DateField(null=True)  # TRAVELREQ_AUTH_FLGDT (DATE)
    travelreq_auth_newflg = models.CharField(max_length=1, null=True)  # TRAVELREQ_AUTH_NEWFLG (VARCHAR2(1 BYTE))
    travelreq_auth_newflgto = models.IntegerField(null=True)  # TRAVELREQ_AUTH_NEWFLGTO (NUMBER)
    travelreq_auth_remarks = models.CharField(max_length=300, null=True)  # TRAVELREQ_AUTH_REMARKS (VARCHAR2(300 BYTE))

    class Meta:
        managed = False
        db_table = 'travelreq_auth'


class TwZone(models.Model):
    zone_id = models.IntegerField(primary_key=True)  # ZONE_ID (NUMBER(3), NOT NULL)
    zone_desc = models.CharField(max_length=30)  # ZONE_DESC (VARCHAR2(30 BYTE), NOT NULL)
    tot_tubewell = models.IntegerField()  # TOT_TUBEWELL (NUMBER(3), NOT NULL)
    tot_supervisor = models.IntegerField()  # TOT_SUPERVISOR (NUMBER(3), NOT NULL)
    remarks = models.CharField(max_length=50, null=True, blank=True)  # REMARKS (VARCHAR2(50 BYTE), Nullable)

    class Meta:
        managed = False
        db_table = 'tw_zone'


class TwZone1(models.Model):
    zone_id = models.IntegerField(primary_key=True)  # ZONE_ID (NUMBER(3), NOT NULL)
    zone_desc = models.CharField(max_length=30)  # ZONE_DESC (VARCHAR2(30 BYTE), NOT NULL)
    tot_tubewell = models.IntegerField()  # TOT_TUBEWELL (NUMBER(3), NOT NULL)
    tot_supervisor = models.IntegerField()  # TOT_SUPERVISOR (NUMBER(3), NOT NULL)
    remarks = models.CharField(max_length=200, null=True, blank=True)  # REMARKS (VARCHAR2(200 BYTE), Nullable)

    class Meta:
        managed = False
        db_table = 'tw_zone_1'


class Uc(models.Model):
    uc_id = models.IntegerField(primary_key=True)  # UC_ID (NUMBER(3), NOT NULL)
    uc_desc = models.CharField(max_length=50)  # UC_DESC (VARCHAR2(50 BYTE), NOT NULL)
    uc_zone = models.IntegerField(null=True, blank=True)  # UC_ZONE (NUMBER(3), Nullable)

    class Meta:
        managed = False
        db_table = 'uc'


class UcBkp(models.Model):
    uc_id = models.IntegerField(primary_key=True)  # Unique ID for UC
    uc_desc = models.CharField(max_length=50)  # UC Description
    uc_zone = models.IntegerField()  # Associated Zone

    class Meta:
        managed = False
        db_table = 'uc_bkp'


class UserCtrl(models.Model):
    user_ctrl_user = models.IntegerField()  # User ID (not linked to Django's User)
    user_ctrl_menu = models.IntegerField()  # Menu ID

    class Meta:
        managed = False
        db_table = 'user_ctrl'


class UserDeptt(models.Model):
    user_deptt_id = models.IntegerField(primary_key=True)  # Department ID
    user_deptt_desc = models.CharField(max_length=35)  # Department Description

    class Meta:
        managed = False
        db_table = 'user_deptt'


class UserDesig(models.Model):
    user_desig_id = models.IntegerField(primary_key=True)  # Designation ID
    user_desig_desc = models.CharField(max_length=25)  # Designation Description

    class Meta:
        managed = False
        db_table = 'user_desig'


class UserGrd(models.Model):
    user_grd_id = models.IntegerField(primary_key=True)  # Grade ID
    user_grd_desc = models.CharField(max_length=15)  # Grade Description

    class Meta:
        managed = False
        db_table = 'user_grd'


class UserLvl(models.Model):
    user_lvl_id = models.IntegerField(primary_key=True)  # Level ID
    user_lvl_desc = models.CharField(max_length=20)  # Level Description

    class Meta:
        managed = False
        db_table = 'user_lvl'


class UserRole(models.Model):
    ROLE_ID = models.IntegerField(primary_key=True)  # Role ID
    ROLE_DESC = models.CharField(max_length=80)  # Role Description

    class Meta:
        managed = False
        db_table = 'user_role'


class Users(models.Model):
    USER_ID = models.CharField(max_length=10, primary_key=True)  # User ID
    USER_DESC = models.CharField(max_length=50, null=True, blank=True)  # User Description
    USER_PSWD = models.CharField(max_length=15)  # User Password
    USER_ROLE = models.IntegerField()  # Role ID (ForeignKey can be added if related)
    USER_EMAIL = models.EmailField(max_length=50, null=True, blank=True)  # User Email
    USER_CELL = models.CharField(max_length=20, null=True, blank=True)  # User Cell Number
    USER_DEPTT = models.IntegerField(null=True, blank=True)  # Department ID (ForeignKey can be added if related)
    USER_FLG = models.CharField(max_length=1, null=True, blank=True)  # User Flag
    USER_PSWD_FLG = models.CharField(max_length=20, null=True, blank=True)  # Password Flag

    class Meta:
        managed = False
        db_table = 'users'


class UsersBkp(models.Model):
    USER_ID = models.CharField(max_length=10, primary_key=True)  # User ID
    USER_DESC = models.CharField(max_length=50, null=True, blank=True)  # User Description
    USER_PSWD = models.CharField(max_length=15)  # User Password
    USER_ROLE = models.IntegerField()  # Role ID (ForeignKey can be added if needed)
    USER_EMAIL = models.EmailField(max_length=50, null=True, blank=True)  # User Email
    USER_CELL = models.CharField(max_length=20, null=True, blank=True)  # User Cell Number
    USER_DEPTT = models.IntegerField(null=True, blank=True)  # Department ID (ForeignKey can be added if needed)
    USER_FLG = models.CharField(max_length=1, null=True, blank=True)  # User Flag
    USER_PSWD_FLG = models.CharField(max_length=20, null=True, blank=True)  # Password Flag

    class Meta:
        managed = False
        db_table = 'users_bkp'


class WaiverTyp(models.Model):
    WAIVER_TYP_ID = models.IntegerField(primary_key=True)  # Waiver Type ID
    WAIVER_TYP_DESC = models.CharField(max_length=80)  # Waiver Type Description

    class Meta:
        managed = False
        db_table = 'waiver_typ'


class WsspAsaanAccountCheque(models.Model):
    ID = models.IntegerField(primary_key=True)  # Unique Payment ID
    PAYEE_NAME = models.CharField(max_length=100)  # Payee Name
    PAY_DATE = models.DateField()  # Payment Date
    AMOUNT = models.DecimalField(max_digits=20, decimal_places=2)  # Amount

    class Meta:
        managed = False
        db_table = 'wssp_asaan_account_cheque'


class WsspEntitledPost(models.Model):
    ID = models.IntegerField(primary_key=True)  # Unique ID
    JOB_ID = models.IntegerField()  # Job ID
    GRD_ID = models.IntegerField(null=True, blank=True)  # Grade ID (optional)
    ENT_POSTS = models.IntegerField(null=True, blank=True)  # Entered Posts (optional)

    class Meta:
        managed = False
        db_table = 'wssp_entitled_post'


class WsspOffices(models.Model):
    ID = models.IntegerField(primary_key=True)  # Unique ID
    NAME = models.CharField(max_length=20)  # Name field with max length 20

    class Meta:
        managed = False
        db_table = 'wssp_offices'


class WsspUc(models.Model):
    ID = models.IntegerField(primary_key=True)  # Unique ID
    UC_NO = models.CharField(max_length=10)  # UC Number
    UC_NAME = models.CharField(max_length=50)  # UC Name
    ZONE_ID = models.IntegerField(null=True, blank=True)  # Zone ID (can be optional)

    class Meta:
        managed = False
        db_table = 'wssp_uc'


class WsspUc1(models.Model):
    ID = models.IntegerField(primary_key=True)  # Unique ID
    UC_NO = models.CharField(max_length=100)  # UC Number
    UC_NAME = models.CharField(max_length=500)  # UC Name
    ZONE_ID = models.IntegerField(null=True, blank=True)  # Zone ID (can be optional)

    class Meta:
        managed = False
        db_table = 'wssp_uc1'


class WsspUc2(models.Model):
    ID = models.CharField(max_length=3, primary_key=True)  # Unique ID
    UC_NO = models.CharField(max_length=240)  # UC Number
    UC_NAME = models.CharField(max_length=240)  # UC Name
    ZONE_ID = models.CharField(max_length=240)  # Zone ID

    class Meta:
        managed = False
        db_table = 'wssp_uc2'


class Zone(models.Model):
    ZONE_ID = models.PositiveIntegerField(primary_key=True)  # Unique Zone ID
    ZONE_DESC = models.CharField(max_length=30)  # Zone Description
    ZONE_TEHSIL = models.PositiveIntegerField(null=True, blank=True)  # Zone Tehsil (optional)

    class Meta:
        managed = False
        db_table = 'zone'


##################### Access Control ###################3

class ViewsAccess(models.Model):
    view_id = models.AutoField(primary_key=True)
    view_name = models.CharField(max_length=100, unique=True)
    view_desc = models.TextField(blank=True)
    # Add this field to your model
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'views_access'
        verbose_name = 'View Access'
        verbose_name_plural = 'Views Access'

    def __str__(self):
        return f"{self.view_name} - {self.view_desc}"

class UserViewPermission(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()  # FK to your custom users table
    view = models.ForeignKey(ViewsAccess, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.IntegerField(null=True, blank=True)  # Who granted this permission

    class Meta:
        db_table = 'user_view_permission'
        unique_together = ('user_id', 'view')
        verbose_name = 'User View Permission'
        verbose_name_plural = 'User View Permissions'

    def __str__(self):
        return f"User {self.user_id} -> {self.view.view_name}"