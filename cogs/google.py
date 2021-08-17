import datetime as dt
import random
import pickle
import discord
from discord.ext import commands
from utils.google_api import yt_api_build


class GoogleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='곡추천')
    async def track_recommend(self, ctx):
        """릴라 최애곡 재생목록에서 랜덤으로 하나 추천"""
        try:
            with open('data/last_update.pkl', 'rb') as f:
                last_update = pickle.load(f)
        except FileNotFoundError:
            last_update = {'track_recommend': '19700101-000000'}
        fmt = '%Y%m%d-%H%M%S'

        def update_ids():
            # YouTube API
            ids = []
            page_token = None
            while True:
                request = yt_api_build().playlistItems().list(
                    part="contentDetails",
                    maxResults=50,
                    pageToken=page_token,
                    playlistId="PLt4PlBZPJX7EFiE_D2hjgiH712J95SjVc"
                )
                response = request.execute()

                # ids에 영상 ID들을 append하고 pickle로 저장
                for i in range(len(response['items'])):
                    ids.append(response['items'][i]['contentDetails']['videoId'])

                # 다음 페이지
                try:
                    page_token = response['nextPageToken']
                except KeyError:
                    break

            with open('data/track_recommend_ids.pkl', 'wb') as f:
                pickle.dump(ids, f)

            # last_update 갱신
            last_update['track_recommend'] = dt.datetime.now().strftime(fmt)
            with open('data/last_update.pkl', 'wb') as f:
                pickle.dump(last_update, f)

        # 오늘 update한 적 없으면 update_ids() 실행
        if dt.datetime.strptime(
                last_update['track_recommend'], fmt
        ) < dt.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            await ctx.send('목록 갱신 중! 잠깐만 기다려봐―')
            update_ids()

        with open('data/track_recommend_ids.pkl', 'rb') as f:
            ids = pickle.load(f)
        await ctx.send('https://youtu.be/' + random.choice(ids))


def setup(bot):
    bot.add_cog(GoogleCommands(bot))
