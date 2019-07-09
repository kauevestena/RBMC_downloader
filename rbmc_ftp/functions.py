# -*- coding: latin-1 -*-
#bibliotecas

import os
from ftplib import FTP
import sys
import datetime


def disclaimer():
    """destinada a imprimir instruções gerais a um usuário"""

    print ("bem vindo ao RBMC downloader, baixe dados da RBMC de diversas datas, a partir de 2010")
    print ("para informações sobre a lista de estações e situação operacional ao longo do tempo, acesse: ")
    print ("")
    print ("https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/rede-geodesica/16258-rede-brasileira-de-monitoramento-continuo-dos-sistemas-gnss-rbmc.html?=&t=situacao-operacional")

def RBMC_list():
    """destinada a gerar a lista de todas as estações que já existiram da RBMC"""

    #acessando e realizando login
    ftp = FTP("geoftp.ibge.gov.br")
    ftp.login()

    #acessando o diretorio "relatorio", no qual será possível obter os nomes das estações
    ftp.cwd("informacoes_sobre_posicionamento_geodesico")

    ftp.cwd("rbmc")
    ftp.cwd("relatorio")

    stationslist = []

    ftp.dir(stationslist.append)

    #we can now close the connection
    ftp.quit()

    #removing if not contains a station name
    stationslist[:] = [item for item in stationslist if item.find("escritivo") != -1]

    # only acronyms now
    temp = []
    key = "escritivo"
    for item in stationslist:
        pos = item.find(key)+len(key)
        stationName = item[pos+1:pos+4+1]
        temp.append(stationName)

    stationslist = temp

    #check for inconsistencies
    if stationslist == []:
        sys.exit("lista de estações vazia")

    for item in stationslist:
        if len(item) != 4:
            sys.exit("problemas com a lista de nomes das estações, possível mudança de estrutura do servidor do IBGE, contate os desenvolvedores")

    return stationslist

def check_date_inconsistency(dDay,dMonth,dYear):
    """testa se uma data entrada é válida"""

    # errDate = ["entrada inválida para o Dia","entrada inválida para o Mês",
    # "entrada inválida para o Ano",
    # "data negativa fornecida como entrada"]

    # # non integer
    # if not isinstance(dDay,int):
    #     print(errDate[0])
    #     return True

    # elif not isinstance(dMonth,int):
    #     print(errDate[1])
    #     return True

    # elif not isinstance(dYear,int):
    #     print(errDate[2])
    #     return True

    # # non positive
    # elif dDay < 0 or dMonth < 0 or dYear < 0:
    #     print(errDate[3])
    #     return True
    
    # #impossible dates
    # elif dDay > 31:
    #     print(errDate[0])
    #     return True
    #     #TODO: a month-dependant check
    
    # elif dMonth > 12:
    #     print(errDate[1])
    #     return True

    # elif dYear < 2010 or dYear > datetime.date.today().year:
    #     print(errDate[3])
    #     return True
    
    # else:
    #     return False
    try:
        # print([dDay,dMonth,dYear])
        theDate = datetime.date(dYear,dMonth,dDay)
        #we don't have future data
        if theDate > datetime.date.today():
            return True
        return False
    except:
        return True

def download_station_day(station_name,dDay,dMonth,dYear,outPath,rinex3=False,download_all=False):
    """principal função, todas as demais chamam essa, uma ou mais vezes. 
    Pode ser usada também pra baixar todas as estações disponíveis para um determinado dia"""

    #check input inconsistencies:
    if len(station_name) != 4 and not download_all:
        print("deve-se entrar com a sigla da estação, consulte no site do IBGE")
        return

    if check_date_inconsistency(dDay,dMonth,dYear): #para a data
        print("data fornecida inconsistente")
        return

    #retrieve stations list:
    stations = RBMC_list()

    station_name = station_name.upper() #if the user enters as a lowercase or mixed

    if station_name in stations or download_all:

        filesList = []

        ftp = FTP("geoftp.ibge.gov.br")
        ftp.login()

        ftp.cwd("informacoes_sobre_posicionamento_geodesico")

        ftp.cwd("rbmc")

        #date as a structure:
        theDate = datetime.date(dYear,dMonth,dDay)
        # print theDate.year

        #Day Of Year, also as string
        DOY = theDate.timetuple().tm_yday
        # print(DOY)

        DOYstr = str(DOY)

        if DOY <= 9:
            DOYstr = "00"+DOYstr
        elif DOY <= 99:
            DOYstr = "0"+DOYstr

        if not rinex3:
            ftp.cwd("dados")
            try:
                ftp.cwd(str(dYear))
                #######################
                ftp.cwd(DOYstr)
                filesList = ftp.nlst()
                downList = [item for item in filesList if station_name in item]
                if downList == []:
                    downList = [item for item in filesList if station_name.lower() in item]

                if(download_all):
                    downList = filesList

                if downList == []:
                    print("estação indisponivel para a data ou previamente desativada")
                    return
                else:
                    # print(downList)
                    for file in downList:
                        local_filename = os.path.join(outPath,file)
                        try:
                            folder = open(local_filename, "wb")
                            ftp.retrbinary("RETR " + file, folder.write, 8*1024)

                            folder.close()
                        except:
                            print("problema ao tentar acessar o caminho especificado")
                            return

            except:
                print("ano indisponível")
                return
        else:
            ftp.cwd("dados_RINEX3")
            try:
                ftp.cwd(str(dYear))
                if dYear < 2018:
                    print("dia do ano indisponível, para RINEX 3, dados somente a partir do dia 242 de 2018")
                    return
                elif DOY < 242 and dYear <= 2018:
                    print("dia do ano indisponível, para RINEX 3, dados somente a partir do dia 242 de 2018")
                    return
                else:
                    ######################
                    ftp.cwd(DOYstr)
                    filesList = ftp.nlst()

                    # print(filesList)

                    downList = [item for item in filesList if station_name in item]
                    if downList == []:
                        downList = [item for item in filesList if station_name.lower() in item]

                    
                    if(download_all):
                        downList = filesList

                    if downList == []:
                        print("estação indisponivel para a data, previamente desativada ou sem suporte para RINEX3")
                        return
                    else:
                        #######################
                        for file in downList:
                            local_filename = os.path.join(outPath,file)
                            try:
                                folder = open(local_filename, "wb")
                                ftp.retrbinary("RETR " + file, folder.write, 8*1024)

                                folder.close()
                            except:
                                print("problema ao tentar acessar o caminho especificado")
                                return

            except:
                print("ano indisponível, para RINEX 3, dados somente a partir do dia 242 de 2018")
                return

        ftp.quit()

    else:
        print("nome de estação inválido, entre com as siglas, consulte no site do IBGE")
        return

# def download_station_today(station_name,outPath,rinex3=False):
#     download_station_day(station_name,datetime.date.today().day,
#     datetime.date.today().month,datetime.date.today().year,outPath,rinex3)

def download_station_list_date(station_list: list,dDay,dMonth,dYear,outPath,rinex3=False):
    """faz download de uma lista de estações para uma data"""
    for item in station_list:
        download_station_day(item,dDay,dMonth,dYear,outPath,rinex3)

def downBetw2dates(station_name,dDay1,dMonth1,dYear1,dDay2,dMonth2,dYear2,outPath,rinex3=False,download_all=False):
    """faz download para todos os dias no intervalo entre duas datas, da pra usar pra baixar de todas as estações disponíveis pra um dia"""


    try:
        date1 = datetime.date(dYear1,dMonth1,dDay1)
    except:
        return
        print("data de início inválida")
    
    try:
        date2 = datetime.date(dYear2,dMonth2,dDay2)
    except:
        return
        print("data de fim inválida")       

    dateList = []

    if date2 > date1:
        interval = date2 - date1
        days = interval.days

        for num in range (0,interval.days+1):
            dateList.append(date1 + datetime.timedelta(days = num))
        
    else:
        interval = date1 - date2
        days = interval.days

        for num in range (0,interval.days+1):
            dateList.append(date2 + datetime.timedelta(days = num))

    for date in dateList:
        download_station_day(station_name,date.day,date.month,date.year,outPath,rinex3,download_all)
    
def download_date_plus_days(station_name,dDay,dMonth,dYear,DAYS,outPath,rinex3=False,download_all=False):

    """faz download para todos os dias no intervalo de uma data adicionada de tantos dias, da pra usar pra baixar de todas as estações disponíveis pra um dia"""

    try:
        date1 = datetime.date(dYear,dMonth,dDay)
    except:
        return
        print("data de início inválida")
    
    try:
        date2 = date1 + datetime.timedelta(days = DAYS)
        if date2 > datetime.date.today():
            print("data final inválida")
            return
    except:
        return
        print("data final inválida")

    downBetw2dates(station_name,dDay,dMonth,dYear,date2.day,date2.month,date2.year,outPath,rinex3,download_all)

def download_date_minus_days(station_name,dDay,dMonth,dYear,DAYS,outPath,rinex3=False,download_all=False):
    """faz download para todos os dias no intervalo de uma data subtraída de tantos dias, da pra usar pra baixar de todas as estações disponíveis pra um dia"""

    try:
        date1 = datetime.date(dYear,dMonth,dDay)
    except:
        return
        print("data de início inválida")
    
    try:
        date2 = date1 - datetime.timedelta(days = DAYS)

    except:
        return
        print("data final inválida")

    downBetw2dates(station_name,dDay,dMonth,dYear,date2.day,date2.month,date2.year,outPath,rinex3,download_all)


def downloadFromList(listPath):
    """"
    
    faz o download a partir de um csv de entrada com a seguinte formatação:
    
    estacao,dia,mes,ano,caminho,rinex3?(bool, opcional),baixar todas?(bool, opcional)

    """
    file = open(listPath,"r")

    for line in file:
        # print( line)
        data = line.split(",")
        if data[len(data)-1].find('\n'):
            data[len(data)-1] = data[len(data)-1][0]

        try:
            data[1] = int(data[1])
            data[2] = int(data[2])
            data[3] = int(data[3])
            if len(data) > 5:
                data[5] = bool(int(data[5]))
                if len(data) > 6:
                    data[6] = bool(int(data[6]))
        except:
            print("checar arquivo de entrada")
            return

        # print(data)


        try:
            if len(data) == 5 or len(data) == 6 or len(data) == 7:
                download_station_day(*data)            
        except:
            print("checar arquivo de entrada")
