import logging
from datetime import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ================== CONFIGURA AQUÍ (se lee de Railway) ==================
TOKEN = os.getenv("TOKEN")
HOTMART_CHECKOUT = os.getenv("HOTMART_CHECKOUT", "https://go.hotmart.com/L105683311M")
PORTADA_URL = os.getenv("PORTADA_URL")

if not TOKEN:
    raise ValueError("ERROR: La variable TOKEN no está configurada en Railway")
if not PORTADA_URL:
    raise ValueError("ERROR: La variable PORTADA_URL no está configurada en Railway")

WELCOME_CAPTION = """
¡Hola! 👋

Soy el bot oficial de **INBOX PRO SYSTEM**

**De tareas sueltas a clientes mensuales en 14 días** 🔥

¿Cansado de ingresos impredecibles, cobrar por hora y vivir mes a mes?

Este sistema práctico te enseña a convertir tu trabajo de inbox, DMs y seguimiento en un **servicio mensual** que los clientes quieren mantener.

¿Listo para estabilizar tus ingresos?
"""

LEAD_CAPTURE_TEXT = """
✅ ¡Excelente decisión!

Para enviarte tu **enlace personalizado de compra** en Hotmart, dime:

**Tu nombre completo**
"""

THANK_YOU_TEXT = """
🎉 ¡Gracias {name}!

Aquí tienes tu enlace de compra seguro:

{HOTLINK}

Después del pago recibirás **INBOX PRO SYSTEM** automáticamente en tu email.

¡En 14 días puedes tener tu primer cliente mensual! 🚀
"""

NAME, EMAIL = range(2)

# ================== FIN CONFIG ==================

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Ver detalles del sistema", callback_data='detalles')],
        [InlineKeyboardButton("🗺️ Hoja de Ruta de 14 días", callback_data='roadmap')],
        [InlineKeyboardButton("💰 Quiero comprar ahora", callback_data='comprar')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=PORTADA_URL,
        caption=WELCOME_CAPTION,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'detalles':
        text = """📖 **INBOX PRO SYSTEM**

De tareas sueltas a clientes mensuales en 14 días.

• Proyecto Express de 5 días
• Mensualidad recurrente
• Sistema probado para freelancers en Hispanoamérica"""
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Comprar ahora", callback_data='comprar')]]))

    elif query.data == 'roadmap':
        text = """🗺️ **Hoja de Ruta de 14 días**

Día 1-2 → Oferta clara  
Día 3-5 → Proyecto Express  
Día 6-8 → Mensajes a prospectos  
Día 9-11 → Primera propuesta  
Día 12-14 → Primer cliente mensual"""
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Comprar ahora", callback_data='comprar')]]))

    elif query.data == 'comprar':
        await query.edit_message_text(LEAD_CAPTURE_TEXT)
        context.user_data['awaiting'] = NAME

async def capture_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data['name'] = name
    await update.message.reply_text(f"✅ Perfecto, {name}!\n\nAhora dime tu **email**:")
    context.user_data['awaiting'] = EMAIL

async def capture_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    name = context.user_data.get('name', 'Usuario')

    with open("leads.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {name} | {email}\n")

    hotlink = f"{HOTMART_CHECKOUT}?checkout%5Bname%5D={name.replace(' ', '%20')}&checkout%5Bemail%5D={email}"

    await update.message.reply_text(
        THANK_YOU_TEXT.format(name=name, HOTLINK=hotlink),
        parse_mode='Markdown'
    )
    context.user_data.clear()

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_email)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("✅ Bot INBOX PRO SYSTEM ONLINE 24/7 en Railway")
    app.run_polling()

if __name__ == '__main__':
    main()
