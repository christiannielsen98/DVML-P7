

def str_split(string):
    if isinstance(string, str):
        return string.split(", ")
    else:
        return string


def long_com_substring(st1: str, st2: str):
    """
    This function is used for matching business categories with schema.org types.
    :param st1: The string we want to check for.
    :param st2: The string we check longest substring in.
    :return: Returns the length of the longest substring
    """

    ans = 0
    for a in range(len(st1)):
        for b in range(len(st2)):
            k = 0
            while (a + k) < len(st1) and (b + k) < len(st2) and st1[a + k] == st2[b + k]:
                k = k + 1
            ans = max(ans, k)

    return ans


def split_words_inc_slash(word):
    # Splitting the words that have a slash in them, and turning them into two words
    word_space = word.split(' ')
    word_space
    new_wordlist_a = []
    new_wordlist_b = []
    for i in word_space:
        i = i.lower()
        if '/' not in i:
            new_wordlist_a.append(i)
            new_wordlist_b.append(i)
        else:
            slash_split = i.split('/')
            new_wordlist_a.append(slash_split[0])
            new_wordlist_b.append(slash_split[1])
    new_word_a = ' '.join(new_wordlist_a)
    new_word_b = ' '.join(new_wordlist_b)
    return [new_word_a, new_word_b]


def split_words(categories_unique, split_word_inc_slash):
    categories_dict = {}
    for word in categories_unique:
        if '&' in word:
            word_list = list(filter(None, word.lower().split(sep=' & ')))
            categories_dict[word] = word_list
        elif '/' in word:
            categories_dict[word] = split_word_inc_slash(word)
        else:
            categories_dict[word] = [word.lower()]
    return categories_dict


def turn_words_singular(categories_dict):
    p = inflect.engine()
    categories_dict_singular = {}
    for key, value in categories_dict.items():
        new_value = []
        for word in value:
            if p.singular_noun(word) is False:
                word = word
            else:
                word = p.singular_noun(word)
            new_value.append(word)
        categories_dict_singular[key] = new_value
    return categories_dict_singular

if __name__ == '__main__':
    pass