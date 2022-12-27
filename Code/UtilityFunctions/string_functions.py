import inflect
import re

def string_is_float(string):
    """
    This function checks if a string is a float.
    :param string: The string to be checked.
    :return: True if the string is a float, False if not.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def turn_words_singular(categories_dict):
    """
    For each key in the dictionary, the function takes the value (a list of words) and turns each word
    into its singular form
    
    :param categories_dict: a dictionary of categories and their associated words
    :return: A dictionary with the same keys as the original dictionary, but with the values being a
    list of singular words.
    """
    p = inflect.engine()
    categories_dict_singular = {}
    for key, value in categories_dict.items():
        new_value = []
        for word in value:
            word = word.lower()
            if p.singular_noun(word) is False:  # If the word is already singular p.singular_noun  returns False
                word = word
            else:
                word = p.singular_noun(word)
            new_value.append(word)
        categories_dict_singular[key] = new_value
    return categories_dict_singular

def space_words_lower(string):
    return re.sub('(?<!^)([A-Z])([^A-Z])', r' \1\2', string).lower()

if __name__ == '__main__':
    p = inflect.engine()
    print(p.singular_noun('bakery'))
    print(p.singular_noun('bakeries'))


