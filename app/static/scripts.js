document.addEventListener('DOMContentLoaded', function () {
    // Обновление цен при загрузке страницы и при смене типа принтера
    document.querySelectorAll('select[name="machine_type"]').forEach(function(selectElement) {
        updatePrintOptions(selectElement.value, selectElement);
        selectElement.addEventListener('change', function() {
            updatePrintOptions(this.value, this);
        });
    });
});

// Функция для обновления опций печати в зависимости от выбранного принтера
function updatePrintOptions(machineType, element) {
    const parentDiv = element.closest('.form-group');
    const printSelect = parentDiv.querySelector('select[name="print_type"]');

    // Если тип машины не выбран, ничего не меняем в отображении цен
    if (!machineType) {
        return;
    }

    // Обновление цен в зависимости от выбранной машины
    printSelect.querySelectorAll('option').forEach(function(option) {
        // Пропускаем плейсхолдеры без цен
        if (!option.hasAttribute('data-xerox') && !option.hasAttribute('data-konica')) {
            return;
        }
        const xeroxPrice = option.getAttribute('data-xerox');
        const konicaPrice = option.getAttribute('data-konica');
        const price = machineType === 'xerox' ? xeroxPrice : konicaPrice;
        const baseName = option.textContent.split('-')[0].trim();
        option.textContent = `${baseName} - ${price} руб/лист`;
    });
}

function addPrintSection() {
    const template = document.getElementById('print-section-template');
    const clone = template.content.cloneNode(true);
    const printSections = document.getElementById('print_sections');
    printSections.appendChild(clone);

    const newMachineSelect = printSections.lastElementChild.querySelector('select[name="machine_type"]');
    updatePrintOptions(newMachineSelect.value, newMachineSelect);
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
    window.location.reload();  // Reload the page to reset the form
}

function saveOrder() {
    const totalCost = document.querySelector('input[name="total_cost"]').value;
    const retailPrice = document.querySelector('input[name="retail_price"]').value;

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

        formData.append('order_id', orderId);

        // Добавляем total_cost и retail_price из скрытых полей
        const totalCost = document.querySelector('input[name="total_cost"]').value;
        const retailPrice = document.querySelector('input[name="retail_price"]').value;
        const materials = document.querySelector('input[name="materials"]').value;
        formData.append('total_cost', totalCost);
        formData.append('retail_price', retailPrice);
        formData.append('materials', materials);

        // Логирование всех данных формы
        //        for (let [key, value] of formData.entries()) {
        //            console.log(key, value);
        //        }

        fetch('/calculator/save_order', {
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

function toggleManualInput() {
    const manualInputSection = document.getElementById('manualInputSection');
    if (manualInputSection.classList.contains('d-none')) {
        manualInputSection.classList.remove('d-none');
        manualInputSection.classList.add('d-block');
    } else {
        manualInputSection.classList.remove('d-block');
        manualInputSection.classList.add('d-none');
    }
}

// Добавить введенный вручную материал
function addManualMaterial() {
    const materialName = document.getElementById('manualMaterialName').value;
    const materialPrice = parseFloat(document.getElementById('manualMaterialPrice').value);
    const materialQuantity = parseInt(document.getElementById('manualMaterialQuantity').value, 10);

    if (materialName && materialPrice > 0 && materialQuantity > 0) {
        // Добавление материала к total_cost и в materials_text
        totalCost += materialPrice * materialQuantity;
        materialsText += `Ручной ввод: ${materialName} - ${materialQuantity} шт по цене ${materialPrice} руб/шт\r\n`;

        // Очистка полей
        document.getElementById('manualMaterialName').value = '';
        document.getElementById('manualMaterialPrice').value = '';
        document.getElementById('manualMaterialQuantity').value = '';
    } else {
        alert('Пожалуйста, заполните все поля корректными значениями.');
    }
}