"""

"""

# Words that are flagged when anywhere (example: prettySHITpretty  -> True)
BAD_ANYWHERE = [
    'fuck', 'shit', 'cunt', 'bitch', 'cock', 'niger', 'kike',
    'chink', 'fagot', 'fagots', 'fucks', 'fucking', 'fucked',
    'nigers', 'kikes', 'cocks', 'bitches', 'cunts', 'shits',
    'chinks', 'kiek', 'kunt'
]
# Words that are only bad when used by themselves.
#   (examples: clASSic -> False; my ASS is -> True)
BAD_ALONE = [
    'piss', 'ass', 'fag', 'jew', 'tit', 'tity', 'tities', 'boobs',
    'dyke', 'nig', 'cum', 'semen', 'rape', 'beaner',
    'suck', 'dick', 'penis', 'vagina', 'breast', 'nipple', 'clit',
    'pises', 'asses', 'fags', 'jews', 'tits', 'dykes', 'kunts',
    'nigs', 'cums', 'rapes', 'raped', 'beaners', 'sucks', 'sucked',
    'dicks', 'penises', 'vaginas', 'breasts', 'nipples', 'clits',
    'shite', 'shites', 'fagit', 'faget', 'fagits',
    'faget', 'fagot', 'fagity', 'fagety', 'cuck', 'clitoris',
    'blowjob', 'anal', 'whore', 'slut', 'prostitute', 'wiger', 'sex',
    'pusy', 'pusies'
]
VOWELS = ('*', '-', '_', '+', '#')
SPACES = ('.', ' ', '-', '_', ',', '+', '=', '`', '~')
REPLACEMENTS = {
    # TODO
}


def has_bad_words(string):
    return False


def filter_bad_words(string):
    return string
