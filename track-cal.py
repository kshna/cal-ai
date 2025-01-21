import subprocess
res = subprocess.run(['rm -f *.tmp'], capture_output=True, text=True, shell=True)
print(res)

while True:
    r=subprocess.call(['python','cal.py'])
    print(f"return{r}")


