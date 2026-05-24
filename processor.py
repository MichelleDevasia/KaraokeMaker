import os
import sys
from spleeter.separator import Separator

def separate_vocals(input_file_path):
    separator = Separator('spleeter:2stems')
    output_base_folder = "karaoke_output"
    
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    try:
        separator.separate_to_file(input_file_path, output_base_folder)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        separate_vocals(sys.argv[1])