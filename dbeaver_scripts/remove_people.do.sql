do
$$
    declare
        v_people_id                      crm_people.id%TYPE;
        v_people_full_name               varchar;
        v_people_national_code           crm_people.national_code%TYPE = '0023403616';
        v_tables_have_people_id constant varchar[]=array [
            'crm_specification',
            'crm_servicelocation',
            'crm_peopletype',
            'crm_peoplerole',
            'crm_peopledetailedinfo'];
        v_table_have_people_id           varchar;
        v_dynamic_query                  text;
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

        foreach v_table_have_people_id in array v_tables_have_people_id
            loop
                v_dynamic_query = 'delete from ' || v_table_have_people_id || ' where people_id =' || v_people_id;
                execute v_dynamic_query;
                raise notice '% table data related deleted', v_table_have_people_id;
            end loop;

        delete
        from crm_people
        where id = v_people_id;
        raise notice 'people deleted';
    end;
$$