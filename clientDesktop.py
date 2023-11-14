import socket
import threading
from simple_term_menu import TerminalMenu

HOST = 'localhost'
PORT = 7578

# Linha de comando:
def command_line_interface():

    options = ['[1] Menu Lampada', '[2] Menu Ar-Condicionado', '[3] Menu Sistema de Controle de Incêndio' ,'[4] Sair']
    main_menu = TerminalMenu(options, title="\n\nHome Assistant", cycle_cursor=True, clear_screen=True, menu_cursor_style=("fg_green", "bold"), menu_highlight_style=("bg_cyan", ),)
    main_menu_exit = False



    while not main_menu_exit:
            main_sel = main_menu.show()

            # Menu lampada ==================================================================================================
            if main_sel == 0:
                lamp_menu_title = "\n\nMenu Lampada\n  Precione Q ou Esc para retornar ao menu principal. \n"
                lamp_menu_items = ["[1] Obter luminosidade atual", "[2] Ligar Lampada (modo automático)", "[3] Desligar Lampada (modo automático)", "[4] Sair"]
                lamp_menu_back = False
                lamp_menu = TerminalMenu(lamp_menu_items, title=lamp_menu_title, cycle_cursor=True, clear_screen=False, menu_cursor_style=("fg_green", "bold"), menu_highlight_style=("bg_yellow", "fg_black"))

                while not lamp_menu_back:
                    choice_lamp = lamp_menu.show()
                    if choice_lamp == 0:
                        send_tcp_msgn(f"{lamp_menu_items[choice_lamp].split(' ')[0]} lamp")
                    elif choice_lamp == 1:
                        send_tcp_msgn(f"{lamp_menu_items[choice_lamp].split(' ')[0]} lamp")

                    elif choice_lamp == 2:
                        send_tcp_msgn(f"{lamp_menu_items[choice_lamp].split(' ')[0]} lamp")

                    elif choice_lamp == 3 or choice_lamp == None:
                        lamp_menu_back = True
                        
                lamp_menu_back = False

            # Menu ar-condicionado ==========================================================================================
            elif main_sel == 1:
                ar_menu_title = "\n\nMenu Ar-Condicionado\n  Precione Q ou Esc para retornar ao menu principal. \n"
                ar_menu_items = ["[1] Obter temperatura atual", "[2] Ligar Ar-Condicionado (modo automático)", "[3] Desligar Ar-Condicionado (modo automático)", "[4] Mudar temperatura", "[5] Sair"]
                ar_menu_back = False
                ar_menu = TerminalMenu(ar_menu_items, title=ar_menu_title, cycle_cursor=True, clear_screen=False, menu_cursor_style=("fg_green", "bold"), menu_highlight_style=("bg_yellow", "fg_black"))

                while not ar_menu_back:
                    choice_ar = ar_menu.show()
                    if choice_ar == 0:
                        send_tcp_msgn(f"{ar_menu_items[choice_ar].split(' ')[0]} ar")

                    elif choice_ar == 1:
                        send_tcp_msgn(f"{ar_menu_items[choice_ar].split(' ')[0]} ar")

                    elif choice_ar == 2:
                        send_tcp_msgn(f"{ar_menu_items[choice_ar].split(' ')[0]} ar")

                    elif choice_ar == 3:
                        temp = int(input("Digite a temperatura alvo desejada: "))
                        send_tcp_msgn(f"{ar_menu_items[choice_ar].split(' ')[0]} {temp} ar")

                    elif choice_ar == 4 or choice_ar == None:
                        ar_menu_back = True


            # Menu Sistema Controlador de Incendio ==========================================================================
            elif main_sel == 2:
                sis_menu_title = "\n\nMenu Sis.Controlador de Incendio\n  Precione Q ou Esc para retornar ao menu principal. \n"
                sis_menu_items = ["[1] Obter status atual do sensor de fumaça", "[2] Obter status do alarme", "[3] Desligar Alarme", "[4] Sair"]
                sis_menu_back = False
                sis_menu = TerminalMenu(sis_menu_items, title=sis_menu_title, cycle_cursor=True, clear_screen=False, menu_cursor_style=("fg_green", "bold"), menu_highlight_style=("bg_yellow", "fg_black"))

                while not sis_menu_back:
                    choice_sis = sis_menu.show()
                    if choice_sis == 0:
                        send_tcp_msgn(f"{sis_menu_items[choice_sis].split(' ')[0]} sis")

                    elif choice_sis == 1:
                        send_tcp_msgn(f"[1] {sis_menu_items[choice_sis].split(' ')[0]} sis alarm")

                    elif choice_sis == 2:
                        send_tcp_msgn(f"{sis_menu_items[choice_sis].split(' ')[0]} sis")

                    elif choice_sis == 3 or choice_sis == None:
                        sis_menu_back = True
            
            # Exit ==========================================================================================================
            elif main_sel == 3 or main_sel == None:
                main_menu_exit = True
                print("Quit Selected")


def send_tcp_msgn(msgn:str, sucess_msg="Mensagem enviada com sucesso!"):
    '''Responsável por enviar uma mensagem TCP'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
        # Envie a mensagem e verifique se ocorreu um erro
        if s.sendall(msgn.encode("utf-8")) is None:
            # print(sucess_msg)
            data = s.recv(65536).decode('utf-8')
            s.close()
            print(data)
        else:
            print("Erro ao enviar a mensagem.")

        return True
    except Exception as e:
        print(f"Erro ao enviar a mensagem: {str(e)}.\nVerifique se o arquivo gateway.py está em execução!")
        return False
    finally:
        s.close()



if __name__ == '__main__':
    command_line_interface()
