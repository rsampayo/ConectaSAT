import sys

def fix_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Remove trailing whitespace from each line
    lines = content.splitlines()
    fixed_lines = [line.rstrip() for line in lines]
    fixed_content = '\n'.join(fixed_lines) + '\n'  # Add single newline at end
    
    with open(filename, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed trailing whitespace in {filename}")

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        fix_file(filename) 