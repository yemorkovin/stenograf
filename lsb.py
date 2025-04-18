from PIL import Image


def hide_message(image_path, message, output_path):
    """Скрывает сообщение в изображении методом LSB"""
    try:
        # Открываем изображение
        img = Image.open(image_path)
        # Преобразуем в RGB, если изображение в другом формате
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Получаем размеры изображения
        width, height = img.size
        # Вычисляем максимальную длину сообщения (в байтах)
        # 3 канала (RGB) на пиксель, 8 бит на байт, -4 байта для хранения длины
        max_message_length = (width * height * 3) // 8 - 4

        # Проверяем, не слишком ли длинное сообщение
        if len(message) > max_message_length:
            raise ValueError(f"Сообщение слишком длинное. Максимальная длина: {max_message_length}")

        # Преобразуем сообщение в битовый поток
        message_length = len(message)
        message_bits = []

        # Добавляем длину сообщения (4 байта = 32 бита)
        for i in range(32):
            # Побитово извлекаем каждый бит длины сообщения
            message_bits.append((message_length >> (31 - i)) & 1)

        # Добавляем само сообщение
        for char in message:
            # Для каждого символа извлекаем 8 бит
            for i in range(8):
                message_bits.append((ord(char) >> (7 - i)) & 1)

        # Получаем все пиксели изображения
        pixels = list(img.getdata())
        new_pixels = []
        message_index = 0

        # Обрабатываем каждый пиксель
        for pixel in pixels:
            # Если все биты сообщения уже записаны, оставляем пиксель без изменений
            if message_index >= len(message_bits):
                new_pixels.append(pixel)
                continue

            # Разбираем пиксель на каналы R, G, B
            r, g, b = pixel
            # Модифицируем младший бит каждого канала
            if message_index < len(message_bits):
                r = (r & 0xFE) | message_bits[message_index]
                message_index += 1
            if message_index < len(message_bits):
                g = (g & 0xFE) | message_bits[message_index]
                message_index += 1
            if message_index < len(message_bits):
                b = (b & 0xFE) | message_bits[message_index]
                message_index += 1
            new_pixels.append((r, g, b))

        # Создаем новое изображение с модифицированными пикселями
        new_img = Image.new('RGB', img.size)
        new_img.putdata(new_pixels)
        # Сохраняем в формате BMP (без сжатия)
        new_img.save(output_path, 'BMP')
        return True
    except Exception as e:
        raise e
def extract_message(image_path):
    """Извлекает сообщение из изображения, используя метод LSB"""
    try:
        # Открываем изображение
        img = Image.open(image_path)
        # Преобразуем в RGB, если необходимо
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Получаем все пиксели изображения
        pixels = list(img.getdata())
        message_bits = []

        # Собираем все младшие биты из каждого канала каждого пикселя
        for pixel in pixels:
            r, g, b = pixel
            message_bits.append(r & 1)
            message_bits.append(g & 1)
            message_bits.append(b & 1)

        # Извлекаем длину сообщения (первые 32 бита)
        message_length = 0
        for i in range(32):
            # Собираем 32-битное число из битов
            message_length = (message_length << 1) | message_bits[i]

        # Проверяем корректность длины сообщения
        if message_length < 0 or message_length > (len(message_bits) - 32) // 8:
            return ""  # Некорректная длина - возможно, в изображении нет сообщения

        # Извлекаем само сообщение
        message = []
        for i in range(32, 32 + message_length * 8, 8):
            char = 0
            # Собираем каждый символ из 8 бит
            for j in range(8):
                if i + j < len(message_bits):
                    char = (char << 1) | message_bits[i + j]
                else:
                    char = (char << 1)  # Если битов не хватает, дополняем нулями
            message.append(chr(char))

        # Возвращаем собранное сообщение
        return ''.join(message)
    except Exception as e:
        raise e