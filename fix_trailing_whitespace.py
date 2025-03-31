import sys
import os
import glob

def fix_file(filename):
    try:
        if os.path.isdir(filename):
            print(f"Processing directory: {filename}")
            # Process all Python files in the directory recursively
            for root, dirs, files in os.walk(filename):
                for file in files:
                    if file.endswith('.py'):
                        fix_file(os.path.join(root, file))
            return

        # Skip directories and non-Python files
        if not filename.endswith('.py'):
            return

        print(f"Processing file: {filename}")
        with open(filename, 'r') as f:
            content = f.read()
        
        # Remove trailing whitespace from each line
        lines = content.splitlines()
        fixed_lines = [line.rstrip() for line in lines]
        fixed_content = '\n'.join(fixed_lines) + '\n'  # Add single newline at end
        
        with open(filename, 'w') as f:
            f.write(fixed_content)
        
        print(f"Fixed trailing whitespace in {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            fix_file(filename)
    else:
        print("Usage: python fix_trailing_whitespace.py [file_or_directory]") 