// import "jquery"
// import { ajax } from "jquery"

let previewUrlStack = Array()

function persianize(value) {
    if (value === null || value === undefined) return
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
    <div class="flex flex-row-reverse gap-2 ">
        ${buttonsHTML}
    </div>
        <div class="bg-white rounded-md shadow-md p-4 h-fit text-primarytext flex flex-col gap-2 w-full">
            <div class="flex flex-row gap-2 font-semibold bg-primary text-white p-2 rounded-md">
                <span>
                    اطلاعات ${persianize(data.description)}
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
    let displayButton = undefined
    if (icon !== "") {
        displayButton = `<img class="h-4 w-4 fill-successtext" src="/static/svg/${icon}.svg" alt="${title}"/>`
    } else {
        displayButton = `${title}`
    }
    return `<a class="p-2 text-sm bg-successbg  text-successtext rounded-md" href="${link}">
        ${displayButton}
    </a>`
}

function makeButtonSet(buttonsData) {
    let html = ""
    if (buttonsData === undefined) { return "" }
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
    let displayText = dataObj.link ? `<a href="${dataObj.link}">${persianize(dataObj.value) || "-"}</a>` : persianize(dataObj.value) || "-"
    return `<tr class="${color ? 'bg-searchbox' : ''}">
        <td class="p-2 text-sm font-semibold text-primary rounded rounded-md">${dataObj.title}</td>
        <td class="p-2 text-sm">${displayText}</td>
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
    for (let i = totalDataCount - rowNeeded; i < totalDataCount; i++) {
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
    if (obj.link !== undefined && obj.link != "") {
        return `<tr data-link="${obj.link}">${HTML}</tr>`
    } else {
        return `<tr>${HTML}</tr>`
    }
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
            // HTML += previewPane(
            //     obj.title,
            //     undefined,
            //     `<span class="align-middle text-failed">داده یافت نشد</span>`
            // )
        } else {
            let headersHTML = makeDataTableHeaders(obj)
            let body = makeDataTableRows(obj)
            HTML += previewPane(
                obj.title,
                undefined,
                `<table class="display  compact text-black text-sm" id="dt-${counter}">${headersHTML + body}</table>`
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
        previewUrlStack.push(url)
        new_preview = makePreview(data)
        flushCurrentPreview()
        replaceNewPreview(new_preview.previewContainer)
        loadDataTables(new_preview.dataTableIds)
    })
}

function addDataTableRowSelectionStyle(row) {
    row.css({
        "background-color": "rgb(203, 213, 225 )"
    })
}

function removeDataTableRowsSelectionStyle() {
    $('div[id^="tab-container"]').find('tr').removeAttr("style")
}

$(document).ready(function () {

    // click on datatable beside preview pane
    $(document).on('click', "div[id^='tab-container'] table.dataTable tr[data-link]", function () {
        let url = $(this).attr("data-link")
        if (url == "" || url === undefined) return

        // flush preview url stack and hide back button
        previewUrlStack = Array()
        $("div[id='preview-container']").parent().find(".preview-back").addClass("hidden")


        loadNewPreview(url)
        removeDataTableRowsSelectionStyle()
        addDataTableRowSelectionStyle($(this))
    });

    // click on preview datatables
    $(document).on('click', "div[id='preview-container'] table.dataTable tr[data-link]", function () {

        if (previewUrlStack.length >= 1) {
            $("#preview-container").parent().find(".preview-back").removeClass("hidden")
        }

        let url = $(this).attr("data-link")
        if (url == "" || url === undefined) return
        loadNewPreview(url)
        addDataTableRowSelectionStyle($(this))
    });

    $("div[id='preview-container']").parent().find(".preview-back").on('click', function () {
        previewUrlStack.pop()
        previousUrl = previewUrlStack.pop()

        // hidden back if it was last URL
        if (previewUrlStack.length === 0) {
            $(this).addClass("hidden")
        }

        loadNewPreview(previousUrl)
    });


    
});