const requiredClientInputsValidator = {
  // input id: array of validators
  "national-code": [notEmptyInputValidator, isDigitValidator],
  "firstname": [notEmptyInputValidator],
  "lastname": [notEmptyInputValidator],
  "joined-date": [notEmptyInputValidator, dateValidator],
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

const inputCallBacks = {
  national_code: {
      get: () => $("#national-code").val().trim(),
      set: (value) => $("#national-code").val(value)
  },
  firstname: {
      get: () => $("#firstname").val().trim(),
      set: (value) => $("#firstname").val(value)
  },

  lastname: {
      get: () => $("#lastname").val().trim(),
      set: (value) => $("#lastname").val(value)
  },
  birthdate: {
      get: () => convertPersianDigitsToEnglish($("#birthdate").val()),
      set: (value) => $("#birthdate").val(convertPersianDigitsToEnglish(value))
  },
  joined_at: {
      get: () => convertPersianDigitsToEnglish($("#joined-date").val()),
      set: (value) => $("#joined-date").val(convertPersianDigitsToEnglish(value))
  },
  gender: {
      get: () => $("#male").is(":checked") ? "M" : "F",
      set: (value) => {
          if (value) value === "F" ? $("#female").prop("checked", true) : $("#male").prop("checked", true)
      }
  },
  numbers: {
      get: () => {
          let value = []
          $(".numbers-section .form-row-container").each(function () {
              const number = $(this).find(".phone-number").val().trim()
              const note = $(this).find(".phone-number-note").val().trim()
              const id = $(this).find(".phone-number").attr("data-key")

              let obj = { value: number }
              if (note) obj.note = note
              if (id) obj.id = id

              value.push(obj)
          })
          return value
      },
      set: (numbers) => {
          for (numberObj of numbers) {
              $('#add-phone-number').trigger("click")
              $(".numbers-section .form-row-container").each(function () {
                  let numberInput = $(this).find(".phone-number")
                  if (!numberInput.val()) {
                      numberInput.val(numberObj.value)
                      numberInput.attr("data-key", numberObj.id)
                      $(this).find(".phone-number-note").val(numberObj.note)
                  }
              })
          }
      }
  },
  addresses: {
      get: () => {
          let value = []
          $(".service-locations-section .form-row-container").each(function () {
              const address = $(this).find(".service-location").val().trim()
              const note = $(this).find(".service-location-note").val().trim()
              const id = $(this).find(".service-location").attr("data-key")

              let obj = { value: address }
              if (note) obj.note = note
              if (id) obj.id = id

              value.push(obj)
          })
          return value
      },
      set: (service_locations) => {
          for (slObj of service_locations) {
              $('#add-service-location').trigger("click")
              $(".service-locations-section .form-row-container").each(function () {
                  let addressInput = $(this).find(".service-location")
                  if (!addressInput.val()) {
                      addressInput.val(slObj.value)
                      addressInput.attr("data-key", slObj.id)
                      $(this).find(".service-location-note").val(slObj.note)
                  }
              })
          }
      }
  }
}


$(document).ready(function () {

  $("#joined-date").pDatepicker({
      format: "L",
      autoClose: true,
      initialValue: true,
      persianDigit: false
  });


  const peopleId = $("#people-id").val()

  if (peopleId) {
      $("#national-code").attr("disabled", true)
  }

  if (peopleId) {
      // if state edit now go and fetch data 
      // Second send data to server
      $.ajax({
          url: apiUrls.clientEdit + `${peopleId}/`,
          type: 'GET',
          contentType: 'application/json',
          success: function (data) {
              console.log(data)
              for (const key in inputCallBacks) {
                  if (inputCallBacks[key].set) {
                      inputCallBacks[key].set(data[key])
                  }
                  console.log(key);
              }
          },
          error: function (xhr, status, error) {
              error_toast("خطا هنگام  دریافت اطلاعات", "خطایی در سرور رخ داده است")
              console.error('Error:', xhr.responseJSON);
          }
      });
  } else {
      $('#add-service-location').trigger("click")
      $('#add-phone-number').trigger("click")
  }


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
      // First, we need to gather data and transform it.



      let data = {}
      for (const key in inputCallBacks) {
          const val = inputCallBacks[key].get()
          if (val) data[key] = val
          console.log(key);
          console.log(inputCallBacks[key].get());
      }

      data.types = ["TYP_CLIENT"]
      if (peopleId) {
          data.person_id = peopleId
      }

      // Second send data to server
      $.ajax({
          url: apiUrls.personnelInitiate,
          type: 'POST',
          contentType: 'application/json',
          data: JSON.stringify(data),
          success: function (data) {

              success_toast("ثبت موفق", "اطلاعات با موفقیت در پایگاه داده ذخیره شد")
              // redirectTo(apiUrls.peopleSection)

          },
          error: function (xhr, status, error) {
              error_toast("خطا", "خطایی در سرور رخ داده است")
              console.error('Error:', xhr.responseJSON);
          }
      });
  });



})
