import PySimpleGUIQt as sg
import gspread
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from pyrobot import Robot
import sys

#Importando Pyrobot
robot = Robot()

#Importando Webdriver e ActionsChains
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

#Variavel contadora
i = 0

#Layout Tela Principal
sg.theme('DarkGrey')
layout_tela_inicial = [ 
    [sg.Text("Email"), sg.Input(key="email_informado")],
    [sg.Text("Senha"), sg.Input(key="senha_informada", password_char="*")],
    [sg.Button("Enviar Convites", button_color=("white", "#0096FF")), sg.Button("Adicionar ID", button_color=('white', 'green'))]
]

#Layout Tela Adicionar ID
layout_tela_adicionar = [
    [sg.Text("ID"), sg.Input(key="id_informado")],
    [sg.Button("Adicionar", button_color=("white", "#0096FF"))]
]

janela_adicionar = sg.Window("Adicionar ID", layout_tela_adicionar)
janela_inicial = sg.Window("Enviar Convites Skype", layout_tela_inicial)

class Planilha():
    #Importando coluna do Google Sheets
    def importar_planilha(self, chave):
        gc = gspread.service_account(filename='projetoidskype.json')
        sh = gc.open_by_key(chave)
        worksheet = sh.sheet1
        return worksheet

class Interface():
    #Abrindo a janela inicial
    def abrir_janela_inicial(self):
        global janela_inicial
        while True:
            eventos, valores = janela_inicial.read()
            if (eventos == sg.WINDOW_CLOSED):
                sys.exit()
            
            if (eventos == "Enviar Convites"):
                email = valores["email_informado"]
                senha = valores["senha_informada"]
                resposta = [email, senha, '-adicionar_contatos-']
                janela_inicial.close()
                return resposta
            
            if (eventos == "Adicionar ID"):
                janela_inicial.close()
                return "-adicionar_id-"
    
    #Abrindo a janela para adicionar id a planilha
    def abrir_janela_adicionar(self):
        global janela_adicionar
        while True:
            eventos, valores = janela_adicionar.read()

            if (eventos == sg.WINDOW_CLOSED):
                sys.exit()

            if (eventos == "Adicionar" and valores["id_informado"] != ""):
                id_extra = valores["id_informado"]
                janela_adicionar.close()
                return id_extra
                
class Robo():
    #Fazer login na página
    def abrir_pagina_login(self, driver, email, senha):
        driver.get('https://web.skype.com/')
        driver.maximize_window()
        sleep(2)
        driver.find_element_by_xpath('//*[@id="i0116"]').send_keys(email)
        driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
        sleep(1)
        driver.find_element_by_xpath('//*[@id="i0118"]').send_keys(senha)
        driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()
        sleep(20)

    #Abre a aba de contatos -> addicionar novo
    def contatos(self, driver):
        sleep(2)
        driver.find_element_by_css_selector("[title*='Contatos']").click()
        #driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div/div[1]/div[3]/div[1]/div[1]/button[3]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div/div[1]/div[3]/div[1]/div[3]/button').click()
        sleep(1)

    #coloca o id do contato e clicla no perfil
    def adicionar_contato(self, driver, id):
        driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[2]/div[3]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div/div/input').send_keys(id)
        sleep(2)
        robot.move_and_click(707, 356, 'left')
        sleep(1)

    #Clicla em adicionar contato
    def botao_adicionar(self, driver):
        driver.find_element_by_css_selector("[title*='Adicionar contato']").click()
        sleep(2)

    #Fecha o pop up de contatos  
    def fechar(self, action):
        action.send_keys(Keys.ESCAPE).perform()
        sleep(1)

class Principal():
    #Metodo main
    def main(self):
        global options

        #Chamando as classes
        menu = Interface()
        scraping = Robo()
        sheets = Planilha()

        #Inserir a chave de uma planilha aqui embaixo
        chave = ''
        planilha  = sheets.importar_planilha(chave)
        
        #Verificando o que o usúario deseja fazer
        info = menu.abrir_janela_inicial()
        if info == '-adicionar_id-':
            id_novo = menu.abrir_janela_adicionar()
            planilha.insert_row([id_novo])

        if info[2] == '-adicionar_contatos-':
            #Início do webscraping
            driver = webdriver.Chrome(options=options)
            action = ActionChains(driver)
            email = info[0]
            senha = info[1]
            global i
            scraping.abrir_pagina_login(driver, email, senha)
            skype_ID = planilha.col_values(1)
            while (i <= len(skype_ID)-1):
                contato = skype_ID[i]
                i = i + 1
                scraping.contatos(driver)
                try:
                    scraping.adicionar_contato(driver, contato)
                except:
                    scraping.fechar(action)
                else:
                    pass
                try:
                    scraping.botao_adicionar(driver)
                except:
                    print("Usuario não encontrado 😒")
                    scraping.fechar(action)
                else:
                    scraping.fechar(action)
                    print("Adicionado com sucesso 😁")

            driver.quit()
            
if __name__ == "__main__":
    principal = Principal()
    principal.main()
