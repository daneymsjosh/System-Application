from math import sqrt, ceil
import random
from collections import deque

def rail_fence_encrypt(text, key):
    cipher_char = 0 # starting position
    p_len = len(text) 
    plaintext = [char for char in text]
    ciphertext = [None] * p_len
    rail_no = key

    for i in range(rail_no):
        flag = 1
        plain_char = i
        if rail_no == 1:
            ciphertext = plaintext
            break
        while plain_char < p_len:
            ciphertext[cipher_char] = plaintext[plain_char]
            cipher_char += 1
            if i == 0 or i == rail_no - 1:
                # perform formula for first and last row
                plain_char = plain_char + (rail_no - 1) * 2
            else:
                if flag == 1:
                    # perform formula for when rail is going down
                    plain_char += (rail_no - (i + 1)) * 2
                    flag = 0
                else:
                    # perform formula for when rail is going up
                    plain_char += (i * 2)
                    flag = 1
    
    return "".join(ciphertext), rail_no


def rail_fence_decrypt(ciphertext, key):
    cipher_char = 0
    c_len = len(ciphertext)
    ciphertext = [char for char in ciphertext]
    plaintext = [None] * c_len
    rail_no = key
    
    if rail_no == 1:
        return "".join(ciphertext)

    for i in range(rail_no):
        flag = 1
        plain_char = i

        while plain_char < c_len:
            plaintext[plain_char] = ciphertext[cipher_char]
            cipher_char += 1
            if i == 0 or i == rail_no - 1:
                plain_char += (rail_no - 1) * 2
            else:
                if flag == 1:
                    plain_char += (rail_no - (i + 1)) * 2
                    flag = 0
                else:
                    plain_char += (i * 2)
                    flag = 1
                    
    return "".join(plaintext)

#########################################################
            ## VIGENERE ##
#########################################################

def vigenere_encrypt(plaintext, key):
    
    # dictionary mapping characters to their numerical positions starting from "?" to "~" in the ascii table
    characters = {chr(i): i - ord('?') for i in range(ord('?'), ord('~') + 1)}
    
    # Encrypt the message character by character
    ciphertext = ""
    for i, char in enumerate(plaintext):
        # Get the shift value based on the keyword letter
        shift = characters[key[i % len(key)]]
        # Perform Caesar cipher shift with modular arithmetic
        new_char_index = (characters[char] + shift) % 64
        new_char = chr(new_char_index + ord('?'))
        ciphertext += new_char


    return ciphertext

def vigenere_decrypt(ciphertext, key):
    
    # dictionary mapping characters to their numerical positions starting from "?" to "~" in the ascii table
    characters = {chr(i): i - ord('?') for i in range(ord('?'), ord('~') + 1)}
    
    # decrypt the message character by character
    plaintext = ""
    for i, char in enumerate(ciphertext):
        # Get the shift value based on the keyword letter
        shift = characters[key[i % len(key)]]
        # Perform Caesar cipher shift with modular arithmetic
        new_char_index = (characters[char] - shift) % 64
        new_char = chr(new_char_index + ord('?'))
        plaintext += new_char

    return plaintext

#########################################################
            ## ENHANCED RAIL FENCE ##
#########################################################

def text_to_binary(text):
    binary = ""
    for char in text:
        binary = binary + bin(ord(char))[2:].zfill(8)
        
    return binary

def generate_block_sizes(plaintext_length):
    # Loop for dividing the binary into blocks of random sizes, 3 being the smallest possible value
    block_sizes = []
    sum_block_sizes = 0
    while sum_block_sizes != plaintext_length:
        # generate a random block size from 3 to the length of the plaintext, reroll if not valid
        while True:
            block_size = random.randint(3, plaintext_length)
            
            # if the last block size would be less than 3, regenerate block size
            if plaintext_length - (sum_block_sizes + block_size) < 3:
                # remaining block size is 0, meaning there would be no block sizes left, then it is valid
                if plaintext_length - (sum_block_sizes + block_size) == 0:
                    break
                else:
                    continue
            else:
                break

        # append valid block size to list
        block_sizes.append(block_size)
        sum_block_sizes += block_size
        
    return block_sizes

def shuffle_blocks(bin_ciphertext):
    shuffle_order = [i for i in range(1, len(bin_ciphertext) + 1)]
    
    # shuffle the block order using fisher yates algorithm
    for i in range(len(bin_ciphertext) - 1, 0, -1):
        # Randomly select an index
        j = random.randint(0, i)
        
        # swap blocks
        bin_ciphertext[i], bin_ciphertext[j] = bin_ciphertext[j], bin_ciphertext[i]
        
        # swap shuffle order
        shuffle_order[i], shuffle_order[j] = shuffle_order[j], shuffle_order[i]
        
    return shuffle_order, bin_ciphertext

def add_padding(bin_ciphertext):
    ## add padding if binary length is not a multiple of 6
    padding = 6 - (len(bin_ciphertext) % 6)
    if padding != 0:
        bin_ciphertext = bin_ciphertext.zfill(len(bin_ciphertext) + padding)
    
    ## divide bin_ciphertext into 6 bit blocks then append 01 at the beginning and convert back ascii
    ## this is so characters would not convert into escape characters in the ascii table
    padded_bin_ciphertext = []
    padded_ciphertext = []
    for i in range(0, len(bin_ciphertext), 6):
        bin_char = "01" + bin_ciphertext[i:6 + i]
        if bin_char == "01111111":
            bin_char = "00111111"
            
        char = chr(int(bin_char, 2))
        padded_ciphertext.append(char)
        
        padded_bin_ciphertext.append(bin_char)
        
    # convert back into single string
    ciphertext = "".join(padded_ciphertext)
    
    return padded_ciphertext

def rail_fence_encrypt_round(bin_plaintext):
    ## get block sizes
    block_sizes = generate_block_sizes(len(bin_plaintext))
        
    ## apply rail fence to each block of the plaintext, key is the square root of block size
    bin_ciphertext = []
    i = 0
    for block_size in block_sizes:
        block = bin_plaintext[i:i + block_size]
        
        encrypted_block, x = rail_fence_encrypt(block, ceil(sqrt(block_size)))
        bin_ciphertext.append(encrypted_block)

        i += block_size

    ## shuffle blocks using fisher yates and get shuffle order
    shuffle_order, bin_ciphertext = shuffle_blocks(bin_ciphertext)

    bin_ciphertext = "".join(bin_ciphertext)
    
    return bin_ciphertext, block_sizes, shuffle_order

def enhanced_rail_fence_encrypt(plaintext):
    
    ## convert plaintext into its binary equivalent
    bin_plaintext = text_to_binary(plaintext)           
        
    ## enhanced rail fence round 1
    bin_ciphertext_1, block_sizes_1, shuffle_order_1 = rail_fence_encrypt_round(bin_plaintext)
    
    ## enhanced rail fence round 2
    bin_ciphertext_2, block_sizes_2, shuffle_order_2 = rail_fence_encrypt_round(bin_ciphertext_1)
    
    ## add padding to binary ciphertext
    padded_ciphertext = add_padding(bin_ciphertext_2)
    
    ## convert back to string
    ciphertext = "".join(padded_ciphertext)

    ## apply vigenere cipher, using result of first round of rail fence as key
    vigenere_key = "".join(add_padding(bin_ciphertext_1))
    
    ## Final ciphertext
    ciphertext = vigenere_encrypt(ciphertext, vigenere_key)
    
    ## convert to binary
    bin_ciphertext = text_to_binary(ciphertext) 
    
    ## convert back to string removing padding
    stripped_ciphertext = remove_padding(bin_ciphertext)
    
    ## enhanced rail fence round 3
    bin_ciphertext_3, block_sizes_3, shuffle_order_3 = rail_fence_encrypt_round(stripped_ciphertext)
    
    ## add padding to binary ciphertext
    padded_ciphertext = add_padding(bin_ciphertext_3)
    
    ## convert back to string
    ciphertext = "".join(padded_ciphertext)
    
    ## compile blocksizes and shuffle order
    block_sizes = [block_sizes_1, block_sizes_2, block_sizes_3]
    shuffle_orders = [shuffle_order_1, shuffle_order_2, shuffle_order_3]
            
    return ciphertext, str(block_sizes) + "." + str(shuffle_orders) + "." + vigenere_key


################# DECRYPTION FUNCTIONS

def remove_padding(bin_ciphertext):
    ## divide into 8 bit blocks, remove 01 at start of each byte, and join into one string
    stripped_ciphertext = []
    for i in range(0, len(bin_ciphertext), 8):
        stripped_ciphertext.append(bin_ciphertext[i + 2: 8 + i])
    
    # convert to string
    stripped_ciphertext = "".join(stripped_ciphertext)

    4
    ## remove padding
    padding = len(stripped_ciphertext) % 8
    if padding != 0:
        stripped_ciphertext = stripped_ciphertext[padding:]
        
    return stripped_ciphertext

def reorder_blocks(block_sizes, shuffle_order, stripped_ciphertext):
    ## reorder the block sizes to match shuffle order
    shuffled_block_sizes = [None for x in shuffle_order]
    i = 0
    for order in shuffle_order:
        shuffled_block_sizes[i] = block_sizes[order - 1]
        i += 1
        
    
    ## divide ciphertext binary into proper block sizes
    block_ciphertext = []
    i = 0
    for block_size in shuffled_block_sizes:
        block_ciphertext.append(stripped_ciphertext[i:i + block_size])
        i += block_size
        
    
    ## reorder the blocks into proper order
    ordered_ciphertext = [None for x in block_sizes]
    i = 0
    for order in shuffle_order:
        ordered_ciphertext[order - 1] = block_ciphertext[i]
        i += 1
        
    return ordered_ciphertext

def rail_fence_decrypt_round(bin_ciphertext, block_sizes, shuffle_order):
    ## reorder the blocks
    reordered_blocks = reorder_blocks(block_sizes, shuffle_order, bin_ciphertext)
     
    ordered_ciphertext = "".join(reordered_blocks)
    
    ## decrypt with rail fence
    bin_plaintext = []
    i = 0
    for block_size in block_sizes:
        block = ordered_ciphertext[i:i + block_size]
        
        decrypted_block = rail_fence_decrypt(block, ceil(sqrt(block_size)))
        bin_plaintext.append(decrypted_block)

        i += block_size
        
    return bin_plaintext

def binary_to_text(binary):
    ## convert binary plaintext to ascii
    plaintext = []
    for i in range(0, len(binary), 8):
        plaintext.append(chr(int(binary[i:8+i], 2)))
        
    return "".join(plaintext)
        

def enhanced_rail_fence_decrypt(ciphertext, key):
    keys = key.split(".")
    block_sizes = eval(keys[0])
    shuffle_order = eval(keys[1])
    vigenere_key = keys[2]
    
    ## convert ciphertext into its binary equivalent
    bin_ciphertext = text_to_binary(ciphertext)
        
    ## divide into 8 bit blocks, remove 01 at start of each byte, and join into one string
    stripped_ciphertext = remove_padding(bin_ciphertext)
    
    ## first decrypt round
    bin_plaintext_0 = rail_fence_decrypt_round(stripped_ciphertext, block_sizes[2], shuffle_order[2])
    
    bin_plaintext_0 = "".join(bin_plaintext_0)
    
    ## convert back to string with padding
    padded_ciphertext = add_padding(bin_plaintext_0)
    
    ## decrypt vigenere cipher
    ciphertext = vigenere_decrypt(padded_ciphertext, vigenere_key)
    
    ## convert ciphertext into its binary equivalent
    bin_ciphertext = text_to_binary(ciphertext)
        
    ## divide into 8 bit blocks, remove 01 at start of each byte, and join into one string
    stripped_ciphertext = remove_padding(bin_ciphertext)
    
    ## first decrypt round
    bin_plaintext_1 = rail_fence_decrypt_round(stripped_ciphertext, block_sizes[1], shuffle_order[1])
    
    ## second decrypt round
    bin_plaintext_2 = rail_fence_decrypt_round("".join(bin_plaintext_1), block_sizes[0], shuffle_order[0])
        
    bin_plaintext = "".join(bin_plaintext_2)
        
    ## convert binary plaintext to ascii
    plaintext = binary_to_text(bin_plaintext)
    
    return "".join(plaintext)