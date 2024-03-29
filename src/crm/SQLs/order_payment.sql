SELECT row_number() OVER (ORDER BY co.id) AS id,
    co.id AS order_id,
    services.order_cost AS cost_without_discount,
    services.order_cost - co.discount::numeric AS cost,
    services.order_healthcare_franchise_cost - co.discount::numeric AS healthcare_franchise,
    services.order_personnel_franchise_cost AS personnel_fee,
    COALESCE(sum(personnel_payment.personnel_paid), 0::numeric) AS personnel_paid,
    COALESCE(sum(client_payment.client_paid), 0::numeric) AS client_paid,
    services.order_personnel_franchise_cost - COALESCE(sum(personnel_payment.personnel_paid), 0::numeric) AS personnel_debt,
    services.order_cost - co.discount::numeric - COALESCE(sum(client_payment.client_paid), 0::numeric) AS client_debt
   FROM crm_order co
     JOIN ( SELECT co_1.order_id,
            sum(co_1.service_healthcare_franchise_cost) AS order_healthcare_franchise_cost,
            sum(co_1.service_personnel_franchise_cost) AS order_personnel_franchise_cost,
            sum(co_1.cost) AS order_cost
           FROM ( SELECT co2.order_id,
                    co2.cost,
                    cs.id,
                    co2.cost / 100 * cs.healthcare_franchise AS service_healthcare_franchise_cost,
                    co2.cost - co2.cost / 100 * cs.healthcare_franchise AS service_personnel_franchise_cost
                   FROM crm_orderservices co2
                     JOIN crm_service cs ON cs.id = co2.service_id) co_1
          GROUP BY co_1.order_id) services ON services.order_id = co.id
     LEFT JOIN ( SELECT cp.order_id,
            sum(cp.amount) AS client_paid
           FROM crm_payment cp
          WHERE cp.destination_id IS NULL
          GROUP BY cp.order_id) client_payment ON co.id = client_payment.order_id
     LEFT JOIN ( SELECT cp.order_id,
            sum(cp.amount) AS personnel_paid
           FROM crm_payment cp
          WHERE cp.source_id IS NULL
          GROUP BY cp.order_id) personnel_payment ON co.id = personnel_payment.order_id
  GROUP BY co.id, services.order_cost, (services.order_cost - co.discount::numeric), (services.order_healthcare_franchise_cost - co.discount::numeric), services.order_personnel_franchise_cost;