function findTabTabels() {
    tables = $("[id^='tab-table-']")
    tables.each(function () {
        $(this).DataTable(tabTable)
    })
}

function hideAllTabExceptFirst() {
    $("[id^='tab-container-']").each(function () {
        $(this).addClass("hidden")
    })
    $("[id^='tab-container-0']").removeClass("hidden")
}
$(document).ready( function () {
    findTabTabels()
    hideAllTabExceptFirst()
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

    // persianize
    $('.dataTable').find('td, th').css('text-align', 'right');

    // make table flexible (remove static width)
    $('.dataTable').each(function(){
        $(this).removeAttr("style", "width")
    })

    $(document).on('click', "[id^='tab-button']", function () {
        if ($(this).hasClass("open-tab")){
            return
        }
        newTabCounter = $(this).attr("id").match(/\d+/)[0]
        currentTabCounter = $("[id^='tab-button'][class*='open-tab']").attr("id").match(/\d+/)[0]

        // deactive current tab
        $(`#tab-button-${currentTabCounter}`).removeClass("open-tab bg-white")
        $(`#tab-button-${currentTabCounter}`).addClass("closed-tab bg-slate-300")



        // hide current tab container 
        $(`#tab-container-${currentTabCounter}`).addClass("hidden")
        
        // active new tab 
        $(this).removeClass("closed-tab bg-slate-300")
        $(this).addClass("open-tab bg-white")
        
        // show new tab container 
        $(`#tab-container-${newTabCounter}`).removeClass("hidden")
        
    });
     
} );