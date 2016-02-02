#!/usr/bin/env python3
import calendar
import urllib3
import xml.etree.ElementTree as etree
import peewee


class Rate(peewee.Model):
    date = peewee.DateField()
    rate = peewee.DecimalField(decimal_places=4)
    currency = peewee.FixedCharField(max_length=3)

    class Meta:
        database = peewee.MySQLDatabase('test', user='test', passwd='test')

        indexes = (
            # create a unique on from/to/date
            (('date', 'rate', 'currency'), True),)


class NbpParser:
    def __init__(self, num=5, start=calendar.datetime.date.today()):
        self.db = peewee.MySQLDatabase('test', user='test', passwd='test')
        self.num = num
        current_year = calendar.datetime.date.today().year
        if start.year != current_year:
            year = str(start.year)
        else:
            year = ''
        filename = 'dir' + year + '.txt'
        list = self.download_list(filename)
        try:
            Rate.create_table()
        except:
            pass
        for i in list:
            xml = self.get_xml(i)
            waluta = 'USD'
            kurs = self.parse_xml(xml, waluta)
            date = calendar.datetime.date(year=int('20' + i[5:7]), month=int(i[7:9]), day=int(i[9:11]))
            print(date, waluta, kurs)
            rk = Rate(rate=kurs, currency=waluta, date=date)
            try:
                rk.save()
            except:
                pass
            waluta = 'GBP'
            kurs = self.parse_xml(xml, waluta)
            date = calendar.datetime.date(year=int('20' + i[5:7]), month=int(i[7:9]), day=int(i[9:11]))
            print(date, waluta, kurs)
            rk = Rate(rate=kurs, currency=waluta, date=date)
            try:
                rk.save()
            except:
                pass
            waluta = 'EUR'
            kurs = self.parse_xml(xml, waluta)
            date = calendar.datetime.date(year=int('20' + i[5:7]), month=int(i[7:9]), day=int(i[9:11]))
            print(date, waluta, kurs)
            rk = Rate(rate=kurs, currency=waluta.lower(), date=date)
            try:
                rk.save()
            except:
                pass

    def download_list(self, filename):
        self.http = urllib3.PoolManager()
        r = self.http.request('GET', 'http://www.nbp.pl/kursy/xml/' + filename)
        if r.status != 200:
            raise ConnectionError('cannot download list file')
        data = r.data.decode('utf-8-sig').splitlines()
        data = [d for d in data if (d[0] == 'a')]
        if self.num > len(data):
            self.num = len(data)
        lim = - self.num
        return data[lim::]

    def get_xml(self, filename):
        r = self.http.request('GET', 'http://www.nbp.pl/kursy/xml/' + filename + '.xml')
        root = etree.ElementTree(etree.fromstring(r.data)).getroot()
        return root

    def parse_xml(self, xml, currency):
        for i in xml:
            if i.tag == 'pozycja':
                k = False
                for j in i.iter():
                    if j.tag == 'kod_waluty' and j.text == currency:
                        k = True
                if k == True:
                    for j in i.iter():
                        if j.tag == 'kurs_sredni':
                            t = list(j.text)
                            poz = 0
                            for m in t:
                                if m == ',':
                                    t[poz] = '.'
                                poz += 1
                            return float(''.join(t))


if __name__ == '__main__':
    NbpParser(num=1000, start=calendar.datetime.date(2014, 1, 1))
    NbpParser(num=1000, start=calendar.datetime.date(2015, 1, 1))
    NbpParser(num=7, start=calendar.datetime.date(2016, 1, 1))
