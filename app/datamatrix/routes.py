from flask import Blueprint, render_template, request, current_app, send_file, jsonify
from pdf2image import convert_from_bytes
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import io
import base64
from typing import Optional

datamatrix_bp = Blueprint('datamatrix', __name__, url_prefix='/datamatrix')

@datamatrix_bp.route('/', methods=['GET', 'POST'])
def datamatrix_index():
    if request.method == 'POST':
        return datamatrix_processing()
    return render_template('DataMatrix/datamatrix_processing.html')

@datamatrix_bp.route('/process', methods=['POST'])
def datamatrix_processing():
    file = request.files.get('kiz_file') or request.files.get('pdf_file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type'}), 400
    try:
        pages = convert_from_bytes(file.read(), dpi=300, fmt='png')
        generated_images = []
        for page_num, img in enumerate(pages, start=1):
            width, height = img.size
            results = dmtx_decode(img, max_count=4)
            for r in results:
                x, y, w, h = r.rect
                pad = 20
                left = max(x - pad, 0)
                top = max(height - (y + h) - pad, 0)
                right = min(x + w + pad, width)
                bottom = min(height - y + 5*pad, height)
                cropped = img.crop((left, top, right, bottom))
                buf = io.BytesIO()
                cropped.save(buf, format='PNG', optimize=False)
                buf.seek(0)
                generated_images.append(base64.b64encode(buf.getvalue()).decode('utf-8'))
        if not generated_images:
            return jsonify({'message': 'DataMatrix коды не найдены в загруженном файле.', 'encoded_images': []})
        return jsonify({'message': f'Сгенерировано {len(generated_images)} DataMatrix кодов.', 'encoded_images': generated_images})
    except Exception as e:
        current_app.logger.error(f'Ошибка при обработке PDF: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500

@datamatrix_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    encoded_images = data.get('images', [])
    if not encoded_images:
        return jsonify({'error': 'No images provided for PDF generation'}), 400
    try:
        images = []
        dpi_needed = 300
        target_height_cm = 5
        target_height_inch = target_height_cm / 2.54
        for enc in encoded_images:
            img_data = base64.b64decode(enc)
            img = Image.open(io.BytesIO(img_data)).convert('RGB')
            dpi_needed = int(max(72, img.height / target_height_inch))
            img.info['dpi'] = (dpi_needed, dpi_needed)
            images.append(img)
        if not images:
            return jsonify({'error': 'No images to include'}), 400
        buf = io.BytesIO()
        first, *rest = images
        first.save(buf, format='PDF', save_all=True, append_images=rest, resolution=dpi_needed)
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='datamatrix_codes.pdf')
    except Exception as e:
        current_app.logger.error(f'Ошибка при создании PDF: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500
