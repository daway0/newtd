const requiredPersonnelInputsValidator = {
  // input id: array of validators
  // "national-code": [notEmptyInputValidator, isDigitValidator],
  "firstname": [notEmptyInputValidator],
  "lastname": [notEmptyInputValidator],
  "birthdate": [notEmptyInputValidator, dateValidator],
  "contract-start": [notEmptyInputValidator, dateValidator],
  "TEMPphone-number": [notEmptyInputValidator, isDigitValidator],
  "active-card-number": [notEmptyInputValidator, isDigitValidator, cardNumberValidator],
  "joined-date": [notEmptyInputValidator, dateValidator],
}

const nonRequiredPersonnelInputsValidator = {
  // there is no need for these input to check notEmptyInputValidator
  "address": [],
  "contract-end": [dateValidator],
  "TEMPphone-number-note": [],
  "TEMPskill-pts": [isDigitValidator]
}


const personnelAdvancedValidators = [
  {
    element: $("#contract-start"),
    validators: [contractDurationValidator],
  },
  {
    element: $("#personnel-role"),
    validators: [personnelRole],
  },
  {
    element: $("#female"),
    validators: [genderSelection],
  },
  // {
  // element: $("#skill"),
  // validators: [skillDuplication],
  // }

]

const mustBeSelect2 = [
  {
    id: "skill",
    qTerm: "SKL"
  }
]


const inputCallBacks = {
  national_code: {
    get: () => $("#national-code").val().trim(),
    set: (value) => $("#national-code").val(value)
  },
  first_name: {
    get: () => $("#firstname").val().trim(),
    set: (value) => $("#firstname").val(value)
  },

  last_name: {
    get: () => $("#lastname").val().trim(),
    set: (value) => $("#lastname").val(value)
  },
  birthdate: {
    get: () => convertPersianDigitsToEnglish($("#birthdate").val()),
    set: (value) => $("#birthdate").val(convertPersianDigitsToEnglish(value))
  },
  addresses: {
    get: () => {
      const address = $("#address").val().trim()
      if (address) {
        return [{
          value: address,
        }]
      }
      return null
    },
    set: (data) => {
      $("#address").val(data.address)
    }
  },
  card_number: {
    get: () => {
      const card_number = $("#active-card-number").val().trim()
      if (card_number) {
        return {
          value: card_number,
        }
      }
      return null
    },
    set: (data) => {
      $("#active-card-number").val(data.card_number)
    }
  },
  joined_at: {
    get: () => convertPersianDigitsToEnglish($("#joined-date").val()),
    set: (value) => $("#joined-date").val(convertPersianDigitsToEnglish(value))
  },

  contract_date: {
    get: () => convertPersianDigitsToEnglish($("#contract-start").val()),
    set:  () => $("#contract-start").val(convertPersianDigitsToEnglish(value))
  },
  end_contract_date: {
    get: () => convertPersianDigitsToEnglish($("#contract-end").val()) || null,
    set:  () => $("#contract-end").val(convertPersianDigitsToEnglish(value))
  },
  gender: {
    get: () => $("#male").is(":checked") ? "M" : "F",
    set: (value) => {
      value==="F" ? $("#female").prop("checked", true) : $("#male").prop("checked", true)
    }
  },
  tags: {
    get: () => $(".tags-select2").val(),
    set: (value) => {
      $(".tags-select2").val(value).trigger('change')
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
      for (numberObj of numbers){
        $('#add-phone-number').trigger("click")
        $(".numbers-section .form-row-container").each(function () {
          let numberInput = $(this).find(".phone-number")
          if (!numberInput.val()) {
            numberInput.val(numberObj.number)
            numberInput.attr("data-key", numberObj.id)
            $(this).find(".phone-number-note").val(numberObj.note)
          }
        })
      }
    }
  },
  roles: {
    get: () => $(".personnel-role-select2").val(),
    set: (value) => {
      $(".personnel-role-select2").val(value).trigger('change')
    }
  },
  service_locations: {
    get: () => $(".service-locations-select2").val(),
    set: (value) => {
      $(".service-locations-select2").val(value).trigger('change')
    }
  },
  skills: {
    get: () => {
      let value = []
      $(".form-row-container.skill-section").each(function () {
        const skill = $(this).find(".skill").val().trim()
        const pts = $(this).find(".skill-pts").val().trim()
        value.push(
          {
            skill: skill,
            pts: pts
          }
        )
      })
      return value
    },
    set: null
  },
}



// const select2Roles = {
//   data: catalogDataSelect2(q="ROLE")
// }
// const select2ServiceLocations = {
//   data: catalogDataSelect2(q="LOC")
// }
// const selec2Roles = {
//   data: transformCatalogToSelect2()
//   ajax: {
//     url: apiUrls.catalog,
//     data: {
//       q: "ROLE"
//     },
//     dataType: 'json',
//     processResults: transformCatalogToSelect2
//   }
// }

// const selec2ServiceLocations = {
//   ajax: {
//     url: apiUrls.catalog,
//     data: {
//       q: "LOC"
//     },
//     dataType: 'json',
//     processResults: transformCatalogToSelect2
//   }
// }

$(document).ready(function () {

  $("#joined-date").pDatepicker({
    format: "L",
    autoClose: true,
    initialValue: true,
    persianDigit:false
  });

  catalogDataSelect2("ROLE")
    .then(function (roleData) {
      const select2Roles = {
        data: transformCatalogToSelect2(roleData)
      };
      $('.personnel-role-select2').select2({ ...select2Roles, ...select2Props });
    })
    .catch(function (error) {
      console.error('Failed to load roles data:', error);
    });

    catalogDataSelect2("LOC")
    .then(function (locationData) {
      const select2ServiceLocations = {
        data: transformCatalogToSelect2(locationData)
      };
      $('.service-locations-select2').select2({ ...select2ServiceLocations, ...select2Props });
    })
    .catch(function (error) {
      console.error('Failed to load service locations data:', error);
    });

    catalogDataSelect2("TAG")
    .then(function (tagData) {
      const select2Tags = {
        data: transformCatalogToSelect2(tagData)
      };
      $('.tags-select2').select2({ ...select2Tags, ...select2Props });
    })
    .catch(function (error) {
      console.error('Failed to load tags data:', error);
    });

    // form save btn
  $(document).on('click', ".form-save", function () {
    // remove all previous error msgs and error styles
    flushFormErrorStyles()
    flushFormErrorDisplay()

    const validationResault = isFormValid(
      requiredPersonnelInputsValidator,
      nonRequiredPersonnelInputsValidator,
      personnelAdvancedValidators)

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

    data.types = ["personnel"]

    // Second send data to server
    $.ajax({
      url: apiUrls.personnelInitiate,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(data),
      success: function (response) {
        success_toast("ثبت موفق", "اطلاعات با موفقیت در پایگاه داده ذخیره شد")
      },
      error: function (xhr, status, error) {
        error_toast("خطا", "خطایی در سرور رخ داده است")
        console.error('Error:', xhr.responseJSON);
      }
    });
  });

  // check if form is in edit state
  const peopleId = $("#people-id").val()
  if (peopleId) {
    // if state edit now go and fetch data 
    // Second send data to server
    // $.ajax({
    //   url: apiUrls.personnelInitiate,
    //   type: 'POST',
    //   contentType: 'application/json',
    //   data: JSON.stringify(data),
    //   success: function (response) {
    //     success_toast("ثبت موفق", "اطلاعات با موفقیت در پایگاه داده ذخیره شد")
    //   },
    //   error: function (xhr, status, error) {
    //     error_toast("خطا", "خطایی در سرور رخ داده است")
    //     console.error('Error:', xhr.responseJSON);
    //   }
    // });
    alert(peopleId)
    for (const key in inputCallBacks) {
      const val = inputCallBacks[key].set()
      
      console.log(key);
    }
  } else {
    $('#add-phone-number').trigger("click")
  }
  


    

  

  


  


  $('#add-phone-number').trigger("click")

})






