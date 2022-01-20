from ltp import LTP
import jieba.analyse


class Extracter:
    def __init__(self):
        self.ltp = LTP()
        self.ltp.init_dict('special_words.txt')
        self.ltp.init_dict('dict.txt')
        self.ltp.init_dict('dict2.txt')
        self.ltp.init_dict('ultimate_accusations_dict.txt')
        self.eth_dict = {}
        self.init_ethnicity_dict()
        self.seg = None
        self.hidden = None
        self.pos = None
        self.srl = None
        self.names = []
        self.birthplace = []
        self.ethnicity = []
        self.gender = []
        self.causes = []
        self.courts_concerned = []

    def init_ethnicity_dict(self):
        with open('ethnicity.txt', encoding='utf-8') as file:
            for line in file:
                self.eth_dict[line.replace('\n', '')] = True

    def seg_sentences(self, sentences):
        self.seg, self.hidden = self.ltp.seg(sentences)

    def seg_and_pos(self, sentences):
        self.seg_sentences(sentences)
        self.pos = self.ltp.pos(self.hidden)

    def seg_pos_srl(self, sentences):
        self.seg_and_pos(sentences)
        self.srl = self.ltp.srl(self.hidden, keep_empty=False)

    def extract_criminal_basic_info(self, sentences):
        self.seg_and_pos(sentences)
        birth_place_flags = ['户籍地', '出生于', '住']
        birth_place_flag = ''
        stop_sign = ['，', '。']

        for i in range(3):
            if birth_place_flags[i] in self.seg[0]:
                birth_place_flag = birth_place_flags[i]
                break

        assert birth_place_flag != ''

        for i in range(len(self.seg[0])):
            if self.pos[0][i] == 'nh':
                self.names.append(self.seg[0][i])
            if self.seg[0][i] == '男' or self.seg[0][i] == '女':
                self.gender.append(self.seg[0][i])
            if self.seg[0][i] in self.eth_dict:
                self.ethnicity.append(self.seg[0][i])
            if self.seg[0][i] == birth_place_flag:
                index = i + 1
                birth_place = ''
                while self.seg[0][index] not in stop_sign:
                    birth_place += self.seg[0][index]
                    index += 1
                self.birthplace.append(birth_place)

        self.ltp.add_words(self.names)

    def extract_principal_crime_info(self, sentences):
        self.seg_pos_srl(sentences)
        for i in range(len(self.seg[0])):
            if (self.pos[0][i] == 'ns' or self.pos[0][i] == 'ni') and ('法院' in self.seg[0][i]):
                self.courts_concerned.append(self.seg[0][i])
        index = self.seg[0].index('指控')
        tmp = ''
        cur = index + 4
        while cur < len(self.seg[0]) and self.seg[0][cur] != '一案':
            tmp += self.seg[0][cur]
            cur += 1
        self.causes.append(tmp)

    def scan_rest_sentences(self, sentences):
        self.seg_and_pos(sentences)
        for i in range(len(self.seg)):
            for j in range(len(self.seg[i])):
                if (self.pos[i][j] == 'ns' or self.pos[i][j] == 'ni') and '法院' in self.seg[i][j]:
                    self.courts_concerned.append(self.seg[i][j])

    def extract_by_tfidf(self, raw_content):
        names = jieba.analyse.extract_tags(raw_content, topK=100, allowPOS=['n'])
        index = 1
        pass

    """for test usage"""

    def print_out(self):
        print('name: ', self.names)
        print('birthplace: ', self.birthplace)
        print('gender: ', self.gender)
        print('ethnicity: ', self.ethnicity)
        print('courts: ', self.courts_concerned)
        print('causes: ', self.causes)



