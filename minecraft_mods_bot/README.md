# Minecraft Modlari Telegram Boti

100 ta mashhur Minecraft modini pastki (Reply) tugmalar orqali ko'rsatuvchi,
telefon ekraniga moslangan Telegram bot. Balans/to'lov tizimi bilan.

## 💰 Balans tizimi
- Har bir mod ma'lumotini ko'rish — **5000 so'm** (o'zgartirish uchun
  `bot.py` ichidagi `MOD_PRICE` qiymatini o'zgartiring).
- **Admin** (ID: `8642218989`) uchun hamma narsa **bepul**.
- Foydalanuvchi "➕ Hisobni to'ldirish" tugmasini bosadi → summani kiritadi
  → so'rov adminga boradi → admin "✅ Tasdiqlash" yoki "❌ Rad etish"
  tugmasi orqali javob beradi → tasdiqlansa, foydalanuvchi balansi
  avtomatik oshadi va unga xabar boradi.
- "💰 Balansim" tugmasi orqali joriy balansni ko'rish mumkin.
- Balanslar `balances.json` faylida saqlanadi (bot ishga tushgach avtomatik yaratiladi).

## 🚀 Render.com'ga joylash
- Bot Render'da **Web Service** sifatida ishlaydi (Render "background worker"ni
  bepul rejada qo'llab-quvvatlamaydi, shu sabab portni tinglaydigan kichik
  `health_server.py` qo'shilgan — bu Render'ga xizmat "ishlayapti" deb bildiradi).
- Render sozlamalarida:
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `python bot.py`
- ⚠️ **Muhim**: Render'ning **bepul** rejasi 15 daqiqa harakatsizlikdan keyin
  xizmatni "uxlatib qo'yadi" (sleep). Health-check server buni to'liq oldini
  ololmaydi — buni oldini olish uchun [UptimeRobot](https://uptimerobot.com)
  kabi xizmat orqali bot manzilingizga har 10-14 daqiqada bir marta so'rov
  yuborib turishni sozlashingiz kerak, yoki Render'ning pullik ("Starter"
  va undan yuqori) rejasiga o'tishingiz kerak — bepul rejada uzluksiz
  ishlashga 100% kafolat yo'q.

## Kategoriyalar (jami 100 ta mod)
- ⚡ Optimallashtirish — 13 ta
- 🎨 Grafika va Shaderlar — 10 ta
- ⚙️ Texnika va Avtomatlashtirish — 15 ta
- 🗺️ Sarguzasht va Yangi Dunyolar — 15 ta
- 🧰 Qulaylik va Interfeys — 15 ta
- 📷 Kamera va Suratga olish — 2 ta
- 🔮 Sehr-jodu — 9 ta
- ⚔️ Jangovar va Qurollar — 6 ta
- 🌾 Qishloq xo'jaligi va Pazandachilik — 5 ta
- 🏠 Bino qurish va Dekorativ — 8 ta
- 📱 Telefon (Bedrock/Pocket Edition) uchun — 2 ta

## Muhim: Java vs Bedrock (telefon)
Yuqoridagi modlarning aksariyati **Java Edition** uchun — ya'ni faqat
**kompyuterda** ishlaydi (Forge/Fabric orqali o'rnatiladi).

Agar siz **telefon** (Bedrock/Pocket Edition)da o'ynasangiz, bu modlar
ishlamaydi — o'rniga **"Add-on"** deb ataladigan boshqa turdagi fayllar
kerak. Shu sabab botga maxsus **📱 Telefon uchun** bo'limi qo'shilgan —
u yerda haqiqiy addon manbalariga (MCPEDL, rasmiy Minecraft Marketplace)
havolalar bor.

## O'rnatish

1. Python 3.10+ borligiga ishonch hosil qiling.
2. Kerakli kutubxonani o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
3. Token `bot.py` ichida `DEFAULT_BOT_TOKEN` sifatida allaqachon kiritilgan.
   Xohlasangiz, uni muhit o'zgaruvchisi orqali ham berishingiz mumkin:
   ```bash
   export BOT_TOKEN="123456:ABC-DEF..."
   ```
4. Botni ishga tushiring:
   ```bash
   python bot.py
   ```

## Foydalanish
- `/start` — bosh menyu (pastki tugmalar chiqadi)
- Kategoriya tugmasini bosing → mod tanlang → tavsif va havola chiqadi
- **📋 Barcha modlar** — hammasini bir ro'yxatda ko'rish
- **⬅️ Orqaga** — oldingi menyuga qaytish

## Yangi mod qo'shish

`mods_data.py` faylini oching va tegishli kategoriya ichidagi `mods`
ro'yxatiga yangi lug'at qo'shing:

```python
{
    "name": "Mod nomi",
    "desc": "Qisqacha tavsif.",
    "link": "https://modrinth.com/mod/mod-slug",
},
```

## Eslatma
- Bot mod fayllarini o'zi saqlamaydi/tarqatmaydi — faqat tavsif va rasmiy
  sahifaga (Modrinth/CurseForge) havola beradi, bu mualliflik huquqlarini
  hurmat qilish uchun.
- Botni faqat bitta joydan (bitta serverda) ishga tushiring, aks holda
  Telegram "Conflict" xatoligini beradi.
