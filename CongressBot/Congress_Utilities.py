import json
import discord
import traceback
from discord.ext import commands

class Utilities():
    def __init__(self, bot):
        self.bot = bot
    def rolefunc(self, ctx):
        try:
            data = json.load(open("CongressSaves.json", "r"))
            data = [discord.utils.get(ctx.guild.roles, id=int(data["Mentionable_Roles"][str(ctx.guild.id)][i])) for i in
                    range(0, len(data["Mentionable_Roles"][str(ctx.guild.id)]))]
            return list(data[i].mention for i in range(0, len(data)))
        except KeyError:
            return []


    async def errormsg(self, ctx):
        embedVar = discord.Embed(
            title=f"{self.bot.get_emoji(751553187453992970)} Invalid Input, type !help for list of commands",
            color=0xc20000)
        await ctx.send(embed=embedVar)


    async def error_core(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            embedVar = discord.Embed(
                title=f"{self.bot.get_emoji(751553187453992970)} You can only do that in a server!",
                color=0xc20000)
            await ctx.send(embed=embedVar)
        elif isinstance(error, commands.CheckFailure):
            embedVar = discord.Embed(
                title=f"{self.bot.get_emoji(751553187453992970)} You do not have the permission to do that",
                color=0xc20000)
            await ctx.send(embed=embedVar)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command))
            traceback.print_exception(type(error), error, error.__traceback__, )
            await self.errormsg(ctx)


    def getsave(self, ctx, x, dataname):
            data = json.load(open("CongressSaves.json", "r"))
            try:
                return data[dataname][str(ctx.guild.id)]
            except KeyError:
                return data[f'Default_{x}']


    def prefix(self, ctx):
        data = json.load(open("CongressSaves.json", "r"))
        try:
            return data['Command_Prefix'][str(ctx.guild.id)]
        except KeyError:
            return data['Default_Prefix']

    def convert(self, seconds):
        min, sec = divmod(seconds, 60)
        hour, min = divmod(min, 60)
        return "%d:%02d:%02d" % (hour, min, sec)

