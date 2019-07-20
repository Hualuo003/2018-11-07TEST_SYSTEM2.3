#!/usr/bin/env python
# -*- coding: utf-8 -*-



from .orm import Model
''' 所有模块都继承Model '''

# 选择题
class Choice_model(Model):
    __table__ = 'choice'
    __pk__ = 'question_qt_id'
    __attr__ = set(['question_qt_id','cc_a','cc_b','cc_c','cc_d','cc_e','cc_f','cc_answer',])
    __insertable__ = set({'question_qt_id','cc_a','cc_b','cc_c','cc_d','cc_e','cc_f','cc_answer',})
    __updateable__ = set({'cc_a','cc_b','cc_c','cc_d','cc_e','cc_f','cc_answer',})
    __notnull__ = set({})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 班级
class Class_model(Model):
    __table__ = 'class'
    __pk__ = 'cl_id'
    __attr__ = set(['cl_id','cl_name',])
    __insertable__ = set({'cl_name',})
    __updateable__ = set({'cl_name',})
    __notnull__ = set({'cl_name',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 编程题
class Coding_model(Model):
    __table__ = 'coding'
    __pk__ = 'question_qt_id'
    __attr__ = set(['question_qt_id','co_test_coding','co_test_answer_in','co_test_answer_out',])
    __insertable__ = set({'question_qt_id','co_test_coding','co_test_answer_in','co_test_answer_out',})
    __updateable__ = set({'co_test_coding','co_test_answer_in','co_test_answer_out',})
    __notnull__ = set({})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 考试表
class Exam_model(Model):
    __table__ = 'exam'
    __pk__ = 'ex_id'
    __attr__ = set(['ex_id','ex_name','ex_state','ex_type','ex_duration','ex_auto','ex_time_start','ex_time_end','ex_login_password','ex_change_password','ex_delay_password','ex_restart_password','ex_node','strategy_sg_id',])
    __insertable__ = set({'ex_name','ex_state','ex_type','ex_duration','ex_auto','ex_time_start','ex_time_end','ex_login_password','ex_change_password','ex_delay_password','ex_restart_password','ex_node','strategy_sg_id',})
    __updateable__ = set({'ex_name','ex_state','ex_type','ex_duration','ex_auto','ex_time_start','ex_time_end','ex_login_password','ex_change_password','ex_delay_password','ex_restart_password','ex_node','strategy_sg_id',})
    __notnull__ = set({'ex_name','ex_type','ex_duration','ex_time_start','ex_time_end','strategy_sg_id',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 试题表
class Exam_question_model(Model):
    '''2018-08-23 更改：添加了eq_lang字段'''
    __table__ = 'exam_question'
    __pk__ = 'eq_id'
    __attr__ = set(['eq_id','information_in_id','qt_id','eq_qt_type','eq_pre_score','eq_get_score','eq_answer','fillb_coding', 'eq_lang'])
    __insertable__ = set({'information_in_id','qt_id','eq_qt_type','eq_pre_score','eq_get_score','eq_answer','fillb_coding', 'eq_lang'})
    __updateable__ = set({'information_in_id','qt_id','eq_qt_type','eq_pre_score','eq_get_score','eq_answer','fillb_coding', 'eq_lang'})
    __notnull__ = set({'information_in_id'})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 读程序写结果
class Filla_model(Model):
    __table__ = 'filla'
    __pk__ = 'question_qt_id'
    __attr__ = set(['question_qt_id','fa_answer',])
    __insertable__ = set({'question_qt_id','fa_answer',})
    __updateable__ = set({'fa_answer',})
    __notnull__ = set({})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 程序填空
class Fillb_model(Model):
    __table__ = 'fillb'
    __pk__ = 'question_qt_id'
    __attr__ = set(['question_qt_id','fb_pre_coding','fb_test_coding','fb_test_answer_in','fb_test_answer_out',])
    __insertable__ = set({'question_qt_id','fb_pre_coding','fb_test_coding','fb_test_answer_in','fb_test_answer_out',})
    __updateable__ = set({'fb_pre_coding','fb_test_coding','fb_test_answer_in','fb_test_answer_out',})
    __notnull__ = set({})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 试卷信息表
class Information_model(Model):
    __table__ = 'information'
    __pk__ = 'in_id'
    __attr__ = set(['in_id','exam_ex_id','sg_id','in_score','in_ip','in_endtime','in_state','class_cl_id','student_st_id','in_temp_ip'])
    __insertable__ = set({'in_id','exam_ex_id','sg_id','in_score','in_ip','in_endtime','in_state','class_cl_id','student_st_id','in_temp_ip'})
    __updateable__ = set({'in_id','exam_ex_id','sg_id','in_score','in_ip','in_endtime','in_state','class_cl_id','student_st_id','in_temp_ip'})
    __notnull__ = set({'exam_ex_id','class_cl_id','student_st_id',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 判断题
class Judge_model(Model):
    __table__ = 'judge'
    __pk__ = 'question_qt_id'
    __attr__ = set(['question_qt_id','jd_answer',])
    __insertable__ = set({'question_qt_id','jd_answer',})
    __updateable__ = set({'jd_answer',})
    __notnull__ = set({})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 知识点
class Knowledge_model(Model):
    __table__ = 'knowledge'
    __pk__ = 'kl_id'
    __attr__ = set(['kl_id','kl_name','kl_node',])
    __insertable__ = set({'kl_name','kl_node',})
    __updateable__ = set({'kl_name','kl_node',})
    __notnull__ = set({'kl_name',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 题目表
class Question_model(Model):
    '''2018-08-23 更改：添加了qt_lang字段'''
    __table__ = 'question'
    __pk__ = 'qt_id'
    __attr__ = set(['qt_id','qt_type','qt_stem','qt_use_number','qt_right_number','qt_pre_rate','qt_diffculty','qt_node','knowledge_kl_id','qt_state', 'qt_lang'])
    __insertable__ = set({'qt_type','qt_stem','qt_use_number','qt_right_number','qt_diffculty','qt_node','knowledge_kl_id','qt_state', 'qt_lang'})
    __updateable__ = set({'qt_type','qt_stem','qt_use_number','qt_right_number','qt_diffculty','qt_node','knowledge_kl_id','qt_state', 'qt_lang'})
    __notnull__ = set({'qt_type','qt_stem'})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 题库表
class Questions_bank_model(Model):
    '''2018-08-23 更改：添加了qb_lang字段'''
    __table__ = 'questions_bank'
    __pk__ = 'qb_id'
    __attr__ = set(['qb_id','qb_name','qb_node', 'qb_lang'])
    __insertable__ = set({'qb_name','qb_node', 'qb_lang'})
    __updateable__ = set({'qb_name','qb_node', 'qb_lang'})
    __notnull__ = set({'qb_name'})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 题库包含的题目
class Questions_bank_has_question_model(Model):
    __table__ = 'questions_bank_has_question'
    __pk__ = 'qbhq_id'
    __attr__ = set(['qbhq_id','question_qt_id','questions_bank_qb_id',])
    __insertable__ = set({'question_qt_id','questions_bank_qb_id',})
    __updateable__ = set({'question_qt_id','questions_bank_qb_id',})
    __notnull__ = set({'question_qt_id','questions_bank_qb_id',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 策略表
class Strategy_model(Model):
    __table__ = 'strategy'
    __pk__ = 'sg_id'
    __attr__ = set(['sg_id','sg_name','sg_score','sg_node',])
    __insertable__ = set({'sg_name','sg_score','sg_node',})
    __updateable__ = set({'sg_name','sg_score','sg_node',})
    __notnull__ = set({'sg_name',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 策略项
class Strategy_term_model(Model):
    __table__ = 'strategy_term'
    __pk__ = 'sm_id'
    __attr__ = set(['sm_id','strategy_sg_id','qb_id','sm_type','sm_difficulty_high','sm_difficulty_low','sm_knowledge','sm_number','sm_score',])
    __insertable__ = set({'strategy_sg_id','qb_id','sm_type','sm_difficulty_high','sm_difficulty_low','sm_knowledge','sm_number','sm_score',})
    __updateable__ = set({'strategy_sg_id','qb_id','sm_type','sm_difficulty_high','sm_difficulty_low','sm_knowledge','sm_number','sm_score',})
    __notnull__ = set({'strategy_sg_id',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 学生表
class Student_model(Model):
    __table__ = 'student'
    __pk__ = 'st_id'
    __attr__ = set(['st_id','st_name','st_sex','st_specialty','st_phone','st_picture',])#'student_number','password','islogin','stu_number','sex','name','status','class_id','nation','birthday','card_number','login_name','password',])
    __insertable__ = set({'st_id','st_name','st_sex','st_specialty','st_phone','st_picture',})#'student_number','password','islogin','stu_number','sex','name','status','class_id','nation','birthday','card_number','login_name','password',})
    __updateable__ = set({'st_name','st_sex','st_specialty','st_phone','st_picture',})#'student_number','password','islogin','stu_number','sex','name','status','class_id','nation','birthday','card_number','login_name','password',})
    __notnull__ = set({'st_id','st_name',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 班级包含的学生表
class Student_has_class_model(Model):
    __table__ = 'student_has_class'
    __pk__ = 'shc_id'
    __attr__ = set(['shc_id','student_st_id','class_cl_id',])
    __insertable__ = set({'student_st_id','class_cl_id',})
    __updateable__ = set({'student_st_id','class_cl_id',})
    __notnull__ = set({'student_st_id','class_cl_id',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10


# 教师表
class Teacher_model(Model):
    __table__ = 'teacher'
    __pk__ = 'tc_id'
    __attr__ = set(['tc_id','tc_name','tc_password','tc_level',])
    __insertable__ = set({'tc_id','tc_name','tc_password','tc_level',})
    __updateable__ = set({'tc_name','tc_password','tc_level',})
    __notnull__ = set({'tc_name','tc_password','tc_level',})
    __attrnum__ = len(__attr__)
    __countperpage__ = 10

