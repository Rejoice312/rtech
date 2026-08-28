create table subscribers(
    id serial primary key,
    full_name varchar(40),
    email varchar(40),
    courses varchar(40),
    occupation varchar(40),
    goal varchar(40),
    phone varchar(20),
    country varchar(40),
    sub_timestamp timestamp
);


create table users(
    id serial primary key,
    full_name varchar(40) not null,
    email varchar(50) not null,
    country varchar(40) not null,
    password_hash text not null,
    signup_timestamp timestamp,
    role varchar(15) default 'user',
    resume text not null,
    balance float default 0,
    linkedin varchar(60) not null,
    portfolio varchar(60),
    verified boolean default false,
    verification_token varchar(60),
    application_email varchar(50),

    check(balance >= 0),
    check(role in ('user', 'admin'))
);


create table txns(
    id serial primary key,
    txn_ref varchar(60) not null,
    amount float not null,
    user_id int not null,
    type varchar(10) not null,
    description varchar(100),
    txn_timestamp timestamp not null,
    status varchar(10),

    check(type in ('debit', 'credit')),
    check(status in ('pending', 'successful', 'failed')),
    foreign key (user_id) references users(id)
        on delete cascade
);

create table applications(
    id serial primary key,
    job_title varchar(20),
    organization varchar(20),
    job_description text not null,
    application_timestamp timestamp not null,
    user_id int not null,
    resume varchar(100) not null,

    foreign key (user_id) references users(id)
        on delete cascade
);