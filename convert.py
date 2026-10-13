from PIL import Image
import os
import glob

# Nativní rozlišení panelu dle Pervasive
TARGET_WIDTH = 480
TARGET_HEIGHT = 800

ROW_BYTES = TARGET_WIDTH // 8  # 60
BUF_SIZE = ROW_BYTES * TARGET_HEIGHT  # 48000

def convert_png_to_bin(png_path, bin_path):
    img = Image.open(png_path).convert("RGB")

    # Otočení landscape dashboardu do portrait formátu displeje
    img = img.rotate(90, expand=True)

    if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT))

    bw_buffer = bytearray([0xFF] * BUF_SIZE)
    red_buffer = bytearray([0x00] * BUF_SIZE)

    pixels = img.load()

    for y in range(TARGET_HEIGHT):
        for x in range(TARGET_WIDTH):

            r, g, b = pixels[x, y]

            byte_idx = y * ROW_BYTES + (x // 8)
            bit_pos = 7 - (x % 8)

            # RED plane
            if r > 140 and g < 90 and b < 90:

                # red pixel
                red_buffer[byte_idx] |= (1 << bit_pos)

                # BW musí být bílé pod červenou
                bw_buffer[byte_idx] |= (1 << bit_pos)

            else:

                red_buffer[byte_idx] &= ~(1 << bit_pos)

                luminance = (r * 299 + g * 587 + b * 114) // 1000

                if luminance < 100:
                    # black
                    bw_buffer[byte_idx] &= ~(1 << bit_pos)
                else:
                    # white
                    bw_buffer[byte_idx] |= (1 << bit_pos)

    with open(bin_path, "wb") as f:
        f.write(bw_buffer)
        f.write(red_buffer)

    print(f"Vytvořeno: {bin_path}")
    print(f"Velikost: {os.path.getsize(bin_path)} B")


if __name__ == "__main__":

    out_dir = "out"
    png_files = glob.glob(os.path.join(out_dir, "*.png"))

    if not png_files:
        print(f"Ve složce {out_dir} nejsou PNG soubory.")
    else:
        for png_file in png_files:
            bin_file = os.path.splitext(png_file)[0] + ".bin"
            convert_png_to_bin(png_file, bin_file)
