from flask import Blueprint, render_template, request, jsonify, current_app

import logging
from ..models import *

main_bp = Blueprint('main', __name__)
logger = logging.getLogger('app_logger')


@main_bp.route('/')
@main_bp.route('/home')
def index():
    return render_template('index.html')


@main_bp.route('/calculator/sheet_printing', methods=['GET', 'POST'])
@main_bp.route('/sheet_printing', methods=['GET', 'POST'])
@main_bp.route('/calculator', methods=['GET', 'POST'])
def sheet_printing_func():
    if request.method == 'POST':
        paper_type_ids = request.form.getlist('paper_type')
        paper_quantities = request.form.getlist('paper_quantity')
        machine_types = request.form.getlist('machine_type')
        print_type_ids = request.form.getlist('print_type')
        print_quantities = request.form.getlist('print_quantity')
        postprint_types = request.form.getlist('postprint_type')
        postprint_quantities = request.form.getlist('postprint_quantity')
        work_time = float(request.form['work_time'])

        materials_text = ""

        paper_details = []
        paper_cost = 0
        total_paper = 0
        for i in range(len(paper_type_ids)):
            paper = PaperType.query.get(paper_type_ids[i])
            quantity = int(paper_quantities[i])
            paper_cost += quantity * paper.price_per_unit
            total_paper += quantity
            paper_details.append((paper, quantity))
            materials_text += f"Бумага {i + 1} - {paper.name} - {quantity} шт по цене {paper.price_per_unit}\r\n"

        print_details = []
        print_cost = 0
        for i in range(len(machine_types)):
            machine_type = machine_types[i]
            print_type = PrintType.query.get(print_type_ids[i])
            quantity = int(print_quantities[i])
            if machine_type == 'xerox':
                print_cost += quantity * print_type.price_per_unit_xerox
                materials_text += f"Печать {i + 1} - {machine_type} - {print_type.name} - {quantity} шт по цене {print_type.price_per_unit_xerox}\r\n"
            else:
                print_cost += quantity * print_type.price_per_unit_konica
                materials_text += f"Печать {i + 1} - {machine_type} - {print_type.name} - {quantity} шт по цене {print_type.price_per_unit_konica}\r\n"
            print_details.append((machine_type, print_type, quantity))

        postprint_details = []
        postprint_cost = 0
        for i in range(len(postprint_types)):
            postprint_type = PostPrintProcessing.query.get(postprint_types[i])
            quantity = int(postprint_quantities[i])
            postprint_cost += quantity * postprint_type.price_per_unit
            postprint_details.append((postprint_type, quantity))
            materials_text += f"Постпечатка {i + 1} - {postprint_type.name} - {quantity} шт по цене {postprint_type.price_per_unit}\r\n"

        work = Variables.query.get(1)
        margin_ratio = Variables.query.get(2)
        regulars_discount = Variables.query.get(5)
        partners_discount = Variables.query.get(6)
        urgency = Variables.query.get(7)

        work_cost = work_time * work.value if work else 0
        materials_text += f"Работа - {work_time} ч. по цене {work.value}\r\n"

        total_cost = round(paper_cost + print_cost + postprint_cost + work_cost, 2)
        retail_price = round(total_cost * margin_ratio.value * (1 + (1 / total_paper)), 2)
        regulars_price = round(retail_price * regulars_discount.value, 2)
        partners_price = round(retail_price * partners_discount.value, 2)
        urgent_price = round(retail_price * urgency.value, 2)

        # current_app.logger.info(f'Print details: {print_details}')

        return render_template('Calculator/sheet_printing.html', total_cost=total_cost,
                               paper_details=paper_details, print_details=print_details,
                               postprint_details=postprint_details, work_time=work_time,
                               paper_cost=paper_cost, postprint_cost=postprint_cost,
                               paper_types=PaperType.query.all(), print_types=PrintType.query.all(),
                               postprint_types=PostPrintProcessing.query.all(), work_cost=work_cost,
                               print_cost=print_cost, retail_price=retail_price,
                               regulars_price=regulars_price, partners_price=partners_price,
                               urgent_price=urgent_price, machine_type=machine_types[0],
                               materials_text=materials_text)

    return render_template('Calculator/sheet_printing.html',
                           paper_types=PaperType.query.all(),
                           print_types=PrintType.query.all(),
                           postprint_types=PostPrintProcessing.query.all(),
                           machine_type='xerox',
                           paper_details=[(0,)],
                           print_details=[('xerox', 0,)],
                           postprint_details=[(0,)])  # Default values for initial load


@main_bp.route('/update_print_options', methods=['GET'])
def update_print_options():
    machine_type = request.args.get('machine_type')
    print_types = PrintType.query.all()
    options = []

    for print_type in print_types:
        if machine_type == 'xerox':
            options.append({
                'id': print_type.id,
                'name': print_type.name,
                'price': print_type.price_per_unit_xerox
            })
        elif machine_type == 'konica':
            options.append({
                'id': print_type.id,
                'name': print_type.name,
                'price': print_type.price_per_unit_konica
            })

    return jsonify(options)


@main_bp.route('/save_order', methods=['POST'])
def save_order():
    try:
        # current_app.logger.info(f"Received form data: {request.form}")
        order_id = request.form.get('order_id')
        retail_price = request.form.get('retail_price')
        cost_price = request.form.get('total_cost')
        materials = request.form.get('materials')

        if not order_id or not retail_price or not cost_price or not materials:
            raise ValueError("Missing one or more required fields: order_id, retail_price, cost_price, materials")

        order = Order(id=order_id, retail_price=float(retail_price), cost_price=float(cost_price), materials=materials)
        db.session.add(order)
        db.session.commit()

        logger.info(
            f'Добавлена новая запись: Заказ ID: {order_id}, Розничная цена: {retail_price}, Себестоимость: {cost_price}, Материалы: {materials}')

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        # current_app.logger.error(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


@main_bp.route('/multi_page_printing')
def multi_page_printing():
    # current_app.logger.info('Multi page printing calculator accessed')
    return render_template('Calculator/multi_page_printing.html')


@main_bp.route('/orders')
@main_bp.route('/calculator/orders')
def show_orders():
    # current_app.logger.info('Orders page accessed')
    orders = Order.query.all()
    return render_template('Calculator/orders.html', orders=orders)


@main_bp.route('/calculator/wide_format_printing', methods=['GET', 'POST'])
@main_bp.route('/wide_format_printing', methods=['GET', 'POST'])
def calculate_wide_format():
    # current_app.logger.info('Wide format printing calculator accessed')
    if request.method == 'POST':
        paper_ids = request.form.getlist('paper_type')
        print_ids = request.form.getlist('print_type')
        process_ids = request.form.getlist('post_processing')
        paper_quantities = request.form.getlist('paper_quantity')
        print_quantities = request.form.getlist('print_quantity')
        process_quantities = request.form.getlist('postprint_quantity')
        hours = int(request.form.get('hours', 0))
        materials_text = ""

        paper_details = [(PaperTypeLarge.query.get(paper_id), int(paper_quantity)) for paper_id, paper_quantity in
                         zip(paper_ids, paper_quantities)]
        print_details = [(PrintTypeLarge.query.get(print_id), int(print_quantity)) for print_id, print_quantity in
                         zip(print_ids, print_quantities)]
        postprint_details = [(PostPrintProcessingLarge.query.get(process_id), int(process_quantity)) for
                             process_id, process_quantity in zip(process_ids, process_quantities)]

        for i, (paper, quantity) in enumerate(paper_details):
            materials_text += f"Бумага {i + 1} - {paper.name} - {quantity} м² по цене {paper.price_per_unit}\r\n"

        for i, (print_type, quantity) in enumerate(print_details):
            materials_text += f"Печать {i + 1} - {print_type.name} - {quantity} м² по цене {print_type.price_per_unit_canon}\r\n"

        for i, (process, quantity) in enumerate(postprint_details):
            materials_text += f"Постпечатка {i + 1} - {process.name} - {quantity} шт по цене {process.price_per_unit}\r\n"

        work_cost_variable = Variables.query.get(1)
        hourly_rate = work_cost_variable.value if work_cost_variable else 0
        work_cost = hours * hourly_rate
        materials_text += f"Работа - {hours} ч. по цене {hourly_rate}\r\n"

        total_cost = sum([detail[1] * detail[0].price_per_unit for detail in paper_details]) + \
                     sum([detail[1] * detail[0].price_per_unit_canon for detail in print_details]) + \
                     sum([detail[1] * detail[0].price_per_unit for detail in postprint_details]) + work_cost

        coefficient = Variables.query.get(2).value
        regulars_discount = Variables.query.get(5).value
        partners_discount = Variables.query.get(6).value
        urgent_coefficient = Variables.query.get(4).value

        retail_price = total_cost * coefficient
        regulars_price = retail_price * regulars_discount
        partners_price = retail_price * partners_discount
        urgent_price = retail_price * urgent_coefficient

        # current_app.logger.info(f'Retail Price: {retail_price}, Total Cost: {total_cost}')

        return render_template('Calculator/wide_format_printing.html', total_cost=total_cost, work_cost=work_cost,
                               paper_details=paper_details, print_details=print_details,
                               postprint_details=postprint_details, work_time=hours, retail_price=retail_price,
                               regulars_price=regulars_price, partners_price=partners_price, urgent_price=urgent_price,
                               papers=PaperTypeLarge.query.all(), print_types=PrintTypeLarge.query.all(),
                               post_processings=PostPrintProcessingLarge.query.all(), materials_text=materials_text)

    return render_template('Calculator/wide_format_printing.html',
                           papers=PaperTypeLarge.query.all(),
                           print_types=PrintTypeLarge.query.all(),
                           post_processings=PostPrintProcessingLarge.query.all(),
                           paper_details=[], print_details=[], postprint_details=[])
