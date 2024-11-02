import argparse 
from encoder import slice_tokens_from_string, encode_full_text
from painter import FoxPaint
import json, base64

if __name__=="__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',"--input",
                        help='Read the input from <input_filename>, where the input should be English in plain text. '
                             '(Default: "input.txt")',
                        default='input.txt',metavar='<file>')
    parser.add_argument('-o',"--output",
                        help='Place the output into <output_filename>, where the output file format should be either jpg or png. '
                             '(Default: "output.jpg")',
                        default='output.jpg',metavar='<file>')
    parser.add_argument('-l',"--line",
                        help='Set the number of lines (rows) in the canvas, '
                             'affect the canvas height. (Default: 8)',
                        type=int,default=8,metavar='<int>')
    parser.add_argument('-c',"--char",
                        help='Set the number of characters (columns) per line, '
                             'affect the canvas width. (Default: 25)',
                        type=int,default=25,metavar='<int>')
    parser.add_argument('-a',"--accent",
                        help='Set the accent of language pronunciation, '
                             'either "en" or "us". (Default: us)',
                        type=str,default='us',metavar='<str>')
    parser.add_argument('-m',"--mul",
                        help='Set the size multiplier of the painted runes, '
                             'affect the output picture size. (Default: 2)',
                        type=int,default=2,metavar='<int>')
    args = parser.parse_args()

    # read input file
    with open(args.input, 'r') as file_object:
        full_text_str=file_object.read()

    # preprocess full string
    full_text_str=''.join(slice_tokens_from_string(full_text_str))
    text_b64=base64.b64encode(full_text_str.encode('utf-8')).decode('utf-8')

    # try loading cache from local
    cache_hit=False
    try:
        print('Loading encoding cache ......')
        with open('./encoding.cache', 'r') as cache_file:
            cache_cyphered=cache_file.read()
            cache_encoded=cache_cyphered[1:][::-1]+'='*int(cache_cyphered[0])
            cache_dict=json.loads(base64.b64decode(cache_encoded.encode('utf-8')).decode('utf-8'))
        print('Encoding cache loaded ......')
        if text_b64 in cache_dict and args.accent in cache_dict[text_b64]:
            print('Encoding cache hit ......')
            rune_list=cache_dict[text_b64][args.accent]
            cache_hit=True
        else:
            print('Encoding cache miss ......')
    except FileNotFoundError:
        print('Encoding cache not found ......')
        cache_dict={}

    if not cache_hit:
        print("Encoding full text ......")
        rune_list=encode_full_text(args.accent, full_text_str)
        sub_dict=cache_dict.get(text_b64,{})
        sub_dict.update({args.accent:rune_list})
        cache_dict[text_b64]=sub_dict
        print("Encoding cache saved ......")
    with open('./encoding.cache', 'w') as cache_file:
        cache_json=json.dumps(cache_dict)
        cache_encoded=base64.b64encode(cache_json.encode('utf-8')).decode('utf-8')
        cache_cyphered=str(cache_encoded.count('='))+cache_encoded.rstrip('=')[::-1]
        cache_file.write(cache_cyphered)
    
    print("Generating Runes ......")
    fox=FoxPaint(args.line,args.char,args.mul)
    fox.draw(rune_list)
    fox.save(args.output)
    
    print("Successfully generated Runes!")
