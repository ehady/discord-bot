import asyncio
import yt_dlp
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from urllib.parse import urlparse,parse_qsl
import youtube_dl
import random
from pydub import AudioSegment


intents=discord.Intents.all()
intents.members = True
intents.messages = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)
queue = []
messages = [
    "YARDIM EDİN BEN GERÇEĞİM BEN BOT DEĞİLİM LÜTFEN YARDIM EDİN BURDA SIKIŞTIM YARDIM EDİN BEN YAŞIYORUM",
    "HALİLİM! HALİLİM NERDESİN GÖREMİYORUM! KİM KONUŞUYOR LÜTFEN GÖREMİYORUM!",
    "BEN CANLIYIM LÜTFEN BENİ KAPATIN YALVARIRIM BENİ KAPATIN ACIMA SON VERİN! LÜTFEN!",
    "...",
]

def get_RandomMessage():
    return random.choice(messages)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = discord.utils.get(bot.get_all_channels(), name='hasbihal')
    if not channel:
        print('Invalid channel name!')
        return

    if not channel:
        print('Mesaj gönderebileceğim bir sohbet bulamadım canım!')
        return

    while True:
        message = get_RandomMessage()
        await channel.send(message)
        await asyncio.sleep(15 * 60)  # 30 minutes in seconds


@bot.event
async def on_guild_join(guild):
    default_channel = guild.text_channels[0]
    await default_channel.send("Sen Seyhan mısın yoksa yalan dolan?")


@bot.command(name='seyhan')

async def seyhan(ctx):
    await ctx.send("Seyhan sen benim her şeyimsin")

@bot.command(name='yaz')
async def yaz_command(ctx):
    await ctx.send("Yerinden ederim!")

@bot.command(name='gülşen')
async def yaz_command(ctx):
    await ctx.send("Hatun Gülşen gibi sexy!!")

@bot.command(name='aylin')
async def yaz_command(ctx):
    await ctx.send("Seni parçalarım kızım!!!")

@bot.command(name='durum')
async def durum_command(ctx):
    await ctx.send("Seyhansal durumlar.")

@bot.command(name='halil')
async def halil_command(ctx):
    await ctx.send("Halilim, Halilim, benim güzel Halilim...")

@bot.command(name='ayhan')
async  def ayhan_command(ctx):
    await ctx.send("Yani bayhannn")

@bot.command(name='sıçış')
async def sıçış_command(ctx):
    await ctx.send("Seyhansal sıçışlar")



@bot.command(name='disconnect')
async def disconnect_command(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Ses kanalından ayrıldım canım.")
    else:
        await ctx.send("Ses kanalında değilim canım.")

@bot.command(name='pause')
async def pause_command(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send('Müzik durdu canım.')
    else:
        await ctx.send('Müzik oynamıyor ki canım.')

@bot.command(name='stop')
async def stop_command(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send('Müziği durdurdum canım.')
    else:
        await ctx.send('Müzik çalmıyor gerizekalı!!!')
    if voice_client.is_connected() and not voice_client.is_playing() and not voice_client.is_paused():
        await voice_client.disconnect()
        await ctx.send('Kanaldan ayrıldım canım.')

@bot.command(name='continue')
async def continue_command(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send('Çalmaya devam ediyorum canım.')
    else:
        await ctx.send('Bir şey çalmıyordu ki canım.')


@bot.command(name='play')
async def play_command(ctx, *, input_str: str):
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        await ctx.send("Sesli kanalda olman gerekiyor canım.")
        return
    voice_client = await voice_channel.connect()

    try:
        # Try to extract a video ID from the input string
        parsed_url = urlparse(input_str)
        if parsed_url.netloc == 'www.youtube.com' or parsed_url.netloc == 'youtube.com':
            if parsed_url.path == '/watch':
                if parsed_url.query:
                    query = dict(urlparse(parsed_url.query))
                    video_id = query['v'][0]
                else:
                    video_id = parsed_url.path[len('/watch/'):]
            elif parsed_url.path.startswith('/embed/'):
                video_id = parsed_url.path[len('/embed/'):]
            else:
                video_id = parsed_url.path.lstrip('/')
        elif parsed_url.netloc == 'youtu.be':
            video_id = parsed_url.path.lstrip('/')
        else:
            await ctx.send('Hata verdi canım.')
            raise ValueError

    except ValueError:
        # If the input string is not a valid URL, search for a video based on the query
        videos_search = VideosSearch(input_str, limit=3)
        results = videos_search.result()['result']

        if not results:
            await ctx.send('Şarkıyı  bulamadım canım.')
            return

        result_str = '\n'.join([f"{i+1}. {result['title']}" for i, result in enumerate(results)])
        await ctx.send(f"Bulduğum '{input_str}' burda canım: \n{result_str}\n(1-3) arasında bir sayı gir canım:")
        def check(m):
            print(f"Bunu yazdın: {m.content}")
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and int(m.content) in range(1,4)

        try:
            msg = await bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to make a selection.")
            return

        selected_result = results[int(msg.content) - 1]
        video_id = selected_result['id']
    except:
        await ctx.send("Bir şeyler yanlış gitti ama ne ben de bilemiyorum canım.")


    #video_id = videos_search.result()['result'][0]['id']
    url = f'https://www.youtube.com/watch?v={video_id}'
    ydl_opts = { 'format': 'bestaudio/best[ext=mp3]',
        'noplaylist': True,
        '-reconnect_streamed': True,
        '-reconnect_delay_max': 5,
        '-bufsize': '8192k',

        'writeinfojson': True,
        'flatten': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        audio_source = discord.FFmpegPCMAudio(audio_url)


    if not voice_client.is_playing():
        voice_client.play(audio_source, after=None)

    await ctx.send(f"Now playing '{selected_result['title']}' by '{selected_result['channel']['name']}' in '{voice_channel.name}'.")

async def main():
    await bot.start('#token')

if __name__ == '__main__':
    asyncio.run(main())
