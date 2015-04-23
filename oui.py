__author__ = 'Eshin Kunishima'
__license__ = 'MIT License'

import sqlite3
import threading


class OUI:
    def __init__(self):
        self.__db = sqlite3.connect('oui.db', check_same_thread=False)
        self.__lock = threading.Lock()
        self.cache = {}

    def search(self, mac48: str) -> str:
        oui = ':'.join(mac48.split(':')[0:3])

        if oui in self.cache:
            return self.cache[oui]

        self.__lock.acquire()

        cursor = self.__db.cursor()
        cursor.execute('SELECT name FROM oui WHERE oui LIKE ?;', (oui,))

        result = cursor.fetchone()

        self.__lock.release()

        if result:
            self.cache[oui] = result[0]
        else:
            self.cache[oui] = 'Unknown Vendor'

        return self.cache[oui]

    def update(self):
        self.__lock.acquire()

        cursor = self.__db.cursor()

        cursor.execute('DELETE FROM oui;')

        with open('oui.txt', mode='r') as file:
            for line in file:
                if line.find('(hex)') != -1:
                    mac, vendor = line.strip().split("(hex)")

                    try:
                        cursor.execute('INSERT INTO oui VALUES (?, ?);',
                                       (mac.replace('-', ':').replace(' ', ''), vendor.replace('\t', '')))
                    except sqlite3.IntegrityError:
                        print(mac, vendor)

        self.__db.commit()

        self.__lock.release()


if __name__ == "__main__":
    o = OUI()
    o.update()