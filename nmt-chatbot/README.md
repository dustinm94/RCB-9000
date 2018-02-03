nmt-chatbot
===================


Introduction
-------------

nmt-chatbot is the implementation of chatbot using NMT - Neural Machine Translation (seq2seq). Includes BPE/WPM-like tokenizator (own implementation). Main purpose of that project is to make a NMT chatbot, but it's fully compatible with NMT and still can be used for sentence translations between two languages.

The code is built on top of NMT but because of lack of available interfaces, some things are "hacked", and parts of the code had to be copied into that project (and will have to be maintained to follow changes in NMT).

This project forks NMT. We had to make a change in our code allowing the use of a stable TensorFlow (1.4) version. Doing so allowed us also to fix some bug before official patch as well as do couple of necessary changes.



Setup
-------------

Steps to setup project for your needs:
It is *highly* recommended that you use Python 3.6+. Python 3.4 and 3.5 is likely to work in Linux, but you will eventually hit encoding errors with 3.5 or lower in a Windows environment.

If you want to use exactly what's in tutorial made by Sentdex, use v0.1 tag. There are multiple changes after last part of tutorial.

 1. ```$ git clone --recursive https://github.com/daniel-kukiela/nmt-chatbot```  
    (or)  
    ```$ git clone --recursive https://github.com/daniel-kukiela/nmt-chatbot/tree/v0.1``` (for a version featured in Sentdex tutorial)
 2. ```$ cd nmt-chatbot```
 3. ```$ pip install -r requirements.txt``` TensorFlow-GPU is one of the requirements. You also need CUDA Toolkit 8.0 and cuDNN 6.1. (Windows tutorial: https://www.youtube.com/watch?v=r7-WPbx8VuY  Linux tutorial: https://pythonprogramming.net/how-to-cuda-gpu-tensorflow-deep-learning-tutorial/)
 4. ```$ cd setup```
 5. (optional) edit settings.py to your liking. These are a decent starting point for ~4GB of VRAM, you should first start by trying to raise vocab if you can. 
 6. (optional) Edit text files containing rules in the setup directory.
 7. Place training data inside "new_data" folder (train.(from|to), tst2013.(from|to), tst2013(from|to)). We have provided some sample data for those who just want to do a quick test drive.
 8. ```$ python prepare_data.py``` ...Run setup/prepare_data.py - a new folder called "data" will be created with prepared training data
 9. ```$ cd ../```
 10. ```$ python train.py``` Begin training



Standard vs BPE/WPM-like (subword) tokenization, embedded detokenizer
---------------------------------------------------------------------------------------

v0.1 includes only standard (own, first version) tokenizer.

Standard tokenizer is based on moses-smt one. It's highly modified own python implementation of that tokenizer. The adventage of tokenizer like that is lack of duplicates in vocab file (more on that later). Biggest disadventage - it needs bunch of regex-based rules for detokenization process and it's hard to write ones that covers all cases.

Standard tokenizer splits sentences by space, period (and other grammar chars), speparates digits, etc.

BPE/WPM-like (subword) tokenizer is based on subword-nmt one, but (like for "standard" one) it's highly modified to fit our needs and for speed. The biggest adventage is ability to fit any number of words (tokens) in much smaller vocab thanks to subwords.

BPE/WPM-like (subword) tokenizer is doing similar splits like standard one, but in addition it splits every entity by char, counts most common pairs of chars (chars next to other chars in entities), and joins that pairs to make a vocab of desired number of tokens. As a result, most common words are joined back together, when the rarest ones will stay split into multiple pieces (subwords) shared with other words. That way near any number of vocab tokens can be lowered to number as small as couple of thousands (or lower - depending on training set). Basically it's something between char model and word model (as for model not beeing a char model, vocab size should be held as big as possible to include most common words in one piece as well ass some elemental tokens like single chars). Subword-based model should produce way less (to none) `<unk>` special tokens in output at the exchange for sentences with higher number of tokens (possibly shorter sentences outputted by network for purposes like chatbot).

Standard vs. BPE/WPM-like (subword) tokenization examples:

    > Aren ' t they streaming it for free online ... ?
    > Aren ' t they streaming it for free online ... ?

    > THE GREATEST FOOTBALL TEAM !
    > THE GRE AT EST F OO TB ALL TEAM !

    > Become a tourist , I hear lots of Kerbals go on vacation there ...
    > B ec ome a tou rist , I hear lots of Ker b als go on vacation there ...

Embeded detokenizer (option for standard tokenizer, forced to 'on' for BPE/WPM-like one - you can see why above) allows to do a perfect detokenization at the exchange for higher number of tokens in vocab - duplicate-like entities in vocab (variations with and without meta symbol '▁', where that meta symbol is all is needed for detokenization).
Biggest adventage of that detokenizer is lack of any rules for detokenization. Detokenization is easy as doing two replaces in resulting sentence - first remove all spaces, then replace meta symbol '▁' with space character.

Examples:

    > ▁B ec ome ▁a ▁tou rist , ▁I ▁hear ▁lots ▁of ▁Ker b als ▁go ▁on ▁vacation ▁there ...
    > ▁I ' d ▁w ager ▁it ' s ▁appropriate ▁for ▁all ▁kinds ▁of ▁things .



Rules files
-------------

Setup folder contains multiple "rules" files (All of them are regex-based:

 - answers_blacklist.txt - disallows answer from being returned (more on that later).
 - answers_detokenize.txt - detokenization rules (removes unnecessary spaces).
 - answers_replace - synonyms, replaces phrase or it's part with a replacement.
 - protected_phrases_standard.txt - ensures that matching phrases will remain untouched when building vocab file with standard tokenizer.
 - protected_phrases_bpe.txt - same as above but for BPE/WPM-like tokenizer.




Tests
-------------

Every rules file has related test script. Those test scripts might be treated as some kind of unit testing. Every modification of rules files might be checked against those tests but every modification should be also followed by new test cases in those scripts.

It's important to check everything before training new model. Even slight change might break something.

Test scripts will display check status, checked sentence and eventually check result (if different than assumed).




More detailed information about training a model
-------------

setup/settings.py consist of multiple settings:

 - untouched file/folder paths should fit for most cases
 - "preprocessing" dictionary should be easy to understand
 - "hparams" dictionary will be passed to NMT like command line options with standard usage

setup/prepare_data.py:

 - walks thru files placed in "new_data" folder - train.(from|to), tst2012.(from|to)m tst2013(from|to)
 - tokenizes all sentences (adds spaces based on internal rules)
 - for "train" files - builds vocabulary files and checks entities against vocab_replace.txt rules, then vocab_blacklist_rules.txt, finally makes dictionary unique and saves up to the number of entities set in setup/settings.py file, rest of entities will be saved to separate file

train.py - starts training process




Utils
-------------

utils/run_tensorboard.py is easy to use wrapper starting Tensorboard with model folder

utils/pairing_testing_outputs.py - joins model/output_dev file with data/tst2012.form file and prints result to a console allowing easy check if things are going ok during training. The console will consist of input phrase, inference output frame, and separator.



Inference
-------------

Whenever a model is trained, inference.py, when directly called, allows to "talk to" AI in interactive mode. It will start and setup everything needed to use trained model (using saved hparams file within the model folder and setup/settings.py for the rest of settings or lack of hparams file).

For every question will be printed up to a number of responses set in setup/settings.py. Every response will be marked with one of three colors:

 - green - first one with that color is a candidate to be returned. Answers to the color passed blacklist check (setup/response_blacklist.txt)
 - orange - still proper responses, but doesn't pass check against the blacklist
 - red - improper response - includes `<unk>`

Steps from the question to the answers:

 1. Pass question
 2. Compute up to number of responses set in setup/settings.py
 3. Detokenize answers using rules from setup/answers_detokenized.txt
 3. Replace responses or their parts using rules from setup/answers_replace.txt
 4. Score responses with -1 (includes `<unk>`, 0 (matches against at least one rule in setup/answers_blacklist.txt file) or 1 (passes all checks)
 5. Return (show with interactive mode) responses

It is also possible to process a batch of the questions by simply using command redirection:

    python inference.py < input_file

or:

    python inference.py < input_file > output_file

Importing nmt-chatbot
-------------

The project allows being imported for the needs of inference. Simply embed folder within your project and import, then use:

    from nmt-chatbot.inference import inference

    print(inference("Hello!"))

inference() takes two parameters:

 - `question` (required)
 - `include_blacklisted = True` (optional)

For a single question, function will return dictionary containing:

 - answers - list of all answers
 - scores - list of scores for answers
 - best_index - index of best answer
 - best_score - score of best answer (-1, 0 or 1)

Score:

 - -1 - inproper response - includes `<unk>`
 - 0 - proper response but blacklisted
 - 1 - proper response - passed checks

With a list of questions, the function will return a list of dictionaries.

For every empty question, the function will return `None` instead of result dictionary.

With `include_blacklisted` set to false function will return either -1 or 1 for the score (and related to that score index)


----------
