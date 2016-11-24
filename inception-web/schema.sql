create database if not exists sqlaudit;

use sqlaudit;
drop table if exists inception_log;
create table inception_log (
	id int not null auto_increment comment '主键ID',
	dbinstance varchar(32) not null comment '数据库实例(IP:PORT)',
	dbname varchar(32) not null comment '数据库名',
	ioutput text not null comment 'Inception输出结果',
	optime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP comment '成功执行的时间',
	primary key (id)
) engine=innodb default charset=utf8 comment '各业务数据库上线记录表';

drop table if exists operator_log;
create table operator_log (
	id int not null auto_increment comment '主键ID',
	operator varchar(16) not null comment '执行人姓名',
	redmineissue varchar(16) not null comment 'Redmine工单号',
	errlevel tinyint not null comment '错误类型：0-执行成功，1-审核未通过但不影响执行，2-语法错误',
	errmsg text not null comment '审核建议及错误信息',
	audittime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP comment '每次提交审核的时间',
	primary key (id)
) engine=innodb default charset=utf8 comment '执行人审核记录表';

drop table if exists dyncode;
create table dyncode (
	id int not null auto_increment comment '主键ID',
	code int not null comment '动态登录码（UNIX时间戳-秒数）',
	ctime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP comment '创建时间',
	primary key (id)
) engine=innodb default charset=utf8 comment '动态登录码生成表';
