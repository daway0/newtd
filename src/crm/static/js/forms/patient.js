const requiredClientInputsValidator = {
    // input id: array of validators
    "national-code": [notEmptyInputValidator, isDigitValidator],
    "firstname": [notEmptyInputValidator],
    "lastname": [notEmptyInputValidator],
    "birthdate": [notEmptyInputValidator, dateValidator],
  }
  
  const nonRequiredClientInputsValidator = {
    // there is no need for these input to check notEmptyInputValidator
  }
  
  
  const clientAdvancedValidators = [
    {
      element: $("#female"),
      validators: [genderSelection],
    }
  ]
  const mustBeSelect2 = []
  
  
  $(document).ready(function () {
    
    $('.js-example-basic-multiple').select2(select2Props);
  
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
  
    });
  })
  
  
  
  
  
  
  
  
  
  