import requests
import json
from pdfminer.high_level import extract_text
import re
import os
from gooey import Gooey, GooeyParser
OUT_PATH = './reference/'


class paper_query:
    payload = {'format': 'json'}
    hit = False

    def __init__(self, query_string):
        self.payload['q'] = query_string
        self.r = requests.get('https://dblp.org/search/publ/api', params=self.payload)
        self.content = json.loads(self.r.text)

        # with open('r2.json', 'w') as f:
        #     f.write(self.r.text)

        if int(self.content['result']['hits']['@total']) != 0:
            self.hit = True
            self.url = self.content['result']['hits']['hit'][0]['info']['url']


class read_pdf:
    text = ''
    ref_list = []
    valid_ref_urls = []

    def __init__(self, input_file):
        self.text = extract_text(input_file)
        with open('text.txt', 'wb') as f:
            f.write(self.text.encode())

        self.text = self.text.replace('-\n', '')
        self.text = self.text.replace('.\n', '. ')
        self.text = self.text.replace('\n', ' ')
        self.text = self.text.replace('+', '')
        self.text = self.text.replace('', '')

        Ref_pos = [a.start() for a in re.finditer('References', self.text)]

        if len(Ref_pos):
            self.text = self.text[Ref_pos[0]:]

        ref_pattern = re.compile('\[\d+\][^\[\]]*\d\.')
        raw_list = ref_pattern.findall(self.text)

        title_pattern = re.compile('\.[^\.\\\/]*\.')
        for i in raw_list:
            m = title_pattern.search(i)
            if m is None:
                continue
            else:
                title = m.group(0)[2: -1]
                self.ref_list.append(title)

        if not os.path.exists(OUT_PATH):
            os.mkdir(OUT_PATH)

        count = 0
        for i in self.ref_list:
            q = paper_query(i)
            if q.hit is not False:
                print(str(count)+': '+i+' downloaded')
                file_stream = requests.get(q.url+'.bib', stream=True)
                with open(OUT_PATH+i+'.bib', 'wb') as f:
                    f.write(file_stream.content)
                count += 1
