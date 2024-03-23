$(document).ready( function () {
    $(document).on('click', '#sidemenu, #sidemenu-minimized', function () {
        $("#sidemenu").toggleClass("hidden")
        $("#sidemenu-minimized").toggleClass("hidden")
        
    });
    $(document).on('click', '.menu-item', function () {
        $("#sidemenu").toggleClass("hidden")
        $("#sidemenu-minimized").toggleClass("hidden")
    });
})