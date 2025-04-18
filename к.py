from PIL import Image


def hide_message(image_path, message, output_path):
    """Скрывает сообщение в изображении методом LSB (поддерживает Unicode)"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size
        # Преобразуем сообщение в байты (UTF-8)
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)

        # 3 бита на пиксель (RGB), поэтому максимальная длина в байтах:
        max_message_length = (width * height * 3) // 8 - 4

        if message_length > max_message_length:
            raise ValueError(f"Сообщение слишком длинное. Максимальная длина: {max_message_length}")

        # Преобразуем длину сообщения и само сообщение в биты
        message_bits = []

        # Добавляем длину сообщения (4 байта = 32 бита)
        for i in range(32):
            message_bits.append((message_length >> (31 - i)) & 1)

        # Добавляем само сообщение (каждый байт как 8 бит)
        for byte in message_bytes:
            for i in range(8):
                message_bits.append((byte >> (7 - i)) & 1)

        pixels = list(img.getdata())
        new_pixels = []
        message_index = 0

        for pixel in pixels:
            if message_index >= len(message_bits):
                new_pixels.append(pixel)
                continue

            r, g, b = pixel
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

        new_img = Image.new('RGB', img.size)
        new_img.putdata(new_pixels)
        new_img.save(output_path, 'BMP')
        return True
    except Exception as e:
        raise e


def extract_message(image_path):
    """Извлекает сообщение из изображения, используя метод LSB (поддерживает Unicode)"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        pixels = list(img.getdata())
        message_bits = []

        for pixel in pixels:
            r, g, b = pixel
            message_bits.append(r & 1)
            message_bits.append(g & 1)
            message_bits.append(b & 1)

        # Извлекаем длину сообщения (первые 32 бита)
        message_length = 0
        for i in range(32):
            message_length = (message_length << 1) | message_bits[i]

        # Проверяем корректность длины
        if message_length < 0 or message_length > (len(message_bits) - 32) // 8:
            return ""

        # Извлекаем байты сообщения
        message_bytes = bytearray()
        for i in range(32, 32 + message_length * 8, 8):
            byte = 0
            for j in range(8):
                if i + j < len(message_bits):
                    byte = (byte << 1) | message_bits[i + j]
            message_bytes.append(byte)

        # Декодируем из UTF-8
        return message_bytes.decode('utf-8')
    except Exception as e:
        raise e