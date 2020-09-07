import discord
from discord.ext import commands
import asyncio
import re
import random
import string
import traceback
import json
import datetime
from CongressBot.Congress_Utilities import Utilities


async def determine_prefix(bot, message):
    guild = message.guild
    # Only allow custom prefixs in guild
    if guild:
        try:
            return json.load(open("CongressSaves.json", "r"))[f'Command_Prefix'][str(guild.id)]
        except KeyError:
            return json.load(open("CongressSaves.json", "r"))[f'Default_Prefix']
    else:
        return json.load(open("CongressSaves.json", "r"))[f'Default_Prefix']


bot = commands.Bot(command_prefix=determine_prefix)
bot.remove_command("help")


class vote_master():
    async def demote_check(self, ctx, command, name, target):
        if target == "": target = [ctx.message.author]
        name = discord.utils.get(ctx.guild.roles, name=name)
        if command == "demote" and not all(name in sl.roles for sl in target):
            embedVar = discord.Embed(
                title=f"{bot.get_emoji(751553187453992970)} Role not found/Specified user does not have that role",
                color=0xc20000)
            await ctx.send(embed=embedVar)
            return False
        else:
            return True

    async def checking(self, ctx, command):
        master_list = {"giverole": ["Give Role of", " to "], "addchannel": ["Add the channel of", ""],
                       "givepower": ["Give power of", " to "], "demote": ["Remove the role of", " from "],
                       "misc": ["", ""]}
        try:
            return master_list[command.lower()]
        except KeyError:
            await util.errormsg(ctx)
            return False

    async def action(self, ctx, command, embedVar):
        if command[0].lower() == "misc" or command[0].lower() == "addchannel":
            await ctx.guild.owner.send("A vote has just passed that requires manual implementation",
                                       embed=embedVar)
        elif command[0].lower() == "demote":
            for i in command[1]:
                try:
                    await i.remove_roles(discord.utils.get(ctx.guild.roles, name=command[2]))
                except:
                    print('error: cannot find role')
                    await ctx.guild.owner.send(
                        "A vote has just passed that requires manual implementation due to an error, we are "
                        "sorry for the inconvenience",
                        embed=embedVar)
        elif command[0].lower() == "giverole":
            x = False
            if not discord.utils.get(ctx.guild.roles, name=string.capwords(str(command[2]))):
                msg = await ctx.author.send("What colour do you want the role to be? (reply in hex)")
                highest = discord.utils.find(lambda role: role in ctx.guild.roles, reversed(ctx.author.roles))

                def check(message):
                    return message.author == ctx.author and message.channel == msg.channel and re.search(
                        r'^#(?:[0-9a-fA-F]{1,2}){3}$', reply.content.lower())

                reply = await bot.wait_for('message', check=check)
                role = await ctx.guild.create_role(name=string.capwords(str(command[2])),
                                                   colour=discord.Colour(
                                                       int(f"0x{reply.content.lower().replace('#', '')}", 0)),
                                                   hoist=True,
                                                   reason="voted in")
                await ctx.message.author.add_roles(role)
                try:
                    await role.edit(position=highest.position)
                    embedVar = discord.Embed(
                        title=f"{bot.get_emoji(751553187529490513)} Confirmed! Enjoy your new role!",
                        color=0x00c943)
                    await ctx.author.send(embed=embedVar)
                except discord.Forbidden or discord.HTTPException:
                    embedVar = discord.Embed(
                        title=f"{bot.get_emoji(751653673628860476)} Sorry, something went wrong on our end. You will"
                              " still receive your role. Please contact an administrator for more info",
                        color=0xfff30a)
                    await ctx.author.send(embed=embedVar)
                return
            else:
                embedVar = discord.Embed(
                    title=f"{bot.get_emoji(751553187453992970)} That is not a valid hex code",
                    color=0xc20000)
                await ctx.author.send(embed=embedVar)
        else:
            await ctx.message.author.add_roles(
                discord.utils.get(ctx.guild.roles, name=string.capwords(str(command[2]))))
            embedVar = discord.Embed(
                title=f"{bot.get_emoji(751553187529490513)} Confirmed! Enjoy your new role!",
                color=0x00c943)
            await ctx.author.send(embed=embedVar)


util = Utilities(bot)

class vote_main():
    async def vote(self, ctx, command, members: commands.Greedy[discord.Member], *, name):
        classmaster = vote_master()
        Yes = bot.get_emoji(749126458164641813)
        No = bot.get_emoji(749126458521157632)
        target = ", ".join(x.name for x in members)
        role = util.rolefunc(ctx)
        master = await classmaster.checking(ctx, command)
        if not master or not await classmaster.demote_check(ctx, command, name, members):
            return
        if str(ctx.guild.owner.name) in target:
            embedVar = discord.Embed(
                title=f"{bot.get_emoji(751553187453992970)} Votes cannot affect the server's owner",
                color=0xc20000)
            await ctx.send(embed=embedVar)
            return
        if not target and master[0]:
            target = "themselves"
        if target:
            target = target + " "
        embedVar = discord.Embed(title="Vote", description="{0} {2}{3}{1}".format(master[0], target, name, master[1]),
                                 color=0xffbf00)
        waittime = util.getsave(ctx, "Time", "time_value")
        embedVar.add_field(name="Vote will last for {0}".format(util.convert(waittime)),
                           value="\u200b")
        embedVar.set_footer(text=f"Vote Created by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        sent_message = await ctx.send(" ".join(role), embed=embedVar)
        await sent_message.add_reaction(No)
        await sent_message.add_reaction(Yes)


# vote command
@bot.command()
@commands.guild_only()
async def vote(ctx, command, members: commands.Greedy[discord.Member], *, name):
    print(members)
    classmaster = vote_master()
    Yes = bot.get_emoji(749126458164641813)
    No = bot.get_emoji(749126458521157632)
    target = ", ".join(x.name for x in members)
    role = util.rolefunc(ctx)
    master = await classmaster.checking(ctx, command)
    if not master or not await classmaster.demote_check(ctx, command, name, members): return
    if str(ctx.guild.owner.name) in target:
        embedVar = discord.Embed(
            title=f"{bot.get_emoji(751553187453992970)} Votes cannot affect the server's owner",
            color=0xc20000)
        await ctx.send(embed=embedVar)
        return
    if not target and master[0]: target = "themselves"
    if target: target = target + " "
    embedVar = discord.Embed(title="Vote", description="{0} {2}{3}{1}".format(master[0], target, name, master[1]),
                             color=0xffbf00)
    waittime = util.getsave(ctx, "Time", "time_value")
    embedVar.add_field(name="Vote will last for {0}".format(util.convert(waittime)),
                       value="\u200b")
    embedVar.set_footer(text=f"Vote Created by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
    sent_message = await ctx.send(" ".join(role), embed=embedVar)
    await sent_message.add_reaction(No)
    await sent_message.add_reaction(Yes)
    await asyncio.sleep(waittime)
    cache = await ctx.fetch_message(id=sent_message.id)
    matching = [s for s in cache.reactions if Yes or No in s]
    if cache.reactions[cache.reactions.index(matching[0])].count >= cache.reactions[
        cache.reactions.index(matching[1])].count:
        await ctx.send("{} Vote Failed to Pass".format(" ".join([roles for roles in role])), embed=embedVar)
        return
    elif cache.reactions[cache.reactions.index(matching[0])].count < cache.reactions[
        cache.reactions.index(matching[1])].count:
        await ctx.send("{} Vote Passed".format(" ".join([roles for roles in role])), embed=embedVar)
        await vote_master().action(ctx, [command, members, name], embedVar)


@vote.error
async def vote_error(ctx, error):
    await util.error_core(ctx, error)


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Welcome to Congress!", description=" Created by Alex_123456", color=0x0084ff)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name="!vote(command, users(optional), Description)",
                    value="`Command`: input commands \n\n `Users`: Target user (leave empty if not needed or you "
                          "are the "
                          "target) \n\n `Description`: Name of Role, General Description of idea, whatever \n\n\n "
                          "**Examples**"
                          " \n\n !Vote giverole @dummy nerd \n\n !Vote demote @dummy God \n\n !Vote giverole King\n\n",
                    inline=True)
    embed.add_field(name="!vote Commands",
                    value="\n`Giverole`: Creates and gives the role specified in the description field \n\n"
                          " `Addchannel`: Adds "
                          "the channel explained in the description field (Manual) \n\n `Givepower`: Gives the power "
                          "specified in the description field (Manual) \n\n `Demote`: Remove the role specified in the "
                          "description \n\n `Misc`: Any other votes\n\n",
                    inline=True)
    embed.add_field(name="!multichoice (command, choices)",
                    value="Supports up to 9 choices, Choices separated by a comma\n\n`timed`: A timed vote\n\n`open`: "
                          "An open poll\n\n",
                    inline=True)
    embed.add_field(name="Admin Only Commands",
                    value="`!settime (number)`: (Admin only) Sets time of voting for all future votes (default time: 24 hours)\n\n`!settrole "
                          "(@role)`: (Admin only) Sets roles pinged every new vote\n\n `!commandprefix (prefix)`: (Admin onlt) Sets "
                          "the prefix for commands (default prefix: !)",
                    inline=True)
    embed.add_field(name="Information Commands",
                    value="`!readtime`: Displays what the current voting time is set to for future votes\n\n`!readroles"
                          "`: Displays what roles are pined for all future votes",
                    inline=True)
    embed.add_field(name="\u200b",
                    value="\u200b",
                    inline=True)

    await ctx.author.send(embed=embed)


# multichoice
@bot.command()
@commands.guild_only()
async def multichoice(ctx, setting, *, choices):
    if str(setting).lower() != "open" and str(setting).lower() != "timed":
        multichoice.close()
    role = util.rolefunc(ctx)
    emojis = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 10)]
    choices = " ".join(choices.split())
    embedVar = discord.Embed(title="Vote", description="Choose between {0}".format(choices),
                             color=0xffbf00)
    waittime = util.getsave(ctx, "Time", "time_value")
    embedVar.add_field(name="Vote will last for {0}".format(util.convert(waittime)),
                       value="\u200b")
    embedVar.set_footer(text=f"Vote Created by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
    sent_msg = await ctx.send(" ".join(role), embed=embedVar)
    choices = choices.split(",")
    for i in range(len(choices)):
        await sent_msg.add_reaction(emojis[i])
    if str(setting).lower() == "timed":
        await asyncio.sleep(waittime)
        cache = await ctx.fetch_message(id=sent_msg.id)
        ranges = [cache.reactions[num].count for num in range(0, len(choices))]
        embedVar = discord.Embed(title="Vote", description="The winning choice is {0}".format(','.join(
            [choices[i] for i, x in enumerate(ranges) if x == max(ranges)])),
                                 color=0xffbf00)
        embedVar.set_footer(text=f"Vote Created by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(" ".join(role), embed=embedVar)


@multichoice.error
async def multichoice_error(ctx, error):
    await util.error_core(ctx, error)


# set time
@bot.command()
@commands.guild_only()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def settime(ctx, time: int):
    data = json.load(open("CongressSaves.json", "r"))
    data["time_value"][str(ctx.guild.id)] = int(time)
    with open("CongressSaves.json", "w") as file:
        json.dump(data, file)
    time = util.convert(time)
    embedVar = discord.Embed(
        title=f"{bot.get_emoji(751553187529490513)} Confirmed! The new voting time is {time}!",
        color=0x00c943)
    await ctx.send(embed=embedVar)


@settime.error
async def settime_error(ctx, error):
    await util.error_core(ctx, error)


# read time
@bot.command()
@commands.guild_only()
async def readtime(ctx):
    waittime = util.convert(util.getsave(ctx, "Time", "time_value"))
    embedVar = discord.Embed(
        title="The voting time is {}".format(waittime),
        color=0x00058f)
    await ctx.send(embed=embedVar)


# set roles
@bot.command()
@commands.guild_only()
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def setrole(ctx, roles: discord.role.Role):
    data = json.load(open("CongressSaves.json", "r"))
    if data["Mentionable_Roles"].get(str(ctx.guild.id)):
        if str(roles.id) in data["Mentionable_Roles"][str(ctx.guild.id)]:
            data["Mentionable_Roles"][str(ctx.guild.id)].remove(str(roles.id))
            embedVar = discord.Embed(
                title="{} Confirmed! I will no longer mention {} every vote!".format(bot.get_emoji(751553187529490513),
                                                                                     roles.name),
                color=0x00c943)
            await ctx.send(embed=embedVar)
        else:
            data["Mentionable_Roles"][str(ctx.guild.id)].append(str(roles.id))
            tempvar = [discord.utils.get(ctx.guild.roles, id=int(data["Mentionable_Roles"][str(ctx.guild.id)][i])) for i
                       in
                       range(0, len(data["Mentionable_Roles"][str(ctx.guild.id)]))]
            embedVar = discord.Embed(
                title="{} Confirmed! I will now mention {} every vote!".format(bot.get_emoji(751553187529490513),
                                                                               ", ".join(list(tempvar[i].name for i in
                                                                                              range(0, len(tempvar))))),
                color=0x00c943)
            await ctx.send(embed=embedVar)
    else:
        data["Mentionable_Roles"][str(ctx.guild.id)] = []
        data["Mentionable_Roles"][str(ctx.guild.id)].append(str(roles.id))
        embedVar = discord.Embed(
            title="{} Confirmed! I will now mention {} every vote!".format(bot.get_emoji(751553187529490513),
                                                                           roles.name),
            color=0x00c943)
        await ctx.send(embed=embedVar)
    with open("CongressSaves.json", "w") as file:
        json.dump(data, file)


@setrole.error
async def setrole_error(ctx, error):
    await util.error_core(ctx, error)


@bot.command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def commandprefix(ctx, prefix):
    data = json.load(open("CongressSaves.json", "r"))
    data["Command_Prefix"][str(ctx.guild.id)] = str(prefix)
    with open("CongressSaves.json", "w") as file:
        json.dump(data, file)
    embedVar = discord.Embed(
        title=f"{bot.get_emoji(751553187529490513)} Confirmed! The new prefix is {prefix}!",
        color=0x00c943)
    await ctx.send(embed=embedVar)
    bot.command_prefix = prefix


@commandprefix.error
async def commandprefix_error(ctx, error):
    await util.error_core(ctx, error)


# read roles
@bot.command()
@commands.guild_only()
async def readroles(ctx):
    data = json.load(open("CongressSaves.json", "r"))
    tempvar = [discord.utils.get(ctx.guild.roles, id=int(data["Mentionable_Roles"][str(ctx.guild.id)][i])) for i
               in
               range(0, len(data["Mentionable_Roles"][str(ctx.guild.id)]))]
    embedVar = discord.Embed(
        title="The pinged roles are {}".format(", ".join(list(tempvar[i].name for i in
                                                              range(0, len(tempvar))))),
        color=0x00058f)
    await ctx.send(embed=embedVar)


@readroles.error
async def readrole_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embedVar = discord.Embed(
            title=f"{bot.get_emoji(751553187453992970)} You do not have the permission to do that",
            color=0xc20000)
        await ctx.send(embed=embedVar)
    elif isinstance(error, commands.NoPrivateMessage):
        embedVar = discord.Embed(
            title=f"{bot.get_emoji(751553187453992970)} You can only do that in a server!",
            color=0xc20000)
        await ctx.send(embed=embedVar)
    if isinstance(getattr(error, "original", error), KeyError):
        embedVar = discord.Embed(
            title=f"{bot.get_emoji(751553187453992970)} No pinged roles, type !setrole @role to add your first role to the list!",
            color=0xc20000)
        await ctx.send(embed=embedVar)
    else:
        print('Ignoring exception in command {}:'.format(ctx.command))
        traceback.print_exception(type(error), error, error.__traceback__, )
        await util.errormsg(ctx)


@bot.command()
@commands.is_owner()
async def say(ctx, *, msg):
    await ctx.send(msg)
    await ctx.message.delete()


@bot.command()
@commands.is_owner()
async def halt(ctx, *, msg):
    def check(m):
        return m.content.lower() == 'yes', 'no' and m.channel == ctx.message.channel

    try:
        await ctx.send("This will halt Congressbot immediately until the bot can be turned back on, Confirm? (Yes/No)")
        message = await bot.wait_for('message', check=check, timeout=60)
        if message.content.lower() == "no":
            await ctx.send("Aborted")
            return
        await ctx.send("Confirmed")
    except asyncio.TimeoutError:
        await ctx.send("Aborted")
        return
    msg = discord.Embed(
        title=f"{bot.get_emoji(751653673628860476)} Something went wrong on our end and Congressbot has to temporarily "
              f"shut down. We are sorry for the inconvenience",
        description=f"Reason: {msg}",
        color=0xfff30a)
    for server in bot.guilds:
        try:
            data = discord.utils.get(server.channels,
                                     name=json.load(open("CongressSaves.json", "r"))["Announce_Channel"][
                                         str(server.id)])
            if data:
                await data.send(embed=msg)
        except KeyError:
            for channel in server.channels:
                try:
                    await channel.send(embed=msg)
                except Exception:
                    continue
                else:
                    break
    exit("Emergency stop")


@bot.command()
@commands.is_owner()
async def announce(ctx, *, msg):
    def check(m):
        return m.content.lower() == 'yes', 'no' and m.channel == ctx.message.channel

    try:
        await ctx.send("Are you sure you want to announce this to every server? Yes/No")
        message = await bot.wait_for('message', check=check, timeout=60)
        if message.content.lower() == "no":
            await ctx.send("Aborted")
            return
        await ctx.send("Confirmed")
    except asyncio.TimeoutError:
        await ctx.send("Aborted")
        return
    msg = discord.Embed(
        title=f"\U0001F4E2 Announcement: {msg}",
        color=0x00058f)
    msg.set_footer(text=f"Announcement by {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
    for server in bot.guilds:
        try:
            data = discord.utils.get(server.channels,
                                     name=json.load(open("CongressSaves.json", "r"))["Announce_Channel"][
                                         str(server.id)])
            if data:
                await data.send(embed=msg)
        except KeyError:
            for channel in server.channels:
                try:
                    await channel.send(embed=msg)
                except Exception:
                    continue
                else:
                    break


@bot.command()
@commands.guild_only()
@commands.check_any(commands.is_owner(),
                    commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True))
async def setannounce(ctx):
    data = json.load(open("CongressSaves.json", "r"))
    data["Announce_Channel"][str(ctx.guild.id)] = str(ctx.message.channel)
    json.dump(data, open("CongressSaves.json", "w"))
    embedVar = discord.Embed(
        title=f"{bot.get_emoji(751553187529490513)} Confirmed! The announce channel is {str(ctx.message.channel.name)}!",
        color=0x00c943)
    await ctx.send(embed=embedVar)


# startup
@bot.event
async def on_ready():
    # {i.id: default_time for i in bot.guilds}
    democracy = ["Democracy is an abuse of statistics.",
                 "People shouldn't be afraid of their government. Governments should be afraid of their people.",
                 "The best argument against democracy is a five-minute conversation with the average voter.",
                 "Democracy must be something more than two wolves and a sheep voting on what to have for dinner.",
                 "Elections belong to the people. It's their decision. If they decide to turn their back on the fire "
                 "and burn their behinds, then they will just have to sit on their blisters.",
                 "I am a firm believer in the people. If given the truth, they can be depended upon to meet any "
                 "national crisis.", "A vote is like a rifle: its usefulness depends upon the character of the user.",
                 "Secrecy begets tyranny.", "Democracy is not just the right to vote, it is the right to live in "
                                            "dignity.",
                 "The ballot is stronger than the bullet.", "Politics is the art of the possible, the attainable — the "
                                                            "art of the next best",
                 "Every election is determined by the people who show up.", "A society without democracy is a society "
                                                                            "of slaves and fools.",
                 "Democracy is a device that ensures we shall be governed no better than we deserve.",
                 "A great democracy has got to be progressive or it will soon cease to be great or a democracy.",
                 "Democracy is the worst form of government, except for all the others.", "As I would not be a slave, "
                                                                                          "so I would not be a master. "
                                                                                          "This expresses my idea of "
                                                                                          "democracy.",
                 "Democracy is worth dying for, because it's the most deeply honorable form of government ever devised "
                 "by man.",
                 "...I do not want art for a few; any more than education for a few; or freedom for a few...",
                 "it is the people who control the Government, not the Government the people."]
    print('We have logged in as {0.user}'.format(bot))
    while bot.is_ready():
        await bot.change_presence(activity=discord.Game(name="!help for help"))
        await asyncio.sleep(60)
        await bot.change_presence(activity=discord.Game(name="Created by Alex_123456"))
        await asyncio.sleep(60)
        await bot.change_presence(activity=discord.Game(name=f'"{democracy[random.randint(0, len(democracy) - 1)]}"'))
        await asyncio.sleep(60)


bot.run('token')
