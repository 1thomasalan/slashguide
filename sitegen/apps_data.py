# Built-in slash commands in apps (not AI prompts). Checked against each vendor's
# own help page on 2026-11-04; the "source" link on each section is that page.
# Each command: (cmd, does, add, example)
# cmd may contain capitals (shown as written); its page slug is the lowercase form.

ACRONYMS = {
    "dnd": "Do Not Disturb",
    "brb": "Be Right Back",
    "tts": "Text To Speech",
    "toc": "Table Of Contents",
    "msg": "Message",
    "h1": "Heading 1",
    "gif": "Graphics Interchange Format",
}

APP_SECTIONS = [
 {
  "id": "slack", "name": "Slack", "where": "the Slack message box",
  "blurb": "Built into every Slack workspace. Type / in the message box.",
  "source": "https://slack.com/help/articles/201259356-Use-built-in-slash-commands",
  "note": "Some commands can be limited to admins in your workspace.",
  "commands": [
   ("remind", "Sets a reminder for you, someone else or a channel.", "Who, what, and when, in plain words.", "/remind me to send the report tomorrow at 9am"),
   ("status", "Sets you to away or active.", "Nothing else needed.", "/status"),
   ("dnd", "Turns Do Not Disturb on or off to pause notifications.", "Optional: how long.", "/dnd for 1 hour"),
   ("huddle", "Starts a huddle (a quick audio call) in the current conversation.", "Nothing else needed.", "/huddle"),
   ("msg", "Sends a message to a person or a channel without leaving where you are.", "@someone or #channel, then your message.", "/msg @dana the deck is in the shared folder"),
   ("invite", "Adds someone to a channel.", "@someone and, if it's another channel, #channel.", "/invite @sam #project-launch"),
   ("leave", "Leaves the current channel.", "Nothing else needed.", "/leave"),
   ("topic", "Sets the topic shown at the top of the channel.", "The new topic.", "/topic Launch week: questions here, decisions in the doc"),
   ("mute", "Mutes or unmutes a conversation.", "Optional: #channel. Leave it off for the current one.", "/mute #random"),
   ("search", "Searches messages and files.", "Your search words.", "/search budget spreadsheet"),
   ("shrug", "Adds \u00af\\_(\u30c4)_/\u00af to the end of your message.", "Optional: your message.", "/shrug no idea who moved the meeting"),
  ],
 },
 {
  "id": "notion", "name": "Notion", "where": "any Notion page",
  "blurb": "Type / on a Notion page and keep typing to pick a block.",
  "source": "https://www.notion.com/help/keyboard-shortcuts",
  "note": "",
  "commands": [
   ("todo", "Adds a checkbox to-do list.", "Your first task after it appears.", "/todo"),
   ("toggle", "Adds a toggle list that opens and closes.", "A short title; tuck details inside.", "/toggle"),
   ("callout", "Adds a highlighted box with an icon, for notes and warnings.", "The text you want to stand out.", "/callout"),
   ("table", "Adds a simple table.", "Fill in rows and columns after it appears.", "/table"),
   ("code", "Adds a code block with syntax colors.", "Paste your code, then pick the language.", "/code"),
   ("quote", "Adds a larger quote block.", "The quote.", "/quote"),
   ("h1", "Adds a large heading. /h2 and /h3 make smaller ones.", "The heading text.", "/h1"),
   ("div", "Adds a light gray divider line.", "Nothing else needed.", "/div"),
   ("toc", "Adds a table of contents built from your headings.", "Nothing else needed; it updates itself.", "/toc"),
   ("comment", "Adds a comment to the current block.", "Your comment.", "/comment"),
  ],
 },
 {
  "id": "discord", "name": "Discord", "where": "any Discord text channel or DM",
  "blurb": "Discord's own built-in commands, before any bots are added.",
  "source": "https://support-apps.discord.com/hc/en-us/articles/26501837786775-Slash-Commands-FAQ",
  "note": "Some commands need a server permission, such as changing your nickname or sending text-to-speech.",
  "commands": [
   ("giphy", "Searches Giphy for a GIF to send.", "A word or two to search for.", "/giphy happy dance"),
   ("tenor", "Searches Tenor for a GIF to send.", "A word or two to search for.", "/tenor thumbs up"),
   ("spoiler", "Sends your message hidden until someone clicks it.", "The message to hide.", "/spoiler the twist is in episode 6"),
   ("nick", "Changes your nickname in this server.", "Your new nickname.", "/nick Alan (Okinawa)"),
   ("me", "Sends your message styled as an action.", "What you're doing.", "/me is brewing more coffee"),
   ("tts", "Reads your message aloud to people viewing the channel.", "The message to read.", "/tts dinner is ready"),
   ("thread", "Starts a new thread for one topic.", "The thread name and a first message.", "/thread weekend plans"),
   ("tableflip", "Adds (\u256f\u00b0\u25a1\u00b0)\u256f\ufe35 \u253b\u2501\u253b to your message.", "Optional: your message.", "/tableflip"),
   ("shrug", "Adds \u00af\\_(\u30c4)_/\u00af to your message.", "Optional: your message.", "/shrug"),
  ],
 },
 {
  "id": "obsidian", "name": "Obsidian", "where": "the Obsidian editor",
  "blurb": "Turn on Slash commands in Settings, then Core plugins. Type / at the start of a line or after a space.",
  "source": "https://help.obsidian.md/plugins/slash-commands",
  "note": "Obsidian matches loosely, so a few letters find any command. These are the words that land on each one.",
  "commands": [
   ("table", "Runs Insert table to add a Markdown table.", "Fill in the cells after it appears.", "/table"),
   ("callout", "Runs Insert callout to add a callout block.", "Your note. Change the type, like [!tip], if you like.", "/callout"),
   ("codeblock", "Runs Insert code block.", "Paste your code and name the language.", "/codeblock"),
   ("template", "Runs Templates: Insert template. Needs the Templates core plugin.", "Pick a template from your templates folder.", "/template"),
   ("date", "Runs Templates: Insert current date. Needs the Templates core plugin.", "Nothing else needed.", "/date"),
   ("today", "Runs Daily notes: Open today's daily note. Needs the Daily notes core plugin.", "Nothing else needed.", "/today"),
   ("property", "Runs Add file property, for tags, dates and other note details.", "The property name and value.", "/property"),
   ("checkbox", "Runs Toggle checkbox status on the current line.", "Nothing else needed.", "/checkbox"),
  ],
 },
 {
  "id": "teams", "name": "Teams", "where": "the Teams compose box or search bar",
  "blurb": "Microsoft Teams on desktop. Type / in a chat or in the search bar at the top.",
  "source": "https://support.microsoft.com/en-us/teams/chat/use-commands-in-microsoft-teams",
  "note": "Built-in commands work in Teams desktop only, and your organization can turn some off.",
  "commands": [
   ("available", "Sets your status to Available.", "Nothing else needed.", "/available"),
   ("busy", "Sets your status to Busy.", "Nothing else needed.", "/busy"),
   ("brb", "Sets your status to Be right back.", "Nothing else needed.", "/brb"),
   ("away", "Sets your status to Away.", "Nothing else needed.", "/away"),
   ("dnd", "Sets your status to Do not disturb.", "Nothing else needed.", "/dnd"),
   ("goto", "Jumps straight to a chat or channel.", "The chat or channel name.", "/goto Marketing team"),
   ("chat", "Sends a quick message from the search bar.", "The person, then your message.", "/chat Dana running 5 minutes late"),
   ("meetnow", "Starts or joins a quick meeting.", "Nothing else needed.", "/meetnow"),
   ("schedulemessage", "Schedules the message you're writing to send later.", "The day and time.", "/schedulemessage"),
   ("mute", "Mutes the current chat. /unmute turns it back on.", "Nothing else needed.", "/mute"),
   ("code", "Inserts a code block in your message.", "Paste your code.", "/code"),
  ],
 },
 {
  "id": "copilot", "name": "Copilot", "where": "GitHub Copilot Chat in your code editor",
  "blurb": "GitHub Copilot Chat in VS Code, Visual Studio, JetBrains and Xcode.",
  "source": "https://docs.github.com/en/copilot/reference/chat-cheat-sheet",
  "note": "The list changes by editor. Type / in Copilot Chat to see what yours offers.",
  "commands": [
   ("explain", "Explains how the selected code works.", "Select the code first. Add a question if you have one.", "/explain why this loop skips the last item"),
   ("fix", "Proposes a fix for problems in the selected code.", "Select the code. Paste the error if there is one.", "/fix TypeError: cannot read 'name' of undefined"),
   ("tests", "Writes unit tests for the selected code.", "Select the code. Name your test framework.", "/tests using pytest"),
   ("doc", "Adds a documentation comment. Visual Studio and Xcode.", "Put the cursor on the function or class.", "/doc"),
   ("optimize", "Suggests faster code for the selection. Visual Studio.", "Select the code.", "/optimize"),
   ("simplify", "Simplifies the selected code. Xcode.", "Select the code.", "/simplify"),
   ("new", "Starts a new project from a description. VS Code.", "What you want to build.", "/new a Flask app with one page and a contact form"),
   ("clear", "Clears the chat so you can start fresh.", "Nothing else needed.", "/clear"),
   ("help", "Shows a quick guide to using Copilot Chat.", "Nothing else needed.", "/help"),
  ],
 },
]

# The "/" key that jumps to the search box on many websites.
SEARCH_KEY = {
 "id": "web", "name": "Web",
 "slug": "search-key", "cmd": "/",
 "does": "Press / on many websites to jump straight to the search box, no mouse needed.",
 "add": "Just the / key, then type what you're looking for.",
 "example": "On YouTube, press / and type: how to repot a bonsai",
 "works": ["YouTube", "GitHub", "Gmail (with keyboard shortcuts on)", "MDN", "Slash Guide"],
 "blurb": "Not a command you type into a box: a key that takes you to the box.",
}
