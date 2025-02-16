import os
import telebot
import requests
from bs4 import BeautifulSoup
import re

# Pegando o token do bot das variáveis de ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Dicionário para armazenar informações dos usuários
usuarios = {}

def buscar_vagas_fake(area):
    """
    Simula a busca de vagas sem precisar de scraping.
    Você pode substituir essa função para buscar de APIs reais, como Indeed, Glassdoor, etc.
    """
    vagas_fake = [
        f"https://site-de-vagas.com/{area.replace(' ', '-')}-vaga-{i}" for i in range(1, 6)
    ]
    return vagas_fake

@bot.message_handler(commands=['start'])
def iniciar_conversa(message):
    """ Inicia a conversa e armazena o nome do usuário automaticamente """
    chat_id = message.chat.id
    nome_usuario = message.from_user.first_name  # Obtém o nome do usuário automaticamente
    usuarios[chat_id] = {"nome": nome_usuario}  # Registra o usuário no dicionário
    bot.send_message(chat_id, f"Olá, {nome_usuario}! Qual é a sua área de interesse?")
    bot.register_next_step_handler(message, buscar_e_enviar_vagas)

def buscar_e_enviar_vagas(message):
    """ Busca e envia as vagas baseadas na área de interesse do usuário """
    chat_id = message.chat.id
    area_interesse = message.text.strip()

    # Se o usuário não existir no dicionário, cria um registro
    if chat_id not in usuarios:
        usuarios[chat_id] = {"nome": message.from_user.first_name}

    usuarios[chat_id]["area"] = area_interesse
    bot.send_message(chat_id, "🔎 Buscando vagas, aguarde...")

    links = buscar_vagas_fake(area_interesse)  # Aqui você pode mudar para uma API real

    if links:
        for link in links:
            bot.send_message(chat_id, f"🔗 {link}")
        bot.send_message(chat_id, "O que deseja fazer agora?", reply_markup=criar_botoes())
    else:
        bot.send_message(chat_id, "❌ Não encontrei vagas para essa área. Tente outra.")
        bot.register_next_step_handler(message, buscar_e_enviar_vagas)

def criar_botoes():
    """ Cria botões interativos para o usuário escolher a próxima ação """
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("🔄 Ver mais vagas", "🎯 Trocar área", "🚪 Finalizar Sessão")
    return markup

@bot.message_handler(func=lambda message: message.text in ["🔄 Ver mais vagas", "🎯 Trocar área", "🚪 Finalizar Sessão"])
def opcao_usuario(message):
    """ Trata as opções que o usuário escolheu nos botões interativos """
    chat_id = message.chat.id

    # Garante que o usuário está registrado antes de qualquer ação
    if chat_id not in usuarios:
        usuarios[chat_id] = {"nome": message.from_user.first_name}

    if message.text == "🔄 Ver mais vagas":
        buscar_e_enviar_vagas(message)

    elif message.text == "🎯 Trocar área":
        bot.send_message(chat_id, "Digite a nova área de interesse:")
        bot.register_next_step_handler(message, buscar_e_enviar_vagas)

    elif message.text == "🚪 Finalizar Sessão":
        usuarios.pop(chat_id, None)  # Remove o usuário do dicionário
        bot.send_message(chat_id, "Sessão finalizada! Digite /start para começar novamente.")

# Mantém o bot rodando
bot.polling()

