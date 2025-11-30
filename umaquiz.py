from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

import discord
from discord.ext import commands
import random
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "quiz_data.json"

# ------------------------
# データ読み込み
# ------------------------
def load_quiz():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ------------------------
# データ保存
# ------------------------
def save_quiz(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# メモリ上の問題リスト
quiz_list = load_quiz()

# 出題中の答え保存
current_answer = {}

# ------------------------
# ランダム出題
# ------------------------
@bot.command()
async def quiz(ctx):
    if not quiz_list:
        await ctx.send("まだ問題が登録されていません。")
        return

    quiz = random.choice(quiz_list)
    current_answer[ctx.channel.id] = quiz["answer"]

    embed = discord.Embed(title="【クイズ】このキャラは誰？")
    embed.set_image(url=quiz["image"])
    await ctx.send(embed=embed)

# ------------------------
# 回答
# ------------------------
@bot.command()
async def answer(ctx, *, guess):
    answer = current_answer.get(ctx.channel.id)

    if answer is None:
        await ctx.send("まず !quiz で問題を出してください。")
        return
    
    if guess.strip() == answer:
        await ctx.send(f"🎉 正解！ `{answer}` です！")
        del current_answer[ctx.channel.id]
    else:
        await ctx.send("❌ 不正解！")

# ------------------------
# 管理者：問題追加
# 画像を添付 → !addquiz 答え
# ------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def addquiz(ctx, *, answer):
    if not ctx.message.attachments:
        await ctx.send("画像を添付してください。")
        return

    image_url = ctx.message.attachments[0].url

    new_quiz = {
        "image": image_url,
        "answer": answer.strip()
    }

    quiz_list.append(new_quiz)
    save_quiz(quiz_list)

    await ctx.send(f"問題を追加しました！（No.{len(quiz_list)-1}）")

# ------------------------
# 管理者：問題削除
# ------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def delquiz(ctx, number: int):
    if number < 0 or number >= len(quiz_list):
        await ctx.send("その番号の問題はありません。")
        return

    removed = quiz_list.pop(number)
    save_quiz(quiz_list)

    await ctx.send(f"問題 No.{number}（{removed['answer']}）を削除しました。")

# ------------------------
# 管理者：一覧表示
# ------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def listquiz(ctx):
    if not quiz_list:
        await ctx.send("登録されている問題はありません。")
        return

    msg = "【問題一覧】\n"
    for i, q in enumerate(quiz_list):
        msg += f"No.{i} : 答え = {q['answer']}\n"

    await ctx.send(msg)

bot.run(TOKEN)
