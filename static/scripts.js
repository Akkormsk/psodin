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
        .then(response => response.json())
        .then(options => {
            let optionsHtml = '';
            options.forEach(option => {
                optionsHtml += `<option value="${option.id}" data-xerox="${option.price}" data-konica="${option.price}">
                                    ${option.name} - ${option.price} руб/лист
                                </option>`;
            });
            contentDiv.querySelector('select[name="print_type"]').innerHTML = optionsHtml;
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

function saveOrder() {
    const totalCost = document.getElementById('total_cost').value;
    const retailPrice = document.getElementById('retail_price').value;

    if (!totalCost || !retailPrice) {
        alert('Сначала необходимо произвести расчет.');
        return;  // Не открывать модальное окно
    }

    console.log('Записать нажата');
    $('#orderIdModal').modal('show');
}

function confirmOrderId() {
    const orderId = document.getElementById('orderIdInput').value;
    console.log('ID заказа:', orderId);
    if (orderId) {
        const form = document.getElementById('calcForm');
        const formData = new FormData(form);

        // Собираем данные о материалах и добавляем в formData
//        const materials = gatherMaterials();
        formData.append('order_id', orderId);


        // Добавляем total_cost и retail_price из скрытых полей
        const totalCost = document.getElementById('total_cost').value;
        const retailPrice = document.getElementById('retail_price').value;
        const materials = document.getElementById('materials').value;
        formData.append('total_cost', totalCost);
        formData.append('retail_price', retailPrice);
        formData.append('materials', materials);

        // Логирование всех данных формы
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }

        fetch('/save_order', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) {
                alert('Заказ сохранен успешно!');
                $('#orderIdModal').modal('hide');
            } else {
                response.json().then(data => {
                    alert('Ошибка при сохранении заказа: ' + data.message);
                });
            }
        }).catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка при сохранении заказа: ' + error.message);
        });
    } else {
        alert('Введите ID заказа.');
    }
}
