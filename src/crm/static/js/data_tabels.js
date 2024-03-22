let lang = {
            
    "decimal":        "",
    "emptyTable":     "داده یافت نشد",
    "info":           "نمایش _START_ تا _END_ از _TOTAL_ سطر",
    "infoEmpty":      "نمایش 0 تا 0 از 0 سطر",
    "infoFiltered":   "(فیلترشده از تمامی _MAX_ سطر)",
    "infoPostFix":    "",
    "thousands":      ",",
    "lengthMenu":     "نمایش _MENU_ سطر",
    "loadingRecords": "بارگذاری...",
    "processing":     "",
    "search":         "جستجو:",
    "zeroRecords":    "داده یافت نشد",
    "paginate": {
        "first":      "ابتدا",
        "last":       "انتها",
        "next":       "بعدی",
        "previous":   "قبلی"
    },
    "aria": {
        "orderable":  "مرتب سازی بر اساس این ستون",
        "orderableReverse": "مرتب سازی معکوس بر اساس این ستون"
    }

}

let informTable = {
    select:false,
    paging:false,
    searching:false,
    info:false,
    language: lang
}
$(document).ready( function () {
    $('#UserTable').DataTable({
        select:true,
        paging:true,
        direction:"right",
        language: lang
    });
    $('#AddressesTable').DataTable(informTable);
    $('#PhoneNumbersTable').DataTable(informTable);
    $('#ClientPaymentsTable').DataTable(informTable);
    $('#ClientServicesTable').DataTable(informTable);
    $('#ClientCallsTable').DataTable(informTable);

    
    $('.dataTable').find('td, th').css('text-align', 'right');

     
} );