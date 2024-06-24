function addPrintSection() {
    const template = document.getElementById('print-section-template');
    const clone = template.content.cloneNode(true);
    const printSections = document.getElementById('print_sections');
    printSections.appendChild(clone);

    const newMachineSelect = printSections.lastElementChild.querySelector('select[name="machine_type"]');
    updatePrintOptions(newMachineSelect.value, newMachineSelect);

    const newPrintContent = printSections.lastElementChild.querySelector('[id^=print-content-template]');
    updatePrintPrices(newMachineSelect.value, newPrintContent);
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('select[name="machine_type"]').forEach(function(select) {
        updatePrintOptions(select.value, select);
    });

    document.querySelectorAll('select[name="print_type"]').forEach(function(select) {
        const machineType = select.closest('.form-group').querySelector('select[name="machine_type"]').value;
        updatePrintPrices(machineType, select.closest('[id^=print-content]'));
    });
});

function updatePrintOptions(machineType, element) {
    const parentDiv = element.closest('.form-group');
    const contentDiv = parentDiv.querySelector('[id^=print-content]');

    fetch(`/update_print_options?machine_type=${machineType}`)
        .then(response => response.text())
        .then(html => {
            contentDiv.innerHTML = html;
            updatePrintPrices(machineType, contentDiv);
        });
}

function updatePrintPrices(machineType, contentDiv) {
    contentDiv.querySelectorAll('option').forEach(function(option) {
        if (machineType === 'xerox') {
            option.innerText = `${option.innerText.split('-')[0]} - ${option.getAttribute('data-xerox')} руб/лист`;
        } else if (machineType === 'konica') {
            option.innerText = `${option.innerText.split('-')[0]} - ${option.getAttribute('data-konica')} руб/лист`;
        }
    });
}

function addPaperSection() {
    const template = document.getElementById('paper-section-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('paper-sections').appendChild(clone);
}

function addPostprintSection() {
    const template = document.getElementById('postprint-section-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('postprint-sections-wrap').appendChild(clone);
}

function removeSection(button) {
    const section = button.closest('.form-group');
    section.remove();
}

function resetForm() {
    window.location.href = "/sheet_printing";
}
