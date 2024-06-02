class Validatable {
    constructor(inputId, payloadKey, required, validators, elementErrorSelector) {
        this.inputId = inputId
        this.payloadKey = payloadKey
        this.required = required
        this.validators = validators || []
        this._error = null
        this._element = $(`#${this.inputId}`)
        this._errorContainer = elementErrorSelector || this._element.parents(".form-input-container").find(".form-input-error")

    }
    getVal() {
        // it just works for text and select2
        return this._element.val()
    }
    getError() {
        return this._error
    }
    hasError(){
        return Boolean(this._error)
    }
    isValid() {
        if (this.validators.length === 0) return true
        for (const validator of this.validators) {
            const data = this._element.val()
            const validationResault = validator(data)
            if (!validationResault.valid) {
                this._error = validationResault.msg
                return false
            }
        }
        return true
    }
    displayError() {
        if (this._errorContainer) $(this._errorContainer).text(this._error)
    }
    flushStyle() {
        this._element.removeClass("form-input-error-color")
        this._element.addClass("form-input-normal-color")
    }
    flushErrorMsg() {
        this._element.text("")
        this._error = null
    }
    displayErrorStyle() {
        this._element.removeClass("form-input-normal-color")
        this._element.addClass("form-input-error-color")
    }
}

class TextField extends Validatable {
    constructor(...args) {
        super(...args)
    }
}

class RadioField extends Validatable {
    constructor(...args) {
        super(...args)
    }
}

class SingleSelect2Field extends Validatable {
    constructor(...args) {
        super(...args)
    }
    isValid() { }
}

class RadioGroup extends Validatable {
    constructor(radioInputs, payloadKey, required, validators, elementErrorSelector) {
        this.radioInputs = radioInputs
        this.payloadKey = payloadKey
        this.required = required
        this.validators = validators
        this.elementErrorSelector = elementErrorSelector
    }

    getVal() {
        for (const raidoInput of this.radioInputs) {
            if ($(`#${raidoInput}`).is(":checked")) {
                return $(`#${raidoInput}`).attr("data")
            }
        }
        return null
    }

    displayError() {
        if (this._errorContainer) $(this._errorContainer).text(this._error)
    }
    flushStyle() {
        this._element.removeClass("form-input-error-color")
        this._element.addClass("form-input-normal-color")
    }
    flushErrorMsg() {
        this._element.text("")
    }
    displayErrorStyle() {
        this._element.removeClass("form-input-normal-color")
        this._element.addClass("form-input-error-color")
    }

}

class GroupField extends Validatable{
    constructor(inputs, elementErrorSelector) {
        this.inputs = inputs
        this._errorContainer = elementErrorSelector
    }
}

class Form {
    constructor(inputs, complexValidators) {
        this.inputs = inputs
        this.complexValidators = complexValidators
    }

    isValid() {

        for (const input of this.inputs) {
            if (!input.getVal() && !input.required) continue;
            if (!input.isValid()) {
                this.valid = false
            }
        }

        return this.valid
    }

    flushErrors() {
        for (const input of this.inputs) {
            input.flushStyle()
            input.flushErrorMsg()
        }
    }
    displayErrors() {
        for (const input of this.inputs) {
            if (input.hasError()){
                input.displayErrorStyle()
                input.displayError()
            }
        }

    }
    get_payload() { }

}



$(document).ready(function () {

    // when the HTML loaded
    let personnelForm = new Form(
        [
            new TextField("national-code", "national_code", true, [notEmptyInputValidator, isDigitValidator]),
            new TextField("firstname", "first_name", true, [notEmptyInputValidator]),
            new TextField("lastname", "last_name", true, [notEmptyInputValidator]),
            new TextField("birthdate", "last_name", true, [notEmptyInputValidator, dateValidator]),
            new TextField("address", "address", false, []),
            new TextField("active-card-number", "card_number", true, [notEmptyInputValidator, isDigitValidator, cardNumberValidator]),
            new TextField("contract-start", "contract_start", true, [notEmptyInputValidator, dateValidator]),
            new TextField("contract-end", "contract_end", false, [dateValidator]),



            // new RadioGroup(
            //     new RadioField("male", null, true, [notEmptyInputValidator]),
            //     new RadioField("female", null, true, [notEmptyInputValidator]),
            // ),
            // new GroupSimpleField(
            //     new SimpleField("phone-number", null, true, [notEmptyInputValidator]),
            //     new SimpleField("phone-number-note", null, true, [notEmptyInputValidator]),
            // ),
            // new GroupSimpleField(
            //     new SimpleField("skill", null, true, [notEmptyInputValidator]),
            //     new SimpleField("skill-pts", null, true, [notEmptyInputValidator]),
            // )
        ]
    )
    // form save btn
    $(document).on('click', ".form-save", function () {
        info_toast("test")
        personnelForm.flushErrors()

        if (!personnelForm.isValid()) {
            personnelForm.displayErrors()
            return
        }

        personnelForm.flushErrors()
    })

    $('#add-phone-number').trigger("click")
})