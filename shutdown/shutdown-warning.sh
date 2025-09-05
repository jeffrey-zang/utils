#!/bin/bash
osascript -e 'display notification "Mac will shut down in 5 minutes. Run `sudo killall shutdown` to cancel." with title "Shutdown Scheduled"'
