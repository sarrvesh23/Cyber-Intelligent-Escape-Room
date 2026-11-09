import json
import ipaddress
import math
import os
import random
import re
import string
import tkinter as tk
import unicodedata
from collections import deque
from datetime import datetime
from tkinter import messagebox
from urllib.parse import urlsplit

WIDTH = 1000
HEIGHT = 700
FONT = "TkFixedFont"
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")
HINT_COST = 5
WRONG_TIME_PENALTY = 5
POINTS_BY_MISTAKES = (10, 5, 2, 0)

BG = "#05080f"
PANEL = "#0b1220"
PANEL_LIGHT = "#101a2e"
WHITE = "#e8f1ff"
MUTED = "#5b6b8a"
GREEN = "#00ff9c"
CYAN = "#00e5ff"
YELLOW = "#ffd23f"
PINK = "#ff2e97"
PURPLE = "#a678ff"
ORANGE = "#ff9f1c"
RED = "#ff3b3b"

ESCAPE_QUOTES = [
    "The exit is not hidden. It is disguised as the next right decision.",
    "In the Archive, curiosity opens doors. Panic opens traps.",
    "Trust evidence, verify identities, and never let the clock think for you.",
    "A quiet alert is still a clue. A loud message is still unverified.",
    "Every locked door is a question. Every careful answer is a key.",
    "The best escape plan is the one you can explain to your whole team.",
]

BRAND_DOMAINS = {
    "google": ("google.com", "google.co.in"),
    "microsoft": ("microsoft.com", "live.com", "office.com"),
    "apple": ("apple.com", "icloud.com"),
    "amazon": ("amazon.com", "amazon.in", "amazon.co.uk"),
    "paypal": ("paypal.com", "paypal.me"),
    "netflix": ("netflix.com",),
    "facebook": ("facebook.com", "meta.com"),
    "instagram": ("instagram.com",),
    "whatsapp": ("whatsapp.com",),
    "bank": (),
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly",
    "rb.gy", "ow.ly", "shorturl.at", "buff.ly",
}

RISK_WORDS = {
    "verify", "login", "secure", "account", "update", "billing", "invoice",
    "password", "wallet", "reward", "prize", "claim", "urgent", "support",
    "confirm", "suspend", "unlock", "payment", "limited", "gift",
}

SUSPICIOUS_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".com", ".js", ".jse", ".vbs", ".vbe",
    ".ps1", ".hta", ".msi", ".lnk", ".iso", ".img", ".jar", ".apk",
    ".docm", ".xlsm", ".pptm", ".xll",
}

SECTORS = [
    {
        "name": "01  |  INTAKE LOBBY",
        "short": "INTAKE",
        "room": "The Checkpoint",
        "color": GREEN,
        "time": 240,
        "puzzles": [
            {
                "type": "mcq", "tag": "SAFER SIGN-IN", "difficulty": "WARM-UP",
                "question": "A classmate asks to borrow your account for a minute. What is the safest response?",
                "options": ["Share your password if they promise to log out", "Sign in for them, then leave the device", "Keep your password private and help them use their own account", "Send them a screenshot of your password hint"],
                "answer": 2,
                "why": "Accounts are personal. Sharing credentials makes it difficult to know who performed an action and puts your account at risk.",
                "hint": "Choose the option that keeps your account credentials private."
            },
            {
                "type": "mcq", "tag": "PUBLIC WI-FI", "difficulty": "CHALLENGING",
                "question": "At a cafe, you need to check a sensitive bank account. What is the best choice?",
                "options": ["Use the open Wi-Fi because it has a strong signal", "Wait for trusted mobile data or a trusted network", "Ask a stranger to share their hotspot password", "Turn off your phone lock to connect faster"],
                "answer": 1,
                "why": "Open public networks can expose your activity. For sensitive accounts, use a trusted network or mobile data and keep your device protected.",
                "hint": "A strong Wi-Fi signal does not mean the network is trustworthy."
            },
            {
                "type": "mcq", "tag": "LINK CHECK", "difficulty": "ADVANCED",
                "question": "A delivery text says a tiny fee is due. Which link should make you pause?",
                "options": ["The official delivery app you opened yourself", "A link whose domain is misspelled and asks for card details", "A tracking number in the official app", "A phone number printed on your delivery receipt"],
                "answer": 1,
                "why": "Unexpected payment links and look-alike domains are common phishing tricks. Open the official app or type the known website yourself.",
                "hint": "Look for a message that combines an unexpected fee with a suspicious domain."
            },
            {
                "type": "mcq", "tag": "ACCOUNT RECOVERY", "difficulty": "EXPERT",
                "question": "You receive a login approval prompt you did not initiate. What should you do?",
                "options": ["Approve it in case it is a delayed notification", "Share the code with the caller claiming to be support", "Deny it, change your password from the official app, and report it", "Ignore repeated prompts and keep approving them"],
                "answer": 2,
                "why": "Unexpected sign-in prompts can mean someone has your password. Deny the request, secure the account using the official service, and report it.",
                "hint": "Never approve a sign-in you did not start. Secure the account using a trusted route."
            },
        ],
    },
    {
        "name": "02  |  SERVICE TUNNEL",
        "short": "TUNNEL",
        "room": "The Maintenance Passage",
        "color": CYAN,
        "time": 210,
        "puzzles": [
            {
                "type": "jumble", "tag": "WORD FRAGMENTS", "difficulty": "STANDARD",
                "question": "Rearrange the letters to identify software that secretly records what you do.",
                "scramble": "PYSWARE", "answer": "SPYWARE",
                "why": "Spyware secretly monitors activity or collects information. Install apps only from trusted sources and review permissions.",
                "hint": "The word starts with SPY and ends with WARE."
            },
            {
                "type": "jumble", "tag": "WORD FRAGMENTS", "difficulty": "ADVANCED",
                "question": "Unscramble the incident-response action: restore files from a safe copy after an attack.",
                "scramble": "KACBUP", "answer": "BACKUP",
                "why": "A separate, tested backup can help recover files after device failure or ransomware. Keep at least one backup disconnected from the computer.",
                "hint": "It is a six-letter word that begins with B."
            },
        ],
    },
    {
        "name": "03  |  CIPHER SHAFT",
        "short": "CIPHER",
        "room": "The Signal Elevator",
        "color": PURPLE,
        "time": 350,
        "puzzles": [
            {
                "type": "decrypt", "tag": "CAESAR SHIFT", "difficulty": "STANDARD",
                "question": "The old access panel uses a Caesar cipher. Shift each letter BACK by 3 to reveal the phrase.",
                "cipher": "WKH NHB LV 4826", "answer": "THE KEY IS 4826", "shift": 3,
                "why": "A Caesar cipher is a simple letter-shift puzzle, not safe modern encryption. Real systems need strong, reviewed cryptography.",
                "hint": "For example, W shifted back by 3 becomes T. Numbers stay the same."
            },
            {
                "type": "decrypt", "tag": "CAESAR SHIFT", "difficulty": "ADVANCED",
                "question": "Shift every letter BACK by 3. Spaces and punctuation do not change.",
                "cipher": "YHULIB WKH GRPDLQ ILUVW", "answer": "VERIFY THE DOMAIN FIRST", "shift": 3,
                "why": "Before trusting a login or payment page, inspect the actual domain. A lock icon alone does not prove a site is legitimate.",
                "hint": "The first word means to check something carefully; Y shifted back by 3 becomes V."
            },
        ],
    },
    {
        "name": "04  |  PIN VAULT",
        "short": "PIN",
        "room": "The Keypad Corridor",
        "color": YELLOW,
        "time": 300,
        "puzzles": [
            {
                "type": "pin", "tag": "4-DIGIT PIN", "difficulty": "STANDARD",
                "question": "The vault keypad is dead. A technician left sticky notes about the 4-digit PIN. Work it out and key it in.",
                "pin": "5294",
                "clues": [
                    "Note 1: Digit 1 is the number of letters in the word PHISH.",
                    "Note 2: Digit 2 is the number of factors in two-factor authentication.",
                    "Note 3: The first three digits add up to 16.",
                    "Note 4: The last digit is double digit 2.",
                ],
                "why": "Two-factor authentication adds a second proof of identity. Never write a real PIN on a sticky note; anyone passing by can read it.",
                "hint": "Digit 1 is 5 and digit 2 is 2. Use the sum to find digit 3."
            },
            {
                "type": "pin", "tag": "4-DIGIT PIN", "difficulty": "CHALLENGING",
                "question": "A second keypad, a harder PIN. These notes only give rules, so use them to rule digits out. Wrong tries show how many tumblers line up.",
                "pin": "7413",
                "clues": [
                    "Note 1: All four digits are different and none is zero.",
                    "Note 2: The digits add up to 15.",
                    "Note 3: Digit 1 is the biggest digit of all.",
                    "Note 4: Digit 2 is the biggest of the last three digits.",
                    "Note 5: The last digit is odd and bigger than digit 3.",
                    "Note 6: Digit 1 minus digit 4 is exactly 4.",
                ],
                "why": "Attackers try patterns first (1234, 1111, birth years). A random PIN with no pattern is far harder to guess.",
                "hint": "Try digit 1 = 7. Digit 4 must then be 3."
            },
            {
                "type": "pin", "tag": "5-DIGIT PIN", "difficulty": "ADVANCED",
                "question": "The vault now wants a 5-digit PIN. Combine the clues with what the lock tells you after each wrong try.",
                "pin": "44385",
                "clues": [
                    "Note 1: Digits 1 and 2 are the same.",
                    "Note 2: Digits 1-3 add up to 11 and spell the port number of HTTPS, the secure web door.",
                    "Note 3: Digit 4 is the number of bits in one byte.",
                    "Note 4: Digit 5 is the number of letters in the word ADMIN.",
                    "Note 5: All five digits add up to 24.",
                ],
                "why": "Ports are numbered doors on a computer. HTTPS uses port 443 for encrypted browsing. Knowing common ports helps defenders spot strange traffic.",
                "hint": "HTTPS uses port 443, a byte has 8 bits, and ADMIN has 5 letters."
            },
            {
                "type": "pin", "tag": "6-DIGIT PIN", "difficulty": "EXPERT",
                "question": "The master lock needs a 6-digit PIN. Every digit depends on the one before it. Think in order.",
                "pin": "225380",
                "clues": [
                    "Note 1: Digits 1 and 2 are the same and together add up to 4.",
                    "Note 2: Digit 3 is the number of letters in MALWARE, minus 2.",
                    "Note 3: Digit 4 is digit 3 minus 2.",
                    "Note 4: Digits 5-6 form a two-digit number equal to 10 x (digit 4 + 5).",
                ],
                "why": "A 4-digit PIN has 10,000 combinations; a 6-digit PIN has 1,000,000. Longer codes are much harder to brute-force, but only if they are random.",
                "hint": "MALWARE has 7 letters, so digit 3 is 5. Then digit 4 is 3 and the last two digits are 80."
            },
        ],
    },
    {
        "name": "05  |  SEQUENCE TUNNEL",
        "short": "SEQUENCE",
        "room": "The Looping Hallway",
        "color": PINK,
        "time": 300,
        "puzzles": [
            {
                "type": "sequence", "tag": "FAILED LOGINS", "difficulty": "STANDARD",
                "question": "A server counts failed logins every minute. Watch the bars and find the next count.",
                "seq": [1, 2, 4, 8, 16], "answer": "32",
                "why": "Counts that double every minute point to an automated password-guessing bot. Account lockouts and rate limits slow bots down.",
                "hint": "Each number is multiplied by the same value."
            },
            {
                "type": "sequence", "tag": "ALERT SPREAD", "difficulty": "CHALLENGING",
                "question": "Malware alerts are spreading between computers. The pattern is not a simple multiplication. What comes next?",
                "seq": [1, 1, 2, 3, 5, 8], "answer": "13",
                "why": "Each number is the sum of the two before it. Spreading malware grows faster than people expect, so isolate an infected device early.",
                "hint": "Add the two numbers just before the missing one."
            },
            {
                "type": "sequence", "tag": "PORT SCAN GROWTH", "difficulty": "ADVANCED",
                "question": "A scanner probes more ports every round. Look at the gaps between the numbers, not the numbers themselves.",
                "seq": [3, 6, 11, 18, 27], "answer": "38",
                "why": "The gaps are 3, 5, 7, 9 and then 11. Attackers often start small and grow, so rising scan activity deserves attention early.",
                "hint": "The gaps between the numbers go up by 2 each time."
            },
            {
                "type": "sequence", "tag": "TWO SENSORS", "difficulty": "EXPERT",
                "question": "Two sensors send their readings mixed into one stream. Separate the odd places from the even places.",
                "seq": [5, 2, 10, 4, 20, 8, 40], "answer": "16",
                "why": "Odd places double (5, 10, 20, 40) while even places also double (2, 4, 8, 16). Real logs often mix several sources, so split them before judging.",
                "hint": "Read every second number as its own sequence."
            },
            {
                "type": "sequence", "tag": "BRUTE FORCE BOSS", "difficulty": "EXPERT",
                "question": "Final tunnel lock. The multiplier changes every step. How many tries come next?",
                "seq": [1, 2, 6, 24, 120], "answer": "720",
                "why": "The numbers are multiplied by 1, 2, 3, 4, 5 and now 6. This is how fast the ways to arrange characters explode, which is why password length matters most.",
                "hint": "Multiply by 2, then 3, then 4, then 5. What is next?"
            },
        ],
    },
    {
        "name": "06  |  LOG ANALYZER",
        "short": "LOGS",
        "room": "The Monitoring Room",
        "color": ORANGE,
        "time": 330,
        "puzzles": [
            {
                "type": "inspect", "tag": "LOGIN LOG", "difficulty": "STANDARD",
                "question": "The login log shows a night attack. Click a row to read its IP note, then flag every suspicious line.",
                "detail_label": "IP NOTE",
                "cols": ["TIME", "USER", "SOURCE IP", "RESULT"], "widths": [7, 8, 15, 9],
                "rows": [
                    (["02:11", "admin", "185.220.101.9", "FAILED"], "Unknown overseas address. Nobody should use the admin account at 2 AM."),
                    (["02:11", "admin", "185.220.101.9", "FAILED"], "Same overseas address, same second. A person cannot type this fast."),
                    (["02:12", "admin", "185.220.101.9", "FAILED"], "Third failure in a row from the same unknown address."),
                    (["02:12", "admin", "185.220.101.9", "SUCCESS"], "Success right after repeated failures from one address: the password was probably guessed."),
                    (["09:01", "anita", "10.0.4.21", "FAILED"], "Office laptop. One typo before a normal login is common."),
                    (["09:02", "anita", "10.0.4.21", "SUCCESS"], "Same office laptop, one minute later. Normal."),
                    (["09:15", "ravi", "10.0.4.35", "SUCCESS"], "Office desktop at the start of the working day. Normal."),
                    (["13:30", "meena", "10.0.4.50", "SUCCESS"], "Office network, normal working hours. Normal."),
                ],
                "sus": [0, 1, 2, 3],
                "why": "Many failures from one unknown address followed by a success is the classic sign of a password-guessing attack. A single typo is not.",
                "hint": "Look for repeated failures from the same strange address, then a success."
            },
            {
                "type": "inspect", "tag": "IMPOSSIBLE TRAVEL", "difficulty": "CHALLENGING",
                "question": "Meena's account looks busy. Check where each login comes from and flag the suspicious lines.",
                "detail_label": "ANALYST NOTE",
                "cols": ["TIME", "USER", "LOCATION", "ACTION"], "widths": [7, 8, 14, 18],
                "rows": [
                    (["03:05", "svc-backup", "Chennai, IN", "RUN BACKUP"], "Scheduled backup from the company server, runs every night. Normal."),
                    (["08:55", "meena", "Chennai, IN", "LOGIN"], "Office PC in Chennai. Normal."),
                    (["09:20", "meena", "Moscow, RU", "LOGIN"], "Only 25 minutes after the Chennai login. Nobody can travel that far that fast."),
                    (["09:22", "meena", "Moscow, RU", "EXPORT CONTACTS"], "Downloading the whole contact list right after a strange login."),
                    (["09:25", "meena", "Moscow, RU", "DISABLE 2-STEP"], "Turning off two-step sign-in is what attackers do to keep their access."),
                    (["10:05", "ravi", "Chennai, IN", "LOGIN"], "Office PC in Chennai. Normal."),
                    (["10:30", "ravi", "Bengaluru, IN", "LOGIN (PHONE)"], "Ravi's registered phone. His travel was approved this week. Normal."),
                    (["12:45", "anita", "Chennai, IN", "DOWNLOAD REPORT"], "Anita downloads her own monthly report from her office PC. Normal."),
                ],
                "sus": [2, 3, 4],
                "why": "Impossible travel, bulk exports and switched-off two-step sign-in together strongly suggest a stolen account. Report it and reset the password.",
                "hint": "One location cannot follow another 25 minutes later. Then see what happens next."
            },
            {
                "type": "inspect", "tag": "ACCOUNT ACTIVITY", "difficulty": "ADVANCED",
                "question": "Read the account events. Four lines belong to a takeover. Flag them without flagging the normal admin work.",
                "detail_label": "ANALYST NOTE",
                "cols": ["TIME", "USER", "EVENT", "FROM"], "widths": [7, 8, 24, 12],
                "rows": [
                    (["01:50", "meena", "PASSWORD RESET ASKED", "New device"], "Meena is on leave and the device has never been seen before."),
                    (["01:52", "meena", "RECOVERY EMAIL CHANGED", "New device"], "Changing the recovery email lets the attacker take the account permanently."),
                    (["01:53", "meena", "2-STEP TURNED OFF", "New device"], "Security protection removed minutes after the reset."),
                    (["01:55", "meena", "MAIL FORWARD TO OUTSIDE", "New device"], "A rule that silently copies all her mail to an outside address."),
                    (["09:10", "ravi", "PASSWORD CHANGED", "Office PC"], "Ravi changed his own password from his usual office PC. Normal."),
                    (["11:20", "anita", "2-STEP TURNED ON", "Office PC"], "Adding protection from a known device. Good habit. Normal."),
                    (["15:00", "it-admin", "PASSWORD POLICY UPDATED", "Admin console"], "Planned change recorded in the IT ticket system. Normal."),
                    (["16:40", "ravi", "LOGIN FAILED x1", "Office PC"], "A single failed login from a known device. Normal."),
                ],
                "sus": [0, 1, 2, 3],
                "why": "A new device, a changed recovery email, switched-off 2-step sign-in and silent forwarding are the standard steps of an account takeover.",
                "hint": "Four lines in a row from the same new device in the middle of the night."
            },
            {
                "type": "inspect", "tag": "NETWORK TRAFFIC", "difficulty": "EXPERT",
                "question": "The firewall noticed something at 2 AM. Compare data sizes and destinations. Not every large transfer is an attack.",
                "detail_label": "ANALYST NOTE",
                "cols": ["TIME", "DEVICE", "DESTINATION", "DATA"], "widths": [7, 10, 22, 11],
                "rows": [
                    (["02:14", "SRV-DB", "198.51.100.77", "2.4 GB OUT"], "The customer database server sending 2.4 GB to an address nobody knows."),
                    (["02:16", "SRV-DB", "x7f9q2.cdn-top.xyz", "600 MB OUT"], "A random-looking domain receiving company data. Common data-theft trick."),
                    (["02:20", "PC-RAVI", "10.0.4.1 - 10.0.4.254", "254 PROBES"], "One PC checking every address on the network. That is a scan, not normal work."),
                    (["03:00", "SRV-BKP", "backup.company.in", "1.1 GB OUT"], "Big transfer, but a scheduled backup to the known company backup server. Normal."),
                    (["09:10", "PC-RAVI", "windowsupdate.microsoft.com", "45 MB IN"], "Official operating-system update. Normal."),
                    (["10:30", "PC-ANITA", "mail.company.in", "2 MB OUT"], "Normal company email traffic."),
                    (["12:00", "PC-MEENA", "zoom.us", "120 MB IN"], "A video call during working hours. Normal."),
                    (["14:30", "PC-ANITA", "github.com", "15 MB IN"], "A developer downloading code from a well-known site. Normal."),
                ],
                "sus": [0, 1, 2],
                "why": "Look at who sends data, to where and when. Big transfers to unknown places at night and network scans are red flags; scheduled backups to known servers are not.",
                "hint": "Compare each destination: is it a place the company knows and expects?"
            },
        ],
    },
    {
        "name": "07  |  EVIDENCE INSPECTOR",
        "short": "EVIDENCE",
        "room": "The Forensics Closet",
        "color": RED,
        "time": 330,
        "puzzles": [
            {
                "type": "inspect", "tag": "DOWNLOADS FOLDER", "difficulty": "STANDARD",
                "question": "Open the suspect's Downloads folder. Preview each file and flag the dangerous ones.",
                "detail_label": "FILE PREVIEW",
                "cols": ["FILE NAME", "SIZE", "TYPE"], "widths": [26, 8, 14],
                "rows": [
                    (["holiday_photo.jpg", "2.1 MB", "JPEG image"], "A normal photo. Opens in the image viewer."),
                    (["invoice_october.pdf.exe", "340 KB", "Application"], "Double extension. It looks like a PDF but is really a program that runs when opened."),
                    (["lecture_notes.txt", "4 KB", "Text file"], "Plain text notes. Safe."),
                    (["salary_update.docm", "88 KB", "Word macro"], "Arrived by email from an unknown sender. It asks you to Enable Content to see the salary."),
                    (["resume_ravi.pdf", "210 KB", "PDF"], "A normal PDF resume from a known student. Safe."),
                    (["free_game_crack.scr", "1.2 MB", "Screen saver"], ".scr files are programs in disguise. Cracked games often carry malware."),
                    (["budget.xlsx", "54 KB", "Excel sheet"], "Plain spreadsheet with numbers, no macros. Safe."),
                    (["report_final.docx", "120 KB", "Word file"], "A normal Word report without macros. Safe."),
                ],
                "sus": [1, 3, 5],
                "why": "Double extensions, macro documents from strangers and .scr files are classic malware disguises. Always check the real file type.",
                "hint": "Look for files that are really programs or ask you to enable something."
            },
            {
                "type": "inspect", "tag": "BREACH TIMELINE", "difficulty": "CHALLENGING",
                "question": "The breach happened between 02:10 and 02:30. Flag every file that was touched by the intruder inside that window.",
                "detail_label": "FILE PREVIEW",
                "cols": ["FILE", "BY", "MODIFIED"], "widths": [20, 12, 10],
                "rows": [
                    (["payroll.xlsx", "hr_team", "02:05"], "Scheduled payroll job. Finished before the breach window began."),
                    (["customers.db", "tmp_user", "02:14"], "Copied by tmp_user, an account created at 02:09 tonight. Inside the window."),
                    (["export_dump.zip", "tmp_user", "02:21"], "A new archive made by the same fresh account. Inside the window."),
                    (["clear_logs.bat", "tmp_user", "02:27"], "A script that wipes the event log, made by the same account. Inside the window."),
                    (["app.config", "dev_team", "02:55"], "Edited by a developer on night shift, approved in ticket 4471. After the window."),
                    (["backup_nightly.zip", "svc_backup", "01:30"], "Normal nightly backup. Before the window."),
                    (["policy.pdf", "hr_team", "11:02"], "HR updated a policy during the day. Normal."),
                    (["readme.txt", "admin", "09:15"], "Admin note from yesterday morning. Normal."),
                ],
                "sus": [1, 2, 3],
                "why": "Investigators build a timeline. Files changed inside the breach window by an unknown new account are the key evidence; ordinary work outside the window is not.",
                "hint": "Only 02:10 to 02:30 counts, and look at the account that appears three times."
            },
            {
                "type": "inspect", "tag": "USB DRIVE", "difficulty": "ADVANCED",
                "question": "A found USB stick was plugged into the office. Inspect its root folder and flag the items that can attack a computer.",
                "detail_label": "FILE PREVIEW",
                "cols": ["ITEM", "SIZE", "ATTRIBUTES"], "widths": [20, 8, 16],
                "rows": [
                    (["lecture_notes.pdf", "1.8 MB", "Normal"], "A normal PDF. Safe."),
                    (["autorun.inf", "1 KB", "Hidden"], "Tells Windows to run a program the moment the drive is plugged in."),
                    (["Photos.lnk", "1 KB", "Shortcut"], "A shortcut dressed as a folder. It silently runs a hidden command instead of opening photos."),
                    (["assignment1.docx", "96 KB", "Normal"], "A normal Word file. Safe."),
                    (["svchost.exe", "480 KB", "Application"], "A real system file never lives on a USB stick. This is a program using a trusted name."),
                    (["project_backup.zip", "14 MB", "Normal"], "A normal archive of project files. Safe."),
                    (["cat.png", "300 KB", "Normal"], "A normal image. Safe."),
                    (["thesis_draft.docx", "210 KB", "Normal"], "A normal Word file. Safe."),
                ],
                "sus": [1, 2, 4],
                "why": "Unknown USB sticks can run hidden programs. Never plug one in; give it to IT. Autorun files, fake folder shortcuts and look-alike system programs are the usual tricks.",
                "hint": "Three items are programs or scripts pretending to be something else."
            },
            {
                "type": "inspect", "tag": "RANSOMWARE SCENE", "difficulty": "EXPERT",
                "question": "A computer was locked by ransomware. Flag the four files an investigator must preserve to prove how it happened. Some programs here are innocent.",
                "detail_label": "FILE PREVIEW",
                "cols": ["FILE", "TIME", "SIZE"], "widths": [24, 8, 9],
                "rows": [
                    (["invoice.zip", "09:40", "98 KB"], "Downloaded from an email attachment at 09:40. This is how the attack started."),
                    (["locker_update.exe", "09:41", "640 KB"], "Created one minute after invoice.zip was opened. This is the ransomware program."),
                    (["READ_ME_TO_RESTORE.txt", "09:48", "2 KB"], "The ransom note demanding payment in cryptocurrency."),
                    (["security_log.evtx", "09:50", "4 MB"], "The system record of everything that ran between 09:40 and 09:50."),
                    (["windows_update.exe", "02:00", "52 MB"], "Digitally signed by Microsoft and installed at the planned update time. Innocent."),
                    (["chrome_setup.exe", "Mon 11:20", "1.4 MB"], "Signed installer downloaded from the official site last week. Innocent."),
                    (["cat_meme.png", "Sun 20:15", "300 KB"], "A harmless image saved on the weekend. Not related."),
                    (["notes.txt", "Fri 16:05", "3 KB"], "Normal study notes from last week. Not related."),
                ],
                "sus": [0, 1, 2, 3],
                "why": "Evidence is anything that shows how an attack started, what it did and when. Do not delete or open it; preserve it and give it to the security team.",
                "hint": "Follow the minutes: the email file, the program it created, the note it left and the log that recorded it."
            },
        ],
    },
    {
        "name": "08  |  SUSPECT LINEUP",
        "short": "SUSPECT",
        "room": "The Interrogation Room",
        "color": CYAN,
        "time": 330,
        "puzzles": [
            {
                "type": "suspect", "tag": "THE MIDNIGHT LOGIN", "difficulty": "STANDARD",
                "question": "Three people could have changed the admin password. Compare their profiles with the incident report and accuse the attacker.",
                "incident": [
                    "The admin password was changed at 02:14 AM.",
                    "The change came from a computer INSIDE the office network.",
                    "A USB stick was plugged into that computer at 02:12 AM.",
                ],
                "suspects": [
                    {"name": "RAVI", "role": "Intern",
                     "facts": ["Badge: left at 17:30", "Network at 02:14: home Wi-Fi", "Devices: personal phone only"],
                     "alibi": "I finished work and slept at home."},
                    {"name": "MEENA", "role": "Night-shift sysadmin",
                     "facts": ["Badge: entered at 01:45", "Network at 02:14: office LAN", "Devices: USB drive plugged in at 02:12"],
                     "alibi": "I was just checking the backups."},
                    {"name": "ARJUN", "role": "Former contractor",
                     "facts": ["Badge: no entry for 3 weeks", "Network at 02:14: VPN from another city", "Devices: own laptop"],
                     "alibi": "My contract ended, I have no reason to log in."},
                ],
                "answer": 1,
                "why": "Insider threats are real: a trusted person with access and a USB stick can do serious damage. Logs, badges and device records reveal who was where.",
                "hint": "Only one profile is inside the office network with a USB stick at 02:12."
            },
            {
                "type": "suspect", "tag": "THE VPN GHOST", "difficulty": "ADVANCED",
                "question": "Customer files were stolen through the VPN. Match the profiles with the evidence and check each VPN account carefully.",
                "incident": [
                    "The attacker entered through the VPN at 22:40.",
                    "The VPN account used was already DISABLED, but never deleted.",
                    "The attacker searched for the folders 'client list' and 'salaries'.",
                ],
                "suspects": [
                    {"name": "DIVYA", "role": "Finance analyst",
                     "facts": ["VPN account: active", "Last login: today 10:15 from the office", "Works with salary files daily"],
                     "alibi": "Of course I open salary files, that is my job."},
                    {"name": "KARTHIK", "role": "Left the company last week",
                     "facts": ["VPN account: disabled, not deleted", "Searches at 22:40: 'client list', 'salaries'", "Angry exit interview"],
                     "alibi": "I have not touched that company since leaving."},
                    {"name": "SANJAY", "role": "Sales manager",
                     "facts": ["VPN account: active", "At 22:40: on a recorded client call", "Reads the client list daily"],
                     "alibi": "I was on a late call with a client."},
                ],
                "answer": 1,
                "why": "Accounts of people who leave must be deleted, not just disabled. Forgotten accounts are a favourite way in for attackers.",
                "hint": "Which profile has the disabled VPN account and the exact searches from the report?"
            },
            {
                "type": "suspect", "tag": "THE FRIENDLY INSIDER", "difficulty": "EXPERT",
                "question": "Ransomware started on the finance server. Read the alibis carefully: a profile can say one thing while the logs say another.",
                "incident": [
                    "Ransomware was launched at 03:05 AM from the finance server.",
                    "The attacker knew the admin password.",
                    "A laptop NOT on the company device list joined the office Wi-Fi at 03:02 AM.",
                    "The security camera logs were deleted at 03:20 AM using the admin account.",
                ],
                "suspects": [
                    {"name": "NISHA", "role": "Finance manager",
                     "facts": ["Angry about her bonus", "Company laptop only", "On a recorded client call 02:50-03:30"],
                     "alibi": "I was on a long call with a client."},
                    {"name": "IMRAN", "role": "IT helper",
                     "facts": ["Knows the admin password", "Owns a personal laptop (not on the list)", "Office Wi-Fi shows a personal laptop at 03:02"],
                     "alibi": "I was asleep at home all night."},
                    {"name": "FAIZAL", "role": "Night security guard",
                     "facts": ["Has the camera room key", "No admin password", "Company phone, no laptop"],
                     "alibi": "I was walking my usual rounds."},
                ],
                "answer": 1,
                "why": "Alibis must be checked against logs. The person who looks angriest is not always guilty; the one who has the access, the device and a false alibi is.",
                "hint": "Compare each alibi with the Wi-Fi log and the admin password."
            },
        ],
    },
    {
        "name": "09  |  FINAL MISSION",
        "short": "FINAL",
        "room": "The Backrooms Core",
        "color": GREEN,
        "time": 480,
        "puzzles": [
            {
                "type": "maze", "tag": "BACKROOMS MAZE", "difficulty": "FINAL BOSS",
                "question": "The lights are failing. Walk the maze with the arrow keys or WASD, wake the 4 terminals (T1-T4), avoid the red virus, then reach the EXIT.",
                "terminals": [
                    {"word": "THINK", "q": "A text says your account will be locked in 10 minutes unless you click now. What is the best move?",
                     "options": ["Click fast before it locks", "Pause and open the official app yourself", "Reply with your PIN to be safe"], "answer": 1},
                    {"word": "BEFORE", "q": "Which password is the strongest?",
                     "options": ["Chennai123", "P@ssword", "river-lamp-cloud-orbit-7"], "answer": 2},
                    {"word": "YOU", "q": "A caller asks you to read out the one-time code that was just texted to you. What do you do?",
                     "options": ["Read it if they know your name", "Read it to a bank agent only", "Never share it with anyone"], "answer": 2},
                    {"word": "CLICK", "q": "Which habit helps the most against ransomware?",
                     "options": ["Offline backups and regular updates", "Turning off updates", "Using one password everywhere"], "answer": 0},
                ],
                "why": "You faced the virus the way defenders do: stay calm, answer carefully and keep moving. Every terminal was a real habit that protects you online.",
                "hint": "Terminals are only visible when close. The virus is slower than you; use corners to lose it."
            },
            {
                "type": "phrase", "tag": "FINAL PASSPHRASE", "difficulty": "FINAL BOSS",
                "question": "The exit door wants the passphrase made from the four key words you collected. Click the words in the right order.",
                "words": ["THINK", "BEFORE", "YOU", "CLICK"], "answer": "THINK BEFORE YOU CLICK",
                "why": "The best security tool you have is the pause before the click. Slow down, verify, then act.",
                "hint": "Read the words as a short safety rule that begins with THINK."
            },
        ],
    },
]

ADDITIONAL_PUZZLES = [
    [],
    [
        {"type": "jumble", "tag": "SPOT THE TRICK", "difficulty": "ADVANCED",
         "question": "Unscramble the word for a fake message that tries to steal your password or bank details.",
         "scramble": "HPIISHNG", "answer": "PHISHING",
         "why": "Phishing messages pretend to be from a real person or company. Check the sender before clicking or replying.",
         "hint": "It starts with PH and has eight letters."},
        {"type": "jumble", "tag": "NAME THE ATTACK", "difficulty": "EXPERT",
         "question": "Unscramble the attack that can lock your files and demand money to unlock them.",
         "scramble": "NWRAMOSERA", "answer": "RANSOMWARE",
         "why": "Ransomware can lock important files. Keep a separate backup and report a suspected infection.",
         "hint": "It ends with WARE and begins with RAN."},
    ],
    [
        {"type": "decrypt", "tag": "CAESAR SHIFT", "difficulty": "ADVANCED",
         "question": "Move every letter BACK by 3 to read the safety reminder.",
         "cipher": "RSHQ WKH RIILFLDO DSS", "answer": "OPEN THE OFFICIAL APP", "shift": 3,
         "why": "Open a service's app yourself instead of following an unexpected sign-in link.",
         "hint": "R shifted back by 3 becomes O."},
        {"type": "decrypt", "tag": "CAESAR SHIFT", "difficulty": "EXPERT",
         "question": "Move each letter BACK by 5. Spaces do not move.",
         "cipher": "IT STY YWZXY F QTHP NHTS", "answer": "DO NOT TRUST A LOCK ICON", "shift": 5,
         "why": "A lock icon protects the connection; it does not prove a website is honest. Check the address too.",
         "hint": "I shifted back by 5 becomes D."},
    ],
]

for sector_index, extra_puzzles in enumerate(ADDITIONAL_PUZZLES):
    if extra_puzzles:
        SECTORS[sector_index]["puzzles"][1]["difficulty"] = "CHALLENGING"
        SECTORS[sector_index]["puzzles"].extend(extra_puzzles)

TOTAL_PUZZLES = sum(len(sector["puzzles"]) for sector in SECTORS)


def load_scores():
    """Read saved leaderboard entries; a missing or damaged file starts empty."""
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (OSError, ValueError, TypeError):
        return []


def save_score(entry):
    """Append a score and keep the ten highest entries."""
    scores = load_scores()
    scores.append(entry)
    scores.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    scores = scores[:10]
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as file:
            json.dump(scores, file, indent=2)
    except OSError:
        pass
    return scores


def clean_answer(value):
    """Compare typed puzzle answers while ignoring spaces and punctuation."""
    return "".join(character for character in value.upper() if character.isalnum())


def rank_for(score, escaped):
    if escaped and score >= 300:
        return "ARCHIVE LEGEND"
    if escaped:
        return "GHOST IN THE MACHINE"
    if score >= 100:
        return "SIGNAL HUNTER"
    return "NEW ARRIVAL"


def _registrable_domain(host):
    """Return a simple display domain without pretending to parse every public suffix."""
    host = (host or "").strip(".").lower()
    labels = [part for part in host.split(".") if part]
    if len(labels) < 2:
        return host
    if len(labels) >= 3 and labels[-1] in {"uk", "in", "au", "nz", "jp", "br", "za"}:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def _risk_band(score):
    """Turn the warning-sign count into a short, plain-language label."""
    if score >= 65:
        return "MANY WARNING SIGNS", RED
    if score >= 35:
        return "PAUSE AND CHECK", ORANGE
    if score >= 12:
        return "A FEW WARNING SIGNS", YELLOW
    return "FEW SIGNS FOUND", GREEN


def analyze_url_offline(value):
    """Inspect URL structure with local heuristics; never makes a network request."""
    raw = value.strip()
    findings = []
    score = 0
    if not raw:
        return {"score": 0, "findings": ["Enter a URL to inspect its visible structure."],
                "host": "—", "domain": "—", "scheme": "—", "band": "NO INPUT"}

    candidate = raw
    if candidate.lower().startswith(("hxxp://", "hxxps://")):
        candidate = candidate.replace("hxxps://", "https://", 1).replace("hxxp://", "http://", 1)
        findings.append("This example uses 'hxxp' so it is less likely to be opened by mistake.")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = "https://" + candidate
        findings.append("No web prefix was entered, so the checker added one just to read the address.")
    try:
        parts = urlsplit(candidate)
        host = (parts.hostname or "").lower().rstrip(".")
        scheme = parts.scheme.lower() or "unknown"
        port = parts.port
        username = parts.username
        password = parts.password
    except ValueError:
        return {"score": 100, "findings": ["URL could not be safely parsed; check malformed brackets or port."],
                "host": "unparsed", "domain": "unparsed", "scheme": "unknown", "band": "MALFORMED INPUT"}

    if not host:
        return {"score": 100, "findings": findings + ["No valid hostname could be extracted."],
                "host": "missing", "domain": "missing", "scheme": scheme, "band": "MALFORMED INPUT"}

    if scheme == "http":
        score += 14
        findings.append("This link does not use a secure connection. That is a warning sign, but it does not prove a scam.")
    else:
        findings.append(f"The link starts with {scheme.upper()}. A secure connection still does not prove the site is real.")
    if username or password or "@" in parts.netloc:
        score += 30
        findings.append("There is an @ sign before the site name. It can make a link's real destination harder to spot.")

    try:
        address = ipaddress.ip_address(host.strip("[]"))
        if address.is_global or address.is_private or address.is_loopback:
            score += 22
            findings.append("This link uses a number address instead of a regular website name. Check it before opening.")
    except ValueError:
        if host.startswith("xn--") or ".xn--" in host:
            score += 22
            findings.append("The website name uses encoded letters that can look like another site's spelling.")
        elif any(ord(character) > 127 for character in host):
            try:
                normalized_host = unicodedata.normalize("NFKC", host)
                ascii_host = normalized_host.encode("idna").decode("ascii")
                if "xn--" in ascii_host:
                    score += 22
                    findings.append("The website name uses special letters that can look like familiar letters. Check it carefully.")
            except (UnicodeError, ValueError):
                score += 12
                findings.append("The website name contains unusual characters. Check its spelling carefully.")

    if host.count("-") >= 3:
        score += 8
        findings.append("The website name has several hyphens. Check that it is spelled the way you expect.")
    if len(host) > 55:
        score += 10
        findings.append("The website name is unusually long. Read it slowly and check the ending.")
    if port not in (None, 80, 443):
        score += 8
        findings.append(f"This link has an unusual number after the site name ({port}). Check whether you expected it.")

    domain = _registrable_domain(host)
    subdomain_labels = host.split(".")[:-2]
    if len(subdomain_labels) >= 2:
        score += min(10, 3 * len(subdomain_labels))
        findings.append("There are several parts before the main site name. Read the whole address carefully.")

    combined = (host + " " + parts.path + " " + parts.query).lower()
    matched_words = sorted(word for word in RISK_WORDS if word in combined)
    if matched_words:
        score += min(16, 4 * len(matched_words))
        findings.append("The link contains words often used to rush people: " + ", ".join(matched_words) + ".")

    if domain in SHORTENER_DOMAINS:
        score += 14
        findings.append("This is a shortened link, so it hides the page it will open. Check with the sender first.")

    root = host.split(".")[0]
    for brand, official_domains in BRAND_DOMAINS.items():
        if brand == "bank":
            continue
        mentions_brand = brand in host
        is_official = any(host == good or host.endswith("." + good) for good in official_domains)
        if mentions_brand and not is_official:
            score += 28
            findings.append(f"The website name includes {brand.title()}, but does not match its usual official address.")
            break
        # Catch obvious transpositions such as paypa1 or amaz0n without a network lookup.
        simplified = root.replace("0", "o").replace("1", "l").replace("3", "e")
        if not is_official and brand in simplified and root != brand:
            score += 18
            findings.append(f"The website name looks a little like {brand.title()}. Check every letter before using it.")
            break

    if len(findings) <= 2:
        findings.append("No obvious warning was found. This check cannot prove that a site is safe.")
    score = max(0, min(100, score))
    band, _color = _risk_band(score)
    return {"score": score, "findings": findings, "host": host, "domain": domain,
            "scheme": scheme, "band": band, "path": parts.path or "/"}


def analyze_message_offline(text):
    """Flag common social-engineering language without sending text anywhere."""
    body = text.lower()
    findings = []
    score = 0
    checks = [
        (r"\b(urgent|immediately|act now|within \d+ minutes|expires today)\b", 16,
         "It uses urgent words or a short deadline. Scammers may be trying to rush you."),
        (r"\b(otp|one[- ]time password|verification code|security code)\b", 18,
         "It asks for a one-time code (OTP). Never send that code to anyone."),
        (r"\b(password|pin|passcode|card number|cvv|bank details)\b", 20,
         "It asks for private account or bank details. Do not reply with them."),
        (r"\b(gift card|crypto|wire transfer|urgent payment|buy .* cards)\b", 18,
         "It asks for an unusual payment or gift cards. Check with the person or company first."),
        (r"\b(account (will be|has been) (blocked|closed|suspended|deleted))\b", 14,
         "It threatens to close your account. This may be a trick to make you act quickly."),
        (r"\b(keep this secret|don't tell anyone|do not tell anyone|confidential)\b", 12,
         "It tells you to keep the request secret. Ask someone you trust before acting."),
        (r"\b(click here|tap here|verify your account|confirm your details)\b", 10,
         "It asks you to click a link. Open the official app yourself instead."),
        (r"\b(attachment|download the file|enable macros|invoice\.\w+)\b", 10,
         "It mentions an unexpected file. Check with the sender before opening it."),
        (r"\b(ceo|director|payroll|it support|help desk)\b", 4,
         "It claims to come from a boss or support team. Check using a contact method you already know."),
        (r"https?://|www\.", 6,
         "A web link is included. Read its address carefully before opening it."),
    ]
    for pattern, weight, note in checks:
        if re.search(pattern, body, flags=re.IGNORECASE):
            score += weight
            findings.append(note)
    if not findings:
        findings.append("No listed phrase pattern was detected. A clean result does not prove the message is safe.")
    score = min(score, 100)
    band, _color = _risk_band(score)
    return {"score": score, "findings": findings, "band": band,
            "next_step": "Check the request using a number or app you already trust. Do not use contact details from the message."}


def analyze_password_offline(secret):
    """Estimate visible password qualities and return no copy of the secret."""
    if not secret:
        return {"score": 0, "label": "NO PASSWORD", "findings": ["Type a sample to inspect it locally."],
                "length": 0}
    findings = []
    score = min(45, len(secret) * 3)
    groups = [
        (any(ch.islower() for ch in secret), "It has lowercase letters."),
        (any(ch.isupper() for ch in secret), "It has capital letters."),
        (any(ch.isdigit() for ch in secret), "It has numbers."),
        (any(not ch.isalnum() for ch in secret), "It has symbols or spaces."),
    ]
    for present, note in groups:
        if present:
            score += 8
            findings.append(note)
    lower = secret.lower()
    common = {"password", "password123", "qwerty", "letmein", "admin", "welcome", "iloveyou"}
    if lower in common:
        score = min(score, 8)
        findings.append("This is a very common example password; avoid it entirely.")
    if re.search(r"(.)\1{3,}", lower):
        score -= 12
        findings.append("Several characters repeat in a row. That makes a guess easier." )
    if lower in string.ascii_lowercase or lower in string.digits:
        score -= 18
        findings.append("It uses a simple sequence. A longer, less predictable phrase is safer.")
    if len(secret) < 12:
        findings.append("Try a longer phrase that you do not use on any other account.")
    if not any(present for present, _note in groups):
        findings.append("Try a longer phrase with different kinds of characters.")
    score = max(0, min(100, score))
    label = "GOOD SAMPLE" if score >= 70 else ("OK SAMPLE" if score >= 42 else "WEAK SAMPLE")
    return {"score": score, "label": label, "findings": findings, "length": len(secret)}


def analyze_filename_offline(filename):
    """Inspect filename endings and double extensions without opening a file."""
    clean = os.path.basename(filename.strip().replace("\\", "/"))
    lowered = clean.lower()
    findings = []
    score = 0
    pieces = lowered.split(".")
    extension = "." + pieces[-1] if len(pieces) > 1 else "(no extension)"
    if extension in SUSPICIOUS_EXTENSIONS:
        score += 55
        findings.append(f"Files ending in {extension} can run programs. Do not open one you were not expecting.")
    if len(pieces) >= 3:
        earlier = "." + pieces[-2]
        if earlier in {".pdf", ".doc", ".docx", ".jpg", ".png", ".txt", ".xlsx"} and extension in SUSPICIOUS_EXTENSIONS:
            score += 35
            findings.append(f"This name has two endings ({earlier}{extension}). The last ending tells the computer what kind of file it is.")
    if extension in {".docm", ".xlsm", ".pptm", ".xll"}:
        score += 22
        findings.append("This office file can contain instructions that run when opened. Be careful with unexpected files.")
    if not findings:
        findings.append("No familiar risky ending was found. A file name can be changed, so this does not prove the file is safe.")
    score = min(score, 100)
    band, _color = _risk_band(score)
    return {"filename": clean or "(empty)", "extension": extension,
            "score": score, "findings": findings, "band": band}


class NeonButton(tk.Frame):
    """Original-style neon frame button with a bright hover flash."""

    def __init__(self, parent, text, command, color=GREEN, width=22,
                 font=(FONT, 11, "bold"), wraplength=460, anchor="center",
                 justify="center", padx=10, pady=9):
        super().__init__(parent, bg=color, padx=2, pady=2)
        self.color, self.command, self.enabled = color, command, True
        self.rest_bg = self._shade(color)
        self.rest_fg = color
        self.label = tk.Label(self, text=text, font=font, fg=color, bg=self.rest_bg,
                              width=width, wraplength=wraplength, anchor=anchor,
                              justify=justify, padx=padx, pady=pady, cursor="hand2")
        self.label.pack(fill="x")
        for widget in (self, self.label):
            widget.bind("<Enter>", self._enter)
            widget.bind("<Leave>", self._leave)
            widget.bind("<Button-1>", self._click)

    @staticmethod
    def _shade(color):
        try:
            channels = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
            return "#" + "".join(f"{int(value * .16):02x}" for value in channels)
        except (ValueError, TypeError):
            return PANEL_LIGHT

    def _enter(self, _event=None):
        if self.enabled:
            self.label.configure(bg=self.color, fg=BG)

    def _leave(self, _event=None):
        self._paint()

    def _paint(self):
        tk.Frame.configure(self, bg=self.color)
        self.label.configure(bg=self.rest_bg if self.enabled else PANEL,
                             fg=self.rest_fg,
                             cursor="hand2" if self.enabled else "arrow")

    def _click(self, _event=None):
        if self.enabled and self.command:
            self.command()

    def configure(self, cnf=None, **kwargs):
        """Accept familiar Tk button options while styling the inner label."""
        options = dict(cnf) if isinstance(cnf, dict) else {}
        options.update(kwargs)
        state = options.pop("state", None)
        if state is not None:
            self.enabled = state != "disabled"
            if not self.enabled and "fg" not in options:
                self.color = MUTED
                self.rest_fg = MUTED
        if "fg" in options:
            self.rest_fg = options.pop("fg")
            if state == "disabled":
                self.color = self.rest_fg
        if "bg" in options:
            self.rest_bg = options.pop("bg")
        if "text" in options:
            self.label.configure(text=options.pop("text"))
        for ignored in ("highlightthickness", "highlightbackground", "highlightcolor",
                        "borderwidth", "bd", "activebackground", "activeforeground"):
            options.pop(ignored, None)
        if options:
            self.label.configure(**options)
        self._paint()

    config = configure

    def cget(self, key):
        if key == "state":
            return "normal" if self.enabled else "disabled"
        return self.label.cget(key)

    def lock(self, color=MUTED):
        self.enabled, self.color, self.rest_fg = False, color, color
        self._paint()

    def unlock(self, color):
        self.enabled, self.color, self.rest_fg = True, color, color
        self._paint()

    def set_text(self, text):
        self.label.configure(text=text)


class Terminal(tk.Text):
    """Small colour-coded terminal with non-blocking type and scan effects."""

    def __init__(self, parent, size=9, **options):
        super().__init__(parent, bg="#02060a", fg=GREEN, font=(FONT, size),
                         wrap="word", relief="flat", bd=0, padx=10, pady=8,
                         state="disabled", cursor="arrow", highlightthickness=2,
                         highlightbackground=GREEN, **options)
        for tag, color in (("ok", GREEN), ("info", CYAN), ("warn", YELLOW),
                           ("error", RED), ("lesson", PURPLE), ("pink", PINK),
                           ("dim", MUTED)):
            self.tag_configure(tag, foreground=color)
        self.queue, self.busy = deque(), False

    def say(self, text, tag="ok", speed=7, prefix="> "):
        self.queue.append(("say", prefix + str(text) + "\n", tag, speed))
        self._next()

    def scan(self, text, tag="info"):
        self.queue.append(("scan", str(text), tag))
        self._next()

    def _next(self):
        if self.busy or not self.queue:
            return
        self.busy = True
        item = self.queue.popleft()
        if item[0] == "say":
            self._type(item[1], item[2], item[3], 0)
        elif item[0] == "scan":
            self._scan(item[1], item[2], 0)
        else:
            self.busy = False
            item[1]()
            self._next()

    def _type(self, text, tag, speed, position):
        try:
            if position < len(text):
                self.configure(state="normal")
                self.insert("end-1c", text[position:position + 2], tag)
                self.see("end")
                self.configure(state="disabled")
                self.after(speed, self._type, text, tag, speed, position + 2)
            else:
                self.busy = False
                self._next()
        except tk.TclError:
            self.busy = False

    def _scan(self, message, tag, step, total=14):
        try:
            self.configure(state="normal")
            if step == 0:
                self.mark_set("scan", "end-1c")
                self.mark_gravity("scan", "left")
            self.delete("scan", "end-1c")
            bar = "#" * step + "." * (total - step)
            self.insert("end-1c", f"> {message} [{bar}] {step * 100 // total:3d}%", tag)
            self.see("end")
            self.configure(state="disabled")
            if step >= total:
                self.configure(state="normal")
                self.insert("end-1c", "\n")
                self.configure(state="disabled")
                self.busy = False
                self._next()
            else:
                self.after(42, self._scan, message, tag, step + 1, total)
        except tk.TclError:
            self.busy = False


class MatrixRain:
    """The original falling-letter effect: vertical green character trails only."""

    CHARS = string.ascii_uppercase + string.digits
    SHADES = ["#d6ffee", "#00ff9c", "#00dd88", "#00bb77", "#009966",
              "#007755", "#005544", "#003a2e", "#00251d", "#00130f"]

    def __init__(self, canvas):
        self.canvas, self.alive, self.columns = canvas, True, []
        self.height = HEIGHT
        self.canvas.bind("<Configure>", self.on_resize, add="+")
        self.on_resize(None)
        self.tick()

    def on_resize(self, event):
        if not self.alive:
            return
        width = max(getattr(event, "width", 0) if event else 0,
                    self.canvas.winfo_width(), WIDTH)
        self.height = max(getattr(event, "height", 0) if event else 0,
                          self.canvas.winfo_height(), HEIGHT)
        while len(self.columns) < width // 18:
            index = len(self.columns)
            x = index * 18 + 9
            y = random.randint(0, self.height)
            trail = deque()
            for offset in range(random.randint(4, len(self.SHADES))):
                glyph_y = y - offset * 16
                if glyph_y < 0:
                    break
                item = self.canvas.create_text(x, glyph_y, text=random.choice(self.CHARS),
                    font=(FONT, 11, "bold"), fill=self.SHADES[min(offset, len(self.SHADES)-1)],
                    tags="rain")
                trail.appendleft(item)
            self.columns.append({"x": x, "y": y, "trail": trail})

    def stop(self):
        self.alive = False

    def tick(self):
        if not self.alive:
            return
        try:
            for column in self.columns:
                trail, y = column["trail"], column["y"]
                if y > self.height:
                    if trail:
                        self.canvas.delete(trail.pop())
                    elif random.random() < .08:
                        column["y"] = 0
                    continue
                if y >= 0:
                    item = self.canvas.create_text(column["x"], y,
                        text=random.choice(self.CHARS), font=(FONT, 11, "bold"),
                        fill=self.SHADES[0], tags="rain")
                    trail.appendleft(item)
                    for index, glyph in enumerate(trail):
                        self.canvas.itemconfigure(glyph, fill=self.SHADES[min(index, len(self.SHADES)-1)])
                    if len(trail) > len(self.SHADES):
                        self.canvas.delete(trail.pop())
                column["y"] += 16
            self.canvas.tag_lower("rain")
            self.canvas.after(75, self.tick)
        except tk.TclError:
            self.alive = False


class CyberEscapeRoom(tk.Tk):
    """Main application window and game controller."""

    def __init__(self):
        super().__init__()
        self.title("THE CYBER ESCAPEROOM  ||  CYBER INTELLIGENT PROTOCOL")
        width, height = 1120, 760
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 2 - 12)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(True, True)
        try:
            self.state("zoomed")
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)
            except tk.TclError:
                pass
        self.configure(bg=BG)
        self.option_add("*tearOff", False)
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.timer_job = None
        self.rain = None
        self.quote_job = None
        self.animation_jobs = []
        self.screen_generation = 0
        self.blink_generation = 0
        self.intel_tab = "url"
        self.intel_scans = 0
        self.intel_badges = set()
        self.player = "CYBER WARRIOR"
        self.key_handler = None
        self.body_canvas = None
        self.maze_token = 0
        self.bind("<Key>", self.on_key)
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(sequence, self.on_wheel)
        self.reset_mission()
        self.show_loading_screen()

    def reset_mission(self):
        self.credits = 0
        self.unlocked = {0}
        self.cleared = set()
        self.best = {}
        self.badges = set()
        self.hints_used = 0
        self.saved = False

    def agent_display(self):
        """Format the player's name once, even if it already includes WARRIOR."""
        name = self.player.strip()
        upper = name.upper()
        return name if upper == "WARRIOR" or upper.startswith("WARRIOR ") or upper.endswith(" WARRIOR") else f"WARRIOR {name}"

    def clear_screen(self):
        self.screen_generation += 1
        self.key_handler = None
        self.body_canvas = None
        for job in self.animation_jobs + [self.quote_job, self.timer_job]:
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
        self.animation_jobs.clear()
        self.quote_job = self.timer_job = None
        if self.rain is not None:
            self.rain.stop()
            self.rain = None
        for widget in self.container.winfo_children():
            widget.destroy()

    def safe_after(self, milliseconds, callback):
        """Schedule a screen-local animation that is cancelled on navigation."""
        generation, holder = self.screen_generation, {}

        def run():
            job = holder.get("job")
            if job in self.animation_jobs:
                self.animation_jobs.remove(job)
            if generation == self.screen_generation:
                try:
                    callback()
                except tk.TclError:
                    pass

        holder["job"] = self.after(milliseconds, run)
        self.animation_jobs.append(holder["job"])
        return holder["job"]

    def flash(self, widget, first, second, times=8, delay=110, final=None):
        """Blink a panel or banner between two colour pairs without blocking Tk."""
        def step(number=0):
            if number >= times:
                if final:
                    final()
                return
            try:
                background, foreground = first if number % 2 == 0 else second
                widget.configure(bg=background, fg=foreground)
                self.safe_after(delay, lambda: step(number + 1))
            except tk.TclError:
                return
        step()

    def add_backdrop(self, parent=None, animate=True):
        """Place an animated Matrix-style canvas behind a screen's widgets."""
        target = parent or self.container
        canvas = tk.Canvas(target, bg=BG, highlightthickness=0, bd=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        canvas.tk.call("lower", canvas._w)
        if animate:
            self.rain = MatrixRain(canvas)
        return canvas

    @staticmethod
    def shade(color, factor=0.17):
        """Create a dark tinted panel from a six-digit accent color."""
        try:
            value = color.lstrip("#")
            red, green, blue = (int(value[i:i + 2], 16) for i in (0, 2, 4))
            red, green, blue = (int(channel * factor) for channel in (red, green, blue))
            return f"#{red:02x}{green:02x}{blue:02x}"
        except (TypeError, ValueError):
            return PANEL_LIGHT

    def pulse_label(self, label, colors=None, delay=430):
        """Cycle a label through neon colors until its screen is destroyed."""
        palette = colors or (GREEN, CYAN, PURPLE, GREEN)
        generation = getattr(label, "_pulse_generation", 0) + 1
        label._pulse_generation = generation

        def step(index=0):
            if generation != getattr(label, "_pulse_generation", 0):
                return
            try:
                label.configure(fg=palette[index % len(palette)])
                self.safe_after(delay, lambda: step(index + 1))
            except tk.TclError:
                return

        step()

    def play_quote_rotation(self, label):
        """Rotate the home-screen escape quote without blocking Tk's event loop."""
        self.quote_index = random.randrange(len(ESCAPE_QUOTES))

        def rotate():
            try:
                label.configure(text="\"" + ESCAPE_QUOTES[self.quote_index] + "\"")
                self.quote_index = (self.quote_index + 1) % len(ESCAPE_QUOTES)
                self.quote_job = self.after(4300, rotate)
            except tk.TclError:
                self.quote_job = None

        rotate()

    def title_label(self, parent, text, color=GREEN, size=24):
        label = tk.Label(parent, text=text, bg=BG, fg=color,
                         font=(FONT, size, "bold"), pady=8)
        self.pulse_label(label, (color, WHITE, color, CYAN, color), 480)
        return label

    def button(self, parent, text, command, color=CYAN, width=22, **options):
        return NeonButton(
            parent, text, command, color, width,
            font=options.pop("font", (FONT, 11, "bold")),
            wraplength=options.pop("wraplength", 460),
            anchor=options.pop("anchor", "center"),
            justify=options.pop("justify", "center"),
            padx=options.pop("padx", 10), pady=options.pop("pady", 9))

    def card(self, parent, color=CYAN):
        return tk.Frame(parent, bg=PANEL, highlightthickness=2,
                        highlightbackground=color, padx=14, pady=12)

    def add_terminal(self, parent, height=8):
        return Terminal(parent, size=9, height=height)

    def log(self, text, tag="info"):
        if not hasattr(self, "terminal"):
            return
        try:
            self.terminal.say(text, tag)
        except tk.TclError:
            pass

    def animate_canvas_glow(self, canvas, item, palette=None, delay=520):
        """Give important Canvas headlines a restrained neon color cycle."""
        colors = palette or (GREEN, CYAN, GREEN, PURPLE)
        generation = getattr(self, "canvas_glow_generation", 0) + 1
        self.canvas_glow_generation = generation

        def cycle(index=0):
            if generation != self.canvas_glow_generation:
                return
            try:
                canvas.itemconfigure(item, fill=colors[index % len(colors)])
                self.safe_after(delay, lambda: cycle(index + 1))
            except tk.TclError:
                return

        cycle()

    def show_loading_screen(self):
        """Show a brief archive boot-up sequence before opening the title page."""
        self.clear_screen()
        self.add_backdrop()
        self.title_label(self.container, "CYBER ROOM || INTELLIGENT BOOT", GREEN, 25).pack(pady=(94, 8))
        tk.Label(self.container, text="SECURE TERMINAL INITIALISING  •  PLEASE WAIT",
                 bg=BG, fg=CYAN, font=(FONT, 10, "bold")).pack(pady=(0, 18))
        panel = tk.Frame(self.container, bg=PANEL, highlightthickness=2,
                         highlightbackground=GREEN, padx=12, pady=10)
        panel.pack(fill="x", padx=180, pady=8)
        self.loading_terminal = self.add_terminal(panel, height=5)
        self.loading_terminal.pack(fill="x")
        self.loading_progress = tk.Canvas(self.container, height=20, bg=BG, highlightthickness=0)
        self.loading_progress.pack(fill="x", padx=214, pady=(18, 4))
        self.loading_caption = tk.Label(self.container, text="CONNECTING TO ARCHIVE...",
                                        bg=BG, fg=YELLOW, font=(FONT, 9, "bold"))
        self.loading_caption.pack()
        tk.Label(self.container, text="LOCAL GAME  //  NO NETWORK REQUIRED",
                 bg=BG, fg=MUTED, font=(FONT, 8, "bold")).pack(side="bottom", pady=22)

        self.loading_terminal.scan("Powering up the archive terminal", "info")
        self.loading_terminal.say(f"Loading 09 sectors and {TOTAL_PUZZLES} puzzle locks...", "ok", speed=5)
        self.loading_terminal.say("Checking local game files...", "warn", speed=5)
        self.loading_terminal.say("SYSTEM READY. AGENT ACCESS AVAILABLE.", "ok", speed=5)
        self.loading_value = 0

        def advance_bar():
            self.loading_value = min(100, self.loading_value + random.randint(5, 10))
            canvas = self.loading_progress
            canvas.delete("all")
            width = max(canvas.winfo_width(), 500)
            canvas.create_rectangle(2, 3, width - 2, 17, outline=GREEN, width=1)
            fill_width = int((width - 8) * self.loading_value / 100)
            if fill_width:
                canvas.create_rectangle(5, 6, 5 + fill_width, 14,
                                        fill=GREEN if self.loading_value < 75 else CYAN, outline="")
            label = "ARCHIVE READY // OPENING TITLE SCREEN" if self.loading_value == 100 else "CONNECTING TO ARCHIVE..."
            self.loading_caption.configure(text=f"{label}  {self.loading_value:03d}%",
                                           fg=GREEN if self.loading_value == 100 else YELLOW)
            if self.loading_value < 100:
                self.safe_after(55, advance_bar)

        advance_bar()
        self.safe_after(1750, self.show_menu)

    def show_menu(self):
        self.clear_screen()
        canvas = tk.Canvas(self.container, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.rain = MatrixRain(canvas)
        canvas.create_rectangle(145, 38, 975, 204, fill=BG, outline=GREEN, width=3)
        canvas.create_rectangle(154, 47, 966, 195, outline=CYAN, width=1)
        glow = canvas.create_text(560, 105, text="CYBER ESCAPE ROOM",
                                  fill=GREEN, font=(FONT, 37, "bold"))
        canvas.create_text(560, 161, text="Hack the puzzles.  Beat the clock.  Escape the Room.",
                           fill=CYAN, font=(FONT, 15, "bold"))
        canvas.create_text(560, 185, text=f"9 SECTORS  ||  {TOTAL_PUZZLES} PUZZLES || ONE WAY OUT",
                           fill=WHITE, font=(FONT, 9, "bold"))

        canvas.create_rectangle(350, 222, 770, 690, fill=BG, outline=CYAN, width=2)
        canvas.create_rectangle(359, 231, 761, 681, outline="#173f55", width=1)
        canvas.create_text(560, 262, text="ENTER YOUR WARRIOR NAME",
                           fill=YELLOW, font=(FONT, 12, "bold"))
        entry = tk.Entry(canvas, font=(FONT, 16, "bold"), justify="center", width=20,
                         bg="#02060a", fg=GREEN, insertbackground=GREEN, bd=0,
                         highlightthickness=2, highlightbackground=GREEN,
                         highlightcolor=CYAN)
        entry.insert(0, self.player)
        canvas.create_window(560, 300, window=entry, width=270, height=38)
        entry.focus_set()

        def begin():
            self.player = entry.get().strip()[:14].upper() or "CYBER WARRIOR"
            self.reset_mission()
            self.show_briefing()

        entry.bind("<Return>", lambda _event: begin())
        menu_items = [
            ("START MISSION", begin, GREEN),
            ("CYBER INTEL ROOM", self.show_intel_room, PURPLE),
            ("LEADERBOARD", self.show_leaderboard, YELLOW),
            ("HOW TO PLAY", self.show_help, CYAN),
            ("EXIT", self.destroy, RED),
        ]
        for row, (label, action, color) in enumerate(menu_items):
            button = self.button(canvas, label, action, color, 23,
                                 font=(FONT, 12, "bold"), pady=8, wraplength=300)
            canvas.create_window(560, 357 + row * 59, window=button, width=278, height=43)

        quote = tk.Label(canvas, bg=BG, fg=YELLOW, font=(FONT, 9, "italic"),
                         wraplength=760, justify="center")
        canvas.create_window(560, 711, window=quote, width=820, height=22)
        self.play_quote_rotation(quote)
        canvas.create_text(560, 741, text="PYTHON   |   TKINTER   |   CYBER INTELLIGENT ESCAPE ROOM  |",
                           fill=MUTED, font=(FONT, 8, "bold"))
        self.animate_canvas_glow(canvas, glow, (GREEN, "#6dffc2", CYAN, "#6dffc2", PINK, GREEN), 450)

    def show_briefing(self):
        self.clear_screen()
        self.add_backdrop()
        self.title_label(self.container, "CYBER BRIEFING", RED, 27).pack(pady=(16, 2))
        tk.Label(self.container, text="CYBER THREAT BROADCAST  ||  INCOMING DANGER ALERT",
                 bg=BG, fg=YELLOW, font=(FONT, 9, "bold")).pack(pady=(0, 7))
        shell = tk.Frame(self.container, bg=PANEL, highlightthickness=2,
                         highlightbackground=RED, padx=10, pady=9)
        shell.pack(fill="both", expand=True, padx=42, pady=5)
        tk.Label(shell, text="SECURITY TERMINAL  ||  READ THE MESSAGE BEFORE ENTERING THE THREAT ZONE",
                 bg=PANEL, fg=CYAN, font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.terminal = self.add_terminal(shell, height=17)
        self.terminal.configure(highlightbackground=RED)
        self.terminal.pack(fill="both", expand=True)

        transmission = [
            ("Initialising cyber threat channel", "info", "scan"),
            (f"{self.agent_display()}, you are locked inside the Cyber Escape Room.", "info", "say"),
            ("ALERT: the security system has sealed every exit door.", "error", "say"),
            ("Solve the locks in each sector. Clear a sector to open the next door.", "ok", "say"),
            (f"Nine sectors. {TOTAL_PUZZLES} practical cybersecurity puzzles. One exit.", "warn", "say"),
            ("01 INTAKE LOBBY      ||  Multiple choice and everyday account choices", "ok", "say"),
            ("02 SERVICE TUNNEL    ||  Unscramble the words hidden in the messages", "info", "say"),
            ("03 CIPHER SHAFT      ||  Decode a letter-shift message", "pink", "say"),
            ("04 PIN VAULT         ||  Crack 4 to 6 digit PINs on a keypad", "ok", "say"),
            ("05 SEQUENCE TUNNEL    ||  Find the next number in changing patterns", "info", "say"),
            ("06 LOG ANALYZER      ||  Spot the suspicious lines in real-style logs", "warn", "say"),
            ("07 EVIDENCE INSPECTOR||  Find the files that prove the attack", "error", "say"),
            ("08 SUSPECT LINEUP    ||  Compare three profiles and catch the hacker", "pink", "say"),
            ("09 FINAL MISSION     ||  Survive the Backrooms maze and escape", "ok", "say"),
            ("Correct answers earn credits. Wrong answers cost 5 seconds.", "warn", "say"),
            ("A hint costs 5 credits. Read the real-life lesson after each lock.", "lesson", "say"),
            ("The timer begins when you enter a sector. Your escape route is ready.", "info", "say"),
            ("Good luck, and stay alert. The cyber threat is real.", "error", "say")
        ]
        for text, tag, kind in transmission:
            if kind == "scan":
                self.terminal.scan(text, tag)
            else:
                self.terminal.say(text, tag, speed=3, prefix="  ")
        footer = tk.Frame(self.container, bg=BG)
        footer.pack(side="bottom", before=shell, fill="x", padx=42, pady=(7, 10))
        self.button(footer, "OPEN MISSION CONTROL  >", self.show_dashboard,
                    GREEN, 28, font=(FONT, 12, "bold"), pady=8).pack(side="left")
        tk.Label(footer, text="The mission clock starts when you enter the first sector.",
                 bg=BG, fg=MUTED, font=(FONT, 8)).pack(side="left", padx=14)
        self.button(footer, "BACK TO TITLE", self.show_menu, MUTED, 16,
                    font=(FONT, 9, "bold"), pady=5).pack(side="right")

    def show_help(self):
        self.clear_screen()
        self.add_backdrop()
        self.title_label(self.container, "HOW TO PLAY", CYAN, 27).pack(pady=(18, 3))
        shell = tk.Frame(self.container, bg=PANEL, highlightthickness=2,
                         highlightbackground=CYAN, padx=10, pady=8)
        shell.pack(fill="both", expand=True, padx=48, pady=7)
        tk.Label(shell, text="CYBER WARRIOR   ||  TYPEWRITER MODE",
                 bg=PANEL, fg=GREEN, font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.terminal = self.add_terminal(shell, height=19)
        self.terminal.configure(highlightbackground=CYAN)
        self.terminal.pack(fill="both", expand=True)
        guide = [
            ("Loading the quick-start guide", "scan", "info"),
            ("Choose the next READY sector. Clear it to unlock the room beyond.", "say", "ok"),
            ("Each room has its own puzzles and countdown timer.", "say", "info"),
            ("First-try correct answers earn 10 credits; later tries earn fewer.", "say", "ok"),
            ("A wrong answer costs 5 seconds. A hint costs 5 credits.", "say", "warn"),
            ("Read every lesson: each puzzle connects to a real-life safety habit.", "say", "lesson"),
            ("MCQ: pick an answer. Jumble and cipher: type it.", "say", "info"),
            ("PIN vault: use the keypad or your keyboard digits. Wrong tries show aligned tumblers.", "say", "ok"),
            ("Sequences: study the bars, then type the next number. Logs and files: click a row, then flag it.", "say", "pink"),
            ("Suspects: compare profiles, interrogate, then accuse. Final maze: arrow keys or WASD.", "say", "warn"),
            (f"Escape through all 9 sectors and solve {TOTAL_PUZZLES} puzzles to finish.", "say", "warn"),
            ("The Cyber Intel Room has simple practice checks. It never opens links.", "say", "info"),
            ("Keep your real password and sign-in codes out of the practice tools.", "say", "error"),
        ]
        for text, kind, tag in guide:
            (self.terminal.scan(text, tag) if kind == "scan"
             else self.terminal.say(text, tag, speed=4, prefix="  "))
        self.button(self.container, "BACK TO TITLE", self.show_menu, GREEN,
                    22, font=(FONT, 11, "bold"), pady=7).pack(side="bottom", before=shell, pady=9)

    def show_dashboard(self):
        self.clear_screen()
        self.add_backdrop()
        header = tk.Frame(self.container, bg=BG)
        header.pack(fill="x", padx=26, pady=(10, 3))
        heading = tk.Label(header, text="CYBER CONTROL  ||  SECTOR MAP", bg=BG, fg=GREEN,
                           font=(FONT, 21, "bold"))
        heading.pack(side="left")
        self.pulse_label(heading, (GREEN, CYAN, GREEN, "#6dffc2"), 450)
        tk.Label(header, text=f"{self.agent_display()}   |   CREDITS {self.credits}",
                 bg=BG, fg=YELLOW, font=(FONT, 12, "bold")).pack(side="right")
        tk.Label(self.container,
                 text=f"ROOMS CLEARED: {len(self.cleared)}/9    |    TOTAL PUZZLES: {TOTAL_PUZZLES}"
                      f"    |    BADGES: {len(self.badges)}    |    INTEL TOOLS: {len(self.intel_badges)}/4",
                 bg=BG, fg=CYAN, font=(FONT, 9, "bold")).pack(anchor="w", padx=29)
        progress = tk.Frame(self.container, bg="#0d1420", highlightthickness=1,
                            highlightbackground="#274034", padx=7, pady=5)
        progress.pack(fill="x", padx=28, pady=(4, 0))
        for index, sector in enumerate(SECTORS):
            color = GREEN if index in self.cleared else (sector["color"] if index in self.unlocked else "#354052")
            segment = tk.Frame(progress, bg=color, height=9)
            segment.pack(side="left", fill="x", expand=True, padx=2, pady=2)
            tk.Label(segment, text=f"{index + 1:02d}", bg=color,
                     fg=BG if index in self.unlocked or index in self.cleared else MUTED,
                     font=(FONT, 7, "bold")).pack()
        grid = tk.Frame(self.container, bg=BG)
        grid.pack(fill="both", expand=True, padx=22, pady=(5, 3))
        for index, sector in enumerate(SECTORS):
            row, col = divmod(index, 3)
            unlocked = index in self.unlocked
            cleared = index in self.cleared
            accent = sector["color"] if unlocked else "#3e485a"
            box = tk.Frame(grid, bg=PANEL, highlightthickness=2,
                           highlightbackground=accent, padx=8, pady=6)
            box.grid(row=row, column=col, padx=7, pady=5, sticky="nsew")
            grid.grid_columnconfigure(col, weight=1, uniform="sector")
            grid.grid_rowconfigure(row, weight=1, uniform="sector")
            status = "CLEARED" if cleared else ("READY" if unlocked else "SEALED")
            status_color = GREEN if cleared else (sector["color"] if unlocked else MUTED)
            headline = tk.Frame(box, bg=PANEL)
            headline.pack(fill="x")
            tk.Label(headline, text=sector["name"], bg=PANEL, fg=accent,
                     font=(FONT, 9, "bold")).pack(side="left", anchor="w")
            tk.Label(headline, text=f" {status} ", bg=self.shade(status_color, 0.22),
                     fg=status_color, font=(FONT, 7, "bold"), padx=3).pack(side="right")

            details = tk.Frame(box, bg=PANEL)
            details.pack(fill="x", expand=True, pady=(3, 4))
            door = tk.Canvas(details, width=45, height=57, bg=PANEL, highlightthickness=0)
            door.pack(side="left", padx=(0, 7))
            border = door.create_rectangle(5, 3, 40, 54, fill=self.shade(accent, 0.16),
                                           outline=accent, width=2)
            door.create_rectangle(9, 7, 36, 51, outline=accent, width=1)
            door.create_line(12, 11, 33, 11, fill=accent, width=1)
            door.create_line(12, 15, 33, 15, fill=self.shade(accent, .7), width=1)
            door.create_oval(31, 30, 35, 34, fill=accent, outline=accent)
            if not unlocked:
                door.create_arc(13, 17, 31, 36, start=0, extent=180,
                                style="arc", outline=MUTED, width=2)
                door.create_rectangle(12, 26, 32, 41, fill="#19202c", outline=MUTED, width=1)
                door.create_oval(21, 30, 24, 34, fill=MUTED, outline=MUTED)
                door.create_line(22.5, 33, 22.5, 37, fill=MUTED, width=1)
            else:
                door.create_text(21, 31, text="OPEN" if cleared else f"{index + 1:02d}",
                                 fill=GREEN if cleared else accent,
                                 font=(FONT, 7 if cleared else 10, "bold"))
            text = tk.Frame(details, bg=PANEL)
            text.pack(side="left", fill="both", expand=True)
            tk.Label(text, text=sector["room"], bg=PANEL, fg=WHITE,
                     font=(FONT, 9, "bold")).pack(anchor="w")
            tk.Label(text, text=f"{len(sector['puzzles'])} puzzles  |  {sector['time']//60} min {sector['time']%60:02d}s",
                     bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(anchor="w", pady=(2, 0))
            best_text = f"BEST SCORE: {self.best[index]} credits" if index in self.best else "BEST SCORE: —"
            tk.Label(text, text=best_text, bg=PANEL, fg=YELLOW if index in self.best else MUTED,
                     font=(FONT, 7, "bold")).pack(anchor="w", pady=(3, 0))
            if unlocked:
                action = "REPLAY" if cleared else "ENTER SECTOR"
                self.button(box, action, lambda i=index: self.start_sector(i),
                            sector["color"], 16, font=(FONT, 9, "bold"), pady=4).pack(fill="x")
            else:
                locked_button = self.button(box, "LOCKED — CLEAR THE ROOM BEFORE THIS ONE",
                                            None, MUTED, 16, font=(FONT, 7, "bold"), pady=4,
                                            wraplength=270)
                locked_button.configure(state="disabled")
                locked_button.pack(fill="x")
        footer = tk.Frame(self.container, bg=BG)
        footer.pack(side="bottom", before=grid, pady=(0, 8))
        self.button(footer, "CYBER INTEL ROOM", self.show_intel_room, PURPLE, 20,
                    font=(FONT, 9, "bold"), pady=5).pack(side="left", padx=6)
        self.button(footer, "LEADERBOARD", self.show_leaderboard, YELLOW, 16,
                    font=(FONT, 9, "bold"), pady=5).pack(side="left", padx=6)
        self.button(footer, "END MISSION & SAVE", self.finish_early, ORANGE, 21,
                    font=(FONT, 9, "bold"), pady=5).pack(side="left", padx=6)
        self.button(footer, "TITLE", self.show_menu, MUTED, 11,
                    font=(FONT, 9, "bold"), pady=5).pack(side="left", padx=6)

    def finish_early(self):
        if not self.cleared and self.credits == 0:
            messagebox.showinfo("Mission", "Clear a puzzle before ending the mission.")
            return
        if len(self.cleared) < len(SECTORS):
            if not messagebox.askyesno("End mission", "You have not escaped yet. End and save this score?"):
                return
        self.show_final()

    def start_sector(self, index):
        self.sector_index = index
        self.sector = SECTORS[index]
        self.puzzle_index = 0
        self.time_left = self.sector["time"]
        self.sector_start_credits = self.credits
        self.sector_wrong = 0
        self.build_game_screen()
        self.load_puzzle()
        self.blink_generation += 1
        self.blink_current(self.blink_generation, True)
        self.update_timer()
        self.timer_tick()

    def build_game_screen(self):
        self.clear_screen()
        self.add_backdrop()
        sector = self.sector
        top = tk.Frame(self.container, bg=PANEL, highlightthickness=2,
                       highlightbackground=sector["color"])
        top.pack(fill="x", padx=14, pady=(10, 5))
        left = tk.Frame(top, bg=PANEL)
        left.pack(side="left", padx=12, pady=7)
        tk.Label(left, text=sector["name"], bg=PANEL, fg=sector["color"],
                 font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(left, text=f"{sector['room']}  |  {self.agent_display()}",
                 bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        self.credits_label = tk.Label(top, text="", bg=PANEL, fg=YELLOW,
                                      font=(FONT, 14, "bold"), width=14)
        self.credits_label.pack(side="right", padx=14)
        self.timer_label = tk.Label(top, text="", bg=PANEL, fg=GREEN,
                                    font=(FONT, 21, "bold"), width=8)
        self.timer_label.pack(side="right", padx=8)
        tk.Label(top, text="TIME", bg=PANEL, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(side="right")
        self.timer_bar = tk.Canvas(self.container, height=8, bg="#060a10", highlightthickness=0)
        self.timer_bar.pack(fill="x", padx=18, pady=(0, 2))
        self.update_credits_label()
        self.progress_canvas = tk.Canvas(self.container, height=50, bg=BG,
                                         highlightthickness=0)
        self.progress_canvas.pack(fill="x", padx=16, pady=(2, 0))
        self.progress_canvas.bind("<Configure>", lambda _event: self.draw_puzzle_progress())
        self.progress_label = tk.Label(self.container, text="", bg=BG, fg=CYAN,
                                       font=(FONT, 9, "bold"))
        self.progress_label.pack(pady=(0, 3))
        area = tk.Frame(self.container, bg=BG)
        area.pack(fill="both", expand=True, padx=14, pady=3)
        self.puzzle_card = tk.Frame(area, bg=PANEL, highlightthickness=3,
                                    highlightbackground=sector["color"], padx=14, pady=12)
        self.puzzle_card.pack(side="left", fill="both", expand=True)
        side = tk.Frame(area, bg=BG, width=270)
        side.pack(side="right", fill="y", padx=(10, 0))
        side.pack_propagate(False)
        terminal_heading = tk.Frame(side, bg=self.shade(GREEN, 0.16),
                                    highlightthickness=1, highlightbackground=GREEN)
        terminal_heading.pack(fill="x")
        tk.Label(terminal_heading, text="  LIVE ARCHIVE TERMINAL  //  EVENT FEED",
                 bg=self.shade(GREEN, 0.16), fg=GREEN,
                 font=(FONT, 9, "bold")).pack(anchor="w")
        self.terminal = self.add_terminal(side, 15)
        self.terminal.configure(highlightthickness=2, highlightbackground=GREEN)
        self.terminal.pack(fill="both", expand=True, pady=(4, 0))
        self.terminal.scan(f"Opening {sector['room']} security channel", "info")
        self.log(f"Sector {self.sector_index+1:02d} entered. {len(self.sector['puzzles'])} locks detected.")
        controls = tk.Frame(self.container, bg=BG)
        controls.pack(side="bottom", before=area, fill="x", padx=16, pady=(4, 10))
        self.hint_button = self.button(controls, f"HINT (-{HINT_COST})", self.use_hint, YELLOW, 15)
        self.hint_button.pack(side="left")
        self.feedback = tk.Label(controls, text="", bg=BG, fg=WHITE,
                                 font=(FONT, 9), wraplength=590, justify="left")
        self.feedback.pack(side="left", fill="x", expand=True, padx=12)
        self.button(controls, "LEAVE SECTOR", self.leave_sector, RED, 16).pack(side="right")

    def update_credits_label(self):
        if hasattr(self, "credits_label"):
            self.credits_label.configure(text=f"CREDITS {self.credits}")

    def update_timer(self):
        if not hasattr(self, "timer_label"):
            return
        remaining = max(0, self.time_left)
        color = GREEN if remaining > 60 else (YELLOW if remaining > 25 else (RED if remaining % 2 else ORANGE))
        self.timer_label.configure(text=f"{remaining//60:02d}:{remaining%60:02d}", fg=color)
        if hasattr(self, "timer_bar"):
            try:
                self.timer_bar.delete("all")
                width = max(self.timer_bar.winfo_width(), 10)
                total = max(self.sector["time"], 1)
                fraction = max(0, min(1, remaining / total))
                self.timer_bar.create_rectangle(0, 0, width, 8, fill="#0d1720", outline="")
                self.timer_bar.create_rectangle(0, 0, int(width * fraction), 8,
                                                fill=color, outline="")
                if fraction > 0:
                    self.timer_bar.create_line(0, 0, int(width * fraction), 0,
                                               fill=WHITE, width=2)
            except tk.TclError:
                pass

    def timer_tick(self):
        if self.time_left <= 0:
            self.time_up()
        else:
            self.timer_job = self.after(1000, self.timer_step)

    def timer_step(self):
        self.timer_job = None
        self.time_left -= 1
        self.update_timer()
        if self.time_left <= 0:
            self.time_up()
        else:
            self.timer_tick()

    def blink_current(self, generation, on=True):
        if generation != self.blink_generation or not hasattr(self, "progress_canvas"):
            return
        try:
            color = self.sector["color"] if on else self.shade(self.sector["color"], .38)
            self.progress_canvas.itemconfigure("current-door", outline=color)
            self.safe_after(440, lambda: self.blink_current(generation, not on))
        except tk.TclError:
            return

    def wrong_answer(self):
        if self.solved:
            return
        self.wrong += 1
        self.sector_wrong += 1
        self.time_left -= WRONG_TIME_PENALTY
        self.update_timer()
        self.feedback.configure(text="ACCESS DENIED — 5 seconds lost. Try again.", fg=RED)
        self.flash(self.feedback, (RED, BG), (BG, RED), times=6, delay=95)
        self.flash_puzzle_banner("ACCESS DENIED", RED)
        self.log("Incorrect attempt. Security clock reduced by five seconds.", "error")
        self.bell()
        if self.time_left <= 0:
            self.time_up()

    def time_up(self):
        self.clear_screen()
        self.add_backdrop()
        self.credits = self.sector_start_credits
        alarm = tk.Label(self.container, text="  LOCKDOWN  ", bg=RED, fg=BG,
                         font=(FONT, 32, "bold"), padx=14, pady=6)
        alarm.pack(pady=(45, 8))
        self.flash(alarm, (RED, BG), (BG, RED), times=12, delay=95)
        tk.Label(self.container, text=f"TIME EXPIRED IN {self.sector['room'].upper()}",
                 bg=BG, fg=ORANGE, font=(FONT, 16, "bold")).pack(pady=8)
        tk.Label(self.container,
                 text="Credits earned in this sector were lost. Your other cleared sectors remain safe.",
                 bg=BG, fg=WHITE, font=(FONT, 11), wraplength=650).pack(pady=12)
        self.button(self.container, "RETRY SECTOR", lambda: self.start_sector(self.sector_index), GREEN, 24).pack(pady=8)
        self.button(self.container, "BACK TO SECTOR MAP", self.show_dashboard, CYAN, 24).pack(pady=8)

    def leave_sector(self):
        if messagebox.askyesno("Leave sector", "Leave now? Credits earned in this unfinished sector will be lost."):
            self.credits = self.sector_start_credits
            self.show_dashboard()

    def load_puzzle(self):
        for widget in self.puzzle_card.winfo_children():
            widget.destroy()
        self.puzzle = self.sector["puzzles"][self.puzzle_index]
        self.wrong = 0
        self.solved = False
        self.key_handler = None
        self.maze_token += 1
        self.hint_used_this_puzzle = False
        self.feedback.configure(text="", fg=WHITE)
        self.progress_label.configure(
            text=f"PUZZLE {self.puzzle_index+1}/{len(self.sector['puzzles'])}"
                 f"   •   {self.puzzle['difficulty']}   •   {self.puzzle['tag']}"
        )
        accent = self.sector["color"]
        question_shell = tk.Frame(self.puzzle_card, bg=accent, padx=2, pady=2)
        question_shell.pack(fill="x", pady=(0, 12))
        question_panel = tk.Frame(question_shell, bg=self.shade(accent, 0.20), padx=12, pady=9)
        question_panel.pack(fill="x")
        tag_row = tk.Frame(question_panel, bg=self.shade(accent, 0.20))
        tag_row.pack(fill="x", pady=(0, 5))
        tk.Label(tag_row, text=f"  LOCK {self.puzzle_index + 1:02d}  ",
                 bg=accent, fg=BG, font=(FONT, 8, "bold"), padx=4, pady=2).pack(side="left")
        tk.Label(tag_row, text=f"  {self.puzzle['tag']}  ",
                 bg=PURPLE, fg=BG, font=(FONT, 8, "bold"), padx=4, pady=2).pack(side="left", padx=5)
        tk.Label(tag_row, text=f"  {self.puzzle['difficulty']}  ",
                 bg=self.shade(YELLOW, 0.30), fg=YELLOW,
                 font=(FONT, 8, "bold"), padx=4, pady=2).pack(side="right")
        tk.Label(question_panel, text=self.puzzle["question"],
                 bg=self.shade(accent, 0.20), fg=WHITE,
                 font=(FONT, 12, "bold"), justify="left",
                 wraplength=610).pack(anchor="w", fill="x")
        self.action_area = tk.Frame(self.puzzle_card, bg=PANEL)
        self.action_area.pack(side="bottom", fill="x", pady=(8, 0))
        canvas = tk.Canvas(self.puzzle_card, bg=PANEL, highlightthickness=0, width=1, height=1)
        scroll = tk.Scrollbar(self.puzzle_card, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        self.body_canvas = canvas
        self.body = tk.Frame(canvas, bg=PANEL)
        window = canvas.create_window((0, 0), window=self.body, anchor="nw")

        def fit(_event=None):
            try:
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfigure(window, width=canvas.winfo_width())
                needed = self.body.winfo_reqheight() > canvas.winfo_height() > 1
                if needed and not scroll.winfo_ismapped():
                    scroll.pack(side="right", fill="y", before=canvas)
                elif not needed and scroll.winfo_ismapped():
                    scroll.pack_forget()
            except tk.TclError:
                pass

        self.body.bind("<Configure>", fit)
        canvas.bind("<Configure>", fit)
        builders = {
            "mcq": self.build_mcq, "jumble": self.build_jumble, "decrypt": self.build_decrypt,
            "pin": self.build_pin, "sequence": self.build_sequence, "inspect": self.build_inspect,
            "suspect": self.build_suspect, "maze": self.build_maze, "phrase": self.build_phrase,
        }
        builders[self.puzzle["type"]]()
        self.draw_puzzle_progress()

    def flash_puzzle_banner(self, text, color):
        """Briefly flash an access message above the current puzzle card."""
        if not hasattr(self, "puzzle_card"):
            return
        banner = tk.Label(self.puzzle_card, text=f"  {text}  ", bg=color, fg=BG,
                          font=(FONT, 20, "bold"), padx=14, pady=8)
        banner.place(relx=.5, rely=.55, anchor="center")
        self.flash(banner, (color, BG), (BG, color), times=7, delay=85,
                   final=banner.destroy)

    def draw_puzzle_progress(self):
        """Draw the sector doors and exit as a quick visual progress map."""
        if not hasattr(self, "progress_canvas") or not hasattr(self, "sector"):
            return
        try:
            canvas = self.progress_canvas
            canvas.delete("all")
            total = len(self.sector["puzzles"])
            width = max(canvas.winfo_width(), 360)
            margin = 48
            spacing = (width - margin * 2) / max(total, 1)
            centers = [margin + i * spacing for i in range(total)]
            centers.append(margin + total * spacing)
            if len(centers) > 1:
                canvas.create_line(centers[0], 21, centers[-1], 21,
                                   fill="#526075", width=2)
            for index, x in enumerate(centers):
                is_exit = index == total
                is_done = index < self.puzzle_index
                is_current = index == self.puzzle_index and not is_exit
                accent = GREEN if is_done else (self.sector["color"] if is_current else "#526075")
                if is_exit and self.puzzle_index >= total:
                    accent = GREEN
                left, right = x - 22, x + 22
                canvas.create_rectangle(left, 5, right, 37,
                                        fill=self.shade(accent, 0.18),
                                        outline=accent, width=3 if is_current or (is_exit and self.puzzle_index >= total) else 2,
                                        tags="current-door" if is_current else f"door-{index}")
                if is_exit:
                    label = "OUT" if self.puzzle_index >= total else "EXIT"
                elif is_done:
                    label = "OK"
                else:
                    label = f"{index + 1:02d}"
                canvas.create_text(x, 21, text=label, fill=accent,
                                   font=(FONT, 8 if is_exit else 10, "bold"))
                canvas.create_text(x, 45, text="EXIT" if is_exit else "DOOR",
                                   fill=MUTED if not is_current else WHITE,
                                   font=(FONT, 6, "bold"))
        except tk.TclError:
            return

    def option_buttons(self, options, color):
        choice_colors = (CYAN, PURPLE, YELLOW, PINK, GREEN)
        for index, option in enumerate(options):
            choice_color = choice_colors[index % len(choice_colors)]
            btn = self.button(self.body, f"  {chr(65 + index)}   //   {option}",
                              lambda i=index: self.check_option(i),
                              choice_color, 48, wraplength=560, justify="left", anchor="w",
                              font=(FONT, 10, "bold"))
            btn.configure(bg=self.shade(choice_color, 0.16), padx=12, pady=8)
            btn.pack(fill="x", pady=4)

    def build_mcq(self):
        self.option_buttons(self.puzzle["options"], self.sector["color"])

    def text_entry(self, width, size, label, color):
        """Typed-answer box with a submit button, shared by the typing puzzles."""
        self.answer_entry = tk.Entry(self.body, font=(FONT, size, "bold"), justify="center",
                                     bg="#05080e", fg=GREEN, insertbackground=GREEN,
                                     relief="flat", width=width)
        self.answer_entry.pack(pady=8)
        self.answer_entry.focus_set()
        self.answer_entry.bind("<Return>", lambda _event: self.check_text_answer())
        self.button(self.action_area, label, self.check_text_answer, color, 18).pack()

    def build_jumble(self):
        letters = list(self.puzzle["scramble"])
        while "".join(letters) == self.puzzle["answer"]:
            random.shuffle(letters)
        tiles = tk.Frame(self.body, bg=PANEL)
        tiles.pack(pady=8)
        for letter in letters:
            tk.Label(tiles, text=letter, bg=PANEL_LIGHT, fg=self.sector["color"],
                     font=(FONT, 19, "bold"), padx=8, pady=5).pack(side="left", padx=3)
        tk.Label(self.body, text="Type the decoded word:", bg=PANEL, fg=MUTED,
                 font=(FONT, 9)).pack(pady=(5, 3))
        self.text_entry(20, 16, "UNJUMBLE", PURPLE)

    def build_decrypt(self):
        tk.Label(self.body, text=self.puzzle["cipher"], bg="#05080e", fg=GREEN,
                 font=(FONT, 20, "bold"), padx=12, pady=14).pack(fill="x", pady=6)
        tk.Label(self.body, text=f"CAESAR SHIFT: move letters back by {self.puzzle['shift']}",
                 bg=PANEL, fg=PURPLE, font=(FONT, 9, "bold")).pack(pady=4)
        self.text_entry(37, 14, "DECRYPT", PURPLE)

    def check_option(self, index):
        if self.solved:
            return
        if index == self.puzzle["answer"]:
            self.finish_puzzle()
        else:
            self.wrong_answer()

    def check_text_answer(self):
        if self.solved:
            return
        if clean_answer(self.answer_entry.get()) == clean_answer(self.puzzle["answer"]):
            self.finish_puzzle()
        else:
            self.answer_entry.delete(0, "end")
            self.wrong_answer()

    def on_key(self, event):
        """Send keyboard presses to the puzzle that wants them (PIN pad and maze)."""
        if self.key_handler:
            self.key_handler(event)

    def on_wheel(self, event):
        """Scroll the puzzle area with the mouse wheel so nothing is ever unreachable."""
        try:
            if self.body_canvas is not None and self.body_canvas.winfo_exists():
                up = event.num == 4 or getattr(event, "delta", 0) > 0
                self.body_canvas.yview_scroll(-2 if up else 2, "units")
        except tk.TclError:
            pass

    def build_pin(self):
        length = len(self.puzzle["pin"])
        self.pin_value, self.pin_tries = "", []
        notes = tk.Frame(self.body, bg=PANEL)
        notes.pack(side="left", fill="both", expand=True)
        tk.Label(notes, text="TECHNICIAN'S STICKY NOTES", bg=PANEL, fg=YELLOW,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 4))
        for note in self.puzzle["clues"]:
            tk.Label(notes, text=note, bg="#e8d96b", fg="#1a1600", font=(FONT, 10, "bold"),
                     wraplength=330, justify="left", anchor="w", padx=8, pady=4).pack(fill="x", pady=2)
        self.pin_log = tk.Label(notes, text="Attempts: none yet", bg=PANEL, fg=MUTED,
                                font=(FONT, 9), justify="left", anchor="w")
        self.pin_log.pack(fill="x", pady=(6, 0))
        pad = tk.Frame(self.body, bg=PANEL)
        pad.pack(side="right", padx=(14, 4))
        screen = tk.Frame(pad, bg="#05080e", highlightthickness=2, highlightbackground=YELLOW,
                          padx=6, pady=6)
        screen.pack(pady=(0, 8))
        self.pin_leds = []
        for _ in range(length):
            led = tk.Label(screen, text="_", width=2, bg="#0a1a12", fg=GREEN, font=(FONT, 20, "bold"))
            led.pack(side="left", padx=2)
            self.pin_leds.append(led)
        keys = tk.Frame(pad, bg=PANEL)
        keys.pack()
        for i, key in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9", "CLR", "0", "OK"]):
            color = RED if key == "CLR" else (GREEN if key == "OK" else YELLOW)
            self.button(keys, key, lambda k=key: self.pin_press(k), color, 4,
                        font=(FONT, 13, "bold"), pady=4).grid(row=i // 3, column=i % 3, padx=3, pady=3)
        self.key_handler = self.pin_key

    def pin_key(self, event):
        if event.char.isdigit():
            self.pin_press(event.char)
        elif event.keysym == "BackSpace":
            self.pin_press("CLR")
        elif event.keysym == "Return":
            self.pin_press("OK")

    def pin_press(self, key):
        if self.solved:
            return
        if key == "OK":
            self.pin_submit()
            return
        if key == "CLR":
            self.pin_value = ""
        elif len(self.pin_value) < len(self.puzzle["pin"]):
            self.pin_value += key
        for i, led in enumerate(self.pin_leds):
            led.configure(text=self.pin_value[i] if i < len(self.pin_value) else "_")

    def pin_submit(self):
        pin = self.puzzle["pin"]
        if len(self.pin_value) < len(pin):
            self.feedback.configure(text=f"This lock needs {len(pin)} digits.", fg=YELLOW)
            return
        if self.pin_value == pin:
            for led in self.pin_leds:
                led.configure(bg=GREEN, fg=BG)
            self.finish_puzzle()
            return
        aligned = sum(a == b for a, b in zip(self.pin_value, pin))
        self.pin_tries.append(f"{self.pin_value}  ->  {aligned}/{len(pin)} tumblers aligned")
        self.pin_log.configure(text="Attempts:\n" + "\n".join(self.pin_tries[-4:]), fg=CYAN)
        self.pin_value = ""
        for led in self.pin_leds:
            led.configure(text="_")
        self.wrong_answer()
        if self.time_left > 0:
            self.feedback.configure(text=f"ACCESS DENIED - {aligned} tumblers aligned. 5 seconds lost.", fg=RED)

    def build_sequence(self):
        numbers, answer = self.puzzle["seq"], int(self.puzzle["answer"])
        peak = math.log(max(numbers + [answer]) + 1)
        graph = tk.Canvas(self.body, height=150, bg="#05080e", highlightthickness=1,
                          highlightbackground=PINK)
        graph.pack(fill="x", pady=(0, 8))

        def draw(_event=None):
            graph.delete("all")
            slot = max(graph.winfo_width(), 300) / (len(numbers) + 1)
            for i, value in enumerate(numbers + [answer]):
                hidden = i == len(numbers)
                x = slot * i + slot / 2
                height = 14 + 100 * math.log(value + 1) / peak
                color = YELLOW if hidden else PINK
                graph.create_rectangle(x - slot * .3, 135 - height, x + slot * .3, 135,
                                       fill="" if hidden else self.shade(PINK, .4),
                                       outline=color, width=2, dash=(4, 3) if hidden else ())
                graph.create_text(x, 124 - height, text="?" if hidden else str(value),
                                  fill=color if hidden else WHITE, font=(FONT, 11, "bold"))

        graph.bind("<Configure>", draw)
        draw()
        tk.Label(self.body, text="  ->  ".join(map(str, numbers)) + "  ->  ?", bg="#05080e",
                 fg=PINK, font=(FONT, 16, "bold"), pady=8, wraplength=640).pack(fill="x")
        tk.Label(self.body, text="Type the next number in the pattern:", bg=PANEL, fg=MUTED,
                 font=(FONT, 9)).pack(pady=(8, 3))
        self.text_entry(10, 18, "SEND NEXT VALUE", PINK)

    def build_inspect(self):
        p, accent = self.puzzle, self.sector["color"]
        self.flagged, self.picked, self.rows = set(), None, []
        wrap = tk.Frame(self.body, bg=PANEL)
        wrap.pack(fill="both", expand=True)
        table = tk.Frame(wrap, bg=PANEL)
        table.pack(side="left", fill="both", expand=True)
        head = tk.Frame(table, bg=accent)
        head.pack(fill="x", pady=(0, 2))
        for text, width in zip(["FLAG"] + p["cols"], [5] + p["widths"]):
            tk.Label(head, text=text, width=width, anchor="w", bg=accent, fg=BG,
                     font=(FONT, 9, "bold")).pack(side="left", padx=1)
        for i, (cells, _detail) in enumerate(p["rows"]):
            row = tk.Frame(table, cursor="hand2")
            row.pack(fill="x", pady=1)
            labels = [tk.Label(row, text=text, width=width, anchor="w", font=(FONT, 9))
                      for text, width in zip([""] + cells, [5] + p["widths"])]
            for widget in labels + [row]:
                widget.bind("<Button-1>", lambda _e, k=i: self.pick_row(k))
            for label in labels:
                label.pack(side="left", padx=1)
            self.rows.append(labels)
        side = tk.Frame(wrap, bg="#05080e", highlightthickness=2, highlightbackground=accent,
                        width=230, height=250, padx=8, pady=8)
        side.pack(side="right", fill="y", padx=(10, 0))
        side.pack_propagate(False)
        tk.Label(side, text=p["detail_label"], bg="#05080e", fg=accent,
                 font=(FONT, 9, "bold")).pack(anchor="w")
        self.detail = tk.Label(side, text="Click any row to inspect it, then flag it if it looks suspicious.",
                               bg="#05080e", fg=WHITE, font=(FONT, 9), wraplength=205,
                               justify="left", anchor="nw")
        self.detail.pack(fill="both", expand=True, pady=6)
        self.flag_button = self.button(side, "FLAG AS SUSPICIOUS", self.toggle_flag, RED, 20,
                                       font=(FONT, 9, "bold"), pady=5)
        self.flag_button.pack(fill="x")
        self.flag_count = tk.Label(side, text="", bg="#05080e", fg=YELLOW, font=(FONT, 9, "bold"))
        self.flag_count.pack(pady=(6, 0))
        self.button(self.action_area, "SUBMIT FLAGGED LINES", self.check_inspect, accent, 24).pack()
        self.paint_rows()

    def paint_rows(self):
        for i, labels in enumerate(self.rows):
            flagged, picked = i in self.flagged, i == self.picked
            bg = "#4a1020" if flagged else (self.shade(CYAN, .35) if picked else PANEL_LIGHT)
            for label in labels:
                label.configure(bg=bg, fg=WHITE)
            labels[0].configure(text="FLAG" if flagged else (">>" if picked else ""),
                                fg=RED if flagged else CYAN)
            labels[0].master.configure(bg=bg)
        total = len(self.puzzle["sus"])
        self.flag_count.configure(text=f"Flagged {len(self.flagged)}  |  Find {total}")
        removing = self.picked in self.flagged
        self.flag_button.set_text("REMOVE FLAG" if removing else "FLAG AS SUSPICIOUS")

    def pick_row(self, index):
        if self.solved:
            return
        self.picked = index
        self.detail.configure(text=self.puzzle["rows"][index][1])
        self.paint_rows()

    def toggle_flag(self):
        if self.solved:
            return
        if self.picked is None:
            self.feedback.configure(text="Click a row first, then flag it.", fg=YELLOW)
            return
        self.flagged ^= {self.picked}
        self.paint_rows()

    def check_inspect(self):
        if self.solved:
            return
        real = set(self.puzzle["sus"])
        if not self.flagged:
            self.feedback.configure(text="Nothing flagged yet. Inspect the rows first.", fg=YELLOW)
            return
        if self.flagged == real:
            for i in real:
                for label in self.rows[i]:
                    label.configure(bg="#0f3d2a")
            self.finish_puzzle()
            return
        good, bad = len(self.flagged & real), len(self.flagged - real)
        self.wrong_answer()
        if self.time_left > 0:
            self.feedback.configure(text=f"ACCESS DENIED - {good} correct, {bad} innocent. "
                                         "Read the notes again. 5 seconds lost.", fg=RED)

    def build_suspect(self):
        p = self.puzzle
        report = tk.Frame(self.body, bg="#05080e", highlightthickness=2, highlightbackground=RED,
                          padx=10, pady=6)
        report.pack(fill="x", pady=(0, 8))
        tk.Label(report, text="INCIDENT REPORT  //  THE ATTACKER MATCHES EVERY LINE", bg="#05080e",
                 fg=RED, font=(FONT, 9, "bold")).pack(anchor="w")
        for line in p["incident"]:
            tk.Label(report, text="- " + line, bg="#05080e", fg=WHITE, font=(FONT, 9),
                     wraplength=700, justify="left", anchor="w").pack(fill="x")
        row = tk.Frame(self.body, bg=PANEL)
        row.pack(fill="both", expand=True)
        self.suspect_cards = []
        for i, who in enumerate(p["suspects"]):
            card = tk.Frame(row, bg=PANEL_LIGHT, highlightthickness=2, highlightbackground=MUTED,
                            padx=8, pady=6)
            card.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(card, text=f"SUSPECT {chr(65 + i)}", bg=PANEL_LIGHT, fg=self.sector["color"],
                     font=(FONT, 8, "bold")).pack(anchor="w")
            tk.Label(card, text=who["name"], bg=PANEL_LIGHT, fg=WHITE,
                     font=(FONT, 13, "bold")).pack(anchor="w")
            tk.Label(card, text=who["role"], bg=PANEL_LIGHT, fg=YELLOW, font=(FONT, 9, "bold"),
                     wraplength=200, justify="left").pack(anchor="w", pady=(0, 4))
            for fact in who["facts"]:
                tk.Label(card, text="> " + fact, bg=PANEL_LIGHT, fg=WHITE, font=(FONT, 9),
                         wraplength=200, justify="left", anchor="w").pack(fill="x", pady=1)
            alibi = tk.Label(card, text="", bg=PANEL_LIGHT, fg=CYAN, font=(FONT, 9, "italic"),
                             wraplength=200, justify="left", anchor="w")
            alibi.pack(fill="x", pady=(5, 0))
            buttons = tk.Frame(card, bg=PANEL_LIGHT)
            buttons.pack(side="bottom", fill="x", pady=(8, 0))
            self.button(buttons, "INTERROGATE", lambda a=alibi, w=who: a.configure(text='"' + w["alibi"] + '"'),
                        CYAN, 12, font=(FONT, 8, "bold"), pady=3).pack(fill="x", pady=2)
            accuse = self.button(buttons, "ACCUSE", lambda k=i: self.accuse(k), RED, 12,
                                 font=(FONT, 8, "bold"), pady=3)
            accuse.pack(fill="x", pady=2)
            self.suspect_cards.append((card, accuse))

    def accuse(self, index):
        if self.solved:
            return
        card, button = self.suspect_cards[index]
        name = self.puzzle["suspects"][index]["name"]
        if index == self.puzzle["answer"]:
            card.configure(highlightbackground=GREEN)
            self.log(f"{name} identified as the attacker.", "ok")
            self.finish_puzzle()
            return
        card.configure(highlightbackground=RED)
        button.set_text("RULED OUT")
        button.lock(RED)
        self.log(f"{name} is not the attacker.", "warn")
        self.wrong_answer()

    def build_maze(self):
        cols, rows = 21, 11
        grid = [["#"] * cols for _ in range(rows)]
        grid[1][1] = "."
        stack = [(1, 1)]
        while stack:
            x, y = stack[-1]
            moves = [(dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
                     if 0 < x + dx < cols - 1 and 0 < y + dy < rows - 1 and grid[y + dy][x + dx] == "#"]
            if moves:
                dx, dy = random.choice(moves)
                grid[y + dy // 2][x + dx // 2] = "."
                grid[y + dy][x + dx] = "."
                stack.append((x + dx, y + dy))
            else:
                stack.pop()
        for _ in range(16):
            x, y = random.randrange(2, cols - 2), random.randrange(2, rows - 2)
            if grid[y][x] == "#" and ((grid[y][x - 1] == "." and grid[y][x + 1] == ".") or
                                      (grid[y - 1][x] == "." and grid[y + 1][x] == ".")):
                grid[y][x] = "."
        cells = [(x, y) for y in range(1, rows, 2) for x in range(1, cols, 2)
                 if (x, y) not in ((1, 1), (19, 9), (19, 1))]
        for gap in (8, 6, 4, 2, 0):
            random.shuffle(cells)
            spots = []
            for cell in cells:
                if all(abs(cell[0] - s[0]) + abs(cell[1] - s[1]) >= gap
                       for s in spots + [(1, 1), (19, 9)]):
                    spots.append(cell)
                if len(spots) == 4:
                    break
            if len(spots) == 4:
                break
        self.maze = {"grid": grid, "player": (1, 1), "previous": (1, 1), "virus": (19, 1),
                     "terms": {spot: n for n, spot in enumerate(spots)}, "done": set(),
                     "seen": set(), "words": [], "open": False, "flicker": False}
        self.maze_hud = tk.Label(self.body, text="", bg=PANEL, fg=YELLOW, font=(FONT, 9, "bold"),
                                 anchor="w")
        self.maze_hud.pack(fill="x")
        area = tk.Frame(self.body, bg=PANEL)
        area.pack()
        self.maze_canvas = tk.Canvas(area, width=cols * 24, height=rows * 24, bg="#050500",
                                     highlightthickness=2, highlightbackground=YELLOW)
        self.maze_canvas.pack(side="left")
        pad = tk.Frame(area, bg=PANEL)
        pad.pack(side="left", padx=12)
        for text, dx, dy, r, c in (("UP", 0, -1, 0, 1), ("LEFT", -1, 0, 1, 0),
                                   ("DOWN", 0, 1, 1, 1), ("RIGHT", 1, 0, 1, 2)):
            self.button(pad, text, lambda a=dx, b=dy: self.maze_move(a, b), YELLOW, 5,
                        font=(FONT, 9, "bold"), pady=6).grid(row=r, column=c, padx=2, pady=2)
        self.key_handler = self.maze_key
        self.maze_draw()
        self.maze_status()
        token = self.maze_token
        self.safe_after(900, lambda: self.maze_tick(token))

    def maze_key(self, event):
        moves = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0),
                 "w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        key = event.keysym.lower()
        if key in moves:
            self.maze_move(*moves[key])

    def maze_draw(self):
        m, canvas, size = self.maze, self.maze_canvas, 24
        canvas.delete("all")
        px, py = m["player"]
        reach = 2 if m["flicker"] else 4
        for y, line in enumerate(m["grid"]):
            for x, cell in enumerate(line):
                near = (x - px) ** 2 + (y - py) ** 2 <= reach ** 2
                if near:
                    m["seen"].add((x, y))
                elif (x, y) not in m["seen"]:
                    continue
                if cell == "#":
                    fill = "#b8a64a" if near else "#3b3512"
                else:
                    fill = "#4a4214" if near else "#14120a"
                x0, y0 = x * size, y * size
                canvas.create_rectangle(x0, y0, x0 + size, y0 + size, fill=fill, outline="#050500")
                if (x, y) in m["terms"]:
                    n = m["terms"][(x, y)]
                    canvas.create_text(x0 + size / 2, y0 + size / 2, text=f"T{n + 1}",
                                       fill=GREEN if n in m["done"] else CYAN, font=(FONT, 9, "bold"))
                elif (x, y) == (19, 9):
                    canvas.create_text(x0 + size / 2, y0 + size / 2, text="EXIT", font=(FONT, 7, "bold"),
                                       fill=GREEN if len(m["done"]) == 4 else RED)
        cx, cy = px * size + size / 2, py * size + size / 2
        canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=GREEN, outline=WHITE, width=2)
        vx, vy = m["virus"]
        if (vx - px) ** 2 + (vy - py) ** 2 <= reach ** 2:
            cx, cy = vx * size + size / 2, vy * size + size / 2
            canvas.create_oval(cx - 9, cy - 9, cx + 9, cy + 9, fill=RED, outline=WHITE, width=2)
            canvas.create_text(cx, cy, text="V", fill=WHITE, font=(FONT, 9, "bold"))

    def maze_status(self):
        m = self.maze
        near = abs(m["virus"][0] - m["player"][0]) + abs(m["virus"][1] - m["player"][1]) <= 6
        text = f"TERMINALS {len(m['done'])}/4   KEY WORDS: {' '.join(m['words']) or '-'}"
        self.maze_hud.configure(text=text + ("      !! VIRUS NEARBY !!" if near else ""),
                                fg=RED if near else YELLOW)

    def maze_move(self, dx, dy):
        m = self.maze
        if self.solved or m["open"]:
            return
        x, y = m["player"][0] + dx, m["player"][1] + dy
        if m["grid"][y][x] == "#":
            return
        m["previous"], m["player"] = m["player"], (x, y)
        if (x, y) == m["virus"]:
            self.maze_caught()
            return
        if (x, y) in m["terms"] and m["terms"][(x, y)] not in m["done"]:
            self.maze_terminal(m["terms"][(x, y)])
        elif (x, y) == (19, 9):
            left = 4 - len(m["done"])
            if left == 0:
                self.maze_draw()
                self.finish_puzzle()
                return
            self.feedback.configure(text=f"EXIT SEALED - {left} terminal(s) still offline.", fg=ORANGE)
        self.maze_draw()
        self.maze_status()

    def maze_caught(self):
        m = self.maze
        m["player"], m["virus"] = (1, 1), (19, 1)
        self.wrong_answer()
        if self.time_left > 0:
            self.feedback.configure(text="THE VIRUS CAUGHT YOU. Back to the start. 5 seconds lost.", fg=RED)
            self.maze_draw()
            self.maze_status()

    def maze_tick(self, token):
        m = self.maze
        if token != self.maze_token or self.solved or self.time_left <= 0:
            return
        try:
            if not m["open"]:
                vx, vy = m["virus"]
                px, py = m["player"]
                options = [(vx + dx, vy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                           if m["grid"][vy + dy][vx + dx] != "#"]
                if random.random() < .55:
                    m["virus"] = min(options, key=lambda c: abs(c[0] - px) + abs(c[1] - py))
                else:
                    m["virus"] = random.choice(options)
                m["flicker"] = random.random() < .08
                if m["virus"] == m["player"]:
                    self.maze_caught()
                else:
                    self.maze_draw()
                    self.maze_status()
            if self.time_left > 0:
                self.safe_after(480, lambda: self.maze_tick(token))
        except tk.TclError:
            pass

    def maze_terminal(self, index):
        term = self.puzzle["terminals"][index]
        self.maze["open"] = True
        self.maze_box = tk.Frame(self.body, bg=PANEL, highlightthickness=3,
                                 highlightbackground=CYAN, padx=14, pady=10)
        self.maze_box.place(relx=.5, rely=.5, anchor="center")
        tk.Label(self.maze_box, text=f"TERMINAL T{index + 1}  //  ANSWER TO RELEASE A KEY WORD",
                 bg=PANEL, fg=CYAN, font=(FONT, 9, "bold")).pack(anchor="w")
        tk.Label(self.maze_box, text=term["q"], bg=PANEL, fg=WHITE, font=(FONT, 10, "bold"),
                 wraplength=430, justify="left").pack(anchor="w", pady=(6, 6))
        for n, option in enumerate(term["options"]):
            self.button(self.maze_box, f"{chr(65 + n)}  //  {option}",
                        lambda k=n: self.maze_answer(index, k), CYAN, 44, font=(FONT, 9, "bold"),
                        wraplength=420, anchor="w", justify="left", pady=5).pack(fill="x", pady=3)

    def maze_answer(self, index, choice):
        m, term = self.maze, self.puzzle["terminals"][index]
        self.maze_box.destroy()
        m["open"] = False
        if choice == term["answer"]:
            m["done"].add(index)
            m["words"].append(term["word"])
            self.log(f"Terminal T{index + 1} unlocked. Key word: {term['word']}", "ok")
            self.feedback.configure(text=f"KEY WORD RECEIVED: {term['word']}", fg=GREEN)
        else:
            m["player"] = m["previous"]
            self.wrong_answer()
            if self.time_left <= 0:
                return
        self.maze_draw()
        self.maze_status()

    def build_phrase(self):
        self.phrase_words = []
        words = list(self.puzzle["words"])
        while words == self.puzzle["words"]:
            random.shuffle(words)
        self.phrase_label = tk.Label(self.body, text="- - - -", bg="#05080e", fg=GREEN,
                                     font=(FONT, 18, "bold"), pady=16, wraplength=640)
        self.phrase_label.pack(fill="x", pady=(0, 10))
        tk.Label(self.body, text="Click the key words in the right order:", bg=PANEL, fg=MUTED,
                 font=(FONT, 9)).pack()
        tiles = tk.Frame(self.body, bg=PANEL)
        tiles.pack(pady=10)
        self.phrase_tiles = []
        for i, word in enumerate(words):
            tile = self.button(tiles, word, lambda k=i: self.phrase_add(k), GREEN, 9,
                               font=(FONT, 12, "bold"), pady=6)
            tile.pack(side="left", padx=5)
            self.phrase_tiles.append((word, tile))
        row = tk.Frame(self.action_area, bg=PANEL)
        row.pack()
        self.button(row, "BREAK THE LOCK", self.check_phrase, GREEN, 18).pack(side="left", padx=6)
        self.button(row, "CLEAR", self.phrase_clear, ORANGE, 10).pack(side="left", padx=6)

    def phrase_add(self, index):
        word, tile = self.phrase_tiles[index]
        if self.solved or not tile.enabled:
            return
        tile.lock(MUTED)
        self.phrase_words.append(word)
        self.phrase_label.configure(text=" ".join(self.phrase_words))

    def phrase_clear(self):
        if self.solved:
            return
        self.phrase_words = []
        self.phrase_label.configure(text="- - - -")
        for _word, tile in self.phrase_tiles:
            tile.unlock(GREEN)

    def check_phrase(self):
        if self.solved:
            return
        if " ".join(self.phrase_words) == self.puzzle["answer"]:
            self.finish_puzzle()
        else:
            self.phrase_clear()
            self.wrong_answer()

    def show_escape_page(self):
        self.clear_screen()
        self.add_backdrop()
        footer = tk.Frame(self.container, bg=BG)
        footer.pack(side="bottom", pady=(4, 12))
        self.button(footer, "SEE MY FINAL SCORE  >", self.show_final, GREEN, 26).pack()
        self.title_label(self.container, "YOU SURVIVED THE ESCAPE", GREEN, 30).pack(pady=(14, 0))
        tk.Label(self.container, text=f"{self.agent_display()}   |   THE BACKROOMS ARE BEHIND YOU",
                 bg=BG, fg=YELLOW, font=(FONT, 11, "bold")).pack(pady=(0, 6))
        door = tk.Canvas(self.container, width=420, height=110, bg=BG, highlightthickness=0)
        door.pack()
        door.create_rectangle(110, 5, 310, 105, outline=GREEN, width=3, tags="frame")

        def open_door(step=0):
            door.delete("light")
            half = 4 + step * 7
            door.create_rectangle(210 - half, 8, 210 + half, 102, outline="", tags="light",
                                  fill=self.shade("#fff2a0", .2 + step * .06))
            door.tag_raise("frame")
            if step < 12:
                self.safe_after(110, lambda: open_door(step + 1))

        open_door()
        card = self.card(self.container, GREEN)
        card.pack(fill="both", expand=True, padx=70, pady=8)
        self.terminal = self.add_terminal(card, height=11)
        self.terminal.configure(highlightbackground=GREEN)
        self.terminal.pack(fill="both", expand=True)
        for text, tag in (
            ("Final lock released. Every door in the Archive is open.", "ok"),
            ("You did not escape by luck. You escaped by thinking before clicking.", "info"),
            ("YOUR SURVIVAL RULES, REAL ONES YOU CAN USE TODAY:", "warn"),
            ("1. Pause: urgency is a hacker's favourite tool.", "ok"),
            ("2. Verify: use the official app or a number you already know.", "ok"),
            ("3. Long, unique passwords plus two-step sign-in beat guessing bots.", "ok"),
            ("4. Report strange things early: logs and evidence save the day.", "ok"),
            ("5. Keep backups and updates: they turn a disaster into an inconvenience.", "ok"),
            ("Attackers only need you to be careless once. Defenders only need to stay curious.", "lesson"),
            ("Out there the attacker is not behind a door. They are behind a message.", "pink"),
            ("So stay alert, stay curious, and remember: YOU are the firewall.", "warn"),
        ):
            self.terminal.say(text, tag, speed=4, prefix="  ")

    def finish_puzzle(self):
        if self.solved:
            return
        self.solved = True
        points = POINTS_BY_MISTAKES[min(self.wrong, len(POINTS_BY_MISTAKES)-1)]
        self.credits += points
        self.update_credits_label()
        self.badges.add("First Break-In")
        self.feedback.configure(text=f"ACCESS GRANTED  +{points} credits.  Lesson: {self.puzzle['why']}", fg=GREEN)
        self.flash(self.feedback, (GREEN, BG), (BG, GREEN), times=6, delay=85)
        self.flash_puzzle_banner("ACCESS GRANTED", GREEN)
        self.log(f"Puzzle {self.puzzle_index+1} solved. +{points} credits.")
        self.log("LESSON: " + self.puzzle["why"], "lesson")
        for widget in self.body.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.configure(state="disabled")
        for widget in self.action_area.winfo_children():
            widget.destroy()
        label = "OPEN SECTOR EXIT  >" if self.puzzle_index == len(self.sector["puzzles"])-1 else "NEXT PUZZLE  >"
        self.button(self.action_area, label, self.next_puzzle,
                    GREEN if "EXIT" in label else self.sector["color"], 24).pack()
        self.hint_button.configure(state="disabled")

    def next_puzzle(self):
        self.puzzle_index += 1
        if self.puzzle_index >= len(self.sector["puzzles"]):
            self.complete_sector()
        else:
            self.load_puzzle()

    def use_hint(self):
        if self.solved or self.hint_used_this_puzzle:
            return
        if self.credits < HINT_COST:
            self.feedback.configure(text="Not enough credits for a hint.", fg=RED)
            return
        self.credits -= HINT_COST
        self.hints_used += 1
        self.hint_used_this_puzzle = True
        self.update_credits_label()
        self.feedback.configure(text="HINT: " + self.puzzle["hint"], fg=YELLOW)
        self.log(f"Hint used (-{HINT_COST} credits): {self.puzzle['hint']}", "warn")
        self.hint_button.configure(state="disabled")

    def complete_sector(self):
        self.clear_screen()
        self.add_backdrop()
        index = self.sector_index
        bonus = max(0, self.time_left // 15)
        self.credits += bonus
        earned = self.credits - self.sector_start_credits
        self.best[index] = max(self.best.get(index, 0), earned)
        self.cleared.add(index)
        if index + 1 < len(SECTORS):
            self.unlocked.add(index + 1)
        new_badges = []
        def award(name):
            if name not in self.badges:
                self.badges.add(name)
                new_badges.append(name)
        if self.sector_wrong == 0:
            award("Clean Sector")
        if self.time_left > SECTORS[index]["time"] // 2:
            award("Quick Thinker")
        escaped = len(self.cleared) == len(SECTORS)
        if escaped:
            award("Archive Survivor")
            if self.hints_used == 0:
                award("No Hints Used")
        banner = tk.Label(self.container, text="  SECTOR EXIT UNLOCKED  ",
                          bg=self.sector["color"], fg=BG, font=(FONT, 23, "bold"),
                          padx=14, pady=8)
        banner.pack(pady=(22, 5))
        self.flash(banner, (self.sector["color"], BG), (BG, self.sector["color"]),
                   times=10, delay=105)
        self.title_label(self.container, "SECTOR CLEARED", self.sector["color"], 26).pack(pady=(0, 2))
        tk.Label(self.container, text=self.sector["room"].upper(), bg=BG,
                 fg=WHITE, font=(FONT, 14, "bold")).pack()
        result = self.card(self.container, self.sector["color"])
        result.pack(fill="both", expand=True, padx=170, pady=10)
        tk.Label(result, text="DECRYPTED ROOM REPORT  //  SCORE UPLOAD",
                 bg=PANEL, fg=self.sector["color"], font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.terminal = self.add_terminal(result, height=7)
        self.terminal.configure(highlightbackground=self.sector["color"])
        self.terminal.pack(fill="both", expand=True)
        self.terminal.scan("Calculating room score and opening the next lock", "info")
        self.terminal.say(f"Puzzle credits earned: {earned-bonus}", "ok", speed=4)
        self.terminal.say(f"Time bonus ({self.time_left} seconds remaining): +{bonus}", "warn", speed=4)
        self.terminal.say(f"Wrong attempts: {self.sector_wrong}", "error" if self.sector_wrong else "ok", speed=4)
        self.terminal.say(f"TOTAL MISSION CREDITS: {self.credits}", "info", speed=4)
        for badge in new_badges:
            self.terminal.say(f"NEW BADGE: {badge}", "pink", speed=4)
        if new_badges:
            tk.Label(result, text="BADGES: " + "  |  ".join(new_badges), bg=PANEL,
                     fg=YELLOW, font=(FONT, 9, "bold"), wraplength=600).pack(anchor="w", pady=(8, 0))
        if escaped:
            self.button(self.container, "OPEN THE FINAL DOOR  >", self.show_escape_page, GREEN,
                        30).pack(side="bottom", before=result, pady=12)
        else:
            next_sector = SECTORS[index + 1]
            self.button(self.container, "RETURN TO SECTOR MAP", self.show_dashboard, CYAN,
                        28).pack(side="bottom", before=result, pady=10)
            next_label = tk.Label(self.container, text=f"NEXT ACCESS UNLOCKED: {next_sector['name']}",
                                  bg=BG, fg=next_sector["color"], font=(FONT, 10, "bold"))
            next_label.pack(side="bottom", before=result, pady=5)
            self.pulse_label(next_label, (next_sector["color"], WHITE), 350)

    def show_intel_room(self):
        """Open a set of transparent, offline-only cybersecurity heuristics."""
        self.clear_screen()
        self.add_backdrop()
        masthead = tk.Frame(self.container, bg=BG)
        masthead.pack(fill="x", padx=22, pady=(12, 7))
        heading = tk.Label(masthead, text="CYBER INTEL ROOM", bg=BG, fg=PURPLE,
                           font=(FONT, 23, "bold"))
        heading.pack(side="left")
        self.pulse_label(heading, (PURPLE, CYAN, PURPLE, GREEN), 470)
        tk.Label(masthead, text="TRAINING CHECKS ONLY  //  LINKS ARE NEVER OPENED",
                 bg=BG, fg=GREEN, font=(FONT, 9, "bold")).pack(side="right")

        warning = tk.Frame(self.container, bg="#21121b", highlightthickness=2,
                           highlightbackground=PINK, padx=10, pady=6)
        warning.pack(fill="x", padx=22, pady=(0, 8))
        tk.Label(warning,
                 text="These simple checks can point out warning signs, but can be wrong. They cannot prove that a link or message is safe.",
                 bg="#21121b", fg=PINK, font=(FONT, 9, "bold"),
                 wraplength=1000, justify="left").pack(anchor="w")

        shell = tk.Frame(self.container, bg=BG)
        shell.pack(fill="both", expand=True, padx=22, pady=(0, 8))
        nav = tk.Frame(shell, bg=PANEL, width=238, highlightthickness=2,
                       highlightbackground=PURPLE, padx=10, pady=10)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        tk.Label(nav, text="PICK A SIMPLE TOOL", bg=PANEL, fg=CYAN,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 8))
        entries = [
            ("url", "01  CHECK A LINK", CYAN),
            ("message", "02  CHECK A MESSAGE", ORANGE),
            ("password", "03  PASSWORD TIPS", GREEN),
            ("file", "04  CHECK A FILE NAME", PINK),
        ]
        for key, label, color in entries:
            self.button(nav, label, lambda tab=key: self.open_intel_tab(tab),
                        color, 21, anchor="w").pack(fill="x", pady=4)
        tk.Frame(nav, bg="#27334a", height=1).pack(fill="x", pady=10)
        self.intel_counter_label = tk.Label(nav, text="CHECKS RUN: 0",
                                            bg=PANEL, fg=YELLOW,
                                            font=(FONT, 10, "bold"), justify="left")
        self.intel_counter_label.pack(anchor="w", pady=5)
        self.intel_badge_label = tk.Label(nav, text="TOOLS TRIED: 0/4",
                                          bg=PANEL, fg=PURPLE,
                                          font=(FONT, 9), justify="left")
        self.intel_badge_label.pack(anchor="w", pady=4)
        tk.Label(nav, text="Works on this computer.\nNever enter a real password.",
                 bg=PANEL, fg=MUTED, font=(FONT, 8), justify="left").pack(anchor="w", side="bottom", pady=6)

        self.intel_body = tk.Frame(shell, bg=PANEL, highlightthickness=2,
                                   highlightbackground=CYAN, padx=16, pady=12)
        self.intel_body.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.open_intel_tab(self.intel_tab)

        footer = tk.Frame(self.container, bg=BG)
        footer.pack(side="bottom", before=shell, fill="x", padx=22, pady=(0, 10))
        self.button(footer, "BACK TO SECTOR MAP", self.show_dashboard, CYAN, 22).pack(side="left")
        self.button(footer, "BACK TO TITLE", self.show_menu, MUTED, 18).pack(side="right")

    def open_intel_tab(self, tab):
        """Switch the investigation workspace without changing the mission timer."""
        self.intel_tab = tab
        if not hasattr(self, "intel_body"):
            return
        for widget in self.intel_body.winfo_children():
            widget.destroy()
        builders = {
            "url": self.build_url_tool,
            "message": self.build_message_tool,
            "password": self.build_password_tool,
            "file": self.build_file_tool,
        }
        builders.get(tab, self.build_url_tool)()
        self.update_intel_counters()

    def intel_title(self, title, subtitle, color=CYAN):
        """Show a short heading above one Intel Room tool."""
        bar = tk.Frame(self.intel_body, bg=self.shade(color, 0.18),
                       highlightthickness=1, highlightbackground=color, padx=10, pady=7)
        bar.pack(fill="x", pady=(0, 10))
        heading = tk.Label(bar, text=title, bg=self.shade(color, 0.18), fg=color,
                           font=(FONT, 13, "bold"))
        heading.pack(anchor="w")
        self.pulse_label(heading, (color, WHITE, color), 500)
        tk.Label(bar, text=subtitle, bg=self.shade(color, 0.18), fg=WHITE,
                 font=(FONT, 8), justify="left", wraplength=750).pack(anchor="w", pady=(4, 0))

    def intel_explanation(self, explanation, color=CYAN):
        """Add a bright, easy-to-read box that says what the current tool is for."""
        box = tk.Frame(self.intel_body, bg=self.shade(color, 0.12),
                       highlightthickness=2, highlightbackground=color, padx=10, pady=6)
        box.pack(fill="x", pady=(0, 8))
        tk.Label(box, text="WHAT IS THIS TOOL FOR?", bg=self.shade(color, 0.12),
                 fg=color, font=(FONT, 9, "bold")).pack(anchor="w")
        tk.Label(box, text=explanation, bg=self.shade(color, 0.12), fg=WHITE,
                 font=(FONT, 9), wraplength=740, justify="left").pack(anchor="w", pady=(3, 0))

    def intel_entry(self, parent, label, width=64, secret=False):
        """Create a labeled, high-contrast input for the current local tool."""
        tk.Label(parent, text=label, bg=PANEL, fg=WHITE,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(5, 4))
        field = tk.Entry(parent, font=(FONT, 11), bg="#03070b", fg=GREEN,
                         insertbackground=GREEN, relief="flat", width=width,
                         highlightthickness=2, highlightbackground="#35415a",
                         highlightcolor=CYAN, show="*" if secret else "")
        field.pack(fill="x", pady=(0, 6), ipady=8)
        return field

    def intel_textbox(self, parent, label, height=7):
        """Create an editable dark text area for a message or report."""
        tk.Label(parent, text=label, bg=PANEL, fg=WHITE,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(5, 4))
        field = tk.Text(parent, height=height, bg="#03070b", fg=GREEN,
                        insertbackground=GREEN, font=(FONT, 10), wrap="word",
                        relief="flat", bd=0, padx=9, pady=8,
                        highlightthickness=2, highlightbackground="#35415a",
                        highlightcolor=CYAN)
        field.pack(fill="both", expand=True, pady=(0, 6))
        return field

    def build_url_tool(self):
        self.intel_title("01  //  CHECK A LINK", "Look at the web address before you decide whether to trust it.", CYAN)
        self.intel_explanation(
            "This checks the letters and words in a web address and points out things that may look unusual. "
            "Use it when a link arrives in an email, text, or chat. It does not open the link. Its number is only a count of possible warning signs, not a safety promise.",
            CYAN)
        self.url_input = self.intel_entry(self.intel_body, "PASTE A LINK HERE OR TRY AN EXAMPLE", 72)
        demo = tk.Frame(self.intel_body, bg=PANEL)
        demo.pack(fill="x", pady=4)
        tk.Label(demo, text="TRY AN EXAMPLE:", bg=PANEL, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(side="left")
        for label, value in (
            ("Look-alike", "https://paypa1-login.example/verify"),
            ("Number address", "http://192.0.2.44/account"),
            ("Regular web address", "https://example.org/news"),
        ):
            self.button(demo, label, lambda v=value: self.fill_intel_example(self.url_input, v),
                        PURPLE, 12).pack(side="left", padx=4)
        self.button(self.intel_body, "CHECK THIS LINK", self.run_url_scan, CYAN, 25).pack(anchor="w", pady=7)
        self.url_result = tk.Frame(self.intel_body, bg=PANEL)
        self.url_result.pack(fill="both", expand=True, pady=(4, 0))
        tk.Label(self.url_result,
                 text="The result will show possible warning signs. No warning signs does not guarantee safety.",
                 bg=PANEL, fg=MUTED, font=(FONT, 9), justify="left").pack(anchor="w")

    def build_message_tool(self):
        self.intel_title("02  //  CHECK A MESSAGE", "Look for words that may be trying to rush or trick you.", ORANGE)
        self.intel_explanation(
            "This checks the words in an email or text for warning signs, such as a rush, a request for a code, "
            "or an unusual payment. Use it to help decide when to stop and double-check. It cannot tell who really sent the message.",
            ORANGE)
        self.message_input = self.intel_textbox(self.intel_body,
                                                "PASTE A MESSAGE (REMOVE NAMES AND PRIVATE DETAILS FIRST)", 7)
        sample = ("URGENT: Your account will be suspended in 10 minutes.\n"
                  "Reply with your OTP and click here to verify your bank details.")
        row = tk.Frame(self.intel_body, bg=PANEL)
        row.pack(fill="x", pady=5)
        self.button(row, "SHOW EXAMPLE", lambda: self.fill_intel_text(self.message_input, sample),
                    YELLOW, 24).pack(side="left")
        self.button(row, "CHECK THIS MESSAGE", self.run_message_scan, ORANGE, 25).pack(side="left", padx=8)
        self.message_result = tk.Frame(self.intel_body, bg=PANEL)
        self.message_result.pack(fill="both", expand=True, pady=(4, 0))

    def build_password_tool(self):
        self.intel_title("03  //  PASSWORD TIPS", "Try a made-up sample to see simple ways to make a password stronger.", GREEN)
        self.intel_explanation(
            "This gives simple tips about the length and pattern of a made-up password. Use it to learn why long, different passwords are helpful. "
            "Do not type a password you use for a real account. The sample is not added to your notes.",
            GREEN)
        self.password_input = self.intel_entry(self.intel_body,
                                               "TYPE A MADE-UP SAMPLE — NEVER YOUR REAL PASSWORD", 42, secret=True)
        self.password_input.bind("<KeyRelease>", self.preview_password_strength)
        self.password_meter = tk.Canvas(self.intel_body, height=22, bg="#03070b",
                                        highlightthickness=1, highlightbackground=GREEN)
        self.password_meter.pack(fill="x", pady=(4, 10))
        row = tk.Frame(self.intel_body, bg=PANEL)
        row.pack(fill="x")
        self.button(row, "GET PASSWORD TIPS", self.run_password_scan, GREEN, 23).pack(side="left")
        self.button(row, "CLEAR SAMPLE", self.clear_password_field, MUTED, 15).pack(side="left", padx=8)
        self.password_result = tk.Frame(self.intel_body, bg=PANEL)
        self.password_result.pack(fill="both", expand=True, pady=10)
        tk.Label(self.password_result, text="Nothing you type here is written to the case notebook.",
                 bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w")

    def build_file_tool(self):
        self.intel_title("04  //  CHECK A FILE NAME", "Look at the file name before you open a file you were sent.", PINK)
        self.intel_explanation(
            "This checks only the letters after the last dot in a file name (for example, .pdf or .exe). "
            "It can point out a risky-looking ending, but it does not open or check the file itself.",
            PINK)
        self.filename_input = self.intel_entry(self.intel_body,
                                               "TYPE A FILE NAME", 60)
        self.filename_input.insert(0, "invoice.pdf.exe")
        self.filename_input.bind("<Return>", lambda _event: self.run_file_scan())
        row = tk.Frame(self.intel_body, bg=PANEL)
        row.pack(fill="x", pady=5)
        self.button(row, "CHECK THIS FILE NAME", self.run_file_scan, PINK, 24).pack(side="left")
        self.button(row, "SHOW AN EXAMPLE", lambda: self.fill_intel_example(self.filename_input, "meeting_notes.docm"),
                    PURPLE, 19).pack(side="left", padx=8)
        self.file_result = tk.Frame(self.intel_body, bg=PANEL)
        self.file_result.pack(fill="both", expand=True, pady=8)

    def fill_intel_example(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, value)

    def fill_intel_text(self, textbox, value):
        textbox.delete("1.0", "end")
        textbox.insert("1.0", value)

    def update_intel_counters(self):
        if hasattr(self, "intel_counter_label"):
            self.intel_counter_label.configure(
                text=f"CHECKS RUN: {self.intel_scans}"
            )
        if hasattr(self, "intel_badge_label"):
            self.intel_badge_label.configure(
                text=f"TOOLS TRIED: {len(self.intel_badges)}/4"
            )

    def add_intel_result(self, parent, title, score, findings, accent, note=None):
        """Render a color-coded score card and list the heuristic evidence."""
        for widget in parent.winfo_children():
            widget.destroy()
        band, band_color = _risk_band(score)
        header = tk.Frame(parent, bg=self.shade(accent, 0.16),
                          highlightthickness=2, highlightbackground=accent, padx=10, pady=7)
        header.pack(fill="x", pady=(0, 8))
        tk.Label(header, text=title, bg=self.shade(accent, 0.16), fg=WHITE,
                 font=(FONT, 9, "bold"), wraplength=640, justify="left").pack(side="left", anchor="w")
        score_frame = tk.Frame(header, bg=self.shade(accent, 0.16))
        score_frame.pack(side="right")
        tk.Label(score_frame, text=f"{score:02d}/100", bg=self.shade(accent, 0.16),
                 fg=band_color, font=(FONT, 15, "bold")).pack()
        tk.Label(score_frame, text=band, bg=self.shade(accent, 0.16),
                 fg=band_color, font=(FONT, 7, "bold")).pack()
        meter = tk.Canvas(parent, height=9, bg="#03070b", highlightthickness=0)
        meter.pack(fill="x", pady=(0, 6))

        def draw_meter(_event=None):
            try:
                meter.delete("all")
                width = max(meter.winfo_width(), 10)
                meter.create_rectangle(0, 0, width, 9, fill="#182235", outline="")
                meter.create_rectangle(0, 0, int(width * score / 100), 9, fill=band_color, outline="")
            except tk.TclError:
                return

        meter.bind("<Configure>", draw_meter)
        parent.after(30, draw_meter)
        if note:
            tk.Label(parent, text=note, bg=PANEL, fg=CYAN,
                     font=(FONT, 8, "bold"), wraplength=680,
                     justify="left").pack(anchor="w", pady=3)
        findings_frame = tk.Frame(parent, bg=PANEL)
        findings_frame.pack(fill="both", expand=True, anchor="w")
        for index, finding in enumerate(findings, 1):
            item = tk.Frame(findings_frame, bg="#0d1420", padx=8, pady=5,
                            highlightthickness=1, highlightbackground="#28334a")
            item.pack(fill="x", pady=2)
            tk.Label(item, text=f"{index:02d}", bg="#0d1420", fg=accent,
                     font=(FONT, 8, "bold")).pack(side="left", anchor="n", padx=(0, 8))
            tk.Label(item, text=finding, bg="#0d1420", fg=WHITE,
                     font=(FONT, 8), justify="left", wraplength=690).pack(side="left", fill="x", expand=True)

    def run_url_scan(self):
        result = analyze_url_offline(self.url_input.get())
        self.intel_scans += 1
        self.intel_badges.add("Link Check")
        self.add_intel_result(self.url_result, f"WEBSITE NAME: {result['host']}",
                              result["score"], result["findings"], CYAN,
                              "This check did not open the link or look up the website online.")
        self.update_intel_counters()

    def run_message_scan(self):
        text = self.message_input.get("1.0", "end-1c")
        if not text.strip():
            self.message_result.configure(bg=PANEL)
            tk.Label(self.message_result, text="Paste a message first, or load the example.",
                     bg=PANEL, fg=YELLOW, font=(FONT, 9)).pack(anchor="w")
            return
        result = analyze_message_offline(text)
        self.intel_scans += 1
        self.intel_badges.add("Message Check")
        self.add_intel_result(self.message_result, "MESSAGE CHECK",
                              result["score"], result["findings"], ORANGE,
                              "WHAT TO DO: " + result["next_step"])
        self.update_intel_counters()

    def preview_password_strength(self, _event=None):
        sample = self.password_input.get()
        result = analyze_password_offline(sample)
        canvas = self.password_meter
        canvas.delete("all")
        width = max(canvas.winfo_width(), 10)
        canvas.create_rectangle(0, 0, width, 22, fill="#101827", outline="")
        fill = int(width * result["score"] / 100)
        color = RED if result["score"] < 40 else (YELLOW if result["score"] < 70 else GREEN)
        if fill:
            canvas.create_rectangle(0, 0, fill, 22, fill=color, outline="")
        canvas.create_text(10, 11, text=f"LOCAL ESTIMATE  {result['score']}/100  •  {result['label']}",
                           anchor="w", fill=BG if fill > width * 0.35 else WHITE,
                           font=(FONT, 8, "bold"))

    def run_password_scan(self):
        secret = self.password_input.get()
        if not secret:
            return
        result = analyze_password_offline(secret)
        self.intel_scans += 1
        self.intel_badges.add("Password Tips")
        self.add_intel_result(self.password_result, result["label"], result["score"],
                              result["findings"], GREEN,
                              f"Length: {result['length']} characters. This sample was not added to your notes.")
        self.update_intel_counters()

    def clear_password_field(self):
        self.password_input.delete(0, "end")
        self.password_meter.delete("all")
        for widget in self.password_result.winfo_children():
            widget.destroy()
        tk.Label(self.password_result, text="Sample cleared from the input field.",
                 bg=PANEL, fg=GREEN, font=(FONT, 9)).pack(anchor="w")

    def run_file_scan(self):
        result = analyze_filename_offline(self.filename_input.get())
        self.intel_scans += 1
        self.intel_badges.add("File Name Check")
        self.add_intel_result(self.file_result,
                              f"FILE NAME: {result['filename']}  |  ENDING: {result['extension']}",
                              result["score"], result["findings"], PINK,
                              "Only the name was checked. The file was not opened or read.")
        self.update_intel_counters()

    # ----- final results and saved leaderboard -------------------------------
    def show_final(self):
        self.clear_screen()
        self.add_backdrop()
        escaped = len(self.cleared) == len(SECTORS)
        rank = rank_for(self.credits, escaped)
        entry = {
            "name": self.player, "score": self.credits, "rank": rank,
            "date": datetime.now().strftime("%d-%m-%Y"), "sectors": len(self.cleared),
        }
        if not self.saved:
            save_score(entry)
            self.saved = True
        color = GREEN if escaped else ORANGE
        headline = "YOU REACHED THE SURFACE" if escaped else "MISSION ENDED"
        title = self.title_label(self.container, headline, color, 27)
        title.pack(pady=(22, 4))
        tk.Label(self.container, text=f"{self.agent_display()}     |     FINAL RANK: {rank}",
                 bg=BG, fg=YELLOW, font=(FONT, 12, "bold")).pack(pady=4)
        tk.Label(self.container,
                 text=f"CREDITS: {self.credits}     SECTORS: {len(self.cleared)}/9     HINTS: {self.hints_used}",
                 bg=BG, fg=CYAN, font=(FONT, 12, "bold")).pack(pady=4)
        tk.Label(self.container, text="BADGES", bg=BG, fg=PINK,
                 font=(FONT, 11, "bold")).pack(pady=(8, 3))
        badges = "   |   ".join(sorted(self.badges)) if self.badges else "No badges yet — keep exploring."
        tk.Label(self.container, text=badges, bg=BG, fg=WHITE,
                 font=(FONT, 9), wraplength=850).pack(pady=4)
        certifications = ", ".join(sorted(self.intel_badges)) if self.intel_badges else "None yet"
        tk.Label(self.container, text="INTEL TOOLS USED: " + certifications,
                 bg=BG, fg=PURPLE, font=(FONT, 9, "bold"),
                 wraplength=850).pack(pady=3)
        record = self.card(self.container, color)
        record.pack(fill="both", expand=True, padx=130, pady=12)
        tk.Label(record, text="SECTOR RECORD", bg=PANEL, fg=color,
                 font=(FONT, 10, "bold")).pack(anchor="w")
        names = [sector["short"] for i, sector in enumerate(SECTORS) if i in self.cleared]
        tk.Label(record, text=", ".join(names) if names else "No sectors cleared",
                 bg=PANEL, fg=WHITE, font=(FONT, 9), wraplength=690,
                 justify="left").pack(anchor="w", pady=8)
        tk.Label(record, text="Score saved locally in leaderboard.json.",
                 bg=PANEL, fg=MUTED, font=(FONT, 8)).pack(anchor="w")
        footer = tk.Frame(self.container, bg=BG)
        footer.pack(side="bottom", before=record, pady=(0, 14))
        self.button(footer, "LEADERBOARD", self.show_leaderboard, YELLOW, 18).pack(side="left", padx=8)
        self.button(footer, "PLAY AGAIN", self.show_menu, GREEN, 16).pack(side="left", padx=8)
        self.button(footer, "EXIT", self.destroy, RED, 12).pack(side="left", padx=8)

    def show_leaderboard(self):
        self.clear_screen()
        self.add_backdrop()
        self.title_label(self.container, "ARCHIVE SURVIVORS", YELLOW, 27).pack(pady=(24, 5))
        tk.Label(self.container, text="TOP 10 SAVED SCORES", bg=BG, fg=MUTED,
                 font=(FONT, 10)).pack()
        table = self.card(self.container, YELLOW)
        table.pack(fill="both", expand=True, padx=65, pady=18)
        headers = ("#", "AGENT", "CREDITS", "RANK", "SECTORS", "DATE")
        widths = (4, 18, 10, 22, 9, 13)
        for col, (label, width) in enumerate(zip(headers, widths)):
            tk.Label(table, text=label, width=width, bg=YELLOW, fg=BG,
                     font=(FONT, 9, "bold"), pady=6).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        scores = load_scores()
        if not scores:
            tk.Label(table, text="No saved runs yet. Be the first to escape.",
                     bg=PANEL, fg=MUTED, font=(FONT, 11), pady=25).grid(
                         row=1, column=0, columnspan=len(headers), sticky="ew")
        for index, score in enumerate(scores[:10], start=1):
            values = (str(index), score.get("name", "?"), str(score.get("score", 0)),
                      score.get("rank", ""), str(score.get("sectors", "-")), score.get("date", ""))
            row_bg = PANEL_LIGHT if index % 2 == 0 else PANEL
            for col, (value, width) in enumerate(zip(values, widths)):
                fg = GREEN if index == 1 else WHITE
                tk.Label(table, text=value, width=width, bg=row_bg, fg=fg,
                         font=(FONT, 9), pady=6).grid(row=index, column=col, sticky="nsew", padx=1, pady=1)
        self.button(self.container, "BACK", self.show_menu, CYAN, 18).pack(side="bottom", before=table, pady=12)


if __name__ == "__main__":
    app = CyberEscapeRoom()
    app.mainloop()
