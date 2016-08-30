import requests
import slate
import os
import sys
import string


def LoadToken(FileName):
    '''
    Grab crossref click through api token token from a file.
    '''
    with open(FileName, 'r') as f:
        return f.readline().strip()


def doi2url(doi):
    '''
    Convert a doi into a url. No testing of validity of doi.
    '''
    return ('http://dx.doi.org/{0}').format(doi)


def doiFormat(doi):
    '''
    Remove slashes from a doi.
    '''
    return doi.replace('/', '_')


def doiUnformat(doi):
    '''
    Reinsert slashes into a doi.
    '''
    return doi.replace('_', '/')


def DownloadPaper(doi, Token, Outpath):
    '''
    Only tested on ESPL at present. So gets pdf. Will need to modify code for
    xml journals.
    '''

    url = doi2url(doi)

    # http header for crossref metadata request
    header = {'Accept': 'application/vnd.crossref.unixsd+xml'}

    # get the fulltext link
    r = requests.get(url, headers=header)
    paperURL = r.links['item']['url']

    # Add user's token to the new http header and request the paper
    header = {'CR-Clickthrough-Client-Token': Token}
    fulltext = requests.get(paperURL, headers=header)

    # Build output path + filename, changing / to _ in the doi
    Output = '{0}{1}.pdf'.format(Outpath, doiFormat(doi))

    # write the paper to the supplied path
    with open(Output, 'wb') as f:
        f.write(fulltext.content)


def StripText(text):
    '''
    Remove all punctuation and digits from raw text aside from periods, which
    are needed to identify sentence breaks.
    '''

    TransTable = string.maketrans('', '')
    Replacement = string.punctuation.replace('.', '') + string.digits
    return text.translate(TransTable, Replacement)


def ExtractText(doi, pdfPath, txtPath):
    '''
    Extract raw text from downloaded pdf and save as a txt file.
    '''

    doi = doiFormat(doi)

    with open('{0}{1}.pdf'.format(pdfPath, doi)) as f:
        paper = slate.PDF(f)

    with open('{0}{1}.txt'.format(txtPath, doi), 'w') as w:
        for page in paper:
            w.write(StripText(page))


def Core(dois, pdfPath, txtPath):
    '''
    Pass in list of dois, a path to write pdfs to and a path to write textfiles.
    Does basic error handling and will create paths if they are not found.
    '''

    if not os.path.exists(pdfPath):
        os.mkdir(pdfPath)
    if not os.path.exists(txtPath):
        os.mkdir(txtPath)

    if not os.path.isfile('Token.token'):
        sys.exit('\nToken file cannot be found.\n')

    Token = LoadToken('Token.token')

    for doi in dois:

        DownloadPaper(doi, Token, pdfPath)
        ExtractText(doi, pdfPath, txtPath)

Core(['10.1002/esp.3884'], '/home/sgrieve/StanfordNLP/code/',
     '/home/sgrieve/StanfordNLP/code/')
