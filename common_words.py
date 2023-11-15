# Python program to find the most repeated word 
# in a text file

# A file named "gfg", will be opened with the 
# reading mode.

fname = 'genres.txt'

frequent_word = ""
frequency = 0
words = []

words_found = []
freqs = []
num_words = 10

for i in range (0,num_words):
# Traversing file line by line 
    file = open(fname,"r")
    for line in file:
        
        # splits each line into
        # words and removing spaces 
        # and punctuations from the input
        line_word = line.lower().replace(',','').replace('.','').split(" "); 
        
        # Adding them to list words
        for w in line_word:
            w = w.strip()
            if w not in words_found:
                words.append(w); 
            
    # Finding the max occurred word
    for i in range(0, len(words)): 
        
        # Declaring count
        count = 1; 
        
        # Count each word in the file 
        for j in range(i+1, len(words)): 
            if(words[i] == words[j]): 
                count = count + 1; 

        # If the count value is more
        # than highest frequency then
        if(count > frequency): 
            frequency = count; 
            frequent_word = words[i]; 

    print("Most repeated word: " + frequent_word)
    print("Frequency: " + str(frequency))
    words_found.append(frequent_word)
    freqs.append(frequency)
    file.close()

for i in range(0,len(words_found)):
    print("{num}.) {word}: {freq} occurances".format(num=i+1, word=words_found[i], freq = freqs[i]))
