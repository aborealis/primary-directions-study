"""
Parameters for simplified astrological model to evaluate primary directions
"""

IS_EVENT_FAVORABLE = False
HOUSE = 7               # 0..11 House in question
BRIGHTNESS = 3          # Min |score| for an aspect/antiscion to qualify as a
                        # promissor (the value used to generate the study
                        # data; see the data provenance note in README)
NATURAL_RULER = 4       # Number of planet 0..6 or None
ALLOWANCES = [-6, 6]    # Allowance interval in months
