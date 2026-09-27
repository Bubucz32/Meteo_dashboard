from PIL import Image
import os
import glob

# Cílové fyzické rozlišení E-Paper displeje (vždy 800x480 pixelů)
TARGET_WIDTH = 800
TARGET_HEIGHT = 480
BUF_SIZE = (TARGET_WIDTH * TARGET_HEIGHT) // 8  # Přesně 48 000 bytů pro každý buffer


def convert_png_to_bin(png_path, bin_path):
    img = Image.open(png_path).convert('RGB')
    
    # Pokud jde o orientaci na výšku (Portrait 480x800), otočíme obrázek o 90° doprava,
    # aby fyzicky odpovídal displeji 800x480.
    if img.width == 480 and img.height == 800:
        print(f" Detekován Portrait (480x800), otáčím o 270° na landscape 800x480...")
        img = img.rotate(270, expand=True)

    # Zajištění přesných rozměrů 800x480
    if img.width != TARGET_WIDTH or img.height != TARGET_HEIGHT:
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT))

    bw_buffer = bytearray(BUF_SIZE)
    red_buffer = bytearray(BUF_SIZE)

    # Výchozí stav bufferů: BW bílá (0xFF), RED vypnutá (0x00)
    for i in range(BUF_SIZE):
        bw_buffer[i] = 0xFF
        red_buffer[i] = 0x00

    pixels = img.load()

    for y in range(TARGET_HEIGHT):
        for x in range(TARGET_WIDTH):
            r, g, b = pixels[x, y]

            byte_idx = (y * (TARGET_WIDTH // 8)) + (x // 8)
            bit_pos = 7 - (x % 8)

            # 1. Detekce ČERVENÉ barvy
            if r > 140 and g < 90 and b < 90:
                red_buffer[byte_idx] |= (1 << bit_pos)  # RED = 1
                bw_buffer[byte_idx] |= (1 << bit_pos)   # BW = 1 (Bílá pod červenou)
            else:
                red_buffer[byte_idx] &= ~(1 << bit_pos) # RED = 0
                
                # 2. Výpočet jasu (Luminance) pro ČERNÁ vs BÍLÁ
                luminance = (r * 299 + g * 587 + b * 114) // 1000
                if luminance < 100:
                    bw_buffer[byte_idx] &= ~(1 << bit_pos) # BW = 0 (Černá)
                else:
                    bw_buffer[byte_idx] |= (1 << bit_pos)  # BW = 1 (Bílá)

    # Zápis obou bufferů (48 kB + 48 kB = 96 kB) do jednoho .bin souboru
    with open(bin_path, "wb") as f:
        f.write(bw_buffer)
        f.write(red_buffer)

    file_size = os.path.getsize(bin_path)
    print(f" Vytvořen soubor: {bin_path} ({file_size} B)")


if __name__ == "__main__":
    out_dir = "out"
    png_files = glob.glob(os.path.join(out_dir, "*.png"))

    if not png_files:
        print(f"Chyba: Ve složce '{out_dir}' nebyly nalezeny žádné PNG obrázky.")
    else:
        print(f"Nalezeno {len(png_files)} obrázků ke konverzi do BIN...")
        for png_file in png_files:
            # Nahradí příponu .png za .bin (např. out/index_landscape.png -> out/index_landscape.bin)
            bin_file = os.path.splitext(png_file)[0] + ".bin"
            convert_png_to_bin(png_file, bin_file)
