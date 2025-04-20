import requests
import socket
import os
import sys
from time import sleep
from colorama import Fore, Style, init
import dns.resolver

init(autoreset=True)

# === CONFIG ===
TELEGRAM_BOT_TOKEN = '8053762797:AAGYs_0J8bh2bC3vJVaviFvMVJ5RamR4m4Q'
TELEGRAM_CHAT_ID = '7111874161'
CLOUDFLARE_IP_RANGES = [
    '104.', '172.', '173.', '198.', '199.', '203.',
    '2400:', '2606:', '2803:', '2a06:', '2c0f:'
]

CDN_SIGNATURES = {
    'Cloudflare': ['cloudflare'],
    'Akamai': ['akamaitechnologies', 'akamaiedge', 'akamai.net'],
    'Fastly': ['fastly.net'],
    'Amazon CloudFront': ['cloudfront.net'],
    'Google': ['googleusercontent.com'],
    'Microsoft Azure': ['azureedge.net'],
    'Alibaba': ['alicdn.com']
}

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    clear_screen()
    print(Fore.WHITE + r"""
╔══════════════════════════════════════╗
║                                      ║
║   ██████╗  ██████╗ ███╗   ███╗       ║
║  ██╔════╝ ██╔═══██╗████╗ ████║       ║
║  ██║  ███╗██║   ██║██╔████╔██║       ║
║  ██║   ██║██║   ██║██║╚██╔╝██║       ║
║  ╚██████╔╝╚██████╔╝██║ ╚═╝ ██║       ║
║   ╚═════╝  ╚═════╝ ╚═╝     ╚═╝       ║
║         Subdomain Finder             ║
║                                      ║
╚══════════════════════════════════════╝
""")
    print(Fore.RED + "    Author  : Void")
    print(Fore.RED + "    Contact : t.me/bascex")
    print(Fore.RED + "    TEAM    : Red Team Bekasi\n")

def identify_cdn(ip):
    try:
        host = socket.gethostbyaddr(ip)[0]
        for cdn, keywords in CDN_SIGNATURES.items():
            if any(kw in host.lower() for kw in keywords):
                return cdn
        return "Unknown"
    except:
        return "Unknown"

def is_cloudflare(ip):
    return any(ip.startswith(prefix) for prefix in CLOUDFLARE_IP_RANGES)

def check_subdomain(subdomain, cdn_list, non_cdn_list):
    try:
        ip = socket.gethostbyname(subdomain)
        cdn_name = identify_cdn(ip)
        if is_cloudflare(ip):
            print(Fore.YELLOW + f"[CDN] {subdomain} -> {ip} -> Cloudflare")
            cdn_list.append(f"{subdomain} -> {ip} -> Cloudflare")
        elif cdn_name != "Unknown":
            print(Fore.YELLOW + f"[CDN] {subdomain} -> {ip} -> {cdn_name}")
            cdn_list.append(f"{subdomain} -> {ip} -> {cdn_name}")
        else:
            print(Fore.GREEN + f"[OK ] {subdomain} -> {ip} -> No CDN")
            non_cdn_list.append(f"{subdomain} -> {ip} -> No CDN")
    except socket.error:
        pass

def find_subdomains(domain):
    subdomains = set()
    try:
        print(Fore.CYAN + "[+] Mencari subdomain dari crt.sh...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                name = entry.get('name_value')
                if name:
                    for sub in name.split('\n'):
                        sub = sub.strip()
                        if sub.endswith(domain):
                            subdomains.add(sub)
    except Exception as e:
        print(Fore.RED + f"Error saat mencari subdomain: {e}")
    return list(subdomains)

def report_bug(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"[BUG REPORT]\n{pesan}"
    }
    for attempt in range(1, 3):
        try:
            res = requests.post(url, data=data, timeout=10)
            if res.status_code == 200:
                print(Fore.GREEN + "Bug berhasil dilaporkan!")
                return
            else:
                print(Fore.RED + f"[{attempt}] Gagal kirim. Status: {res.status_code}")
        except Exception as e:
            print(Fore.RED + f"[{attempt}] Kesalahan: {e}")
            sleep(2)
    print(Fore.RED + "[!] Gagal mengirim laporan setelah 2 percobaan.")

def select_language():
    clear_screen()
    print("Pilih Bahasa / Choose Language:")
    print("[1] Bahasa Indonesia")
    print("[2] English")
    pilih = input("> ").strip()
    return "id" if pilih == "1" else "en"

def menu():
    lang = select_language()
    while True:
        banner()
        print("Menu:")
        print("[1] Masukkan URL Target")
        print("[2] Batalkan Script")
        print("[3] Laporkan Bug (Otomatis ke Telegram)")
        print("[4] Keluar")
        pilih = input("> ").strip()

        if pilih == "1":
            target = input("Masukkan domain target (tanpa http/https): ").strip()
            subdomains = find_subdomains(target)
            cdn_list = []
            non_cdn_list = []

            print(Fore.CYAN + f"\n[!] Mulai scanning {len(subdomains)} subdomain...")
            sleep(1)

            for sub in subdomains:
                check_subdomain(sub, cdn_list, non_cdn_list)

            with open("cdn.txt", "w") as f:
                f.write("\n".join(cdn_list))

            print(Fore.CYAN + f"\n[✓] Scan selesai. Ditemukan {len(cdn_list)} subdomain pakai CDN.")
            print(Fore.CYAN + f"[✓] Ditemukan {len(non_cdn_list)} subdomain tanpa CDN.")

            if cdn_list:
                print(Fore.YELLOW + "\n[CDN PROTECTED]:")
                for cdn in cdn_list:
                    print(Fore.YELLOW + f" - {cdn}")
            if non_cdn_list:
                print(Fore.GREEN + "\n[NON-CDN]:")
                for noncdn in non_cdn_list:
                    print(Fore.GREEN + f" - {noncdn}")
            input(Fore.CYAN + "\nTekan Enter untuk kembali ke menu...")

        elif pilih == "2":
            print("Script dibatalkan.")
            sleep(1)
        elif pilih == "3":
            clear_screen()
            banner()
            print(Fore.YELLOW + "[!] Laporkan Bug ke Telegram\n")
            pesan = input("Tulis bug yang ingin kamu laporkan: ").strip()
            if pesan == "":
                print(Fore.RED + "Pesan tidak boleh kosong!")
                sleep(2)
                continue
            report_bug(pesan)
            input("\nTekan Enter untuk kembali ke menu...")
        elif pilih == "4":
            print("Keluar...")
            sleep(1)
            sys.exit()
        else:
            print(Fore.RED + "Pilihan tidak valid!")

if __name__ == "__main__":
    menu()
