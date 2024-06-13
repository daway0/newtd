do
$$
    declare
        v_people_id            crm_people.id%TYPE;
        v_people_full_name     varchar;
        v_people_national_code crm_people.national_code%TYPE = '0023403618';
    begin
        select id
        into v_people_id
        from crm_people
        where national_code = v_people_national_code;

        if v_people_id is null then
            raise notice '404';
            return;
        end if;

        select concat(firstname, ' ', lastname)
        into v_people_full_name
        from crm_people
        where id = v_people_id;

        raise notice 'The People Was: %', v_people_full_name;

        delete
        from crm_specification
        where people_id = v_people_id;
        raise notice 'crm_specification deleted';

        delete
        from crm_servicelocation
        where people_id = v_people_id;
        raise notice 'crm_servicelocation deleted';

        delete
        from crm_peopletype
        where people_id = v_people_id;
        raise notice 'crm_peopletype deleted';

        delete
        from crm_peoplerole
        where people_id = v_people_id;
        raise notice 'crm_peoplerole deleted';

        delete
        from crm_peopledetailedinfo
        where people_id = v_people_id;
        raise notice 'crm_peopledetailedinfo deleted';

        delete
        from crm_people
        where id = v_people_id;
        raise notice 'people deleted';

    end;
$$
