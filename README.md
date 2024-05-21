#   Classification of errors in English text using a Support Vector
Machine

    This project uses a type of machine learning algorithm called a
    support vector machine (SVM) to assist in identification and
    classification of ungrammatical English usage in documents such as
    those written by language learners. Two types of features were
    used to train the algorithm.  One type of feature was the
    ungrammatical part of speech patterns as measured with handwritten
    rules created by analyzing errors in documents similar to those to
    be classified. A simple parser was included so that such rules can
    be written in English. The second feature type was the presence of
    rarely occuring trigrams detected by comparing trigrams in the
    source documents to those in a large Google ngram corpus and Yahoo
    limited web search. Trigrams with rarely used words were excluded
    to avoid false positives where the trigram rareness was because of
    the rareness of a word rather than an unnatural usage. The project
    uses handwritten rules and individual SVMs for different types of
    grammatical errors. At this stage rules for grammatical errors
    involving determiners have been written, and detection and
    classification of determiner errors can be shown to work
    successfully. The SVM provides a model for classifying documents
    that can be improved by adding more features to the SVM. Use of
    the SVM to classify errors seems to show that while handwritten
    rules can work pretty well, training the SVM to evaluate language
    ability more precisely would require more features in addition to
    the rare trigrams used.

    Some python modules are required to be installed before using the
    classifier. They are listed in the "SVM Ungrammatical English
    Detection" document.
 
    The classifier software was originally designed to optionally use
    a Yahoo trigram search (switch -y) that is not selected by
    default. Before it could be used, Yahoo BOSS search had to be
    installed with a working, chargeable Yahoo BOSS account. This
    option required a yahoo-bossmashup directory and a config-json
    file in the application directory. Unfortunately, Yahoo BOSS was
    discontinued so that this option is no longer available. However,
    the software can be demonstrated with the included sample text
    files without using Yahoo search since searches from previously
    analyzed documents are already saved in the 'yahoo_db' file.

    New implementations of the software should use a replacement for
    the Yahoo BOSS search to find common trigram usage. There are many
    options such as those at https://www.english-corpora.org/ or the
    Scrapy internet page scraper.

    The application can also be used without using the -y switch. In
    that case, handwritten rules will be used, and trigram features
    will not.

    Thirty-three Python and Perl scripts were included to facilitate
    working with the language data. They are listed in the
    accompanying document "perl-and-python-scripts.txt".
    
    Individual reports for each document analyzed are put into a
    'report' subdirectory where the file is located. Part-of-speech
    tagged versions of each text file can be found in the 'tag'
    subdirectories.

    For further details, please see the accompanying document "SVM
    Ungrammatical English Detection"

