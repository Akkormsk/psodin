from pylibdmtx.pylibdmtx import decode, encode
import inspect
from PIL import Image
import numpy as np

# Получаем информацию о функции decode
print("=== ПАРАМЕТРЫ pylibdmtx.decode ===")
print(inspect.signature(decode))
print("\n=== ДОКУМЕНТАЦИЯ ===")
print(decode.__doc__)

# Проверяем доступные атрибуты
print("\n=== ДОСТУПНЫЕ АТРИБУТЫ ===")
print(dir(decode))

# Создаем тестовое изображение с простым DataMatrix
print("\n=== ПРОВЕРКА ОБЪЕКТА DECODED ===")

# Создаем минимальное тестовое изображение
test_img = Image.new('RGB', (100, 100), color='white')

try:
    # Пытаемся декодировать (может не найти коды, но покажет структуру)
    result = decode(test_img, max_count=1)
    if result:
        decoded_obj = result[0]
        print("Атрибуты объекта Decoded:")
        print(dir(decoded_obj))
        print(f"\nТип data: {type(decoded_obj.data)}")
        print(f"data: {decoded_obj.data}")
        print(f"rect: {decoded_obj.rect}")
        
        # Анализируем размеры
        print(f"\n=== АНАЛИЗ РАЗМЕРОВ ===")
        print(f"rect.width: {decoded_obj.rect.width}")
        print(f"rect.height: {decoded_obj.rect.height}")
        print(f"rect.left: {decoded_obj.rect.left}")
        print(f"rect.top: {decoded_obj.rect.top}")
        
        # Вычисляем примерный размер матрицы
        # DataMatrix обычно квадратный, поэтому берем минимальный размер
        matrix_size = min(decoded_obj.rect.width, decoded_obj.rect.height)
        print(f"Примерный размер матрицы в пикселях: {matrix_size}x{matrix_size}")
        
    else:
        print("Коды не найдены в тестовом изображении")
except Exception as e:
    print(f"Ошибка: {e}")

print("\n=== ДОСТУПНЫЕ РАЗМЕРЫ MATRIX ===")
# Проверим доступные размеры матриц
from pylibdmtx.wrapper import DmtxSymbolSize
print("Доступные размеры матриц:")
for size in DmtxSymbolSize:
    print(f"  {size.name}: {size.value}")
