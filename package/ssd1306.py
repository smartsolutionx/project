import smbus
import time

class SSD1306:
    def __init__(self, width=128, height=64, i2c_bus=1, address=0x3C):
        self.width = width
        self.height = height
        self.pages = self.height // 8
        self.address = address
        self.buffer = [0x00] * (self.width * self.pages)
        self.bus = smbus.SMBus(i2c_bus)

        self.init_display()

    def command(self, cmd):
        self.bus.write_i2c_block_data(self.address, 0x00, [cmd])

    def data(self, data):
        for i in range(0, len(data), 16):
            self.bus.write_i2c_block_data(self.address, 0x40, data[i:i+16])

    def init_display(self):
        init_cmds = [
            0xAE, 0x20, 0x00, 0xB0, 0xC8, 0x00, 0x10, 0x40,
            0x81, 0x7F, 0xA1, 0xA6, 0xA8, 0x3F, 0xA4,
            0xD3, 0x00, 0xD5, 0x80, 0xD9, 0xF1, 0xDA, 0x12,
            0xDB, 0x40, 0x8D, 0x14, 0xAF
        ]
        for cmd in init_cmds:
            self.command(cmd)
        self.clear()
        self.display()

    def clear(self):
        self.buffer = [0x00] * (self.width * self.pages)

    def display(self):
        for page in range(self.pages):
            self.command(0xB0 + page)
            self.command(0x00)
            self.command(0x10)
            start = page * self.width
            end = start + self.width
            self.data(self.buffer[start:end])

    def draw_pixel(self, x, y, color=1):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        index = x + (y // 8) * self.width
        if color:
            self.buffer[index] |= (1 << (y % 8))
        else:
            self.buffer[index] &= ~(1 << (y % 8))

    def draw_char(self, x, y, char):
        font = FONT.get(char, FONT.get(' '))
        for i in range(5):
            line = font[i]
            for j in range(8):
                if line & (1 << j):
                    self.draw_pixel(x + i, y + j)

    def draw_text(self, x, y, text):
        for i, c in enumerate(text):
            self.draw_char(x + (i * 6), y, c)

# Extended 5x8 FONT with lowercase and symbols
FONT = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    '!': [0x00, 0x00, 0x5F, 0x00, 0x00],
    '"': [0x00, 0x03, 0x00, 0x03, 0x00],
    '#': [0x14, 0x7F, 0x14, 0x7F, 0x14],
    '$': [0x24, 0x2A, 0x7F, 0x2A, 0x12],
    '%': [0x23, 0x13, 0x08, 0x64, 0x62],
    '&': [0x36, 0x49, 0x55, 0x22, 0x50],
    '\'': [0x00, 0x05, 0x03, 0x00, 0x00],
    '(': [0x00, 0x1C, 0x22, 0x41, 0x00],
    ')': [0x00, 0x41, 0x22, 0x1C, 0x00],
    '*': [0x14, 0x08, 0x3E, 0x08, 0x14],
    '+': [0x08, 0x08, 0x3E, 0x08, 0x08],
    ',': [0x00, 0x50, 0x30, 0x00, 0x00],
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],
    '.': [0x00, 0x60, 0x60, 0x00, 0x00],
    '/': [0x20, 0x10, 0x08, 0x04, 0x02],
    '0': [0x3E, 0x45, 0x49, 0x51, 0x3E],
    '1': [0x00, 0x41, 0x7F, 0x40, 0x00],
    '2': [0x62, 0x51, 0x49, 0x49, 0x46],
    '3': [0x22, 0x41, 0x49, 0x49, 0x36],
    '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
    '5': [0x27, 0x45, 0x45, 0x45, 0x39],
    '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
    '7': [0x01, 0x71, 0x09, 0x05, 0x03],
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],
    '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
    ':': [0x00, 0x36, 0x36, 0x00, 0x00],
    ';': [0x00, 0x56, 0x36, 0x00, 0x00],
    '<': [0x08, 0x14, 0x22, 0x41, 0x00],
    '=': [0x14, 0x14, 0x14, 0x14, 0x14],
    '>': [0x00, 0x41, 0x22, 0x14, 0x08],
    '?': [0x02, 0x01, 0x59, 0x09, 0x06],
    '@': [0x3E, 0x41, 0x5D, 0x59, 0x4E],
    'A': [0x7E, 0x11, 0x11, 0x7E, 0x00],
    'B': [0x7F, 0x49, 0x49, 0x36, 0x00],
    'C': [0x3E, 0x41, 0x41, 0x22, 0x00],
    'D': [0x7F, 0x41, 0x41, 0x3E, 0x00],
    'E': [0x7F, 0x49, 0x49, 0x41, 0x00],
    'F': [0x7F, 0x09, 0x09, 0x01, 0x00],
    'G': [0x3E, 0x41, 0x51, 0x32, 0x00],
    'H': [0x7F, 0x08, 0x08, 0x7F, 0x00],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
    'J': [0x20, 0x40, 0x41, 0x3F, 0x00],
    'K': [0x7F, 0x08, 0x14, 0x63, 0x00],
    'L': [0x7F, 0x40, 0x40, 0x40, 0x00],
    'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F],
    'N': [0x7F, 0x04, 0x08, 0x7F, 0x00],
    'O': [0x3E, 0x41, 0x41, 0x3E, 0x00],
    'P': [0x7F, 0x09, 0x09, 0x06, 0x00],
    'Q': [0x3E, 0x41, 0x51, 0x3E, 0x40],
    'R': [0x7F, 0x09, 0x19, 0x66, 0x00],
    'S': [0x46, 0x49, 0x49, 0x31, 0x00],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
    'U': [0x3F, 0x40, 0x40, 0x3F, 0x00],
    'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
    'W': [0x3F, 0x40, 0x38, 0x40, 0x3F],
    'X': [0x63, 0x14, 0x08, 0x14, 0x63],
    'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
    'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
    'a': [0x20, 0x54, 0x54, 0x78, 0x00],
    'b': [0x7F, 0x48, 0x48, 0x30, 0x00],
    'c': [0x38, 0x44, 0x44, 0x28, 0x00],
    'd': [0x30, 0x48, 0x48, 0x7F, 0x00],
    'e': [0x38, 0x54, 0x54, 0x58, 0x00],
    'f': [0x08, 0x7E, 0x09, 0x02, 0x00],
    'g': [0x18, 0xA4, 0xA4, 0x7C, 0x00],
    'h': [0x7F, 0x08, 0x08, 0x70, 0x00],
    'i': [0x00, 0x48, 0x7A, 0x40, 0x00],
    'j': [0x40, 0x80, 0x88, 0x7A, 0x00],
    'k': [0x7F, 0x10, 0x28, 0x44, 0x00],
    'l': [0x00, 0x41, 0x7F, 0x40, 0x00],
    'm': [0x7C, 0x04, 0x18, 0x04, 0x78],
    'n': [0x7C, 0x08, 0x04, 0x7C, 0x00],
    'o': [0x38, 0x44, 0x44, 0x38, 0x00],
    'p': [0xFC, 0x24, 0x24, 0x18, 0x00],
    'q': [0x18, 0x24, 0x24, 0xFC, 0x00],
    'r': [0x7C, 0x08, 0x04, 0x08, 0x00],
    's': [0x48, 0x54, 0x54, 0x24, 0x00],
    't': [0x04, 0x3F, 0x44, 0x40, 0x00],
    'u': [0x3C, 0x40, 0x20, 0x7C, 0x00],
    'v': [0x1C, 0x20, 0x40, 0x20, 0x1C],
    'w': [0x3C, 0x40, 0x30, 0x40, 0x3C],
    'x': [0x44, 0x28, 0x10, 0x28, 0x44],
    'y': [0x4C, 0x90, 0x90, 0x7C, 0x00],
    'z': [0x44, 0x64, 0x54, 0x4C, 0x44],
}
