__author__ = 'Eshin Kunishima'
__license__ = 'MIT License'

import json
import subprocess
import threading
import shlex
import re
import time

from flask import Flask, render_template, Response

from oui import OUI
from epoch import Epoch
from slack import Slack


app = Flask(__name__)
regex_mac48 = re.compile('^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$')
dict_mac_user = {
    'AA:BB:CC:DD:EE:FF': 'LOLCAT'
}
dict_mac_last = {}
lock_dict_mac_last = threading.Lock()
oui = OUI()


def thread_watchdog():
    print('watchdog is running...')

    process = subprocess.Popen(shlex.split('./airodump-ng --berlin 5 --update 1 wlan0'),
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    while process.poll() is None:
        line = process.stdout.readline().decode().rstrip()
        if regex_mac48.match(line):

            if line in dict_mac_user and line in dict_mac_last and int(Epoch()) - int(dict_mac_last[line]) > 1800:
                Slack.notice('TYPE_YOUR_ENDPOINT',
                             '{:s}がプロジェクトルームにいるかもしれません．'.format(dict_mac_user[line]))

            lock_dict_mac_last.acquire()

            dict_mac_last[line] = Epoch()

            lock_dict_mac_last.release()


def thread_anubis():
    print('anubis is running...')

    while True:
        backup()
        time.sleep(600)


def restore():
    lock_dict_mac_last.acquire()

    try:
        with open('backup.tsv', mode='r') as fp:
            for line in fp:
                parts = line.split('\t')
                dict_mac_last[parts[0]] = Epoch(parts[1])
    except FileNotFoundError:
        print('backup.tsv not found.')

    lock_dict_mac_last.release()


def backup():
    lock_dict_mac_last.acquire()

    with open('backup.tsv', mode='w') as fp:
        for mac, last in dict_mac_last.items():
            fp.write('{:s}\t{:d}\n'.format(mac, int(last)))

    lock_dict_mac_last.release()


def generate(api=False):
    result = []

    lock_dict_mac_last.acquire()

    for mac, epoch in dict_mac_last.items():
        client = {}

        if mac in dict_mac_user:
            client.update({'name': dict_mac_user[mac]})
        elif api:
            continue
        else:
            client.update({'name': '妖精さん'})

        if api:
            client.update({'lastseen': int(epoch)})
        else:
            client.update({'lastseen': epoch, 'mac': mac, 'vendor': oui.search(mac)})

        result.append(client)

    lock_dict_mac_last.release()

    result.sort(key=lambda x: int(x['lastseen']), reverse=True)

    return result


def main():
    restore()

    watchdog = threading.Thread(target=thread_watchdog)
    watchdog.daemon = True
    watchdog.start()

    anubis = threading.Thread(target=thread_anubis)
    anubis.daemon = True
    anubis.start()

    app.run(host='0.0.0.0', port=80, debug=False)


@app.route('/')
def view_index():
    return render_template('index.html', stations=generate())


@app.route('/api')
def view_api():
    return Response(json.dumps(generate(api=True)), mimetype='application/json')


@app.route('/favicon.ico')
def view_favicon():
    return Response(None, status=404)


if __name__ == "__main__":
    main()
