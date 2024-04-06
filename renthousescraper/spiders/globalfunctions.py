import re
from html2text import element_style

def normalizeRentstatus(value):
    if value != None:
        value = value.strip()
        value = value.lower()
    if value in ('verhuurd', 'onder optie', 'onder bod', 'verhuurd onder voorbehoud', 'recently rented'):
        return 'rented'
    else:
        return 'available'


def getStreet_StreetNr(streetOriginal):
# Define the pattern for "number tm number" and capture the first number
    tm_pattern = r"(\d+[A-Za-z]*)\s+tm\s+\d+[A-Za-z]*"
    match = re.search(tm_pattern, streetOriginal)
    if match:
        streetOriginal = streetOriginal.replace(match.group(0), match.group(1))

    # Define the patterns to remove from the end of the string
    patterns_to_remove = [" I", " II", " III", " IV", " V"]

    # Remove the patterns if they are found at the end of the string
    for pattern in patterns_to_remove:
        if streetOriginal.endswith(pattern):
            streetOriginal = streetOriginal[:-len(pattern)]
            break

    street = ""
    streetnr = ""
    streetparts = streetOriginal.split()

    # Check if last two elements are a number followed by a letter
    if len(streetparts) > 1 and re.match(r"^\d+$", streetparts[-2]) and re.match(r"^[A-Za-z]$", streetparts[-1]):
        streetnr = streetparts[-2] + " " + streetparts[-1]
        streetparts = streetparts[:-2]

    # Get streetnr part for other cases
    elif streetparts[-1].isdigit() or re.match(r"\d+[A-Za-z]", streetparts[-1]):
        streetnr = streetparts[-1]
        streetparts = streetparts[:-1]

    # Get street part
    street = " ".join(streetparts)

    return street.strip(), streetnr.strip()









