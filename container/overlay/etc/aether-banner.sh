#!/usr/bin/env bash
# The title card, shown once at login. Degrades gracefully so a fresh rootfs
# never produces a broken login: lolcat -> toilet --gay -> plain figlet ->
# plain text. The RPG *feel* comes mostly from app-level ANSI theming, so the
# rainbow pipe is pure garnish.
cols="$(tput cols 2>/dev/null || echo 80)"

title() {
  if command -v figlet >/dev/null 2>&1; then
    figlet -w "$cols" "The Aether"
  else
    printf '\n        T H E   A E T H E R\n\n'
  fi
}

if command -v lolcat >/dev/null 2>&1; then
  title | lolcat
elif command -v toilet >/dev/null 2>&1; then
  toilet -w "$cols" -f mono12 --gay "The Aether" 2>/dev/null || title
else
  title
fi

printf '\n  \033[2mthe physics is the operating system — whisper `help`\033[0m\n\n'
sleep 1
