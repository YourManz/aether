# Drop the player straight into the Aether on the container console, but
# never on a nested shell (machinectl shell, su, the familiar's own
# subprocesses) — the AETHER_IN guard stops a familiar-in-familiar loop.
case "$(tty)" in
  /dev/console|/dev/pts/0)
    if [ -z "${AETHER_IN:-}" ]; then
      export AETHER_IN=1
      [ -r /etc/aether-banner.sh ] && bash /etc/aether-banner.sh
      exec /opt/aether/play
    fi
    ;;
esac
