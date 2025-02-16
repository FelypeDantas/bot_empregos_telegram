import os
import telebot
import requests
from bs4 import BeautifulSoup

# Pega o TOKEN da variável de ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

usuarios = {}

def buscar_vagas(area):
    # Buscando vagas no Indeed
    url_indeed = f"https://www.indeed.com.br/empregos?q={area}&l="
    headers = {"User-Agent": "Mozilla/5.0"}
    response_indeed = requests.get(url_indeed, headers=headers)
    
    # Buscando vagas no InfoJobs
    url_infojobs = f"https://www.infojobs.com.br/vagas-de-emprego/{area}.aspx"
    response_infojobs = requests.get(url_infojobs, headers=headers)

    if response_indeed.status_code != 200 and response_infojobs.status_code != 200:
        return []
    
    vagas = []

    # Scraping do Indeed
    if response_indeed.status_code == 200:
        soup_indeed = BeautifulSoup(response_indeed.text, "html.parser")
        for link in soup_indeed.find_all("a", href=True):
            href = link["href"]
            if "clk" in href:  # Filtrando links de vagas
                url_real = "https://www.indeed.com.br" + href
                if url_real not in vagas and len(vagas) < 10:
                    vagas.append(url_real)

    # Scraping do InfoJobs
    if response_infojobs.status_code == 200:
        soup_infojobs = BeautifulSoup(response_infojobs.text, "html.parser")
        for link in soup_infojobs.find_all("a", href=True):
            href = link["href"]
            if "/vagas-de-emprego" in href:
                url_real = "https://www.infojobs.com.br" + href
                if url_real not in vagas and len(vagas) < 10:
                    vagas.append(url_real)
    
    return vagas

@bot.message_handler(commands=['start'])
def iniciar_conversa(message):
    nome_usuario = message.from_user.first_name  # Pega o nome diretamente
    usuarios[message.chat.id] = {"nome": nome_usuario}
    bot.send_message(message.chat.id, f"Olá, {nome_usuario}! Qual é a sua área de interesse? Exemplo: 'desenvolvedor', 'marketing'.")
    bot.register_next_step_handler(message, buscar_e_enviar_vagas)

def buscar_e_enviar_vagas(message):
    chat_id = message.chat.id
    area_interesse = message.text.strip()
    usuarios[chat_id]["area"] = area_interesse
    bot.send_message(chat_id, "Buscando vagas, aguarde...")

    links = buscar_vagas(area_interesse)
    if links:
        for link in links:
            bot.send_message(chat_id, link)
        bot.send_message(chat_id, "Deseja ver mais vagas ou mudar a área?", reply_markup=criar_botoes())
    else:
        bot.send_message(chat_id, "Não encontrei vagas para essa área. Tente outra.")
        bot.register_next_step_handler(message, buscar_e_enviar_vagas)

def criar_botoes():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("🔄 Ver mais", "🔄 Trocar área", "❌ Finalizar Sessão")
    return markup

@bot.message_handler(func=lambda message: message.text in ["🔄 Ver mais", "🔄 Trocar área", "❌ Finalizar Sessão"])
def opcao_usuario(message):
    if message.text == "🔄 Ver mais":
        buscar_e_enviar_vagas(message)
    elif message.text == "🔄 Trocar área":
        bot.send_message(message.chat.id, "Qual nova área de interesse?")
        bot.register_next_step_handler(message, buscar_e_enviar_vagas)
    elif message.text == "❌ Finalizar Sessão":
        bot.send_message(message.chat.id, "Sessão finalizada. Até mais! 👋", reply_markup=telebot.types.ReplyKeyboardRemove())
        del usuarios[message.chat.id]  # Remove o usuário da lista

bot.polling()
