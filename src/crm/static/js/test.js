

// set the modal menu element
const peopleCreationTrigger = document.getElementById('people-creation-modal');

// options with default values
const options = {
  placement: 'center',
  backdrop: 'dynamic',
  backdropClasses: 'bg-gray-900/50 dark:bg-gray-900/80 fixed inset-0 z-40',
  closable: true
};


const peopleCreationModal = new Modal(peopleCreationTrigger, options);


$(document).ready(function () {
    $(document).on('click', "#people-creation-modal-trigger", function () {
        peopleCreationModal.show()
    });
    $(document).on('input', "#identification", function () {
        let identificationLen = $(this).val().length
        if (identificationLen == 10){
            $.ajax(
                {
                    url: url,
                }
            ).done(function (data) {
                
            })
        }
    });
    
})