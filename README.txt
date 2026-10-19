PROJECT TIMER

Requires Python 3 with Tkinter (included in the standard Windows Python installer).
No third-party libraries or pip installations are needed.

Double-click "Start Project Timer.bat", or run:
    python project_timer.py

Click a project to start its timer. Switching projects stops the previous one.
Clicking the running project keeps it running. Stop All pauses tracking.
The buttons show today's totals. The table shows all recorded days.
Time crossing midnight is divided between the appropriate dates.
Closing the application stops tracking. Reopening restores totals, paused.
Leave the app open and the computer awake while tracking time.

Save exports all dates and projects to a text file you choose, for example:
Project B Security - 01:25 - 2026-10-19
Impact - AI - 00:42 - 2026-10-19

Exports use whole minutes (seconds are truncated, not rounded).
The application retains seconds internally and displays HH:MM:SS.
Save takes a snapshot; a running timer continues afterwards.
Saving over an earlier export replaces it with the current complete totals.

Totals are also automatically stored every second in:
    %LOCALAPPDATA%\ProjectTimer\time_data.json

Run only one copy of the application at a time.
