def get_band_descriptions(band_score):
    """
    Get the band descriptions and skill level based on the band score for the Reading Test.
    """
    band_descriptions = {
        9: {
            "Skill Level": "Expert",
            "Description": "The test taker has a fully operational command of the language. Their use of English is appropriate, accurate, and fluent, and shows complete understanding."
        },
        8: {
            "Skill Level": "Very good",
            "Description": "The test taker has a fully operational command of the language with only occasional unsystematic inaccuracies and inappropriate usage. They may misunderstand some things in unfamiliar situations. They handle complex and detailed argumentation well."
        },
        7: {
            "Skill Level": "Good",
            "Description": "The test taker has operational command of the language, though with occasional inaccuracies, inappropriate usage, and misunderstandings in some situations. They generally handle complex language well and understand detailed reasoning."
        },
        6: {
            "Skill Level": "Competent",
            "Description": "The test taker has an effective command of the language despite some inaccuracies, inappropriate usage, and misunderstandings. They can use and understand reasonably complex language, particularly in familiar situations."
        },
        5: {
            "Skill Level": "Modest",
            "Description": "The test taker has partial command of the language and copes with overall meaning in most situations, although they are likely to make many mistakes. They should be able to handle basic communication in their field."
        },
        4: {
            "Skill Level": "Limited",
            "Description": "The test taker's basic competence is limited to familiar situations. They frequently show problems in understanding and expression."
        },
        3: {
            "Skill Level": "Extremely limited",
            "Description": "The test taker conveys and understands only general meaning in very familiar situations. There are frequent breakdowns in communication."
        },
        2: {
            "Skill Level": "Intermittent",
            "Description": "The test taker has great difficulty understanding spoken and written English."
        },
        1: {
            "Skill Level": "Non-user",
            "Description": "The test taker cannot use the language except a few isolated words."
        },
        0: {
            "Skill Level": "Did not attempt the test",
            "Description": "The test taker did not answer the questions."
        }
    }

    return band_descriptions.get(band_score, {
        "Skill Level": "Unknown",
        "Description": "No description available for this band score."
    })
