import secrets


def dna_to_numbers(dna_string):
    """
    Converts a DNA string (A, T, C, G) into a numerical format.
    A -> 1, T -> 2, C -> 3, G -> 4
    """
    mapping = {'A': 1, 'T': 2, 'C': 3, 'G': 4}
    return [mapping[base] for base in dna_string.upper() if base in mapping]

def numbers_to_dna(num_array):
    """
    Optional function to convert back from numbers to DNA
    """
    mapping = {1: 'A', 2: 'T', 3: 'C', 4: 'G', 0: '-'}
    return "".join([mapping.get(num, '?') for num in num_array])

def pad_sequences(seq1, seq2):
    """
    Pads the shorter sequence with 0s to match the length of the longer sequence.
    """
    len1 = len(seq1)
    len2 = len(seq2)
    max_len = max(len1, len2)
    
    padded_seq1 = seq1 + [0] * (max_len - len1)
    padded_seq2 = seq2 + [0] * (max_len - len2)
    
    return padded_seq1, padded_seq2

def generate_random_mask(length):
    """
    Kriptografik olarak güvenli rastgele maskeleme vektörü üretir.
    Python 'secrets' modülü kullanılarak tahmin edilmesi imkânsız değerler oluşturulur.
    Değerler 1 ile 1000 arasındadır (0 olamaz, çünkü maskeleme sıfırla çarpmayı önlemeli).
    """
    return [secrets.randbelow(1000) + 1 for _ in range(length)]
