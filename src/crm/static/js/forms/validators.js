// utils 

function convertPersianDigitsToEnglish(value) {
    if (!value) return value
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    const englishDigits = '0123456789';
    return value.replace(/[۰-۹]/g, (digit) => {
        return englishDigits[persianDigits.indexOf(digit)];
    });
}

function comparePersianDates(dateStr1, dateStr2) {
    
    const englishDateStr1 = convertPersianDigitsToEnglish(dateStr1);
    const englishDateStr2 = convertPersianDigitsToEnglish(dateStr2);
  
    // Compare the date strings directly
    if (englishDateStr1 < englishDateStr2) {
      return true; // dateStr1 is before dateStr2
    } else if (englishDateStr1 > englishDateStr2) {
      return false; // dateStr1 is after dateStr2
    } else {
      return 0; // dateStr1 is the same as dateStr2
    }
  }

// general validators

function notEmptyInputValidator(value) {
    const trimmedValue = value.trim();
    return {
        valid: trimmedValue.length > 0,
        msg:'ورودی نباید خالی باشد'
    };
}

function notEmptyMultipleSelect2Validator(value) {
    return {
        valid: value.length > 0,
        msg:'موردی را انتخاب کنید'
    };
}

function isDigitValidator(value) {
    return {
        valid: /^\d+$/.test(value),
        msg:'ورودی باید به فرمت تماما عدد باشد'
    };
}

function cardNumberValidator(value) {
    const regex = /^\d{16}$/;
    return {
        valid: regex.test(value),
        msg:'کارت بانکی صحیح نمی باشد'
    };
}

function dateValidator(value) {
    const regex = /^(13|14)\d{2}\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[01])$/;
    return {
        valid: regex.test(convertPersianDigitsToEnglish(value)),
        msg:'تاریخ صحیح نیست'
    };
}



// personnel advanced validators

function skillRowValidator() {
    // skill pts must be valid (check by the max) 
    
}

function contractDurationValidator() {
    // start must be greater than end
    const startDate = $("#contract-start").val()
    const endDate = $("#contract-end").val()    
    return {
        valid: endDate!=="" ? comparePersianDates(startDate, endDate) : true,
        msg:"تاریخ پایان همکاری باید بزرگتر از تاریخ شروع همکاری باشد"
    };

}

function personnelRole() {
    // must be at least one role selected!
    return {
        valid: $(".personnel-role-select2").val().length > 0 ? true: false,
        msg:"پرسنل حداقل باید یک نقش داشته باشد"
    };
}

function genderSelection() {
    return {
        valid: $('input[name="gender"]:checked').length === 0 ? false: true,
        msg:"لطفا جنسیت این فرد را انتخاب کنید"
    };
}

function skillDuplication() {

    // check skill duplication

    let skills = []
    $("[id^='skill-']").each(function(){
        if (getCleanElementId($(this).prop("id"))==="skill") {
            skills.push($(this).val())
        }
    })

    const skillSet = new Set(skills)
    return {
        valid: skillSet.length === skills.length ? true: false,
        msg:"مهارت تکراری در لیست مهارت ها وجود دارد آن را اصلاح کنید"
    };
    
}