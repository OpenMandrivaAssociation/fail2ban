#!/bin/sh
curl "https://github.com/fail2ban/fail2ban/releases" 2>/dev/null |grep "tag/" |sed -e 's,.*tag/,,;s,\".*,,;' |head -n1

