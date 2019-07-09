
# -*- coding: latin-1 -*-
import datetime

import rbmc_ftp.functions as ftpFuncs
 
def main(args):

    """EXEMPLOS"""

    #modificar os caminhos

    outPath = "/home/kaue2/Documents/RBMC"

    # rinex 3 na ufpr nesse ano:
    ftpFuncs.download_station_day("ufpr",10,3,2019,outPath,True)

    # mesmo dia, mas rinex antigo:
    ftpFuncs.download_station_day("ufpr",10,3,2019,outPath)

    #entre duas datas
    ftpFuncs.downBetw2dates("ufpr",4,5,2018,6,5,2018,outPath)

    #de um arquivo:
    ftpFuncs.downloadFromList("/home/kaue2/Dropbox/Kelvin/RBMC_dowload/samples/for_download.csv")


    """FIM"""


    return
 
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))