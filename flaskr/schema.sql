drop table if exists user;
drop table if exists article;
--
--  user
--
create table user (
	id integer primary key autoincrement,
	name string not null,
	password string not null
);

--
-- article
--
create table article (
	id integer primary key autoincrement,
	title string not null,
	text strinnot null,
	author_id integer,
	foreign key(author_id) references user(id)
);