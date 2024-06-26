function findTabTabels() {
    tables = $("[id^='tab-table-']")
    tables.each(function () {
        $(this).DataTable({...tabTable,  order:[]})
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

    $('#preview-contract').DataTable({...informTable, order:[]});
    $('#preview-contract_wrapper').addClass("w-full")

    // persianize
    $('.dataTable').find('td, th').css('text-align', 'right');

    // make table flexible (remove static width)
    $('.dataTable').each(function(){
        $(this).removeAttr("style", "width")
    })

    $("table.dataTable tr[data-link]").addClass("cursor-pointer")
    
    $(document).on('click', "[id^='tab-button']", function () {
        if ($(this).hasClass("open-tab")){
            return
        }
        newTabCounter = $(this).attr("id").match(/\d+/)[0]
        currentTabCounter = $("[id^='tab-button'][class*='open-tab']").attr("id").match(/\d+/)[0]

        // deactive current tab
        $(`#tab-button-${currentTabCounter}`).removeClass("open-tab bg-white")
        $(`#tab-button-${currentTabCounter}`).addClass("closed-tab bg-slate-300 mt-2")



        // hide current tab container 
        $(`#tab-container-${currentTabCounter}`).addClass("hidden")
        
        // active new tab 
        $(this).removeClass("closed-tab bg-slate-300  mt-2")
        $(this).addClass("open-tab bg-white")
        
        // show new tab container 
        $(`#tab-container-${newTabCounter}`).removeClass("hidden")
        
    });
    
    // initiaing selected tab
    let selectedTab = $("#selected-tab").val()
    if (selectedTab) 
        {
            $(`[name="${selectedTab}-tab"]`).trigger("click")
        }
} );