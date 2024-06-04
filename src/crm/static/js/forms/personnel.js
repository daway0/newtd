const requiredPersonnelInputsValidator = {
  // input id: array of validators
  "national-code": [notEmptyInputValidator, isDigitValidator],
  "firstname": [notEmptyInputValidator],
  "lastname": [notEmptyInputValidator],
  "birthdate": [notEmptyInputValidator, dateValidator],
  "contract-start": [notEmptyInputValidator, dateValidator],
  "TEMPphone-number": [notEmptyInputValidator, isDigitValidator],
  "active-card-number": [notEmptyInputValidator, isDigitValidator, cardNumberValidator],
  "joined-date": [notEmptyInputValidator, dateValidator],
  "TEMPskill-pts": [notEmptyInputValidator,isDigitValidator],
  "TEMPskill": [notEmptyMultipleSelect2Validator]
}

const nonRequiredPersonnelInputsValidator = {
  // there is no need for these input to check notEmptyInputValidator
  "address": [],
  "contract-end": [dateValidator],
  "TEMPphone-number-note": [],
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
  addresses: {
    get: () => {
      const address = $("#address").val().trim()
      const id = $("#address").attr("data-key")
      if (address) {
        let dataObj = { value: address }
        if (id) dataObj.id = id
        return [dataObj]
      }
      return null
    },
    set: (data) => {
      const address = data[0]
      if (address) {
        $("#address").val(address.value)
        $("#address").attr("data-key", address.id)
      }

    }
  },
  card_number: {
    get: () => {
      const card_number = $("#active-card-number").val().trim()
      const id = $("#active-card-number").attr("data-key")
      if (card_number) {
        let dataObj = { value: card_number }

        if (id) dataObj.id = id
        return dataObj
      }
      return null
    },
    set: (data) => {
      if (data) {
        $("#active-card-number").val(data.value)
        $("#active-card-number").attr("data-key", data.id)
      }
    }
  },
  joined_at: {
    get: () => convertPersianDigitsToEnglish($("#joined-date").val()),
    set: (value) => $("#joined-date").val(convertPersianDigitsToEnglish(value))
  },

  contract_date: {
    get: () => convertPersianDigitsToEnglish($("#contract-start").val()),
    set: (value) => $("#contract-start").val(convertPersianDigitsToEnglish(value))
  },
  end_contract_date: {
    get: () => convertPersianDigitsToEnglish($("#contract-end").val()) || null,
    set: (value) => $("#contract-end").val(convertPersianDigitsToEnglish(value))
  },
  gender: {
    get: () => $("#male").is(":checked") ? "M" : "F",
    set: (value) => {
      if (value) value === "F" ? $("#female").prop("checked", true) : $("#male").prop("checked", true)
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
        const skills = $(this).find(".skill").val()
        const pts = $(this).find(".skill-pts").val().trim()

        for (skill of skills) {
          value.push(
            {
              id: skill,
              rate: pts
            }
          )
        }
      })
      return value
    },
    set: (skills) => {
      let skillsRate = {}
      for (skillObj of skills) {
        const rateKey = String(skillObj.rate)
        if (!(rateKey in skillsRate)) {
          skillsRate[rateKey] = []
        }
        skillsRate[rateKey].push(String(skillObj.id))
      }

      for (const rate in skillsRate) {
        $('#add-skill').trigger("click")

        $(".skills-section .form-row-container").each(function () {
          if ($(this).is($(".skills-section > div:nth-child(2) > div:nth-child(1)"))) return true
          let skillSelect = $(this).find(".skill")
          let skillRate = $(this).find(".skill-pts")
          if (skillSelect.val().length === 0) {
            skillSelect.val(skillsRate[rate]).trigger("change")
            skillRate.val(rate)
          }
        })
      }
    }
  },
}


function getOverlappingValues(array1, array2) {
  const set2 = new Set(array2);
  return array1.filter(item => set2.has(item));
}

function differentiateArrays(arr1, arr2) {
  const diff1 = arr1.filter(x => !arr2.includes(x));
  const diff2 = arr2.filter(x => !arr1.includes(x));
  return { diff1, diff2 };
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
  const peopleId = $("#people-id").val()

  if (peopleId) {
    $("#national-code").attr("disabled", true)
  }

  // Create an array of promises
  const catalogPromises = [
    catalogDataSelect2("ROLE"),
    catalogDataSelect2("LOC"),
    catalogDataSelect2("TAG"),
    catalogDataSelect2("SKL"),
  ];

  // Execute all catalogDataSelect2 calls and wait for them to complete
  Promise.all(catalogPromises)
    .then(function (results) {
      const [roleData, locationData, tagData, skillData] = results;

      const select2Roles = {
        data: transformCatalogToSelect2(roleData)
      };
      $('.personnel-role-select2').select2({ ...select2Roles, ...select2Props });

      const select2ServiceLocations = {
        data: transformCatalogToSelect2(locationData)
      };
      $('.service-locations-select2').select2({ ...select2ServiceLocations, ...select2Props });

      const select2Tags = {
        data: transformCatalogToSelect2(tagData)
      };
      $('.tags-select2').select2({ ...select2Tags, ...select2Props });

      mustBeSelect2.push({
        id: "skill",
        qTerm: "SKL",
        data: transformCatalogToSelect2(skillData)
      })

      if (peopleId) {
        // if state edit now go and fetch data 
        // Second send data to server
        $.ajax({
          url: apiUrls.personnelEdit + `${peopleId}/`,
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
        $('#add-phone-number').trigger("click")
      }

    })
    .catch(function (error) {
      console.error('Failed to load catalog data:', error);
    });


  $("#joined-date").pDatepicker({
    format: "L",
    autoClose: true,
    initialValue: true,
    persianDigit: false
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

    data.types = ["TYP_PERSONNEL"]
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
        redirectTo(apiUrls.peopleSection)

      },
      error: function (xhr, status, error) {
        error_toast("خطا", "خطایی در سرور رخ داده است")
        console.error('Error:', xhr.responseJSON);
      }
    });
  });

  $(document).on('select2:select', ".skill", function () {
    let changedSelect = $(this)
    $(".skill").each(function () {
      if ($(this).is(changedSelect)) return true;
      const overlappingValues = getOverlappingValues($(this).val(), changedSelect.val())
      console.log(overlappingValues)

      if (overlappingValues.length >= 1) {
        changedSelect.val(differentiateArrays(overlappingValues, changedSelect.val()).diff1).trigger('change')
        error_toast("مهارت تکراری", "امکان اضافه کردن مهارت تکراری وجود ندارد. برای تغییر امتیاز مهارت قبلی را پاک کنید")
      }
    })
  })




})






