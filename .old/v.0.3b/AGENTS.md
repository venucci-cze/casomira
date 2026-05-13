# AGENTS.md

This file provides instructions for AI coding agents working on the ESP8266 Timing System PC side project.

## Project Overview
This is a Python GUI application that fetches timing data from a single ESP8266 device via HTTP and saves it to a CSV file. The ESP8266 device acts as a WiFi access point serving timing data at `/data` endpoint. The application uses tkinter for the GUI and supports manual and automatic data fetching.

## Key Files
- `casomira.py`: Main Python GUI script that fetches data and saves to CSV
- `Požadavky/pozadavky_windows.bat`: Windows installation script
- `Požadavky/pozadavky_linux.sh`: Linux installation script
- `spustit_windows.bat`: Windows launcher script
- `spustit_linux.sh`: Linux launcher script
- `Čti mě README.txt`: Setup and usage instructions
- `esp8266/`: Example ESP8266 firmware code (C++/Arduino)
- `cas_esp_8266main/`: PlatformIO project for ESP8266 firmware development
- `timing_data.csv`: Output CSV file with timing data

## Development Setup
1. Run the appropriate installation script:
   - Windows: `Požadavky\pozadavky_windows.bat`
   - Linux: `Požadavky/pozadavky_linux.sh`
2. Configure ESP8266 IP address in `casomira.py` (SINGLE_ESP_IP variable)
3. Run the application:
   - Windows: `spustit_windows.bat`
   - Linux: `./spustit_linux.sh`

## Code Conventions
- Code is written in Czech (comments and strings)
- Uses Python libraries: tkinter, requests, time, datetime, threading
- Data saved to `timing_data.csv` with format: timestamp,team_a_time,team_b_time
- GUI application with manual and automatic measurement modes
- Error handling for network connectivity issues
- Prevents saving duplicate or invalid data

## Common Tasks
- **Configure IP**: Update SINGLE_ESP_IP in `casomira.py` for your ESP8266 device
- **Test connectivity**: ESP8266 must be running and accessible at configured IP
- **Data format**: ESP8266 should return JSON: `{"team_a_time": "value", "team_b_time": "value"}`
- **Firmware development**: Use `cas_esp_8266main/` PlatformIO project for ESP8266 code

## Pitfalls
- IP address must be changed from default (192.168.4.1)
- ESP8266 firmware must match the expected `/data` endpoint
- Network connectivity issues will show "Chyba spojení" in GUI
- Application requires Python 3 with tkinter support
- Windows requires winget for automatic Python installation

## Shoutout
- This program and corresponding device was created by SVM (venucci)
- Dont do bad stuff with it, it's gonna be open source so..., dont infiltrate our timing system.
- You can send bugs or other stuff to venucci2114@post.cz.
