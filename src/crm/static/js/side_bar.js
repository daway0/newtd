$(document).ready( function () {

    var menuState = localStorage.getItem("menuState")

    if (menuState == "open" || menuState == null){
        $("#sidemenu-minimized").addClass("hidden")
        $("#sidemenu").removeClass("hidden")
    }
    if(menuState == "closed"){
        $("#sidemenu").addClass("hidden")
        $("#sidemenu-minimized").removeClass("hidden")
    }

    $(document).on('click', '#sidemenu, #sidemenu-minimized', function () {
        $("#sidemenu").toggleClass("hidden")
        $("#sidemenu-minimized").toggleClass("hidden")

        if ($("#sidemenu").hasClass("hidden")) {
            localStorage.setItem("menuState",  "closed");  
        }else{
            localStorage.setItem("menuState", "open");
        }
        
    });
    $(document).on('click', '.menu-item', function () {
        $("#sidemenu").toggleClass("hidden")
        $("#sidemenu-minimized").toggleClass("hidden")
    });
    
})
