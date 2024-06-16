-- title: People
select  * FROM crm_people cp WHERE cp.id = 21;

-- title: Phone Number
select
	cp.*
from
	crm_peopledetailedinfo cp
inner join
    crm_people cp21 on
	cp.people_id = cp21.id
where
	cp.detail_type = 'P'
	and cp21.id = 21;

-- title: Addresses
select
	cp.*
from
	crm_peopledetailedinfo cp
inner join
    crm_people cp21 on
	cp.people_id = cp21.id
where
	cp.detail_type = 'A'
	and cp21.id = 21;

-- title: Card Number
select
	cp.*
from
	crm_peopledetailedinfo cp
inner join
    crm_people cp21 on
	cp.people_id = cp21.id
where
	cp.detail_type = 'C'
	and cp21.id = 21;

-- title: Roles
select
	cc.title 
from
	crm_peoplerole cp21 
	inner join crm_people cp on
	cp21.people_id = cp.id
inner join crm_catalog cc on
	cp21.catalog_id = cc.id
where
	cp.id = 21;

-- title: Service Location
select
	cc.title 
from
	crm_servicelocation cs  
	inner join crm_people cp on
	cs.people_id = cp.id
inner join crm_catalog cc on
	cs.catalog_id = cc.id
where
	cp.id = 21;


-- title: Tags
select
	cc.title
from
	crm_specification cs
inner join crm_people cp on
	cs.people_id = cp.id
inner join crm_catalog cc on
	cs.catalog_id = cc.id and cc.code not like 'SKL_%'
where
	cp.id = 21;

-- title: skills
select
	cc.title, cs.rate
from
	crm_specification cs
inner join crm_people cp on
	cs.people_id = cp.id
inner join crm_catalog cc on
	cs.catalog_id = cc.id and cc.code like 'SKL_%'
where
	cp.id = 21;
