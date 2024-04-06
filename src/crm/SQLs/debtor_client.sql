SELECT row_number() OVER (ORDER BY cp.id) AS id,
    cp.id AS client_id,
    concat(cp.firstname, ' ', cp.lastname) AS full_name,
    COALESCE(sum(op.client_debt), 0::numeric) AS order_debt,
    COALESCE(cc.debt, 0::bigint) AS contract_debt,
    COALESCE(sum(op.client_debt) + COALESCE(cc.debt, 0::bigint)::numeric, 0::numeric) AS total_debt
   FROM order_payment op
     JOIN crm_order co ON co.id = op.order_id
     JOIN crm_people cp ON cp.id = co.client_id
     LEFT JOIN ( SELECT cp1.id,
            sum(cc1.healthcare_franchise_amount) AS debt
           FROM crm_contract cc1
             JOIN crm_people cp1 ON cc1.client_id = cp1.id
          GROUP BY cp1.id) cc ON cc.id = cp.id
  GROUP BY cp.id, co.client_id, (concat(cp.firstname, ' ', cp.lastname)), cc.debt
  ORDER BY (COALESCE(sum(op.client_debt) + COALESCE(cc.debt, 0::bigint)::numeric, 0::numeric)) DESC;