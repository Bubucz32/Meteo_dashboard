from PIL import Image
import os
import glob

# Cílové rozměry pro nativní portrétní uspořádání v paměti řadiče
TARGET_WIDTH = 480
TARGET_HEIGHT = 800
ROW_BYTES = TARGET_WIDTH // 8  # 480 / 8 = 60 bajtů na řádek
BUF_SIZE = ROW_BYTES * TARGET_HEIGHT  # 60 * 800 = 48 000 bajtů

def convert_png_to_bin(png_path, bin_path):
    img = Image.open(png_path).convert('RGB')
    
    print(f"Původní rozměry obrázku: {img.width}x{img.height}")

    # Převod a otočení na cílový rozměr 480x800
    if img.width == 800 and img.height == 480:
        print("Otáčím landscape (800x480) na portrét (480x800)...")
        # Transpozice nebo rotace (zde použijeme správnou orientaci pro srovnání)
        img = img.rotate(270, expand=True)
    elif img.width != TARGET_WIDTH or img.height != TARGET_HEIGHT:
        print(f"Měním velikost na {TARGET_WIDTH}x{TARGET_HEIGHT}...")
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT))
    else:
        print("Obrázek již má správný formát 480x800.")

    bw_buffer = bytearray(BUF_SIZE)
    red_buffer = bytearray(BUF_SIZE)

    # Výchozí stav: BW bílá (0xFF), RED vypnutá (0x00)
    for i in range(BUF_SIZE):
        bw_buffer[i] = 0xFF
        red_buffer[i] = 0x00

    pixels = img.load()

    for y in range(TARGET_HEIGHT):
        for x in range(TARGET_WIDTH):
            r, g, b = pixels[x, y]

            byte_idx = (y * ROW_BYTES) + (x // 8)
            bit_pos = 7 - (x % 8)

            # Detekce červené barvy
            if r > 140 and g < 90 and b < 90:
                red_buffer[byte_idx] |= (1 << bit_pos)  # Červená aktivní
                bw_buffer[byte_idx] |= (1 << bit_pos)   # Pod červenou bílý podklad
            else:
                red_buffer[byte_idx] &= ~(1 << bit_pos) # Červená neaktivní
                
                # Výpočet jasu pro černou vs bílou
                luminance = (r * 299 + g * 587 + b * 114) // 1000
                if luminance < 100:
                    bw_buffer[byte_idx] &= ~(1 << bit_pos) # Černá
                else:
                    bw_buffer[byte_idx] |= (1 << bit_pos)  # Bílá

    with open(bin_path, "wb") as f:
        f.write(bw_buffer)
        f.write(red_buffer)

    file_size = os.path.getsize(bin_path)
    print(f"Vytvořen binární soubor: {bin_path} ({file_size} B)")


if __name__ == "__main__":
    out_dir = "out"
    png_files = glob.glob(os.path.join(out_dir, "*.png"))

    if not png_files:
        print(f"Chyba: Ve složce '{out_dir}' nejsou žádné PNG obrázky.")
    else:
        for png_file in png_files:
            bin_file = os.path.splitext(png_file)[0] + ".bin"
            convert_png_to_bin(png_file, bin_file)
