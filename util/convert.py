import string
import unicodedata

import torch

ALL_DIGITS = string.digits
N_DIGIT = len(ALL_DIGITS)
ALL_LETTERS = string.digits+' .,:()+-'
N_LETTER = len(ALL_LETTERS)


def index_to_letter(index: int) -> str:
    return ALL_LETTERS[index]

def index_to_digit(index: int) -> str:
    return ALL_DIGITS[index]

def letter_to_index(letter: str) -> int:
    index = ALL_LETTERS.find(letter)
    if index == -1: raise Exception(f"letter {letter} is not permitted.")
    return index

def digit_to_index(digit: str) -> int:
    index = ALL_DIGITS.find(digit)
    if index == -1: raise Exception(f"digit {digit} is not permitted.")
    return index

def pad_string(original: str, desired_len: int, pad_character: str = ' ') -> str:
    """
    Returns the padded version of the original string to length: desired_len
    """
    return original + (pad_character * (desired_len - len(original)))

def strings_to_tensor(strings: list, max_string_len: int, index_function) -> list:
    """
    Turn a list of strings into a tensor of shape: <max_string_len x batch_size (length of strings)>.
    index_function should be a function that converts a character into an appropriate index.
    Example: strings: ["012","9 ."], max_string_len: 4, index_function: index_to_letter
            => torch.tensor([[0,9],[1,10],[2,11],[10,10]])
    """
    tensor = torch.zeros(max_string_len, len(strings))
    padded_strings = list(map(lambda s: pad_string(s, max_string_len), strings))
    for i_s, s in enumerate(padded_strings):
        for i_char, char in enumerate(s):
            tensor[i_char][i_s] = index_function(char)
    return tensor

def strings_to_probs(strings: list, max_string_len: int, true_index_prob: float = 0.99) -> list:
    """
    Turn a list of strings into probabilities over rows where the element of the index
    of character has probability of 0.99 and others 0.01/(size(n_letters)-1)
    of shape: <max_string_len x batch_size (length of strings list) x n_letters>
    """
    strings = list(map(lambda name: pad_string(name, max_string_len), strings))
    default_index_prob = (1.-true_index_prob)/N_LETTER
    tensor = torch.zeros(max_string_len, len(strings), N_LETTER) + default_index_prob
    for i_s, s in enumerate(strings):
        for i_char, letter in enumerate(s):
            tensor[i_char][i_s][letter_to_index(letter)] += true_index_prob
    return tensor

def to_rnn_tensor(tensor: list) -> list:
    """
    Turn the tensor generated by strings_to_tensor into a one hot version to be passed to the RNN
    """
    n, d = tensor.shape
    encoded = torch.zeros(n,d,N_LETTER)
    for i in range(n):
        for j in range(d):
            encoded[i,j,int(tensor[i,j])] = 1
    return encoded

def tensor_to_string(tensor: list) -> str:
    # For debugging
    result = ""
    n,d = tensor.shape
    for i in range(n):
        for j in range(d):
            result += index_to_letter(int(tensor[i,j].item()))
    return result

def unicode_to_ascii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn' and c in ALL_LETTERS
    )

def format_ext(ext, ext_format) -> str:
    if ext_format == 0: return ext
    elif ext_format == 1: return "+" + ext
    elif ext_format == 2: return ext + "-"
    elif ext_format == 3: return "+" + ext + "-"
    elif ext_format == 4: return ext + " "
    else: return "+" + ext + " "

def format_prefix(prefix, prefix_format) -> str:
    if prefix_format == 0: return prefix
    elif prefix_format == 1: return "(" + prefix + ")"
    elif prefix_format == 2: return prefix + "-"
    elif prefix_format == 3: return "(" + prefix + ")-"
    elif prefix_format == 4: return prefix + " "
    else: return "(" + prefix + ") "

def format_number(number_parts, number_format) -> str:
    if number_format == 0: return "".join(number_parts)
    elif number_format == 1: return "-".join(number_parts)
    else: return " ".join(number_parts)
