

#bibliotecas
import os
from ftplib import FTP
 
# logando no servidor
ftp = FTP("geoftp.ibge.gov.br")
ftp.login()

print(ftp.getwelcome())

# acessando as pastas
ftp.cwd("informacoes_sobre_posicionamento_geodesico")

ftp.cwd("rbmc")

ftp.cwd("dados")

ftp.cwd("2011")

ftp.cwd("011")

filelist = ftp.nlst()

# print(filelist)

name = "UFPR"

res = [i for i in filelist if name.lower() in i] 

# if "011" in filelist:
#     print("ok")

print(res)

filename = "bavc0111.zip"


local_filename = os.path.join("/home/kaue2/Documents/RBMC/", filename)
lf = open(local_filename, "wb")
ftp.retrbinary("RETR " + filename, lf.write, 8*1024)
lf.close()


ftp.quit()

