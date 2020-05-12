"""Clean comment text for easier parsing."""

from __future__ import print_function

import re
import string
import argparse
import sys
import json

__author__ = "Jaehyeong Lee"
__email__ = "ivcrkffody96@g.ucla.edu"

# Depending on your implementation,
# this data may or may not be useful.
# Many students last year found it redundant.
_CONTRACTIONS = {
    "tis": "'tis",
    "aint": "ain't",
    "amnt": "amn't",
    "arent": "aren't",
    "cant": "can't",
    "couldve": "could've",
    "couldnt": "couldn't",
    "didnt": "didn't",
    "doesnt": "doesn't",
    "dont": "don't",
    "hadnt": "hadn't",
    "hasnt": "hasn't",
    "havent": "haven't",
    "hed": "he'd",
    "hell": "he'll",
    "hes": "he's",
    "howd": "how'd",
    "howll": "how'll",
    "hows": "how's",
    "id": "i'd",
    "ill": "i'll",
    "im": "i'm",
    "ive": "i've",
    "isnt": "isn't",
    "itd": "it'd",
    "itll": "it'll",
    "its": "it's",
    "mightnt": "mightn't",
    "mightve": "might've",
    "mustnt": "mustn't",
    "mustve": "must've",
    "neednt": "needn't",
    "oclock": "o'clock",
    "ol": "'ol",
    "oughtnt": "oughtn't",
    "shant": "shan't",
    "shed": "she'd",
    "shell": "she'll",
    "shes": "she's",
    "shouldve": "should've",
    "shouldnt": "shouldn't",
    "somebodys": "somebody's",
    "someones": "someone's",
    "somethings": "something's",
    "thatll": "that'll",
    "thats": "that's",
    "thatd": "that'd",
    "thered": "there'd",
    "therere": "there're",
    "theres": "there's",
    "theyd": "they'd",
    "theyll": "they'll",
    "theyre": "they're",
    "theyve": "they've",
    "wasnt": "wasn't",
    "wed": "we'd",
    "wedve": "wed've",
    "well": "we'll",
    "were": "we're",
    "weve": "we've",
    "werent": "weren't",
    "whatd": "what'd",
    "whatll": "what'll",
    "whatre": "what're",
    "whats": "what's",
    "whatve": "what've",
    "whens": "when's",
    "whered": "where'd",
    "wheres": "where's",
    "whereve": "where've",
    "whod": "who'd",
    "whodve": "whod've",
    "wholl": "who'll",
    "whore": "who're",
    "whos": "who's",
    "whove": "who've",
    "whyd": "why'd",
    "whyre": "why're",
    "whys": "why's",
    "wont": "won't",
    "wouldve": "would've",
    "wouldnt": "wouldn't",
    "yall": "y'all",
    "youd": "you'd",
    "youll": "you'll",
    "youre": "you're",
    "youve": "you've"
}

# You may need to write regular expressions.

def sanitize(text):
  #Replace new lines and tab characters with a single space.
  text = re.sub(r'\t|\n|[\#\$\%\&\*\+\/\<\=\>\@\\\^\_\`\{\|\}\~]', '', text).lower()
  
  #Remove URLs. Replace them with what is inside the []. URLs typically look like [some text](http://www.ucla.edu) in the comment text but also have the standard form http(s)://…. Remove all URLs. The online tool may not match this.
    
  #(NEW!) Do the same with links to subreddits and users that are encoded like in #2 using Markup links. For raw references to subreddits and users (/r/subredditname and /u/someuser) leave them in the text as is, but it is OK if the first slash is removed by an earlier part of the script. The online tool may not match this.
  
  #We will not use test cases that involve #2, 3 and will instead check manually since this was not clear. If your implementation is reasonable, you will not lose points.

  p = re.compile(r'(\[.*?\])(\(.*?\))')
  text = p.sub(r'\1\1', text)

  # work cited: https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
  text = re.sub(r'https?:\/\/(www\.)?[\w+\-@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([\w+\-@:%_\+.~#?&//=]*)', '', text)

  #Split text on a single space. If there are multiple contiguous spaces, you will need to remove empty tokens after doing the split.    
  text = re.sub(r'\s+', ' ', text)

  #Separate all external punctuation such as periods, commas, etc. into their own tokens (a token is a single piece of text with no spaces), but maintain punctuation within words (otherwise he'll gets parsed to hell and thirty-two gets parsed to thirtytwo). The phrase "The lazy fox, jumps over the lazy dog." should parse to "the lazy fox , jumps over the lazy dog ."
  punct = '\\' + '\\'.join(string.punctuation)
  regex = '(?<=\w)[{0}](?=[^\w])|(?<=[^\w])[{0}](?=\w)|(?<=[^\w])[{0}](?=[^\w])|\w+[{0}]\w+|\w+'.format(punct)

  parsed_text = ' '.join(re.findall(regex, text))

  text_arr, bigrams, trigrams = parsed_text.split(), '', ''

  for i in range(len(text_arr)-1):
      if all(x not in string.punctuation for x in [text_arr[i], text_arr[i+1]]):
          bigrams += '_'.join(text_arr[i:i+2]) + ' '

  for i in range(len(text_arr)-2):
      if all(x not in string.punctuation for x in [text_arr[i], text_arr[i+1], text_arr[i+2]]):
          trigrams += '_'.join(text_arr[i:i+3]) + ' '

  bigrams, trigrams = bigrams.rstrip(), trigrams.rstrip()
    
  #Remove all punctuation (including special characters that are not technically punctuation) except punctuation that ends a phrase or sentence and except embedded punctuation (so thirty-two remains intact). Common punctuation for ending sentences are the period (.), exclamation point (!), question mark (?). Common punctuation for ending phrases are the comma (,), semicolon (;), colon (:). While quotation marks and parentheses also start and end phrases, we will ignore them as it can get complicated. We can also ignore RRR's favorite em-dash (--) as it varies (two hyphens, one hyphen, one dash, two dashes or an em-dash).
  regex2 = '(?<!\w)[{0}]|[{0}](?!\w)'.format(punct)
  unigrams = re.sub(regex2, '', text)

  return [parsed_text, unigrams, bigrams, trigrams]


if __name__ == "__main__":
    # This is the Python main function.
    # You should be able to run
    # python cleantext.py <filename>
    # and this "main" function will open the file,
    # read it line by line, extract the proper value from the JSON,
    # pass to "sanitize" and print the result as a list.

    # YOUR CODE GOES BELOW.

    json_obj = []
    with open(sys.argv[1], "r+") as f:
        for com in f:
            json_obj.append(json.loads(com))
        f.close()

    parsed = []
    for com in json_obj:
        parsed.append(sanitize(com["body"]))
    
    print(parsed)

    # We are "requiring" your write a main function so you can
    # debug your code. It will not be graded.
