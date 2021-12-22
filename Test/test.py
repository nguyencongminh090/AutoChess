import subprocess

##engine = subprocess.Popen('Em&bryo.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
##engine = subprocess.run('Embryo.exe', shell=True)
##engine = subprocess.run('Embryo.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x00000008)
engine = subprocess.Popen('Embryo.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  universal_newlines=True, bufsize=1)
print(engine)
engine.stdin.write('ABOUT\n')
text = engine.stdout.readline()
print(text)
engine.stdin.write('END\n')
