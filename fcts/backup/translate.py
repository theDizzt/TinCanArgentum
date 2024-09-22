# 3.2.4. 번역기
#To user who sent message
# await message.author.send(msg)

    if message.author == client.user:
        return

def sendmsg(resultPackage) -> discord.Embed:
        if resultPackage['status']["code"] < 300:
            embed = discord.Embed(
                title=
                f"Translate | {resultPackage['data']['ntl']['name']} -> {resultPackage['data']['tl']['name']}",
                description="",
                color=0x5CD1E5)
            embed.add_field(
                name=f"{resultPackage['data']['ntl']['name']} to translate",
                value=resultPackage['data']['ntl']['text'],
                inline=False)
            embed.add_field(
                name=f"Translated {resultPackage['data']['tl']['name']}",
                value=resultPackage['data']['tl']['text'],
                inline=False)
            embed.set_thumbnail(
                url="https://papago.naver.com/static/img/papago_og.png")
            embed.set_footer(
                text=
                "Service provided by Hoplin. API provided by Naver Open API",
                icon_url=
                'https://avatars2.githubusercontent.com/u/45956041?s=460&u=1caf3b112111cbd9849a2b95a88c3a8f3a15ecfa&v=4'
            )
            return embed
        else:
            embed = discord.Embed(title="Error Code",
                                  description=resultPackage['status']['code'],
                                  color=0x5CD1E5)
            return embed

#3.2.4.1. 한영번역
    if message.content.startswith(prefix + "ke"):
        #띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                resultPackage = streamInstance.returnQuery(trsText)
                embedInstance = sendmsg(resultPackage)
                await message.channel.send("Translate complete",
                                           embed=embedInstance)
        except HTTPError as e:
            await message.channel.send(
                f"Translate Failed. HTTPError Occured : {e}")

#3.2.4.2. 영한번역
    if message.content.startswith(prefix + "ek"):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                resultPackage = streamInstance.returnQuery(trsText)
                embedInstance = sendmsg(resultPackage)
                await message.channel.send("Translate complete",
                                           embed=embedInstance)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

#3.2.4.3. 영중번역
    if message.content.startswith(prefix + "한일번역"):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                resultPackage = streamInstance.returnQuery(trsText)
                embedInstance = sendmsg(resultPackage)
                await message.channel.send("Translate complete",
                                           embed=embedInstance)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

#3.2.4.4. 중영번역
    if message.content.startswith(prefix + "일한번역"):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                resultPackage = streamInstance.returnQuery(trsText)
                embedInstance = sendmsg(resultPackage)
                await message.channel.send("Translate complete",
                                           embed=embedInstance)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

#3.2.4.5. 한중번역
    if message.content.startswith(prefix + "kc"):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                resultPackage = streamInstance.returnQuery(trsText)
                embedInstance = sendmsg(resultPackage)
                await message.channel.send("Translate complete",
                                           embed=embedInstance)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

#3.2.4.6. 중한번역
    if message.content.startswith(prefix + "ck"):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                resultPackage = streamInstance.returnQuery(trsText)
                embedInstance = sendmsg(resultPackage)
                await message.channel.send("Translate complete",
                                           embed=embedInstance)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")