import requests
import json
from pdfminer.high_level import extract_text
import re
import os
from gooey import Gooey, GooeyParser
OUT_PATH = './reference/'


class paper_query:
    """
    Here we define a class of paper query
    to retrieve a .dib file of a paper from
    dblp.org with search string and store
    returned info
    """
    payload = {'format': 'json'}  # payload used to send get message to dblp
    hit = False  # hit denotes whether this paper is found on dblp

    def __init__(self, query_string):
        self.payload['q'] = query_string  # fill payload with search string
        self.r = requests.get('https://dblp.org/search/publ/api', params=self.payload)  # get response from dblp
        self.content = json.loads(self.r.text)  # get the loads info into self.content

        if int(self.content['result']['hits']['@total']) != 0:  # if hit
            self.hit = True
            self.url = self.content['result']['hits']['hit'][0]['info']['url']


class read_pdf:
    """
    Here we define a class to read
    a pdf file, analysis its text info
    and use paper_query to get its ref
    """
    text = ''  # transferred text
    ref_list = []  # title of references we get from text
    valid_ref_urls = []  # url of valid references

    def __init__(self, input_file):
        self.text = extract_text(input_file)  # get text content from a pdf file

        # formalize the text, by removing some meaningless characters
        self.text = self.text.replace('-\n', '')
        self.text = self.text.replace('.\n', '. ')
        self.text = self.text.replace('\n', ' ')
        self.text = self.text.replace('+', '')
        self.text = self.text.replace('', '')

        # find the location of "References" in the text
        Ref_pos = [a.start() for a in re.finditer('References', self.text)]

        # Cut the text to get references
        if len(Ref_pos):
            self.text = self.text[Ref_pos[0]:]

        # use regular expression to find all the references
        ref_pattern = re.compile('\[\d+\][^\[\]]*\d\.')
        raw_list = ref_pattern.findall(self.text)

        # process each title to get our retrieving string
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

        # Get reference one by one
        count = 0
        for i in self.ref_list:
            q = paper_query(i)
            if q.hit is not False:
                print(str(count)+': '+i+' downloaded')
                file_stream = requests.get(q.url+'.bib', stream=True)
                with open(OUT_PATH+i+'.bib', 'wb') as f:
                    f.write(file_stream.content)
                count += 1
