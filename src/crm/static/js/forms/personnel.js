const requiredPersonnelInputsValidator = {
  // input id: array of validators
  // "national-code": [notEmptyInputValidator, isDigitValidator],
  "firstname": [notEmptyInputValidator],
  "lastname": [notEmptyInputValidator],
  "birthdate": [notEmptyInputValidator, dateValidator],
  "contract-start": [notEmptyInputValidator, dateValidator],
  "TEMPphone-number": [notEmptyInputValidator, isDigitValidator],

}

const nonRequiredPersonnelInputsValidator = {
  // there is no need for these input to check notEmptyInputValidator
  "address": [],
  "active-card-number": [isDigitValidator, cardNumberValidator],
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
      console.error('Failed to load service locations data:', error);
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
    // First, we need to gather data

    let dataCallBacks = {
      national_code: () => $("#national-code").val(),
      firstname: () => $("#firstname").val(),
      lastname: () => $("#lastname").val(),
      birthdate: () => $("#birthdate").val(),
      address: () => $("#address").val() || null,
      active_card_number: () => $("#active-card-number").val() || null,
      contract_date: () => $("#contract-start").val(),
      end_contract_date: () => $("#contract-end").val() || null,
      gender: () => $("#male").is(":checked") ? "M" : "F",
      tags: () => $(".tags-select2").val(),
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
      roles: ()=> $(".personnel-role-select2").val(),
      service_locations: ()=> $(".service-locations-select2").val(),
      skills: () => {
        value = []
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

    }

    let data = {}
    for (const key in dataCallBacks){
      data[key] = dataCallBacks[key]()
    }
    success_toast("ثبت موفق", "اطلاعات با موفقیت در پایگاه داده ذخیره شد")
  });


  $('#add-phone-number').trigger("click")

})






