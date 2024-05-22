let lang = {

    "decimal": "",
    "emptyTable": "داده یافت نشد",
    "info": "نمایش _START_ تا _END_ از _TOTAL_ سطر",
    "infoEmpty": "نمایش 0 تا 0 از 0 سطر",
    "infoFiltered": "(فیلترشده از تمامی _MAX_ سطر)",
    "infoPostFix": "",
    "thousands": ",",
    "lengthMenu": "نمایش _MENU_ سطر",
    "loadingRecords": "بارگذاری...",
    "processing": "",
    "search": "جستجو:",
    "zeroRecords": "داده یافت نشد",
    "paginate": {
        "first": "ابتدا",
        "last": "انتها",
        "next": "بعدی",
        "previous": "قبلی"
    },
    "aria": {
        "orderable": "مرتب سازی بر اساس این ستون",
        "orderableReverse": "مرتب سازی معکوس بر اساس این ستون"
    }

}

let informTable = {
    select: false,
    paging: false,
    searching: false,
    info: false,
    language: lang
}

let tabTable = {
    language: lang
}



function customized_toast(obj) {
    const baseObj = {
        position: 'bottom-left',
        textAlign: 'right',
        hideAfter: 4000,
        showHideTransition: 'slide',
        allowToastClose: false
    }
    $.toast({...obj,...baseObj })
}

function success_toast(heading, text) {
    customized_toast({
        heading: `<b>${heading}</b>`,
        text:text,
        icon: "success"
    })
}
function info_toast(heading, text) {
    customized_toast({
        heading: `<b>${heading}</b>`,
        text:text,
        icon: "info"
    })
}
function error_toast(heading, text) {
    customized_toast({
        heading: `<b>${heading}</b>`,
        text:text,
        icon: "error"
    })
}
function warning_toast(heading, text) {
    customized_toast({
        heading: `<b>${heading}</b>`,
        text:text,
        icon: "warning"
    })
}