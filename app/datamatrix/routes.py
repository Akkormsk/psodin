import os
import fitz # PyMuPDF
from flask import Blueprint, render_template, request, current_app, send_file, jsonify
from pylibdmtx.pylibdmtx import decode, encode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
try:
    import treepoem
    TREEPOEM_AVAILABLE = True
except Exception:
    TREEPOEM_AVAILABLE = False

# Если известен путь к Ghostscript под Windows, укажем его для treepoem
if TREEPOEM_AVAILABLE:
    try:
        # Пользовательский путь к бинарнику Ghostscript
        _gs_base = r"C:\Users\d_kor\PycharmProjects\psadmin\gs10051w64"
        _gs_path = _gs_base if os.path.isfile(_gs_base) else _gs_base + ".exe"
        if os.path.isfile(_gs_path):
            os.environ['TREEPOEM_GHOSTSCRIPT_PATH'] = _gs_path
            print(f"TREEPOEM_GHOSTSCRIPT_PATH установлен: {_gs_path}")
    except Exception:
        pass

datamatrix_bp = Blueprint('datamatrix', __name__, url_prefix='/datamatrix')

# Упрощённая конвертация сырых GS1-байтов с GS-разделителями (0x1D)
# в строку с AIs в скобках для GS1 энкодера (BWIPP/treepoem).
def _raw_gs1_bytes_to_ai_string(raw_bytes: bytes) -> str:
    """
    Преобразует входную строку байтов (с возможными GS-разделителями или без них)
    в строку с AIs в скобках для GS1-энкодера (BWIPP/treepoem).

    Ориентировано на КИЗ-формат: (01)(21)(91)(92).
    Корректно выделяет (21) до следующего AI (91/92) даже если нет \x1d.
    """
    try:
        s = raw_bytes.decode('ascii', errors='ignore')

        chunks = []
        i = 0

        # (01) GTIN 14 цифр
        if s.startswith('01') and len(s) >= 16 and s[2:16].isdigit():
            chunks.append('(01)' + s[2:16])
            i = 16
        else:
            # Если нет ожидаемого (01), вернём исходное как есть
            return s.replace('\x1d', '')

        # Пропустить разделитель, если он есть
        if i < len(s) and s[i] == '\x1d':
            i += 1

        # (21) серийный — до следующего AI (91/92) или до разделителя/конца
        if i + 2 <= len(s) and s.startswith('21', i):
            i += 2
            start_serial = i
            while i < len(s):
                if s[i] == '\x1d' or s.startswith('91', i) or s.startswith('92', i):
                    break
                i += 1
            chunks.append('(21)' + s[start_serial:i])
            if i < len(s) and s[i] == '\x1d':
                i += 1

        # (91) крипточасть до (92) или разделителя/конца
        if i + 2 <= len(s) and s.startswith('91', i):
            i += 2
            start_91 = i
            while i < len(s):
                if s[i] == '\x1d' or s.startswith('92', i):
                    break
                i += 1
            chunks.append('(91)' + s[start_91:i])
            if i < len(s) and s[i] == '\x1d':
                i += 1

        # (92) оставшаяся крипточасть до разделителя/конца
        if i + 2 <= len(s) and s.startswith('92', i):
            i += 2
            start_92 = i
            while i < len(s) and s[i] != '\x1d':
                i += 1
            chunks.append('(92)' + s[start_92:i])

        return ''.join(chunks)
    except Exception:
        return raw_bytes.decode('ascii', errors='ignore')

def _looks_like_gs1_kiz(raw_bytes: bytes) -> bool:
    """
    Эвристика: распознаём GS1 (КИЗ) без \x1d по префиксу 01 + 14 цифр.
    """
    try:
        s = raw_bytes.decode('ascii', errors='ignore')
        return s.startswith('01') and len(s) >= 16 and s[2:16].isdigit()
    except Exception:
        return False

def _compute_gtin14_check_digit(first13: str) -> str:
    """
    Возвращает контрольную цифру для 13-значной основы GTIN-14.
    Вес 3 для нечётных позиций справа (1,3,5,...), иначе 1.
    """
    total = 0
    for idx, ch in enumerate(reversed(first13), start=1):
        weight = 3 if idx % 2 == 1 else 1
        total += int(ch) * weight
    return str((10 - (total % 10)) % 10)

def _is_valid_gtin14(gtin14: str) -> bool:
    if len(gtin14) != 14 or not gtin14.isdigit():
        return False
    expected = _compute_gtin14_check_digit(gtin14[:-1])
    return gtin14[-1] == expected

def _extract_gs1_parts(raw_bytes: bytes) -> dict:
    """
    Достаёт из входа строки значений для AI 01/21/91/92.
    Возвращает dict: { '01': gtin14|None, '21': serial|None, '91': v91|None, '92': v92|None }
    Все значения без скобок и без разделителей GS.
    """
    parts = {'01': None, '21': None, '91': None, '92': None}
    try:
        if b"\x1d" in raw_bytes:
            segments = raw_bytes.split(b"\x1d")
            first = segments[0].decode('ascii', errors='ignore')
            if first.startswith('01') and len(first) >= 16 and first[2:16].isdigit():
                parts['01'] = first[2:16]
                rest = first[16:]
                if rest.startswith('21'):
                    parts['21'] = rest[2:]
            for seg in segments[1:]:
                s = seg.decode('ascii', errors='ignore')
                if s.startswith('91'):
                    parts['91'] = s[2:]
                elif s.startswith('92'):
                    parts['92'] = s[2:]
        else:
            s = raw_bytes.decode('ascii', errors='ignore')
            # 01
            if s.startswith('01') and len(s) >= 16 and s[2:16].isdigit():
                parts['01'] = s[2:16]
            # 21
            i = s.find('21', 0)
            if i != -1:
                j = i + 2
                while j < len(s) and not (s.startswith('91', j) or s.startswith('92', j)):
                    j += 1
                parts['21'] = s[i+2:j]
            # 91
            k = s.find('91', 0)
            if k != -1:
                j = k + 2
                while j < len(s) and not s.startswith('92', j):
                    j += 1
                parts['91'] = s[k+2:j]
            # 92
            m = s.find('92', 0)
            if m != -1:
                parts['92'] = s[m+2:]
    except Exception:
        pass
    return parts

def _build_raw_gs1_bytes(parts: dict) -> bytes:
    """
    Формирует «сырые» GS1-байты с FNC1-разделителями (GS=0x1D) для datamatrix format=gs1.
    Схема: 01 + GTIN14 + 21 + serial + GS + [91 + v91 + GS] + [92 + v92]
    """
    chunks = []
    if parts.get('01'):
        chunks.append('01' + parts['01'])
    if parts.get('21'):
        chunks.append('21' + parts['21'])
    data = ''.join(chunks)
    tail = b''
    # После переменной длины 21 ставим GS, если есть последующие поля
    if parts.get('21') and (parts.get('91') is not None or parts.get('92') is not None):
        tail += b"\x1d"
    if parts.get('91') is not None:
        tail += ('91' + parts['91']).encode('ascii', errors='ignore')
        if parts.get('92') is not None:
            tail += b"\x1d"
    if parts.get('92') is not None:
        tail += ('92' + parts['92']).encode('ascii', errors='ignore')
    return data.encode('ascii', errors='ignore') + tail

@datamatrix_bp.route('/', methods=['GET', 'POST'])
def datamatrix_index():
    if request.method == 'POST':
        return datamatrix_processing()
    return render_template('DataMatrix/datamatrix_processing.html')

@datamatrix_bp.route('/process', methods=['POST'])
def datamatrix_processing():
    # Настройки изображения
    TARGET_WIDTH_MM = 30  # Целевая ширина в мм
    TARGET_HEIGHT_MM = 35  # Увеличиваем высоту для текста
    DPI = 600  # Разрешение в DPI
    MM_TO_PIXELS = DPI / 25.4  # Коэффициент перевода мм в пиксели
    
    # Вычисляем размеры в пикселях
    IMAGE_WIDTH_PX = int(TARGET_WIDTH_MM * MM_TO_PIXELS)
    IMAGE_HEIGHT_PX = int(TARGET_HEIGHT_MM * MM_TO_PIXELS)
    
    # Пропорции элементов (относительно размера изображения)
    DATAMATRIX_SIZE_RATIO = 0.92  # DataMatrix занимает 92% от ширины
    MARGIN_RATIO = 0.04  # Отступ 4% от размера изображения
    TEXT_HEIGHT_RATIO = 0.15  # Увеличиваем долю текста до 15% от высоты
    
    # Вычисляем размеры элементов
    DATAMATRIX_SIZE = int(IMAGE_WIDTH_PX * DATAMATRIX_SIZE_RATIO)
    MARGIN = int(IMAGE_WIDTH_PX * MARGIN_RATIO)
    TEXT_HEIGHT = int(IMAGE_HEIGHT_PX * TEXT_HEIGHT_RATIO)
    
    file = None
    if 'kiz_file' in request.files:
        file = request.files['kiz_file']
    elif 'pdf_file' in request.files:
        file = request.files['pdf_file']
    
    if file is None:
        return jsonify({'error': 'No file part'}), 400

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            doc = fitz.open(stream=file.read(), filetype="pdf")
            generated_images = []
            found_codes_count = 0

            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                # БЕЗ МАСШТАБИРОВАНИЯ - используем оригинальный размер
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                img_byte_array = pix.samples
                img_pil = Image.frombytes("RGB", [pix.width, pix.height], img_byte_array)

                # Ищем DataMatrix коды
                codes_found = decode(img_pil, max_count=16)
                print(f"[Страница {page_num + 1}] Найдено {len(codes_found)} кодов")
                
                # Сортируем коды сверху вниз по координате top
                codes_found = sorted(codes_found, key=lambda x: x.rect.top)
                
                for code in codes_found:
                    
                    # Получаем сырые байты (без декодирования в UTF-8)
                    raw_bytes = code.data
                    print(f"Сырые байты: {raw_bytes}")
                    print(f"Тип кода: {code.type if hasattr(code, 'type') else 'Unknown'}")
                    print(f"Размер матрицы: {code.rect.width:.1f}x{code.rect.height:.1f}")
                    
                    # === ДОПОЛНИТЕЛЬНАЯ ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ===
                    print(f"rect.width: {code.rect.width}")
                    print(f"rect.height: {code.rect.height}")
                    print(f"rect.left: {code.rect.left}")
                    print(f"rect.top: {code.rect.top}")
                    
                    # Определяем примерный размер матрицы
                    matrix_size_pixels = min(code.rect.width, code.rect.height)
                    print(f"Размер матрицы в пикселях: {matrix_size_pixels}x{matrix_size_pixels}")
                    
                    # Оцениваем количество модулей (примерно)
                    # DataMatrix модули обычно 2-4 пикселя каждый
                    estimated_modules = matrix_size_pixels // 3  # примерная оценка
                    print(f"Примерное количество модулей: {estimated_modules}x{estimated_modules}")
                    
                    # === КОНЕЦ ОТЛАДОЧНОЙ ИНФОРМАЦИИ ===
                    
                    # Для отображения декодируем в текст (но не используем для кодирования)
                    decoded_text = raw_bytes.decode('utf-8', errors='replace')
                    print(f"Декодированный текст для отображения: {decoded_text}")
                    
                    # Определяем GS1: либо есть GS-разделители, либо формат КИЗ (01+14 цифр)
                    has_gs = b'\x1d' in raw_bytes
                    looks_like_gs1 = _looks_like_gs1_kiz(raw_bytes)
                    is_gs1 = has_gs or looks_like_gs1
                    if is_gs1:
                        reason = 'GS-разделители' if has_gs else 'шаблон 01+14 цифр'
                        print(f"Определено как GS1 ({reason})")
                        gs1_text = decoded_text.replace('\x1d', '')
                        print(f"GS1 текст (без разделителей): {gs1_text}")
                        # Диагностика: проверка GTIN-14 и состав AI(21)
                        try:
                            # взять 14 цифр после '01'
                            idx01 = gs1_text.find('01')
                            if idx01 != -1 and len(gs1_text) >= idx01 + 16:
                                gtin14 = gs1_text[idx01+2:idx01+16]
                                print(f"GTIN14 обнаружен: {gtin14}")
                                print(f"GTIN14 валиден: {_is_valid_gtin14(gtin14)}")
                            # извлечь (21) — от '21' до следующего AI (91/92) или конца
                            idx21 = gs1_text.find('21', idx01 + 16 if idx01 != -1 else 0)
                            serial = None
                            if idx21 != -1:
                                j = idx21 + 2
                                while j < len(gs1_text) and not (gs1_text.startswith('91', j) or gs1_text.startswith('92', j)):
                                    j += 1
                                serial = gs1_text[idx21+2:j]
                                print(f"AI(21) серийный: {serial}")
                                # проверим допустимые символы по GS1: A-Z a-z 0-9 и ограниченный набор
                                # для первичной диагностики отметим наличие пробелов и табов
                                if any(ch in serial for ch in ['\t', '\n', '\r']):
                                    print("ПРЕДУПРЕЖДЕНИЕ: В AI(21) присутствуют управляющие символы")
                        except Exception as _diag_e:
                            print(f"Диагностика GS1 не удалась: {_diag_e}")
                    else:
                        print("Обычный DataMatrix (не GS1)")
                    
                    # Готовим данные для кодирования
                    print(f"Используем сырые байты как есть: {raw_bytes}")
                    print(f"Первый байт: {raw_bytes[0]} (hex: {raw_bytes[0]:02x})")
                    
                    # Определяем размер матрицы исходного кода
                    original_size = int(code.rect.width)
                    print(f"Исходный размер: {original_size}x{original_size}")
                    
                    # Используем проверенный размер 36x36
                    target_size = "36x36"
                    print(f"Выбранный размер: {target_size}")
                    
                    # Основной путь: сырая GS1-строка с GS (\x1d) для BWIPP
                    datamatrix_img = None
                    expected_ver_bytes = raw_bytes
                    if TREEPOEM_AVAILABLE and is_gs1:
                        try:
                            parts = _extract_gs1_parts(raw_bytes)
                            raw_gs1 = _build_raw_gs1_bytes(parts)
                            data_str = raw_gs1.decode('ascii', errors='ignore')
                            print(f"GS1 raw data_str repr: {repr(data_str)}")
                            datamatrix_img = treepoem.generate_barcode(
                                barcode_type='datamatrix',
                                data=data_str,
                                options={'rows': 36, 'columns': 36, 'format': 'gs1'},
                            )
                            print("Создан GS1 DataMatrix через treepoem/datamatrix (format=gs1) из сырой строки с \\x1d")
                            expected_ver_bytes = raw_gs1
                        except Exception as e:
                            print(f"datamatrix(gs1=true) с сырой строкой не удалось: {e}. Пробуем AI-строку со скобками и экранированием")
                            try:
                                # Фолбек: AI-нотация со скобками, экранируем '(' и ')' в значениях
                                def _esc(v: str) -> str:
                                    return v.replace('(', r"\(").replace(')', r"\)")
                                gs1_str_parts = []
                                if parts.get('01'):
                                    gs1_str_parts.append(f"(01){parts['01']}")
                                if parts.get('21') is not None:
                                    gs1_str_parts.append(f"(21){_esc(parts['21'])}")
                                if parts.get('91') is not None:
                                    gs1_str_parts.append(f"(91){_esc(parts['91'])}")
                                if parts.get('92') is not None:
                                    gs1_str_parts.append(f"(92){_esc(parts['92'])}")
                                gs1_str = ''.join(gs1_str_parts)
                                print(f"GS1 AI-строка (escaped) repr: {repr(gs1_str)}")
                                datamatrix_img = treepoem.generate_barcode(
                                    barcode_type='gs1datamatrix',
                                    data=gs1_str,
                                    options={'rows': 36, 'columns': 36},
                                )
                                print("Создан GS1 DataMatrix через treepoem/gs1datamatrix из AI-строки (escaped)")
                                expected_ver_bytes = raw_gs1
                            except Exception as e2:
                                print(f"AI-строка (escaped) через gs1datamatrix не удалась: {e2}. Фолбек на pylibdmtx")

                    if datamatrix_img is None:
                        # Фолбек: обычное кодирование через pylibdmtx без GS1-режима
                        text_bytes = raw_bytes  # не добавляем FNC1, чтобы не искажать данные
                        try:
                            encoded = encode(text_bytes, size=target_size)
                        except TypeError:
                            print("Параметр size не поддерживается, используем базовое кодирование")
                            encoded = encode(text_bytes)
                        datamatrix_img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
                        print(f"Создан DataMatrix через pylibdmtx размером {encoded.width}x{encoded.height} пикселей")
                        if is_gs1:
                            print("ВНИМАНИЕ: код выглядит как GS1, но закодирован без GS1/FNC1 из-за фолбэка. Сканер может сообщить об отсутствии лидирующего символа.")
                    
                    # Верификация: проверим, что закодированные байты совпадают с ожидаемыми (что кодировали)
                    try:
                        _ver_img = datamatrix_img.convert('RGB')
                        _ver_dec = decode(_ver_img, max_count=1)
                        if _ver_dec:
                            _ver_bytes = _ver_dec[0].data
                            print(f"Проверка: совпадение байтов с ожидаемыми: {_ver_bytes == expected_ver_bytes}")
                            if _ver_bytes != expected_ver_bytes:
                                print(f"Новые байты: {_ver_bytes}")
                        else:
                            print("Проверка: не удалось декодировать сгенерированный код")
                    except Exception as _ver_e:
                        print(f"Проверка закодированных байт завершилась ошибкой: {_ver_e}")

                    # Конвертируем в бинарное изображение
                    datamatrix_img = datamatrix_img.convert('1')
                    
                    # Создаем изображение с высоким разрешением
                    final_img = Image.new('1', (IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX), 1)
                    
                    # Масштабируем DataMatrix код
                    datamatrix_resized = datamatrix_img.resize((DATAMATRIX_SIZE, DATAMATRIX_SIZE), Image.Resampling.NEAREST)
                    
                    # Вставляем DataMatrix код с отступом
                    final_img.paste(datamatrix_resized, (MARGIN, MARGIN))
                    
                    # Добавляем текст внизу
                    draw = ImageDraw.Draw(final_img)
                    
                    # Размер шрифта пропорционально размеру изображения
                    FONT_SIZE_RATIO = 0.07
                    font_size = max(8, int(IMAGE_WIDTH_PX * FONT_SIZE_RATIO))
                    
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Сокращаем текст для отображения
                    display_text = decoded_text[:31] if len(decoded_text) > 31 else decoded_text
                    
                    # Разбиваем текст на две строки
                    text_lines = []
                    if len(display_text) > 15:
                        text_lines = [display_text[:15], display_text[15:31]]
                    else:
                        text_lines = [display_text]
                    
                    # Центрируем текст
                    for i, line in enumerate(text_lines):
                        # Получаем размер текста
                        bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = bbox[2] - bbox[0]
                        
                        # Ограничиваем ширину текста до 90% от ширины DataMatrix
                        max_text_width = int(DATAMATRIX_SIZE * 0.9)
                        if text_width > max_text_width:
                            # Если текст слишком широкий, сокращаем его
                            while text_width > max_text_width and len(line) > 1:
                                line = line[:-1]
                                bbox = draw.textbbox((0, 0), line, font=font)
                                text_width = bbox[2] - bbox[0]
                        
                        # Вычисляем позицию для центрирования
                        x = (IMAGE_WIDTH_PX - text_width) // 2
                        y = DATAMATRIX_SIZE + MARGIN + i * (font_size + 2)
                        
                        draw.text((x, y), line, fill=0, font=font)
                    
                    # Сохраняем в base64
                    img_byte_arr = io.BytesIO()
                    final_img.save(img_byte_arr, format='PNG', optimize=False)
                    img_byte_arr.seek(0)
                    generated_images.append(base64.b64encode(img_byte_arr.getvalue()).decode('utf-8'))
                    found_codes_count += 1


            if found_codes_count == 0:
                return jsonify({'message': 'DataMatrix коды не найдены в загруженном файле.', 'encoded_images': []})
            
            return jsonify({
                'message': f'Сгенерировано {found_codes_count} DataMatrix кодов.', 
                'encoded_images': generated_images
            })

        except Exception as e:
            current_app.logger.error(f"Ошибка при обработке PDF: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@datamatrix_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    encoded_images = data.get('images', [])
    
    if not encoded_images:
        return jsonify({'error': 'No images provided for PDF generation'}), 400

    # Используем те же настройки, что и при создании изображений
    TARGET_WIDTH_MM = 30  # Целевая ширина в мм
    TARGET_HEIGHT_MM = 35  # Увеличиваем высоту для текста
    DPI = 600  # Разрешение в DPI
    MM_TO_PIXELS = DPI / 25.4  # Коэффициент перевода мм в пиксели
    
    # Вычисляем размеры в пикселях
    IMAGE_WIDTH_PX = int(TARGET_WIDTH_MM * MM_TO_PIXELS)
    IMAGE_HEIGHT_PX = int(TARGET_HEIGHT_MM * MM_TO_PIXELS)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX))  # Размер как у изображений
    width, height = IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX

    for i, encoded_img_data in enumerate(encoded_images):
        img_data = base64.b64decode(encoded_img_data)
        img = ImageReader(io.BytesIO(img_data))
        
        # Рисуем изображение в оригинальном размере
        c.drawImage(img, 0, 0, width=width, height=height)
        c.showPage()

    c.save()
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='datamatrix_codes.pdf')
