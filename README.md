# Project Timer

A simple Windows desktop application for tracking time spent on different projects. Built with Python and Tkinter, with no third-party dependencies.

## Features

- Click a project button to start tracking time.
- Switching projects automatically stops the previous timer.
- **Stop All** pauses tracking.
- View today’s totals on each button and daily history in the table.
- Automatically saves totals between launches.
- Splits sessions across dates when tracking continues past midnight.
- Export daily totals to a text file using **Save**.

## Projects

Edit the `PROJECTS` tuple in `project_timer.py` to customise the project list.

## Requirements

- Windows
- Python 3 with Tkinter, included in the standard Windows Python installer

No additional packages are required.

## Running

Double-click `Start Project Timer.bat`, or run:

```shell
python project_timer.py
```

## Export format

Each line contains a project, accumulated hours and minutes, and the recorded date:

```text
Project A - 01:25 - 2026-10-19
Travel - 00:42 - 2026-10-19
Training - 00:00 - 2026-10-19
Project B - 02:10 - 2026-10-19
```

Exports include all recorded dates and projects. Seconds are retained internally but truncated to whole minutes in the export. Saving does not stop the active timer.

## Data storage

Totals are saved automatically every second to:

```text
%LOCALAPPDATA%\ProjectTimer\time_data.json
```

Closing the application stops tracking. Reopening restores the totals with all timers paused.

## Timing behaviour

- Locking the computer leaves the timer running while the computer stays awake.
- Time spent asleep or in hibernation is included when the computer resumes.
- Use **Stop All** before a break to exclude that time.
- Run one copy of the application at a time.
