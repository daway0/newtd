const requiredClientInputsValidator = {
  // input id: array of validators
  // "national-code": [notEmptyInputValidator, isDigitValidator],
  "firstname": [notEmptyInputValidator],
  "lastname": [notEmptyInputValidator],
  "birthdate": [notEmptyInputValidator, dateValidator],
  "TEMPphone-number": [notEmptyInputValidator, isDigitValidator],
  "TEMPservice-location": [notEmptyInputValidator],
}

const nonRequiredClientInputsValidator = {
  // there is no need for these input to check notEmptyInputValidator
  "TEMPphone-number-note": [],
  "TEMPservice-location-note": [],
}


const clientAdvancedValidators = [
  {
    element: $("#female"),
    validators: [genderSelection],
  }
]
const mustBeSelect2 = []


$(document).ready(function () {


  // form save btn
  $(document).on('click', ".form-save", function () {
    // remove all previous error msgs and error styles
    flushFormErrorStyles()
    flushFormErrorDisplay()

    const validationResault = isFormValid(
      requiredClientInputsValidator,
      nonRequiredClientInputsValidator,
      clientAdvancedValidators)

    const formValid = validationResault.res
    const formError = validationResault.errors

    if (!formValid) {
      showFormInputErrors(formError)
      return;
    }



    // if code reachs this step it means client validation is done!
    // so remove all error style and must remove all displayed error msgs

    flushFormErrorStyles()
    flushFormErrorDisplay()


    // send data to server
    // First, we need to gather data

    let dataCallBacks = {
      national_code: () => $("#national-code").val(),
      firstname: () => $("#firstname").val(),
      lastname: () => $("#lastname").val(),
      birthdate: () => $("#birthdate").val(),
      gender: () => $("#male").is(":checked") ? "M" : "F",
      numbers: () => {
        value = []
        $(".numbers-section .form-row-container").each(function () {
          const number = $(this).find(".phone-number").val().trim()
          const note = $(this).find(".phone-number-note").val().trim()
          value.push(
            {
              number: number,
              note: note || null
            }
          )
        })
        return value
      },
      service_locations: () => {
        value = []
        $(".service-location-section .form-row-container").each(function () {
          const location = $(this).find(".service-location").val().trim()
          const note = $(this).find(".service-location-note").val().trim()
          value.push(
            {
              location: location,
              note: note || null
            }
          )
        })
        return value
      },
      
    }

    let data = {}
    for (const key in dataCallBacks){
      data[key] = dataCallBacks[key]()
      console.log(key);
      console.log(dataCallBacks[key]())
    }
    success_toast("ثبت موفق", "اطلاعات با موفقیت در پایگاه داده ذخیره شد")
  });



  $('#add-phone-number').trigger("click")
  $('#add-service-location').trigger("click")


})









