from pylibdmtx.pylibdmtx import decode, encode
from pylibdmtx.wrapper import DmtxProperty
from PIL import Image
import io

print("=== ТЕСТ FNC1 СВОЙСТВА ===")

# Создаем тестовый DataMatrix с FNC1
test_data = b'\xe8' + b'0104610337029085215ZahWQAEw;Y(f\x1d91EE11\x1d92hDRpl3jPomP5h3NsMkhhZn6vT1fAWa9NZ5pUsw01Pew='

print(f"Тестовые данные: {test_data}")
print(f"Первый байт: {test_data[0]} (hex: {test_data[0]:02x})")

# Кодируем DataMatrix
encoded = encode(test_data, size="36x36")
img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)

print(f"Создан DataMatrix размером {encoded.width}x{encoded.height}")

# Сохраняем для тестирования
img.save('test_datamatrix.png')

print("\n=== ДЕКОДИРОВАНИЕ БЕЗ FNC1 СВОЙСТВА ===")
# Декодируем без специальных настроек
result1 = decode(img, max_count=1)
if result1:
    print(f"Результат без FNC1 настройки: {result1[0].data}")
    print(f"Первый байт: {result1[0].data[0] if result1[0].data else 'None'} (hex: {result1[0].data[0]:02x if result1[0].data else 'None'})")

print("\n=== ДОСТУПНЫЕ СВОЙСТВА ===")
print("DmtxProperty.DmtxPropFnc1 =", DmtxProperty.DmtxPropFnc1)

# Проверим, есть ли другие свойства, связанные с FNC1
for prop in DmtxProperty:
    if 'fnc' in prop.name.lower():
        print(f"{prop.name} = {prop.value}")
