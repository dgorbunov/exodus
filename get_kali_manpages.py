import subprocess
import os
from tqdm import tqdm
output_dir = "kali_manpages.txt"
os.makedirs(output_dir, exist_ok = True)

with open('manpages_list.txt', 'r') as f:
    commands = [line.strip() for line in f if line.strip()]

for cmd in tqdm(commands):
    try:
        res =  subprocess.run(f'man {cmd} | col -bx',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        text = res.stdout

        fname = os.path.join(output_dir, f"{cmd.replace('/', '_')}.txt")
        with open (fname, 'w') as out_file:
            out_file.write(text)

    except subprocess.CalledProcessError:
        print(f'Failed to get man page for : {cmd}')

