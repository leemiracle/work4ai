import urllib.request

base = "https://web.stanford.edu/~jurafsky/slp3/"
letters = ["G", "H", "I", "J", "K"]

for letter in letters:
    url = base + letter + ".pdf"
    outfile = "/tmp/slp3_" + letter + ".pdf"
    try:
        urllib.request.urlretrieve(url, outfile)
        print(f"Downloaded {letter}.pdf -> {outfile}")
    except Exception as e:
        print(f"Failed {letter}: {e}")
