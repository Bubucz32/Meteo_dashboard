from PIL import Image
import os

WIDTH = 800
HEIGHT = 480
BUF_SIZE = (WIDTH * HEIGHT) // 8 # 48 000 bytů

def convert_png_to_bin(png_path, bin_path):
    img = Image.open(png_path).convert('RGB')
    
    if img.width != WIDTH or img.height != HEIGHT:
        img = img.resize((WIDTH, HEIGHT))

    bw_buffer = bytearray(BUF_SIZE)
    red_buffer = bytearray(BUF_SIZE)

    # Naplnění výchozí hodnotou (BW bílá = 1, RED vypnutá = 0)
    for i in range(BUF_SIZE):
        bw_buffer[i] = 0xFF
        red_buffer[i] = 0x00

    pixels = img.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = pixels[x, y]

            byte_idx = (y * (WIDTH // 8)) + (x // 8)
            bit_pos = 7 - (x % 8)

            # Rozpoznání červené barvy
            if r > 140 and g < 90 and b < 90:
                red_buffer[byte_idx] |= (1 << bit_pos)  # RED = 1
                bw_buffer[byte_idx] |= (1 << bit_pos)   # BW = 1 (bílá pod červenou)
            else:
                red_buffer[byte_idx] &= ~(1 << bit_pos) # RED = 0
                
                # Výpočet jasu (Luminance) pro ČERNÁ vs BÍLÁ
                luminance = (r * 299 + g * 587 + b * 114) // 1000
                if luminance < 100:
                    bw_buffer[byte_idx] &= ~(1 << bit_pos) # BW = 0 (Černá)
                else:
                    bw_buffer[byte_idx] |= (1 << bit_pos)  # BW = 1 (Bílá)

    # Spojení bufferů do jednoho 96KB souboru
    # Prvních 48KB = BW buffer, dalších 48KB = RED buffer
    with open(bin_path, "wb") as f:
        f.write(bw_buffer)
        f.write(red_buffer)

    print(f"Úspěšně vygenerován {bin_path} ({os.path.getsize(bin_path)} bytů).")

if __name__ == "__main__":
    convert_png_to_bin("index_dark_landscape.png", "display_data.bin")
