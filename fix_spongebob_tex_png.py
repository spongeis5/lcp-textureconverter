import os
import sys
import struct

try:
    from PIL import Image
except ImportError:
    print("Error: The 'Pillow' library is required to run this script.")
    print("Please install it by running: pip install Pillow")
    sys.exit(1)

def batch_convert_textures_to_png(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: The provided path is not a valid folder: '{folder_path}'")
        return

    output_folder = os.path.join(folder_path, "png_converted")
    os.makedirs(output_folder, exist_ok=True)
    print(f"Converted PNG files will be saved in: '{output_folder}'\n")

    files_processed = 0
    files_converted = 0
    files_failed = 0
    
    TARGET_PREFIXES = ('tex_', 'tx8_', 'tx1_')
    FOLDERS_TO_IGNORE = ['fixed_dds', 'png_converted']

    for item_name in sorted(os.listdir(folder_path)):
        input_path = os.path.join(folder_path, item_name)

        if os.path.isdir(input_path) and item_name in FOLDERS_TO_IGNORE:
            continue
            
        if os.path.isfile(input_path) and item_name.lower().startswith(TARGET_PREFIXES):
            files_processed += 1
            print(f"--- Processing: {item_name} ---")

            try:
                image_object = open_any_dds(input_path)

                if image_object:
                    if image_object.mode != 'RGBA':
                        image_object = image_object.convert('RGBA')

                    output_path = os.path.join(output_folder, f"{item_name}.png")
                    image_object.save(output_path, 'PNG')
                    
                    print(f"-> Successfully converted and saved to '{output_path}'\n")
                    files_converted += 1
                else:
                    print(f"-> Failed to process file.\n")
                    files_failed += 1

            except Exception as e:
                print(f"-> An unexpected error occurred while processing '{item_name}': {e}\n")
                files_failed += 1

    print("=" * 40)
    print("Batch conversion complete.")
    print(f"Total Texture Files Found: {files_processed}")
    print(f"Successfully Converted: {files_converted}")
    print(f"Failed or Skipped: {files_failed}")
    print("=" * 40)


def open_any_dds(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(128)

    if len(header) < 128 or header[0:4] != b'DDS ':
        print("-> File does not have a valid DDS signature. Skipping.")
        return None

    KNOWN_BROKEN_FLAGS = [0x60, 0x61]
    flags_offset = 0x50
    bit_count_offset = 0x58
    
    current_flag = header[flags_offset]
    is_broken_palettized = (
        current_flag in KNOWN_BROKEN_FLAGS and
        header[bit_count_offset] == 0x08
    )

    if is_broken_palettized:
        print("-> Custom palettized format detected. Fixing in memory...")
        with open(file_path, 'rb') as f:
            full_data = f.read()
        return _fix_and_open_custom_dds(full_data)
    else:
        print("-> Standard DDS format detected. Converting directly...")
        try:
            return Image.open(file_path)
        except Exception as e:
            print(f"-> Pillow could not open standard DDS: {e}")
            return None


def _fix_and_open_custom_dds(dds_data):
    HEADER_SIZE = 128
    PALETTE_SIZE = 1024

    header = dds_data[:HEADER_SIZE]
    palette_data = dds_data[-PALETTE_SIZE:]
    pixel_indices = dds_data[HEADER_SIZE:-PALETTE_SIZE]
    
    height, width = struct.unpack('<II', header[12:20])
    
    img = Image.new('P', (width, height))
    img.putdata(pixel_indices)

    fixed_palette_list = []
    for i in range(0, PALETTE_SIZE, 4):
        r = palette_data[i]
        g = palette_data[i+1]
        b = palette_data[i+2]
        fixed_palette_list.extend([b, g, r])
        
    img.putpalette(fixed_palette_list)

    alpha_lookup = [palette_data[i+3] for i in range(0, PALETTE_SIZE, 4)]
    alpha_mask_data = [alpha_lookup[index] for index in pixel_indices]
    
    mask = Image.new('L', (width, height))
    mask.putdata(alpha_mask_data)
    
    img = img.convert('RGBA')
    img.putalpha(mask)
    
    return img


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_game_textures.py <path_to_folder_with_game_textures>")
        sys.exit(1)
        
    target_folder = sys.argv[1]
    batch_convert_textures_to_png(target_folder)