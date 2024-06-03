-- title: People
select  * FROM crm_people cp WHERE cp.id = 20;

-- title: Phone Number
select
	cp.*
from
	crm_peopledetailedinfo cp
inner join
    crm_people cp2 on
	cp.people_id = cp2.id
where
	cp.detail_type = 'P'
	and cp2.id = 20;

-- title: Addresses
select
	cp.*
from
	crm_peopledetailedinfo cp
inner join
    crm_people cp2 on
	cp.people_id = cp2.id
where
	cp.detail_type = 'A'
	and cp2.id = 20;

-- title: Card Number
select
	cp.*
from
	crm_peopledetailedinfo cp
inner join
    crm_people cp2 on
	cp.people_id = cp2.id
where
	cp.detail_type = 'C'
	and cp2.id = 20;

-- title: Roles
select
	cc.title 
from
	crm_peoplerole cp2 
	inner join crm_people cp on
	cp2.people_id = cp.id
inner join crm_catalog cc on
	cp2.catalog_id = cc.id
where
	cp.id = 20;

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
	cp.id = 20;


-- title: Tags
select
	cc.title
from
	crm_specification cs
inner join crm_people cp on
	cs.people_id = cp.id
inner join crm_catalog cc on
	cs.catalog_id = cc.id
where
	cp.id = 20;
