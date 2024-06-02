const select2Props = {
  placeholder: "برای انتخاب کلیک کنید...",
  dir: "rtl",
  width: "100%",
}

function flushFormErrorDisplay() {
  $(".form-input-error").each(function () {
    $(this).text("")
  })
}
function flushFormErrorStyles() {
  $(".form-input-error-color").each(function () {
    $(this).removeClass("form-input-error-color")
    $(this).addClass("form-input-normal-color")
  })
}

function showFormInputErrors(errors) {
  for (const key in errors) {
    if (errors[key].length > 0) {
      for (const errorMsg of errors[key]) {
        let input = $(`#${key}`)

        // display input error 
        let errorContainer = input.parents(".form-input-container").find(".form-input-error")
        errorContainer.text(errorMsg)

        // change input style to error
        input.removeClass("form-input-normal-color")
        input.addClass("form-input-error-color")
      }
    }
  }
}

function isFormValid(requireds, nonRequireds, advanced) {
  res = true
  const errors = {};

  // requireds validation
  for (const key in mapAllInputsValidator(requireds)) {
    const validators = mapAllInputsValidator(requireds)[key];
    errors[key] = []
    if (validators.length > 0) {
      for (const validator of validators) {
        const data = $(`#${key}`).val()
        const validationResult = validator(data);
        if (!validationResult.valid) {
          errors[key].push(validationResult.msg)
          res = false
          break;
        }
      }
    }
  }

  // non-requireds inputs validation
  for (const key in mapAllInputsValidator(nonRequireds)) {
    const validators = mapAllInputsValidator(nonRequireds)[key];
    errors[key] = []
    if (validators.length > 0) {
      for (const validator of validators) {
        const data = $(`#${key}`).val()
        if (!data) continue;
        const validationResult = validator(data);
        if (!validationResult.valid) {
          errors[key].push(validationResult.msg)
          res = false
          break;
        }
      }
    }
  }

  // advanced validation
  for (const item of advanced) {
    let validators = item.validators
    let elementId = item.element.prop("id")


    if (!(elementId in errors)) errors[elementId] = []
    if (elementId in errors) {
      if (errors[elementId].length > 0) {
        // thats enough to display just one error
        continue;
      }
    }

    for (const validator of validators) {
      const validationResult = validator()
      if (!validationResult.valid) {
        errors[elementId].push(validationResult.msg)
        res = false
        break;
      }
    }
  }

  if (!res) error_toast("اشکال در اطلاعات فرم", "موارد ذکر شده در فرم را اصلاح کنید")

  return { res: res, errors: errors }
}

function mapAllInputsValidator(inputsValidator) {

  let mustDelete = []
  // remove TEMP from validators key
  const cleanedInputsValidator = {}
  for (const key in inputsValidator) {
    if (key.includes("TEMP")) {
      cleanedKey = key.replace("TEMP", "")
      cleanedInputsValidator[cleanedKey] = inputsValidator[key]
      mustDelete.push(cleanedKey)
    } else {
      cleanedInputsValidator[key] = inputsValidator[key]
    }
  }

  // dynamic inputs
  $(".dynamic-row").each(function () {
    if (!($(this).parent().parent().hasClass("form-row-container-hidden"))) {
      let elementId = $(this).prop("id")
      let cleanElementId = getCleanElementId(elementId)
      if (cleanedInputsValidator[cleanElementId] !== undefined) {
        cleanedInputsValidator[elementId] = cleanedInputsValidator[cleanElementId]
      }
    }
  })
  for (const key of mustDelete) {
    delete cleanedInputsValidator[key]
  }
  return cleanedInputsValidator
}


function getCleanElementId(id) {
  return id.replace(/-\d+/, '');
}

function transformCatalogToSelect2(data) {
  const transformedData = $.map(data, function (obj) {
    return {
      id: obj.id,
      text: obj.title
    };
  });
  return transformedData
}

function catalogDataSelect2(q) {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: apiUrls.catalog,
      data: { q: q },
      dataType: 'json',
      success: function (data) {
        resolve(data);
      },
      error: function (jqXHR, textStatus, errorThrown) {
        reject(errorThrown);
      }
    });
  });
}

$(document).ready(function () {
  $(".datePicker").pDatepicker({
    format: "L",
    autoClose: true,
    initialValue: false,
    persianDigit:false
  });

  // inserting input error spans
  $(".form-input-container").each(function () {
    if ($(this).find("input").length > 0 || $(this).find("select").length > 0) {
      $(this).append(
        `<span class="form-input-error"></span>`
      );
    }
  });

  // insert new row with add buttons
  $(document).on('click', ".form-btn-container .form-btn", function () {
    let hiddenRow = $(this).parents(".form-section-inner-container").find(".form-row-container-hidden")
    let newRow = hiddenRow.clone()

    let select2Candidates = []
    // make new id for it's inputs
    newRow.find("input, select").each(function () {
      const id = $(this).attr("id")
      const newId = id.trim().replace("0", String(Date.now()))
      $(this).attr("id", newId)
      select2Candidates.push(newId)
    })

    newRow.addClass("form-row-container")
    newRow.removeClass("form-row-container-hidden")

    $(this).parent().before(newRow)

    // check if this is the element that should be select2 or not, if yes
    // initiate select 2
    for (const obj of mustBeSelect2) {
      const matchingCandidate = select2Candidates.find(candidate => getCleanElementId(candidate) === obj.id);
      if (matchingCandidate) {
        catalogDataSelect2(obj.qTerm)
          .then(function (data) {
            const select2Data = { data: transformCatalogToSelect2(data) };
            $(`#${matchingCandidate}`).select2({ ...select2Data, ...select2Props });
          })
          .catch(function (error) {
            console.error('Failed to load roles data:', error);
          });
      }
    }
    
  })

  // remove whole row by clicking on trashcan in row button 
  $(document).on('click', ".in-row-delete", function () {

    const rowCount = $(this).parents(".form-section-inner-container").find(".form-row-container").length
    if (rowCount - 1 > 0) {
      $(this).parent().parent().remove()
      return
    }
    error_toast("امکان حذف وجود ندارد", "حداقل یک شماره تماس باید برای فرد در سیستم ثبت شود")
  });
})
