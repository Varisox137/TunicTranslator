from typing import Union, Literal

from selenium import webdriver

vowels={
    #     0b_000001: top-right
    #     0b_000010: top-left
    #     0b_000100: upper-left (connected to the middle)
    #     0b_001000: lower-left (unconnected, ==upper-left)
    #     0b_010000: bottom-left
    #     0b_100000: bottom-right
    'ə' : 0b_000011, # 'a'   as in banana; =='u'
    'æ' : 0b_001111, # 'ae'  as in hat
    'ɛr': 0b_101100, # 'air' as in air
    'ɑr': 0b_110011, # 'ar'  as in far
    'ɔ' : 0b_001110, # 'aw'  as in law
    'eɪ': 0b_000010, # 'ay'  as in hay
    'ɛ' : 0b_111100, # 'e'   as in pet
    'e' : 0b_111100, # =='e'
    'i' : 0b_111110, # 'ee'  as in meet
    'ɪr': 0b_101110, # 'eer' as in beer
    'ər': 0b_111101, # 'er'  as in wonder; =='ir'
    'ɪ' : 0b_110000, # 'i'   as in hit
    'aɪ': 0b_000001, # 'ie'  as in pie
    'ɜr': 0b_111101, # 'ir'  as in bird
    'ɑ' : 0b_001110, # 'o'   as in lock; =='aw'
    'oʊ': 0b_111111, # 'oe'  as in toe
    'ʊ' : 0b_011100, # 'oo'  as in book
    'u' : 0b_011111, # 'ooo' as in toon
    'ɔr': 0b_101111, # 'or'  as in more
    'aʊ': 0b_100000, # 'ow'  as in how
    'ɔɪ': 0b_010000, # 'oy'  as in toy
    'ʌ' : 0b_000011, # 'u'   as in sunny
}

consonants={
    #    0b_0_000001_000000: upper-right
    #    0b_0_000010_000000: upper-middle
    #    0b_0_000100_000000: upper-left
    #    0b_0_001000_000000: lower-left
    #    0b_0_010000_000000: lower-middle
    #    0b_0_100000_000000: lower-right
    #    0b_1_000000_000000: upper-center (connected to the middle, ==(upper-middle OR lower-middle))
    'b': 0b_1_100010_000000, # 'b'  as in bat
    'ʧ': 0b_1_010100_000000, # 'ch' as in chat
    'd': 0b_1_101010_000000, # 'd'  as in debt
    'ð': 0b_1_111010_000000, # 'dh' as in this
    'f': 0b_1_011001_000000, # 'f'  as in fret
    'ɡ': 0b_1_110001_000000, # 'g'  as in get
    'h': 0b_1_110010_000000, # 'h'  as in hat
    'ʤ': 0b_1_001010_000000, # 'j'  as in jet
    'k': 0b_1_100011_000000, # 'k'  as in kid
    'l': 0b_1_010010_000000, # 'l'  as in let
    'm': 0b_0_101000_000000, # 'm'  as in met
    'n': 0b_0_101100_000000, # 'n'  as in net
    'ŋ': 0b_1_111111_000000, # 'ng' as in king
    'p': 0b_1_010001_000000, # 'p'  as in pet
    'r': 0b_1_010011_000000, # 'r'  as in rat
    's': 0b_1_011011_000000, # 's'  as in sat
    'ʃ': 0b_1_111101_000000, # 'sh' as in ship
    't': 0b_1_010101_000000, # 't'  as in tent
    'θ': 0b_1_010111_000000, # 'th' as in thin
    'v': 0b_1_100110_000000, # 'v'  as in vet
    'w': 0b_0_000101_000000, # 'w'  as in wet
    'j': 0b_1_010110_000000, # 'y'  as in yet
    'z': 0b_1_110110_000000, # 'z'  as in zit
    'ʒ': 0b_1_101111_000000, # 'zh' as in casual
}

def __initialize_webdriver(accent:Literal['en','us'])->webdriver.Edge:
    # using https://tophonetics.com/ with selenium

    # check accent
    if accent not in ['en','us']:
        raise ValueError(f'Unsupported accent: {accent}')

    # initialize
    options=webdriver.EdgeOptions()
    options.add_argument('--headless')
    driver=webdriver.Edge(options=options)
    driver.get('https://tophonetics.com/')

    # settings
    dialect_label=1 if accent=='en' else 2
    dialect_btn=driver.find_element(by='xpath',
                                    value=f'//*[@id="options"]/div[1]/div/div/label[{dialect_label}]')
    dialect_btn.click()
    style_btn=driver.find_element(by='xpath',
                                  value='//*[@id="options"]/div[2]/div/div/label[1]')
    style_btn.click()

    return driver

def slice_tokens_from_string(text:str)->list[str]:
    # preprocess
    text=text.lower().replace('，',',').replace('。','.').replace('？','?').replace('！','!')
    text=text.replace(',',' , ').replace('.',' . ').replace('?',' ? ').replace('!',' ! ')
    text=text.replace('\n',' \n ')

    # split with whitespaces
    split_list=text.split(' ')
    token_list=[]
    for item in split_list:
        if not item: # skip empty string
            continue
        elif item in '.,?!\n':
            while token_list and token_list[-1]==' ':
                token_list.pop() # remove the ending whitespace
        # add the token and a whitespace
        token_list.append(item)
        if item!='\n': # add a whitespace except for newline
            token_list.append(' ')

    # remove the ending whitespace
    if token_list and token_list[-1]==' ':
        token_list.pop()

    return token_list

def __query_phonetics(driver:webdriver.Edge, text:str)->str:
    # input and submit
    input_box=driver.find_element(value='text_to_transcribe')
    input_box.send_keys(text)
    submit_btn=driver.find_element(value='submit')
    submit_btn.click()
    # save results and clear input box
    transcription=driver.find_element(value='transcr_output')
    phonetics=transcription.text
    clear_btn=driver.find_element(value='clear_button')
    clear_btn.click()

    return phonetics

def __encode_word_phonetics(phonetics:str)->list[int]:
    # preprocess
    phonetics=phonetics.replace('ˈ','').replace('ˌ','').replace(' ','')

    # separate phonemes
    phoneme_list=[]
    # reverse phonetics string to handle v-r+v case
    phonetics=phonetics[::-1]
    while phonetics:
        if phonetics[0]!='r' and phonetics[0] in consonants: # consonant
            phoneme_list.append(('c', consonants[phonetics[0]]))
            phonetics=phonetics[1:]
        elif phonetics[0]=='r': # r functionality judgement
            if phoneme_list and phoneme_list[-1][0]=='v': # r as consonant
                phoneme_list.append(('c', consonants['r']))
                phonetics=phonetics[1:]
            else: # -r vowel judgement
                if phonetics[1:] and phonetics[1]+'r' in vowels: # -r vowel
                    phoneme_list.append(('v', vowels[phonetics[1]+'r']))
                    phonetics=phonetics[2:]
                else: # r as consonant
                    phoneme_list.append(('c', consonants['r']))
                    phonetics=phonetics[1:]
        # non-r non-consonant phoneme
        elif phonetics[1:] and phonetics[1]+phonetics[0] in vowels: # double vowel
            phoneme_list.append(('v', vowels[phonetics[1]+phonetics[0]]))
            phonetics=phonetics[2:]
        elif phonetics[0] in vowels: # single vowel
            phoneme_list.append(('v', vowels[phonetics[0]]))
            phonetics=phonetics[1:]
        else:
            raise ValueError(f'Unsupported phoneme found: {phonetics[0]}')
    # flip back the order of phonemes
    phoneme_list=phoneme_list[::-1]

    print(phoneme_list)

    # pair vowels with consonants to form syllables
    reverse=0b_1_0_000000_000000 # reverse the order of consonant and vowel in one syllable
    syllable_list=[]
    cache=[None, None]
    for phoneme in phoneme_list:
        if cache[0] is None: # wait: |__| -> |c_|/|v_|
            cache[0]=phoneme
        elif cache[1] is None: # judgement: |x_|
            if phoneme[0]==cache[0][0]: # replace: |c_|/|v_| -> |c_|/|v_|
                syllable_list.append(cache[0][1])
                cache[0]=phoneme
            elif phoneme[0]=='v': # cv combine: |c_| -> |__|
                syllable_list.append(cache[0][1] | phoneme[1])
                cache[0]=None
            else: # wait: |v_| -> |vc|
                cache[1]=phoneme
        else: # judgement: |vc|
            if phoneme[0]=='v': # v separate & cv combine: |vc| -> |__|
                syllable_list.append(cache[0][1])
                syllable_list.append(cache[1][1] | phoneme[1])
                cache=[None, None]
            else: # vc combine & c wait: |vc| -> |c_|
                # reverse when vc combine instead of cv
                syllable_list.append(cache[0][1] | cache[1][1] | reverse)
                cache=[phoneme, None]
    # combine and add the last syllable
    if cache[0]:
        if cache[1]:
            if cache[0][0]=='c': # cv combine
                syllable_list.append(cache[0][1] | cache[1][1])
            else: # vc combine
                syllable_list.append(cache[0][1] | cache[1][1] | reverse)
        else: # single phoneme
            syllable_list.append(cache[0][1])

    return syllable_list

def encode_full_text(accent:Literal['en','us'], full_text:str)->list[Union[list[int], int]]:
    # initialize webdriver
    print('Initializing webdriver ......')
    driver=__initialize_webdriver(accent)
    # query phonetics for the text as a whole
    print('Querying phonetics from https://tophonetics.com/ ......')
    phonetics_str=__query_phonetics(driver, full_text)
    # split string into tokens
    print('Parsing phonetics ......')
    token_list=slice_tokens_from_string(phonetics_str)

    # encode each token
    encoded_list=[]
    encodings={' ':-1, ',':-2, '.':-3, '!':-4, '?':-5, '\n':-10}
    for token in token_list:
        # encode each non-word token
        if token in encodings:
            encoded_list.append(encodings[token])
        else:
            word_phonetic_list=__encode_word_phonetics(token)
            encoded_list.append(word_phonetic_list)

    # close webdriver
    driver.quit()

    return encoded_list

if __name__=='__main__':
    # test
    phonetics_str=input('Enter word phonetics string: ')
    print(__encode_word_phonetics(phonetics_str))
