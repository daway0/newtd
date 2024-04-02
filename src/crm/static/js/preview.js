// import "jquery"
// import { ajax } from "jquery"

function persianize(value) {
    const persianNumbers = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    };

    // Use map function for concise character-by-character conversion
    return value.toString().split("").map(char => persianNumbers[char] || char).join("");
}


function makePreview(data) {
    let buttonsData = data.buttons
    let tableData = data.table
    let dataTablesData = data.data_tables

    let buttonsHTML = makeButtonSet(buttonsData)
    let tableHTML = makeInfoTable(tableData)
    let dataTablesHTML = makeDataTable(dataTablesData)

    previewContainer = `
    <div class="flex flex-row-reverse gap-2">
        ${buttonsHTML}
    </div>
        
            
        <div class="bg-white rounded-md shadow-md p-4 h-fit text-primarytext flex flex-col gap-2 w-full">
            <div class="flex flex-row gap-2 font-semibold">
                <span>
                    جزییات
                </span>
            </div>
            <div class="flex flex-row w-full">
                <div class="basis-1/2">
                    <table class="text-black w-full">
                    ${tableHTML.firstTable}  
                    </table>
                </div>
                <div class="basis-1/2">
                    <table class="text-black w-full">
                    ${tableHTML.secondTable}
                    </table>
                </div>
            </div>
        </div>
        <div class="flex flex-col gap-2">
            ${dataTablesHTML.html}
        </div>
    `
    return { previewContainer: previewContainer, dataTableIds: dataTablesHTML.dataTableIds }
}

function makeButton(title, icon, link) {
    return `<a class="p-2 text-sm bg-successbg  text-successtext rounded-md" href="${link}">${title}</a>`
}

function makeButtonSet(buttonsData) {
    let html = ""
    buttonsData.forEach(function (button) {
        html += makeButton(
            button.title,
            button.icon,
            button.link
        )
    })
    return html
}

function makeRow(dataObj, color = false) {
    let displayText = dataObj.link ? `<a href="${dataObj.link}">${dataObj.value || "-"}</a>` : dataObj.value || "-"
    return `<tr class="${color ? 'bg-searchbox' : ''}">
        <td class="p-2 text-sm font-semibold text-primary rounded rounded-md">${dataObj.title}</td>
        <td class="p-2 text-sm">${persianize(displayText)}</td>
    </tr>`
}

function makeInfoTable(data) {
    // calculate for the number of row that is needed
    let listData = Object.values(data)
    let totalDataCount = listData.length
    let rowNeeded = (totalDataCount % 2 === 0) ? totalDataCount / 2 : parseInt(totalDataCount / 2) + 1

    let firstTableHTML = ""
    let secondTableHTML = ""

    // make rows with data
    for (let i = 0; i < rowNeeded; i++) {
        if (i % 2 === 0) {
            firstTableHTML += makeRow(listData[i], true)
        } else {
            firstTableHTML += makeRow(listData[i])

        }
    }
    for (let i = totalDataCount - rowNeeded + 1; i < totalDataCount; i++) {
        if (i % 2 === 0) {
            secondTableHTML += makeRow(listData[i], true)
        } else {
            secondTableHTML += makeRow(listData[i])

        }
    }

    return {
        firstTable: firstTableHTML,
        secondTable: secondTableHTML
    }
}

function makeDataTableHeaders(obj) {
    sampleRow = obj.data[0]
    let HTML = ""
    for (const key in sampleRow) {
        if (sampleRow[key].constructor === Object) {
            HTML += `<th>${sampleRow[key].title}</th>`
        }
    }
    return `<thead><tr>
    ${HTML}</tr></thead>`
}

function makeDataTableRow(obj) {
    let HTML = ""
    for (const key in obj) {
        if (obj[key].constructor === Object) {
            displayData = obj[key].value || "-"
            HTML += `<td>${persianize(displayData)}</td>`
        }
    }
    return `<tr>${HTML}</tr>`
}
function makeDataTableRows(obj) {
    let HTML = ""
    for (const key in obj.data) {
        HTML += makeDataTableRow(obj.data[key])
    }
    return `<tbody>${HTML}</tbody>`

}

function previewPane(header, icon, content) {
    return `<div class="bg-white rounded-md shadow-md p-4 h-fit text-primarytext flex flex-col gap-2 w-full">
        <div class="flex flex-row gap-2 font-semibold">
            <span>
                ${header}
            </span>
        </div>
        ${content}
    </div>`
}

function makeDataTable(tablesData) {
    let HTML = ""
    let dataTableIds = Array()

    let counter = 0
    tablesData.forEach(function (obj) {
        if (obj.data.length === 0) {
            HTML += previewPane(
                obj.title,
                undefined,
                `<span class="align-middle text-failed">داده یافت نشد</span>`
            )
        } else {
            let headersHTML = makeDataTableHeaders(obj)
            let body = makeDataTableRows(obj)
            HTML += previewPane(
                obj.title,
                undefined,
                `<table class="text-black text-sm" id="dt-${counter}">${headersHTML + body}</table>`
            )
            dataTableIds.push(counter)
            counter++
        }
    })
    return { html: HTML, dataTableIds: dataTableIds }
}

function loadDataTables(ids) {
    ids.forEach(function (id) {
        $(`#dt-${id}`).DataTable(informTable)

        // persianize
        $('.dataTable').find('td, th').css('text-align', 'right');

        // make table flexible (remove static width)
        $('.dataTable').each(function () {
            $(this).removeAttr("style", "width")
        })

        $("table.dataTable tr[data-link]").addClass("cursor-pointer")
    })
}


function flushCurrentPreview(url) {
    $("#preview-container").html("")
}

function replaceNewPreview(newHTML) {
    $("#preview-container").append(newHTML)
}

function loadNewPreview(url) {
    // fetch new data
    $.ajax(
        {
            url: url,
        }
    ).done(function (data) {
        new_preview = makePreview(data)
        flushCurrentPreview()
        replaceNewPreview(new_preview.previewContainer)
        loadDataTables(new_preview.dataTableIds)
    })
}


$(document).ready(function () {

    $(document).on('click', "table.dataTable tr[data-link]", function () {
        let url = $(this).attr("data-link")
        loadNewPreview(url)
    });
});