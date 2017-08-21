# -*- coding=utf-8 -*-
import sys



usage = "Usage: python main.py command\n available command are crawl, analyse, cron, script"
if len(sys.argv) < 2:
    print  usage

command = sys.argv[1]
if command == "crawl":
    import crawl.main
    crawl.main.main()
elif command == "analyse":
    import analyse.main
    analyse.main.main()
elif command == "cron":
    import cron.main
    cron.main.main()
elif command == "script":
    import script.main
    script.main.main()
else:
    print usage
